"""Document message handler."""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

from aiogram import Bot, Router
from aiogram.types import Message

from d_brain.bot.chat_context import build_msg_type, get_session_scope, is_work_chat
from d_brain.config import get_settings
from d_brain.services.session import SessionStore
from d_brain.services.storage import VaultStorage

router = Router(name="document")
logger = logging.getLogger(__name__)

TEXT_EXTENSIONS = {
    ".conf",
    ".csv",
    ".json",
    ".log",
    ".md",
    ".txt",
    ".yaml",
    ".yml",
}


def _read_text_preview(data: bytes, filename: str) -> str | None:
    suffix = Path(filename).suffix.lower()
    if suffix not in TEXT_EXTENSIONS:
        return None

    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        try:
            text = data.decode("cp1251")
        except UnicodeDecodeError:
            return None

    text = text.strip()
    if not text:
        return "Файл пустой."

    if len(text) > 3500:
        return text[:3500].rstrip() + "\n\n…обрезано"
    return text


@router.message(lambda m: m.document is not None)
async def handle_document(message: Message, bot: Bot) -> None:
    """Save incoming documents and preview text-like files."""
    if not message.document or not message.from_user:
        return

    settings = get_settings()
    storage = VaultStorage(settings.vault_path)
    scope = get_session_scope(message)
    timestamp = datetime.fromtimestamp(message.date.timestamp())
    filename = message.document.file_name or f"document-{message.message_id}"

    try:
        file = await bot.get_file(message.document.file_id)
        if not file.file_path:
            await message.answer("Не удалось скачать файл.")
            return

        file_obj = await bot.download_file(file.file_path)
        if not file_obj:
            await message.answer("Не удалось скачать файл.")
            return

        data = file_obj.read()
        relative_path = storage.save_document(data, timestamp.date(), filename)
        preview = _read_text_preview(data, filename)

        content = f"![[{relative_path}]]"
        if message.caption:
            content += f"\n\n{message.caption}"
        if preview:
            content += f"\n\n```text\n{preview}\n```"

        storage.append_to_daily(content, timestamp, build_msg_type(message, "[file]"))

        session = SessionStore(settings.vault_path)
        session.append(
            scope,
            "file",
            path=relative_path,
            caption=message.caption,
            text=preview,
            msg_id=message.message_id,
            chat_id=message.chat.id,
            chat_title=message.chat.title,
        )

        if is_work_chat(message, settings):
            logger.info("Saved group document without reply in chat %s", message.chat.id)
            return

        if preview:
            await message.answer(f"Файл прочитал: {filename}\n\n{preview}", parse_mode=None)
        else:
            await message.answer(f"Файл сохранил: {filename}", parse_mode=None)

        logger.info("Document saved: %s", relative_path)

    except Exception as exc:
        logger.exception("Error processing document")
        await message.answer(f"Ошибка при обработке файла: {exc}", parse_mode=None)
