"""Photo message handler with Codex CLI vision analysis."""

from __future__ import annotations

import asyncio
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

_album_ack_tasks: dict[tuple[int, str], asyncio.Task[None]] = {}


async def _analyze_image(image_path: str, caption: str | None = None) -> str | None:
    """Analyze an image with the configured Codex CLI model."""
    try:
        settings = get_settings()
        processor = AgentProcessor(settings.vault_path, settings.todoist_api_key)
        return await asyncio.to_thread(processor.analyze_image, image_path, caption)
    except Exception:
        logger.exception("Vision analysis failed")
        return None


async def _send_album_ack_later(message: Message, key: tuple[int, str]) -> None:
    """Send one acknowledgement for a Telegram media group."""
    try:
        await asyncio.sleep(1.5)
        await message.answer("Фото получил. Что с ними сделать?")
    except asyncio.CancelledError:
        raise
    except Exception:
        logger.exception("Failed to send album acknowledgement")
    finally:
        _album_ack_tasks.pop(key, None)


async def _acknowledge_photo(message: Message) -> None:
    """Ask what to do with received photo(s) without dumping vision text."""
    media_group_id = message.media_group_id
    if not media_group_id:
        await message.answer("Фото получил. Что с ним сделать?")
        return

    key = (message.chat.id, media_group_id)
    existing = _album_ack_tasks.pop(key, None)
    if existing:
        existing.cancel()

    _album_ack_tasks[key] = asyncio.create_task(_send_album_ack_later(message, key))


@router.message(lambda m: m.photo is not None)
async def handle_photo(message: Message, bot: Bot) -> None:
    """Handle photo messages: save them and keep vision text out of chat."""
    if not message.photo or not message.from_user:
        return

    settings = get_settings()
    storage = VaultStorage(settings.vault_path)
    scope = get_session_scope(message)
    photo = message.photo[-1]

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

        work_context = is_work_chat(message, settings)
        if work_context:
            logger.info("Saved group photo without reply in chat %s", message.chat.id)
            return

        await _acknowledge_photo(message)

        logger.info("Photo saved and analyzed: %s", relative_path)

    except Exception as exc:
        logger.exception("Error processing photo")
        await message.answer(f"Ошибка: {exc}")
