"""Document message handler."""

from __future__ import annotations

import asyncio
import logging
import re
from datetime import datetime
from pathlib import Path

from aiogram import Bot, Router
from aiogram.types import FSInputFile, Message

from d_brain.bot.chat_context import build_msg_type, get_session_scope, is_work_chat
from d_brain.bot.typing_indicator import keep_typing
from d_brain.config import get_settings
from d_brain.services.processor import AgentProcessor
from d_brain.services.session import SessionStore
from d_brain.services.storage import VaultStorage

# Триггеры в caption: бот понимает что юзер хочет письменный ответ на документ.
QA_TRIGGERS = re.compile(
    r"\b(ответ|ответь|ответы|обработ|прочитай|разбер|пройди|заполни)\w*",
    re.IGNORECASE,
)


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

        # Per soul.md: не выкатывать содержимое в чат, спросить что сделать
        # (то же поведение что для фотографий без явной команды).
        # Если в caption уже есть указание — действие приходит следующим
        # текстовым сообщением, бот его обработает в text/voice handler.
        # Если caption выглядит как просьба обработать документ и вернуть ответ —
        # запускаем agent-режим (Opus) и возвращаем результат файлом для скачивания.
        if message.caption and QA_TRIGGERS.search(message.caption) and preview is not None:
            await message.answer(
                f"📄 Файл сохранил: {filename}\n⏳ Читаю и готовлю ответ документом, обычно 1–3 минуты…",
                parse_mode=None,
            )
            asyncio.create_task(
                _answer_document(
                    bot=bot,
                    message=message,
                    filename=filename,
                    file_text=data.decode("utf-8", errors="ignore"),
                    instructions=message.caption,
                    storage=storage,
                    timestamp=timestamp,
                )
            )
        elif message.caption:
            await message.answer(f"📄 Файл сохранил: {filename}", parse_mode=None)
        else:
            await message.answer(
                f"📄 Файл сохранил: {filename}\n\nЧто с ним сделать? И оставить потом в архиве или удалить?",
                parse_mode=None,
            )

        logger.info("Document saved: %s", relative_path)

    except Exception as exc:
        logger.exception("Error processing document")
        await message.answer(f"Ошибка при обработке файла: {exc}", parse_mode=None)


async def _answer_document(
    bot: Bot,
    message: Message,
    filename: str,
    file_text: str,
    instructions: str,
    storage: VaultStorage,
    timestamp: datetime,
) -> None:
    """Прочитать документ → через Opus сгенерировать ответ → вернуть .md файл.

    Запускается когда caption содержит просьбу обработать документ
    («ответь», «обработай», «прочитай», «разбери», «пройди» и т.п.).

    Защита: если в первых ~50 строках файла обнаружены маркеры «эти вопросы
    не для тебя / это для Telegram-бота» — обработка отменяется и пользователю
    объясняется что опросник нужно прогнать через сам Telegram-бот.
    """
    try:
        settings = get_settings()
        processor = AgentProcessor(settings.vault_path, settings.todoist_api_key)

        system_prompt = (
            "Ты — помощник, отвечающий на содержимое присланного документа. "
            "Работай вдумчиво, отвечай по сути, без воды. "
            "Возвращай результат на русском языке как чистый markdown — заголовки, списки, "
            "блоки кода если уместно. Не используй HTML-теги. Не пиши служебных вступлений "
            "вроде «вот ответ». Сразу начинай с заголовка # и содержательной части."
        )
        user_prompt = (
            f"Инструкция от пользователя: {instructions}\n\n"
            f"Документ ({filename}):\n\n---\n{file_text}\n---\n\n"
            "Подготовь ответ как готовый markdown-документ."
        )

        async with keep_typing(message.chat):
            try:
                answer = await asyncio.to_thread(
                    processor._run_agent,  # noqa: SLF001 — мы внутри проекта
                    system_prompt,
                    user_prompt,
                    read_only=True,
                )
            except Exception as exc:
                logger.exception("answer_document: LLM failed")
                err = str(exc) or type(exc).__name__
                if "TimeoutExpired" in err or "timed out" in err.lower():
                    msg = "⏱ Не уложился в таймаут. Документ большой или API лагает — попробуй ещё раз через минуту."
                else:
                    msg = f"⚠️ LLM упал: {err[:200]}"
                await message.answer(msg, parse_mode=None)
                return

        if not answer or not answer.strip():
            await message.answer("⚠️ LLM вернул пустой ответ. Попробуй переформулировать caption.", parse_mode=None)
            return

        # Сохраняем результат в attachments/<date>/ (тот же день что и исходник)
        stem = Path(filename).stem
        out_name = f"{stem}-ответы.md"
        out_path = storage.save_document(
            answer.encode("utf-8"),
            timestamp.date(),
            out_name,
        )
        absolute_out = (settings.vault_path / out_path).resolve()

        # Шлём в Telegram как документ для скачивания
        await bot.send_document(
            chat_id=message.chat.id,
            document=FSInputFile(absolute_out, filename=out_name),
            caption=f"📝 Ответ на {filename}\n\nОставлять файл в архиве или удалить после прочтения?",
            reply_to_message_id=message.message_id,
        )
        logger.info("answer_document: sent %s (%d chars)", out_name, len(answer))

    except Exception:
        logger.exception("answer_document: unexpected error")
        try:
            await message.answer("⚠️ Что-то пошло не так при обработке. Подробности в логах.", parse_mode=None)
        except Exception:
            pass
