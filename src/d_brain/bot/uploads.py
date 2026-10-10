"""Файлы и фото одного чата, присланные подряд, — одна пачка и один ответ помощника.

Егор, 9 октября 2026: бот сам не решает, куда деть присланное, и не задаёт шаблонных вопросов
(«Куда сохранить?», «Что с ним сделать?»). Он только сохраняет вложения и передаёт пачку помощнику
вместе с разговором: тот смотрит, что прислано, и действует по контексту. О папке спрашивает,
только если вложение из другой области и место не понять.

Пачка: пауза между соседними вложениями не длиннее BATCH_WINDOW_SECONDS. Общий media_group_id
Telegram даёт только альбому, присланному разом; фото и файлы по одному его не имеют.

Место в очереди ответов (services/chat_queue.py) держит первое вложение пачки, остальные его сразу
отдают. Сообщения после пачки ждут её ответа, а написанные, пока помощник ещё не начал, попадают
в тот же ответ.
"""
from __future__ import annotations

import asyncio
import contextlib
import logging
from collections.abc import Awaitable, Callable
from pathlib import Path

from d_brain.config import get_settings
from d_brain.services.chat_queue import leave_turn
from d_brain.services.session import SessionStore

logger = logging.getLogger(__name__)

BATCH_WINDOW_SECONDS = 10.0

UPLOAD_RULES = (
    'Сначала посмотри, что прислано (открой файлы), и сверь с разговором выше. Если вложение '
    'продолжает текущую тему — ты сам его просил, обсуждали этот проект или задачу, — сразу сделай '
    'с ним то, что следует из разговора, и одной строкой скажи, куда положил; ничего не спрашивай. '
    'Подпись — это задание. Спрашивать, куда положить или что сделать, можно только если вложение '
    'из другой области и по разговору и содержимому этого не понять; тогда коротко предложи 2–3 '
    'подходящих варианта.'
)


class Batch:
    """Вложения одного чата, пришедшие подряд: на всю пачку уходит один ответ."""

    def __init__(self, scope: int | str, message) -> None:
        self.scope = scope
        self.message = message  # последнее пришедшее вложение: через него уходит ответ
        self.last_arrival = asyncio.get_running_loop().time()
        self.working = 0  # вложения, которые ещё скачиваются и разбираются
        self.items: dict[int, dict] = {}  # номер сообщения -> сохранённое вложение
        self.changed = asyncio.Event()


_batches: dict[int, Batch] = {}  # chat_id -> пачка, которая ещё принимает вложения или ждёт ответа


def join(message, scope: int | str) -> tuple[Batch, bool]:
    """Вложение занимает место в пачке при получении: скачивание и разбор идут дольше,
    чем приходит следующее. Второе значение — первое ли это вложение пачки (оно и отвечает)."""
    now = asyncio.get_running_loop().time()
    batch = _batches.get(message.chat.id)
    first = batch is None or now - batch.last_arrival >= BATCH_WINDOW_SECONDS
    if first:
        batch = Batch(scope, message)
        _batches[message.chat.id] = batch
    else:
        leave_turn()  # отвечает первое вложение пачки, это очередь чата не держит
    batch.message = message
    batch.last_arrival = now
    batch.working += 1
    batch.changed.set()
    return batch, first


def leave(batch: Batch, message_id: int, item: dict | None) -> None:
    batch.working -= 1
    if item:
        batch.items[message_id] = item
    batch.changed.set()


def _close(chat_id: int, batch: Batch) -> None:
    """Следующее вложение начнёт новую пачку, а не потеряется в этой."""
    if _batches.get(chat_id) is batch:
        del _batches[chat_id]


async def collect(message, scope: int | str, save: Callable[[], Awaitable[dict | None]]) -> None:
    """Сохранить вложение (save возвращает его описание или None) и, если оно первое в пачке,
    дождаться остальных и отдать всю пачку помощнику."""
    batch, first = join(message, scope)
    item = None
    try:
        item = await save()
    except BaseException:
        if first:
            _close(message.chat.id, batch)  # «стоп» до ответа: пачка больше не ответит
        raise
    finally:
        leave(batch, message.message_id, item)
    if first:
        await answer(batch)


async def _wait_quiet(chat_id: int, batch: Batch) -> None:
    """Новые вложения перестали приходить, и все пришедшие уже сохранены."""
    loop = asyncio.get_running_loop()
    try:
        while True:
            pause = loop.time() - batch.last_arrival
            if not batch.working and pause >= BATCH_WINDOW_SECONDS:
                break
            batch.changed.clear()
            # Пока вложения разбираются, ждём их конца; когда все готовы — остаток паузы.
            timeout = None if batch.working else BATCH_WINDOW_SECONDS - pause
            with contextlib.suppress(TimeoutError):
                await asyncio.wait_for(batch.changed.wait(), timeout)
    finally:
        _close(chat_id, batch)  # до ответа


def _line(item: dict) -> str:
    what = 'фото' if item['kind'] == 'photo' else f"файл «{item['name']}»"
    line = f"- {what}: {item['path']} ({item['where']})"
    if item.get('caption'):
        line += f"; подпись: «{item['caption']}»"
    return line


def prompt(items: list[dict]) -> str:
    """Запрос помощнику: что прислано, где лежит, и как с этим быть."""
    if len(items) == 1:
        head = 'Пользователь прислал ' + ('фото' if items[0]['kind'] == 'photo' else 'файл')
    else:
        head = f'Пользователь прислал подряд {len(items)} вложений'
    head += ' (пути от vault/):'
    return '\n'.join(['[Вложения] ' + head, *map(_line, items), UPLOAD_RULES])


def _record_photo_batch(batch: Batch, items: list[dict]) -> None:
    """Модель видит в журнале каждое фото отдельной строкой; эта строка даёт ей пачку целиком."""
    photos = [item['path'] for item in items if item['kind'] == 'photo']
    if len(photos) < 2:
        return
    try:
        vault = get_settings().vault_path
        SessionStore(vault).append(
            batch.scope,
            'photo_batch',
            text=(f'Пачка из {len(photos)} фото, присланных подряд (пауза не больше '
                  f'{BATCH_WINDOW_SECONDS:g} с). Файлы по порядку, от корня проекта: '
                  + ', '.join(f'{Path(vault).name}/{path}' for path in photos)),
            paths=photos,
            chat_id=batch.message.chat.id,
            chat_title=batch.message.chat.title,
        )
    except Exception:
        logger.exception('Failed to record photo batch')


async def answer(batch: Batch) -> None:
    """Первое вложение пачки: дождаться остальных и отдать всю пачку помощнику."""
    await _wait_quiet(batch.message.chat.id, batch)
    items = [batch.items[number] for number in sorted(batch.items)]
    if not items:
        return  # ни одно вложение не сохранилось: об ошибках уже сказали по каждому
    _record_photo_batch(batch, items)
    from d_brain.bot.handlers.text import dialog_reply
    try:
        await dialog_reply(batch.message, prompt(items), scope=batch.scope)
    except Exception:
        logger.exception('Upload reply failed')
        with contextlib.suppress(Exception):
            await batch.message.answer('Вложения сохранил, но ответить по ним не получилось. '
                                       'Напиши, что с ними сделать.', parse_mode=None)
