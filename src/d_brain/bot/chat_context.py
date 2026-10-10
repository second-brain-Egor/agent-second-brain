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


# Ответ на конкретное сообщение (кнопка «Ответить» в Telegram), поручение Егора 9 октября 2026.
# Боту приходит только текст ответа, поэтому цитату подставляем в запрос сами,
# а ответ бота уходит реплаем, только если вопрос далеко (QUOTE_AFTER ниже).
REPLY_PROMPT_LIMIT = 4000  # в запрос — почти целиком: сообщение Telegram не длиннее 4096
REPLY_LOG_LIMIT = 200      # в журнал беседы — короткая отсылка, полный текст там уже есть


def _clip(text: str, limit: int) -> str:
    text = text.strip()
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def _voice_transcript(vault_path, message: Message, msg_id: int) -> str:
    """Расшифровка своего голосового из журнала беседы: в самом сообщении текста нет."""
    from d_brain.services.session import SessionStore

    entries = SessionStore(vault_path).get_recent(get_session_scope(message), limit=1000)
    for entry in reversed(entries):
        if entry.get("msg_id") == msg_id and entry.get("chat_id") in (None, message.chat.id):
            if entry.get("text"):
                return entry["text"]
    return ""


def replied_message(message: Message, vault_path) -> dict | None:
    """Сообщение, на которое пользователь ответил: время, автор, текст и выделена ли цитата."""
    reply = message.reply_to_message
    if reply is None or reply.forum_topic_created is not None:
        return None
    if message.is_topic_message and reply.message_id == message.message_thread_id:
        return None  # в темах форума каждое сообщение формально отвечает на заголовок темы

    quote = message.quote
    fragment = bool(quote and quote.text and quote.is_manual)
    text = quote.text if fragment else (reply.text or reply.caption or "")
    if not text:
        if reply.voice or reply.video_note:
            transcript = _voice_transcript(vault_path, message, reply.message_id)
            text = f"голосовое: «{transcript}»" if transcript else "голосовое (расшифровка не найдена)"
        elif reply.photo:
            text = "[фото]"
        elif reply.document:
            text = f"[файл {reply.document.file_name or ''}]".replace(" ]", "]")
        elif reply.video:
            text = "[видео]"
        else:
            text = "[сообщение без текста]"

    from_bot = bool(reply.from_user and reply.from_user.is_bot)
    return {
        "stamp": reply.date.astimezone().strftime("%H:%M"),
        "author": "assistant" if from_bot else "user",
        "text": text,
        "fragment": fragment,
    }


def reply_prompt(message: Message, text: str, vault_path) -> str:
    """Текст запроса к модели с цитатой сообщения, на которое ответил пользователь."""
    replied = replied_message(message, vault_path)
    if replied is None:
        return text
    whose = "твоё сообщение" if replied["author"] == "assistant" else "своё сообщение"
    part = "выделенный фрагмент" if replied["fragment"] else "текст"
    return (
        f"[Ответ на {whose} от {replied['stamp']}; {part}:]\n"
        f"«{_clip(replied['text'], REPLY_PROMPT_LIMIT)}»\n\n"
        f"{text}"
    )


def reply_log(message: Message, vault_path) -> str | None:
    """Короткая отсылка для журнала беседы: «07:48 assistant: «…»»."""
    replied = replied_message(message, vault_path)
    if replied is None:
        return None
    return f"{replied['stamp']} {replied['author']}: «{_clip(replied['text'], REPLY_LOG_LIMIT)}»"


# Реплаем ответ уходит, только когда вопрос уже ушёл вверх: после него в чате прошло три
# сообщения. В живом диалоге ответ идёт обычным сообщением (Егор, 9 октября 2026, 08:38).
QUOTE_AFTER = 3
NOT_MESSAGES = {"photo_batch"}  # служебные строки журнала, а не сообщения чата


def messages_since(message: Message, vault_path, own_text: str = "") -> int:
    """Сколько сообщений чата записано в журнал беседы после этого сообщения пользователя.

    Ответ, который уже записан в журнал перед отправкой (own_text), не считается.
    """
    from d_brain.services.session import SessionStore

    entries = SessionStore(vault_path).get_recent(get_session_scope(message), limit=1000)
    for index in range(len(entries) - 1, -1, -1):
        entry = entries[index]
        if entry.get("msg_id") == message.message_id and entry.get("chat_id") in (None, message.chat.id):
            later = [e for e in entries[index + 1:]
                     if e.get("chat_id") in (None, message.chat.id) and e.get("type") not in NOT_MESSAGES]
            if own_text and later and later[-1].get("type") == "assistant" \
                    and str(later[-1].get("text", "")).endswith(own_text):
                later.pop()
            return len(later)
    return 0


def needs_quote(message: Message, vault_path, own_text: str = "") -> bool:
    return messages_since(message, vault_path, own_text) >= QUOTE_AFTER


async def send_reply(message: Message, text: str, vault_path, **kwargs) -> None:
    """Одно сообщение бота: реплаем, если вопрос далеко, иначе обычным сообщением."""
    if needs_quote(message, vault_path):
        await message.reply(text, allow_sending_without_reply=True, **kwargs)
    else:
        await message.answer(text, **kwargs)


async def send_chunks(message: Message, chunks: list[str], vault_path) -> None:
    """Ответ бота: первый кусок реплаем, если вопрос далеко (needs_quote), остальные следом."""
    quote = needs_quote(message, vault_path, "\n\n".join(chunks))
    for index, chunk in enumerate(chunks):
        first = quote and index == 0
        send = message.reply if first else message.answer
        extra = {"allow_sending_without_reply": True} if first else {}
        try:
            await send(chunk, **extra)
        except Exception:
            await send(chunk, parse_mode=None, **extra)
