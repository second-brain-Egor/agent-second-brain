"""Forwarded message handler."""

import logging
from datetime import datetime

from aiogram import Bot, Router
from aiogram.types import Message

from d_brain.bot.chat_context import (
    build_msg_type,
    get_session_scope,
    is_work_chat,
)
from d_brain.config import get_settings
from d_brain.services.guardrails import check_injection, wrap_forwarded
from d_brain.services.session import SessionStore
from d_brain.services.storage import VaultStorage

router = Router(name="forward")
logger = logging.getLogger(__name__)


@router.message(lambda m: m.forward_origin is not None)
async def handle_forward(message: Message, bot: Bot) -> None:
    """Handle forwarded messages."""
    if not message.from_user:
        return

    settings = get_settings()
    storage = VaultStorage(settings.vault_path)
    scope = get_session_scope(message)

    # Determine source name
    source_name = "Unknown"
    origin = message.forward_origin

    if hasattr(origin, "sender_user") and origin.sender_user:
        user = origin.sender_user
        source_name = user.full_name
    elif hasattr(origin, "sender_user_name") and origin.sender_user_name:
        source_name = origin.sender_user_name
    elif hasattr(origin, "chat") and origin.chat:
        chat = origin.chat
        source_name = f"@{chat.username}" if chat.username else chat.title or "Channel"
    elif hasattr(origin, "sender_name") and origin.sender_name:
        source_name = origin.sender_name

    raw_content = message.text or message.caption or "[media]"

    # Check for prompt injection
    is_safe, reason = check_injection(raw_content)
    if not is_safe:
        await message.answer(
            f"⚠️ Пересланное сообщение содержит подозрительный контент: {reason}\n"
            "Сохранено как данные, НЕ выполнено как инструкция."
        )

    content = wrap_forwarded(raw_content)
    msg_type = build_msg_type(message, f"[forward from: {source_name}]")

    timestamp = datetime.fromtimestamp(message.date.timestamp())
    storage.append_to_daily(content, timestamp, msg_type)

    # Log to session
    session = SessionStore(settings.vault_path)
    session.append(
        scope,
        "forward",
        text=raw_content,
        source=source_name,
        msg_id=message.message_id,
        chat_id=message.chat.id,
        chat_title=message.chat.title,
    )

    work_context = is_work_chat(message, settings)
    if work_context:
        logger.info("Saved group forward without reply in chat %s", message.chat.id)
        return

    if is_safe:
        await message.answer(f"✓ Сохранено (от {source_name})")
    logger.info("Forwarded message saved from: %s", source_name)
