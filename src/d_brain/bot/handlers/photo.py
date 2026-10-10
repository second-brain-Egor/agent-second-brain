"""Photo message handler with Codex CLI vision analysis."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from pathlib import Path

from aiogram import Bot, Router
from aiogram.types import Message

from d_brain.bot import uploads
from d_brain.bot.chat_context import (
    build_msg_type,
    get_session_scope,
    is_work_chat,
)
from d_brain.bot.typing_indicator import keep_typing
from d_brain.config import get_settings
from d_brain.services.documents import DocumentStore, folder_label
from d_brain.services.processor import AgentProcessor
from d_brain.services.session import SessionStore
from d_brain.services.storage import VaultStorage

router = Router(name="photo")
logger = logging.getLogger(__name__)


def _save_to_project(folder: Path, vault: Path, data: bytes, timestamp: datetime, extension: str) -> str:
    """Фото при выбранном проекте ложится прямо в его папку (Егор, 8 октября 2026)."""
    folder.mkdir(parents=True, exist_ok=True)
    stem = f"фото {timestamp:%Y-%m-%d %H-%M-%S}"
    path = folder / f"{stem}.{extension}"
    counter = 2
    while path.exists():
        path = folder / f"{stem} ({counter}).{extension}"
        counter += 1
    path.write_bytes(data)
    return path.relative_to(vault).as_posix()


async def _analyze_image(image_path: str, caption: str | None = None) -> str | None:
    """Analyze an image with the configured Codex CLI model."""
    try:
        settings = get_settings()
        processor = AgentProcessor(settings.vault_path, settings.todoist_api_key)
        return await asyncio.to_thread(processor.analyze_image, image_path, caption)
    except Exception:
        logger.exception("Vision analysis failed")
        return None


@router.message(lambda m: m.photo is not None)
async def handle_photo(message: Message, bot: Bot) -> None:
    """Save the photo; the batch of attachments then goes to the assistant (bot/uploads.py)."""
    if not message.photo or not message.from_user:
        return

    settings = get_settings()
    scope = get_session_scope(message)
    if is_work_chat(message, settings):
        await _save_photo(message, bot, settings, scope, work_context=True)
        return
    await uploads.collect(message, scope, lambda: _save_photo(message, bot, settings, scope, work_context=False))


async def _save_photo(message: Message, bot: Bot, settings, scope, work_context: bool) -> dict | None:
    """Save and describe one photo; returns it for the assistant (None in work chats or on failure)."""
    storage = VaultStorage(settings.vault_path)
    photo = message.photo[-1]
    try:
        file = await bot.get_file(photo.file_id)
        if not file.file_path:
            await message.answer("Не удалось скачать фото.")
            return None

        file_bytes = await bot.download_file(file.file_path)
        if not file_bytes:
            await message.answer("Не удалось скачать фото.")
            return None

        timestamp = datetime.fromtimestamp(message.date.timestamp())
        photo_bytes = file_bytes.read()

        extension = "jpg"
        if "." in file.file_path:
            extension = file.file_path.rsplit(".", 1)[-1]

        store = DocumentStore(settings.vault_path)
        project_folder = None if work_context else store.active_folder(scope)
        if project_folder:
            relative_path = _save_to_project(
                project_folder, store.vault, photo_bytes, timestamp, extension
            )
            store.record_placement(scope, relative_path, "photo")
            store.touch_active(scope)
            where = "бот положил в текущий проект: " + folder_label(relative_path)
        elif not work_context:
            # Егор, 10 октября 2026: без проекта фото ждёт во входящих, как документ, и помощник
            # кладёт его по теме (scripts/project_context.py place), а не во вложения по дате.
            doc, fresh = store.receive(
                photo_bytes, f"фото {timestamp:%Y-%m-%d %H-%M-%S}.{extension}", scope,
                message.chat.id, message.message_id, message.caption or "",
            )
            if not fresh:
                return None  # Telegram прислал то же сообщение повторно
            relative_path = doc["path"]
            where = ("такой же снимок уже сохранён раньше, лежит в " + folder_label(relative_path)
                     if doc["state"] == "ready" else "во входящих, место ещё не выбрано")
        else:
            relative_path = storage.save_attachment(
                photo_bytes,
                timestamp.date(),
                timestamp,
                extension,
            )
            where = "бот положил во вложения дня"

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
            return None

        logger.info("Photo saved and analyzed: %s", relative_path)
        return {"kind": "photo", "path": relative_path, "where": where, "caption": message.caption}

    except Exception as exc:
        logger.exception("Error processing photo")
        await message.answer(f"Ошибка: {exc}")
        return None
