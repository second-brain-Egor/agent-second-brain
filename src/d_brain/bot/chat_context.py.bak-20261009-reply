"""Helpers for chat-scoped behavior and work-group policies."""

from __future__ import annotations

import re

from aiogram.types import Message, User

from d_brain.config import Settings


def is_group_chat(message: Message) -> bool:
    return message.chat.type in {"group", "supergroup"}


def is_work_chat(message: Message, settings: Settings) -> bool:
    if not is_group_chat(message):
        return False
    if message.chat.id in settings.work_chat_ids:
        return True
    return settings.treat_all_group_chats_as_work


def get_session_scope(message: Message) -> int | str:
    if is_group_chat(message):
        return f"chat_{message.chat.id}"
    return message.from_user.id if message.from_user else f"chat_{message.chat.id}"


def build_msg_type(message: Message, base_type: str) -> str:
    if not is_group_chat(message):
        return base_type

    title = (message.chat.title or str(message.chat.id)).strip()
    title = re.sub(r"\s+", " ", title)
    return f"{base_type} [чат: {title}]"


def is_explicit_bot_invocation(message: Message, bot_user: User | None) -> bool:
    if not is_group_chat(message):
        return True

    if message.reply_to_message and message.reply_to_message.from_user and bot_user:
        if message.reply_to_message.from_user.id == bot_user.id:
            return True

    username = (bot_user.username or "").lower() if bot_user else ""
    text = (message.text or message.caption or "").lower()
    if username and f"@{username}" in text:
        return True

    entities = list(message.entities or []) + list(message.caption_entities or [])
    for entity in entities:
        if entity.type == "mention" and username:
            mention = (text[entity.offset : entity.offset + entity.length]).lower()
            if mention == f"@{username}":
                return True
        if entity.type == "text_mention" and bot_user and entity.user:
            if entity.user.id == bot_user.id:
                return True

    return False
