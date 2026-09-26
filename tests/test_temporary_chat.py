"""Privacy boundary: no durable inbox, history, task log, or attachment copies."""
import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from d_brain.bot import temporary_chat as module
from d_brain.services import temporary_reply
from d_brain.services.execution import Execution, execution_context, run_bounded
from d_brain.services.temporary_chat import enabled, mode_path, set_enabled
from d_brain.config import Settings


def message(text=None, number=1, **values):
    args = dict(text=text, caption=None, message_id=number,
                date=datetime.now(timezone.utc), chat=SimpleNamespace(id=7, type='private', title=None),
                from_user=SimpleNamespace(id=7), voice=None, photo=None, document=None,
                video=None, video_note=None, audio=None, media_group_id=None,
                answer=AsyncMock())
    args.update(values)
    return SimpleNamespace(**args)


@pytest.fixture
def chat(tmp_path, monkeypatch):
    settings = Settings(_env_file=None, vault_path=tmp_path/'vault', temporary_chat_user_id=7,
                        telegram_bot_token='test', deepgram_api_key='test', allowed_user_ids=[7])
    jobs = SimpleNamespace(stop_scope=AsyncMock())
    instance = module.TemporaryChat(settings, jobs)
    monkeypatch.setattr(module, 'get_settings', lambda: settings)
    monkeypatch.setattr('d_brain.bot.keyboards.get_settings', lambda: settings)
    from contextlib import asynccontextmanager
    @asynccontextmanager
    async def typing(*args):
        yield
    monkeypatch.setattr(module, 'keep_typing', typing)
    set_enabled(settings, True)
    return instance


async def deliver(chat, msg, data=None, handler=None):
    handler = handler or AsyncMock()
    await chat(handler, SimpleNamespace(message=msg), data or {'bot': object()})
    return handler


async def drain(chat):
    await asyncio.gather(*list(chat.tasks))
    await asyncio.sleep(0)


def durable_files(chat):
    return [p for p in chat.settings.vault_path.rglob('*') if p.is_file()]


async def test_text_and_followup_never_enter_normal_pipeline(chat, monkeypatch):
    seen = []
    def reply(settings, workspace, history, images):
        seen.append(history)
        assert str(workspace).startswith('/dev/shm/')
        return 'Временный ответ'
    monkeypatch.setattr(module, 'reply', reply)
    handler = await deliver(chat, message('Мой частный вопрос'))
    await drain(chat)
    await deliver(chat, message('Почему?', 2))
    await drain(chat)
    handler.assert_not_called()
    assert [e['role'] for e in seen[1]] == ['user', 'assistant', 'user']
    assert durable_files(chat) == [mode_path(chat.settings)]
    assert json.loads(mode_path(chat.settings).read_text()) == {'enabled': True}


async def test_exit_clears_context_and_does_not_replay(chat, monkeypatch):
    monkeypatch.setattr(module, 'reply', lambda *a: 'Ответ')
    await deliver(chat, message('Секрет'))
    await drain(chat)
    switch = message('💬 Обычный чат', 2)
    await deliver(chat, switch)
    assert not enabled(chat.settings) and chat.history == [] and chat.images == []
    labels = [b.text for row in switch.answer.call_args.kwargs['reply_markup'].keyboard for b in row]
    assert '🕶 Временный чат' in labels
    normal = await deliver(chat, message('Обычный вопрос', 3))
    normal.assert_awaited_once()
    switch_back = message('🕶 Временный чат', 4)
    await deliver(chat, switch_back)
    assert enabled(chat.settings) and chat.history == []
    labels = [b.text for row in switch_back.answer.call_args.kwargs['reply_markup'].keyboard for b in row]
    assert '💬 Обычный чат' in labels


async def test_restart_keeps_only_mode(chat):
    chat.history.append({'text': 'Секрет'})
    restored = module.TemporaryChat(chat.settings, chat.jobs)
    assert enabled(restored.settings) and restored.history == []
    await chat.close()
    assert enabled(chat.settings) and not chat.history


async def test_stop_and_toggle_interrupt_running_model(chat, monkeypatch):
    started = asyncio.Event()
    def reply(settings, workspace, history, images):
        from d_brain.services.execution import CURRENT_EXECUTION
        execution = CURRENT_EXECUTION.get()
        loop.call_soon_threadsafe(started.set)
        execution.cancelled.wait(5)
        execution.check()
    loop = asyncio.get_running_loop()
    monkeypatch.setattr(module, 'reply', reply)
    first = message('Долгий запрос')
    await deliver(chat, first)
    await asyncio.wait_for(started.wait(), 2)
    await asyncio.wait_for(deliver(chat, message('🕶 Временный чат', 2)), 2)
    assert not chat.tasks and not chat.history
    first.answer.assert_not_called()
    assert durable_files(chat) == [mode_path(chat.settings)]


async def test_voice_stop_bypasses_model_queue(chat, monkeypatch):
    started = asyncio.Event()
    loop = asyncio.get_running_loop()
    def reply(*args):
        from d_brain.services.execution import CURRENT_EXECUTION
        execution = CURRENT_EXECUTION.get()
        loop.call_soon_threadsafe(started.set)
        execution.cancelled.wait(5)
        execution.check()
    monkeypatch.setattr(module, 'reply', reply)
    monkeypatch.setattr('d_brain.bot.handlers.voice._transcribe_voice', AsyncMock(return_value='Стоп.'))
    await deliver(chat, message('Работай'))
    await asyncio.wait_for(started.wait(), 2)
    speech = message(number=2, voice=SimpleNamespace(file_id='voice'))
    await deliver(chat, speech)
    await asyncio.wait_for(drain(chat), 2)
    assert speech.answer.call_args.args[0] == 'Остановил.'
    assert durable_files(chat) == [mode_path(chat.settings)]


async def test_owner_private_chat_only_and_controls(chat):
    for msg in [message('Чужой', from_user=SimpleNamespace(id=8)),
                message('Группа', chat=SimpleNamespace(type='group')),
                message('💬 Обсудить'), message('🛠 Работа'), message('🤖 Модель'),
                message('🧠 Claude'), message('⚙️ Обработать')]:
        normal = await deliver(chat, msg)
        normal.assert_awaited_once()
    # Bot callback buttons also bypass temporary conversation storage.
    callback = AsyncMock()
    await chat(callback, SimpleNamespace(message=None), {})
    callback.assert_awaited_once()
    assert chat.history == []


async def test_album_all_files_in_ram_and_followup_context(chat, monkeypatch):
    paths, calls = [], []
    async def download(media, destination):
        destination.write_bytes(b'image-data')
        paths.append(destination)
    bot = SimpleNamespace(download=AsyncMock(side_effect=download))
    def reply(settings, workspace, history, images):
        calls.append(list(images))
        assert all(Path(p).read_bytes() == b'image-data' for p in images)
        return 'Получил'
    monkeypatch.setattr(module, 'reply', reply)
    for number in [1, 2, 3]:
        await deliver(chat, message(number=number, photo=[SimpleNamespace()], media_group_id='album'), {'bot': bot})
    await drain(chat)
    assert len(calls) == 1 and len(calls[0]) == 3
    assert not any(p.exists() for p in paths + [Path(p) for p in calls[0]])
    await deliver(chat, message('Что на втором фото?', 4))
    await drain(chat)
    assert len(calls[1]) == 3
    assert durable_files(chat) == [mode_path(chat.settings)]
    await deliver(chat, message('🕶 Временный чат', 5))
    assert not chat.images


async def test_document_extraction_and_error_do_not_persist(chat, monkeypatch, caplog):
    paths = []
    async def download(media, destination):
        destination.write_text('Закрытый текст документа')
        paths.append(destination)
    def reply(settings, workspace, history, images):
        assert 'Закрытый текст документа' in history[-1]['text']
        raise RuntimeError('Закрытый текст документа')
    monkeypatch.setattr(module, 'reply', reply)
    bot = SimpleNamespace(download=AsyncMock(side_effect=download))
    doc = message(document=SimpleNamespace(file_name='private.txt'))
    await deliver(chat, doc, {'bot': bot})
    await drain(chat)
    assert not any(p.exists() for p in paths)
    assert 'Закрытый текст документа' not in caplog.text
    assert durable_files(chat) == [mode_path(chat.settings)]
    assert 'не сохранена' in doc.answer.call_args.args[0]


def test_nonpersistent_execution_has_no_task_or_event_files(tmp_path):
    execution = Execution(tmp_path, request='private request', persistent=False)
    with execution_context(execution):
        result = run_bounded([sys.executable, '-c', 'print("private output")'],
                             input='private input', cwd=tmp_path,
                             env=os.environ.copy(), backend='command')
    assert result.stdout.strip() == 'private output'
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize('backend', ['codex', 'claude'])
def test_model_uses_ephemeral_flags_and_selected_model(chat, monkeypatch, tmp_path, backend):
    settings = chat.settings.model_copy(update={'ai_backend': backend, 'codex_reasoning_effort': 'xhigh'})
    monkeypatch.setattr('d_brain.config.get_settings', lambda: settings)
    monkeypatch.setattr('d_brain.services.processor.AgentProcessor._get_codex_bin', lambda _: 'codex')
    monkeypatch.setattr('d_brain.services.processor.AgentProcessor._get_claude_bin', lambda _: 'claude')
    result = ('{"type":"item.completed","item":{"type":"agent_message","text":"Ответ"}}'
              if backend == 'codex' else '{"type":"result","result":"Ответ"}')
    run = Mock(return_value=SimpleNamespace(returncode=0, stdout=result))
    monkeypatch.setattr(temporary_reply, 'run_bounded', run)
    assert temporary_reply.reply(settings, tmp_path, [{'text': 'Вопрос'}], []) == 'Ответ'
    cmd = run.call_args.args[0]
    assert ('--ephemeral' if backend == 'codex' else '--no-session-persistence') in cmd
    assert run.call_args.kwargs['cwd'] == tmp_path
    if backend == 'codex':
        assert 'model_reasoning_effort="xhigh"' in cmd
        assert '--ignore-user-config' in cmd
        assert 'read-only' in cmd
    else:
        assert '--safe-mode' in cmd
        assert 'Read,WebSearch,WebFetch' in cmd


def test_corrupt_flag_fails_closed(chat):
    mode_path(chat.settings).write_text('damaged')
    assert enabled(chat.settings)


async def test_real_dispatcher_intercepts_before_durable_inbox(chat, monkeypatch):
    from aiogram import Bot, Dispatcher, Router
    from aiogram.types import Update, Message, Chat, User
    from d_brain.bot.request_jobs import RequestJobs
    from d_brain.bot.main import create_auth_middleware
    bot = Bot('123456:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijk')
    dp, router = Dispatcher(), Router()
    ordinary = []
    @router.message()
    async def handler(message):
        ordinary.append(message.text)
    dp.include_router(router)
    jobs = RequestJobs(chat.settings)
    chat.jobs = jobs
    dp.update.middleware(create_auth_middleware(chat.settings))
    dp.update.middleware(chat)
    dp.update.middleware(jobs)
    monkeypatch.setattr(Message, 'answer', AsyncMock())
    monkeypatch.setattr(module, 'reply', lambda *a: 'Ответ')
    def update(text, number):
        return Update(update_id=number, message=Message(message_id=number,
            date=datetime.now(timezone.utc), text=text,
            chat=Chat(id=7, type='private'), from_user=User(id=7, is_bot=False, first_name='Test')))
    try:
        await dp.feed_update(bot, update('Приватный текст', 1))
        await drain(chat)
        assert ordinary == []
        with jobs.inbox.connect() as db:
            assert db.execute('SELECT COUNT(*) FROM inbox').fetchone()[0] == 0
        await dp.feed_update(bot, update('🕶 Временный чат', 2))
        await dp.feed_update(bot, update('Обычный текст', 3))
        await asyncio.gather(*list(jobs.tasks))
        assert ordinary == ['Обычный текст']
        with jobs.inbox.connect() as db:
            rows = db.execute('SELECT payload FROM inbox').fetchall()
            assert len(rows) == 1 and 'Приватный' not in rows[0][0]
    finally:
        await chat.close()
        await jobs.close()
        await bot.session.close()


def test_disabled_instance_keeps_weekly_keyboard(chat, monkeypatch):
    from d_brain.bot.keyboards import get_main_keyboard
    monkeypatch.setattr('d_brain.bot.keyboards.get_settings', lambda: chat.settings.model_copy(update={'temporary_chat_user_id': 0}))
    labels = [b.text for row in get_main_keyboard(7).keyboard for b in row]
    assert '📅 Неделя' in labels and '🕶 Временный чат' not in labels
