"""Photo message handler with Codex CLI vision analysis."""

from __future__ import annotations

import asyncio
import contextlib
import logging
from datetime import datetime
from pathlib import Path

from aiogram import Bot, Router
from aiogram.types import Message

from d_brain.bot.chat_context import (
    build_msg_type,
    get_session_scope,
    is_work_chat,
)
from d_brain.bot.typing_indicator import keep_typing
from d_brain.config import get_settings
from d_brain.services.processor import AgentProcessor
from d_brain.services.session import SessionStore
from d_brain.services.storage import VaultStorage

router = Router(name="photo")
logger = logging.getLogger(__name__)

# Фото одного чата — одна пачка («альбом»), пока пауза между соседними не длиннее этого времени.
# Общий media_group_id Telegram даёт только альбому, присланному разом; фото по одному его не имеют.
BATCH_WINDOW_SECONDS = 10.0


class _Batch:
    """Фото одного чата, пришедшие подряд: на всю пачку уходит один ответ."""

    def __init__(self, scope: int | str, message: Message) -> None:
        self.scope = scope
        self.message = message  # последнее пришедшее фото: через него уходит ответ
        self.last_arrival = asyncio.get_running_loop().time()
        self.working = 0  # фото, которые ещё скачиваются и разбираются
        self.saved: dict[int, str] = {}  # номер сообщения -> путь сохранённого файла
        self.changed = asyncio.Event()


_batches: dict[int, _Batch] = {}  # chat_id -> пачка, которая ещё принимает фото или ждёт ответа
_batch_tasks: set[asyncio.Task[None]] = set()


async def _analyze_image(image_path: str, caption: str | None = None) -> str | None:
    """Analyze an image with the configured Codex CLI model."""
    try:
        settings = get_settings()
        processor = AgentProcessor(settings.vault_path, settings.todoist_api_key)
        return await asyncio.to_thread(processor.analyze_image, image_path, caption)
    except Exception:
        logger.exception("Vision analysis failed")
        return None


def _join_batch(message: Message, scope: int | str) -> _Batch:
    """Фото занимает место в пачке при получении: скачивание и разбор идут дольше, чем приходит следующее."""
    now = asyncio.get_running_loop().time()
    batch = _batches.get(message.chat.id)
    if batch is None or now - batch.last_arrival >= BATCH_WINDOW_SECONDS:
        batch = _Batch(scope, message)
        _batches[message.chat.id] = batch
        task = asyncio.create_task(_answer_when_quiet(message.chat.id, batch))
        _batch_tasks.add(task)
        task.add_done_callback(_batch_tasks.discard)
    batch.message = message
    batch.last_arrival = now
    batch.working += 1
    batch.changed.set()
    return batch


def _leave_batch(batch: _Batch, message_id: int, saved_path: str | None) -> None:
    batch.working -= 1
    if saved_path:
        batch.saved[message_id] = saved_path
    batch.changed.set()


async def _answer_when_quiet(chat_id: int, batch: _Batch) -> None:
    """Ответить один раз: новые фото перестали приходить, и все пришедшие уже сохранены."""
    loop = asyncio.get_running_loop()
    try:
        while True:
            pause = loop.time() - batch.last_arrival
            if not batch.working and pause >= BATCH_WINDOW_SECONDS:
                break
            batch.changed.clear()
            # Пока фото разбираются, ждём их конца; когда все готовы — остаток паузы.
            timeout = None if batch.working else BATCH_WINDOW_SECONDS - pause
            with contextlib.suppress(TimeoutError):
                await asyncio.wait_for(batch.changed.wait(), timeout)
    finally:
        # Закрыть до любого ожидания: следующее фото начнёт новую пачку, а не потеряется в этой.
        if _batches.get(chat_id) is batch:
            del _batches[chat_id]

    paths = [batch.saved[number] for number in sorted(batch.saved)]
    if not paths:
        return  # ни одно фото не сохранилось: об ошибках уже сказали по каждому
    if len(paths) == 1:
        text = "Фото получил. Что с ним сделать?"
    else:
        text = f"Фото получил, всего {len(paths)}. Что с ними сделать?"
        # Модель видит в журнале каждое фото отдельной строкой; эта строка даёт ей пачку целиком.
        try:
            vault = get_settings().vault_path
            SessionStore(vault).append(
                batch.scope,
                "photo_batch",
                text=(
                    f"Пачка из {len(paths)} фото, присланных подряд (пауза не больше "
                    f"{BATCH_WINDOW_SECONDS:g} с). Файлы по порядку, от корня проекта: "
                    + ", ".join(f"{Path(vault).name}/{path}" for path in paths)
                ),
                paths=paths,
                chat_id=batch.message.chat.id,
                chat_title=batch.message.chat.title,
            )
        except Exception:
            logger.exception("Failed to record photo batch")
    try:
        await batch.message.answer(text)
    except Exception:
        logger.exception("Failed to acknowledge photo batch")


@router.message(lambda m: m.photo is not None)
async def handle_photo(message: Message, bot: Bot) -> None:
    """Handle photo messages: save them and keep vision text out of chat."""
    if not message.photo or not message.from_user:
        return

    settings = get_settings()
    storage = VaultStorage(settings.vault_path)
    scope = get_session_scope(message)
    photo = message.photo[-1]
    work_context = is_work_chat(message, settings)
    batch = None if work_context else _join_batch(message, scope)
    saved_path = None

    try:
        file = await bot.get_file(photo.file_id)
        if not file.file_path:
            await message.answer("Не удалось скачать фото.")
            return

        file_bytes = await bot.download_file(file.file_path)
        if not file_bytes:
            await message.answer("Не удалось скачать фото.")
            return

        timestamp = datetime.fromtimestamp(message.date.timestamp())
        photo_bytes = file_bytes.read()

        extension = "jpg"
        if "." in file.file_path:
            extension = file.file_path.rsplit(".", 1)[-1]

        relative_path = storage.save_attachment(
            photo_bytes,
            timestamp.date(),
            timestamp,
            extension,
        )

        absolute_image_path = str((Path(settings.vault_path) / relative_path).resolve())

        async with keep_typing(message.chat):
            description = await _analyze_image(absolute_image_path, message.caption)

        content = f"![[{relative_path}]]"
        if message.caption:
            content += f"\n\n{message.caption}"
        if description:
            content += f"\n\n> [!note] Vision\n> {description.replace(chr(10), chr(10) + '> ')}"

        storage.append_to_daily(content, timestamp, build_msg_type(message, "[photo]"))

        session = SessionStore(settings.vault_path)
        session.append(
            scope,
            "photo",
            path=relative_path,
            caption=message.caption,
            text=description,
            msg_id=message.message_id,
            media_group_id=message.media_group_id,
            chat_id=message.chat.id,
            chat_title=message.chat.title,
        )

        if work_context:
            logger.info("Saved group photo without reply in chat %s", message.chat.id)
            return

        saved_path = relative_path
        logger.info("Photo saved and analyzed: %s", relative_path)

    except Exception as exc:
        logger.exception("Error processing photo")
        await message.answer(f"Ошибка: {exc}")
    finally:
        if batch is not None:
            _leave_batch(batch, message.message_id, saved_path)
