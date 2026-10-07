"""Фото, пришедшие подряд, — одна пачка: один ответ и одна строка с файлами в журнале.

Модель и Telegram не вызываются: разбор фото и скачивание подменены. Окно пачки сокращено до долей секунды.
"""
import asyncio
import io
import json
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from d_brain.bot.handlers import photo as module
from d_brain.config import Settings

WINDOW = 0.3


def photo_message(number, *, media_group_id=None, chat_id=7, chat_type='private'):
    return SimpleNamespace(
        message_id=number, photo=[SimpleNamespace(file_id=f'file-{number}')], caption=None,
        date=datetime.now(timezone.utc), media_group_id=media_group_id,
        from_user=SimpleNamespace(id=7),
        chat=SimpleNamespace(id=chat_id, type=chat_type, title=None),
        answer=AsyncMock())


def fake_bot(*, broken=()):
    async def download_file(path):
        return None if path in broken else io.BytesIO(b'jpeg')

    async def get_file(file_id):
        return SimpleNamespace(file_path=f'photos/{file_id}.jpg')

    return SimpleNamespace(get_file=get_file, download_file=download_file)


@pytest.fixture
def setup(tmp_path, monkeypatch):
    (tmp_path / 'vault').mkdir()
    settings = Settings(_env_file=None, vault_path=tmp_path / 'vault', telegram_bot_token='test',
                        deepgram_api_key='test', allowed_user_ids=[7], work_chat_ids=[],
                        treat_all_group_chats_as_work=True)
    monkeypatch.setattr(module, 'get_settings', lambda: settings)
    monkeypatch.setattr(module, 'BATCH_WINDOW_SECONDS', WINDOW)

    @asynccontextmanager
    async def typing(*args):
        yield
    monkeypatch.setattr(module, 'keep_typing', typing)

    delays = []

    async def analyze(path, caption=None):
        await asyncio.sleep(delays.pop(0) if delays else 0)
        return 'описание'
    monkeypatch.setattr(module, '_analyze_image', analyze)
    module._batches.clear()
    yield SimpleNamespace(settings=settings, delays=delays)
    module._batches.clear()


async def send(messages, bot, *, gap=0.05):
    """Фото приходят по одному с паузой gap; возвращается, когда обработаны все."""
    tasks = []
    for number, message in enumerate(messages):
        if number:
            await asyncio.sleep(gap)
        tasks.append(asyncio.create_task(module.handle_photo(message, bot)))
    await asyncio.gather(*tasks)


async def settle(seconds=WINDOW + 0.4):
    await asyncio.sleep(seconds)


def acks(*messages):
    return [call.args[0] for message in messages for call in message.answer.call_args_list]


def batch_entries(setup):
    path = setup.settings.vault_path / '.sessions' / '7.jsonl'
    if not path.exists():
        return []
    entries = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    return [entry for entry in entries if entry['type'] == 'photo_batch']


async def test_photos_sent_one_by_one_get_one_reply_with_all_files(setup):
    messages = [photo_message(number) for number in (11, 12, 13)]
    await send(messages, fake_bot())
    assert acks(*messages) == []  # окно ещё не прошло: пачка может вырасти
    await settle()
    assert acks(*messages) == ['Фото получил, всего 3. Что с ними сделать?']
    [entry] = batch_entries(setup)
    assert len(entry['paths']) == 3
    assert all(path in entry['text'] for path in entry['paths'])
    assert not module._batches


async def test_batch_lists_files_in_arrival_order_not_in_completion_order(setup):
    setup.delays.extend([0.3, 0.0, 0.1])  # первое фото разбирается дольше всех
    messages = [photo_message(number) for number in (21, 22, 23)]
    await send(messages, fake_bot(), gap=0.0)
    await settle()
    lines = (setup.settings.vault_path / '.sessions' / '7.jsonl').read_text().splitlines()
    saved = {entry['msg_id']: entry['path']
             for entry in map(json.loads, lines) if entry['type'] == 'photo'}
    [entry] = batch_entries(setup)
    assert entry['paths'] == [saved[21], saved[22], saved[23]]
    assert all((setup.settings.vault_path / path).exists() for path in entry['paths'])


async def test_pause_longer_than_window_starts_new_batch(setup):
    first, second = photo_message(31), photo_message(32)
    bot = fake_bot()
    await send([first], bot)
    await settle()
    await send([second], bot)
    await settle()
    assert acks(first) == ['Фото получил. Что с ним сделать?']
    assert acks(second) == ['Фото получил. Что с ним сделать?']
    assert batch_entries(setup) == []  # отдельное фото строки пачки не получает


async def test_slow_analysis_does_not_split_batch_or_reply_early(setup):
    setup.delays.extend([0.9, 0.9, 0.9])  # разбор дольше окна
    messages = [photo_message(number) for number in (41, 42, 43)]
    task = asyncio.create_task(send(messages, fake_bot()))
    await asyncio.sleep(WINDOW + 0.4)  # окно после последнего фото уже прошло, фото ещё разбираются
    assert acks(*messages) == []
    await task
    await settle()
    assert acks(*messages) == ['Фото получил, всего 3. Что с ними сделать?']


async def test_real_album_with_uneven_analysis_time_gets_one_reply(setup):
    setup.delays.extend([0.0, 0.5, 1.0])  # раньше ответ уходил по каждому закончившему
    messages = [photo_message(number, media_group_id='album') for number in (51, 52, 53)]
    await send(messages, fake_bot(), gap=0.0)
    await settle()
    assert acks(*messages) == ['Фото получил, всего 3. Что с ними сделать?']


async def test_photo_after_pause_while_previous_batch_still_working_is_new_batch(setup):
    setup.delays.extend([0.8, 0.0])
    first, second = photo_message(61), photo_message(62)
    bot = fake_bot()
    task = asyncio.create_task(send([first, second], bot, gap=WINDOW + 0.2))
    await task
    await settle()
    assert acks(first) == ['Фото получил. Что с ним сделать?']
    assert acks(second) == ['Фото получил. Что с ним сделать?']
    assert not module._batches


async def test_failed_photo_is_not_counted_and_all_failed_means_no_reply(setup):
    good, bad = photo_message(71), photo_message(72)
    await send([good, bad], fake_bot(broken={'photos/file-72.jpg'}))
    await settle()
    # Об ошибке сказано сразу, ответ по пачке — один и считает только сохранённое.
    assert acks(good, bad) == ['Не удалось скачать фото.', 'Фото получил. Что с ним сделать?']
    only_bad = photo_message(73)
    await send([only_bad], fake_bot(broken={'photos/file-73.jpg'}))
    await settle()
    assert acks(only_bad) == ['Не удалось скачать фото.']
    assert not module._batches


async def test_different_chats_do_not_share_a_batch(setup):
    mine, other = photo_message(81), photo_message(82, chat_id=8)
    await asyncio.gather(module.handle_photo(mine, fake_bot()), module.handle_photo(other, fake_bot()))
    await settle()
    assert acks(mine) == ['Фото получил. Что с ним сделать?']
    assert acks(other) == ['Фото получил. Что с ним сделать?']


async def test_work_group_photos_are_saved_without_reply_or_batch(setup):
    message = photo_message(91, chat_id=-100, chat_type='supergroup')
    await module.handle_photo(message, fake_bot())
    assert not module._batches
    await settle()
    assert acks(message) == []
    assert any((setup.settings.vault_path / 'attachments').rglob('img-*.jpg'))


async def test_cancelled_photo_releases_its_place_in_the_batch(setup):
    setup.delays.extend([5.0, 0.0])
    stopped, kept = photo_message(101), photo_message(102)
    bot = fake_bot()
    first = asyncio.create_task(module.handle_photo(stopped, bot))
    await asyncio.sleep(0.05)
    second = asyncio.create_task(module.handle_photo(kept, bot))
    await second
    first.cancel()  # «стоп»
    await asyncio.gather(first, return_exceptions=True)
    await settle()
    assert acks(stopped, kept) == ['Фото получил. Что с ним сделать?']
    assert not module._batches


async def test_journal_failure_does_not_block_reply(setup, monkeypatch):
    original = module.SessionStore.append

    def append(self, scope, entry_type, **data):
        if entry_type == 'photo_batch':
            raise OSError('disk full')
        return original(self, scope, entry_type, **data)
    monkeypatch.setattr(module.SessionStore, 'append', append)
    messages = [photo_message(number) for number in (111, 112)]
    await send(messages, fake_bot())
    await settle()
    assert acks(*messages) == ['Фото получил, всего 2. Что с ними сделать?']
