"""Video and video note message handlers."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime

from aiogram import Bot, Router
from aiogram.types import Message

from d_brain.bot.chat_context import build_msg_type, get_session_scope, is_work_chat
from d_brain.config import get_settings
from d_brain.services.session import SessionStore
from d_brain.services.storage import VaultStorage

router = Router(name="video")
logger = logging.getLogger(__name__)

_album_ack_tasks: dict[tuple[int, str], asyncio.Task[None]] = {}


def _extension_from_path(file_path: str | None, fallback: str = "mp4") -> str:
    if file_path and "." in file_path:
        extension = file_path.rsplit(".", 1)[-1].strip().lower()
        if extension:
            return extension
    return fallback


async def _send_album_ack_later(message: Message, key: tuple[int, str]) -> None:
    try:
        await asyncio.sleep(1.5)
        await message.answer("Видео получил. Что с ними сделать?")
    except asyncio.CancelledError:
        raise
    except Exception:
        logger.exception("Failed to send video album acknowledgement")
    finally:
        _album_ack_tasks.pop(key, None)


async def _acknowledge_video(message: Message, *, is_video_note: bool) -> None:
    if is_video_note:
        await message.answer("Видеосообщение получил. Что с ним сделать?")
        return

    media_group_id = message.media_group_id
    if not media_group_id:
        await message.answer("Видео получил. Что с ним сделать?")
        return

    key = (message.chat.id, media_group_id)
    existing = _album_ack_tasks.pop(key, None)
    if existing:
        existing.cancel()

    _album_ack_tasks[key] = asyncio.create_task(_send_album_ack_later(message, key))


@router.message(lambda m: m.video is not None or m.video_note is not None)
async def handle_video(message: Message, bot: Bot) -> None:
    """Save incoming videos and round video notes to the vault."""
    if not message.from_user:
        return

    media = message.video or message.video_note
    if media is None:
        return

    settings = get_settings()
    storage = VaultStorage(settings.vault_path)
    scope = get_session_scope(message)
    is_video_note = message.video_note is not None

    try:
        file = await bot.get_file(media.file_id)
        if not file.file_path:
            await message.answer("Не удалось скачать видео.")
            return

        file_obj = await bot.download_file(file.file_path)
        if not file_obj:
            await message.answer("Не удалось скачать видео.")
            return

        timestamp = datetime.fromtimestamp(message.date.timestamp())
        extension = _extension_from_path(file.file_path)
        prefix = "video-note" if is_video_note else "video"
        filename = f"{prefix}-{timestamp.strftime('%H%M%S')}.{extension}"
        relative_path = storage.save_document(file_obj.read(), timestamp.date(), filename)

        content = f"![[{relative_path}]]"
        if message.caption:
            content += f"\n\n{message.caption}"

        daily_type = "[video_note]" if is_video_note else "[video]"
        session_type = "video_note" if is_video_note else "video"
        storage.append_to_daily(content, timestamp, build_msg_type(message, daily_type))

        session = SessionStore(settings.vault_path)
        session.append(
            scope,
            session_type,
            path=relative_path,
            caption=message.caption,
            duration=getattr(media, "duration", None),
            msg_id=message.message_id,
            media_group_id=message.media_group_id,
            chat_id=message.chat.id,
            chat_title=message.chat.title,
        )

        if is_work_chat(message, settings):
            logger.info("Saved group video without reply in chat %s", message.chat.id)
            return

        await _acknowledge_video(message, is_video_note=is_video_note)
        logger.info("%s saved: %s", session_type, relative_path)

    except Exception as exc:
        logger.exception("Error processing video")
        await message.answer(f"Ошибка при обработке видео: {exc}", parse_mode=None)
