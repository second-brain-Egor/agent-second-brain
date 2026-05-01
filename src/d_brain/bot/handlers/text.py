"""Text message handler — dialog mode by default."""

import asyncio
import logging
from datetime import datetime

from aiogram import Router
from aiogram import Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from d_brain.bot.chat_context import (
    build_msg_type,
    get_session_scope,
    is_work_chat,
)
from d_brain.bot.states import SilentState
from d_brain.bot.formatters import (
    normalize_telegram_output,
    prepare_telegram_response,
)
from d_brain.config import get_settings
from d_brain.services.processor import AgentProcessor
from d_brain.services.session import SessionStore
from d_brain.services.storage import VaultStorage

router = Router(name="text")
logger = logging.getLogger(__name__)


async def _send_text_response(message: Message, response: str) -> None:
    """Send a formatted Telegram response."""
    for chunk in prepare_telegram_response(response):
        try:
            await message.answer(chunk)
        except Exception:
            await message.answer(chunk, parse_mode=None)


@router.message(SilentState.active, lambda m: m.text is not None and not m.text.startswith("/"))
async def handle_text_silent(message: Message, state: FSMContext) -> None:
    """Handle text in silent mode — save only."""
    if not message.text or not message.from_user:
        return

    settings = get_settings()
    storage = VaultStorage(settings.vault_path)
    scope = get_session_scope(message)

    timestamp = datetime.fromtimestamp(message.date.timestamp())
    storage.append_to_daily(message.text, timestamp, build_msg_type(message, "[text]"))

    session = SessionStore(settings.vault_path)
    session.append(
        scope,
        "text",
        text=message.text,
        msg_id=message.message_id,
        chat_id=message.chat.id,
        chat_title=message.chat.title,
    )

    await message.answer("✓ Сохранено")


@router.message(lambda m: m.text is not None and not m.text.startswith("/"))
async def handle_text(message: Message, state: FSMContext, bot: Bot) -> None:
    """Handle text messages — dialog mode with auto-agent escalation."""
    if not message.text or not message.from_user:
        return

    settings = get_settings()
    storage = VaultStorage(settings.vault_path)
    scope = get_session_scope(message)

    timestamp = datetime.fromtimestamp(message.date.timestamp())
    storage.append_to_daily(message.text, timestamp, build_msg_type(message, "[text]"))

    # Log to session
    session = SessionStore(settings.vault_path)
    session.append(
        scope,
        "text",
        text=message.text,
        msg_id=message.message_id,
        chat_id=message.chat.id,
        chat_title=message.chat.title,
    )

    work_context = is_work_chat(message, settings)
    if work_context:
        logger.info("Saved group text without reply in chat %s", message.chat.id)
        return

    # Dialog mode: respond via Claude
    await message.chat.do(action="typing")

    processor = AgentProcessor(settings.vault_path, settings.todoist_api_key)
    user_id = message.from_user.id

    try:
        result = await asyncio.to_thread(
            processor.execute_raw_prompt,
            message.text,
            user_id,
            session_scope=scope,
            work_context=work_context,
        )

        if "error" in result:
            await message.answer(f"⚠️ {result['error']}", parse_mode=None)
        elif "report" in result:
            response = result["report"]

            # Auto-escalation: sonnet detected complex task
            if processor.needs_agent(response):
                brief = normalize_telegram_output(processor.strip_agent_marker(response))
                await message.answer(f"🤖 Запускаю агента...\n{brief}", parse_mode=None)
                session.append(scope, "assistant", text=f"[agent] {brief}", chat_id=message.chat.id, chat_title=message.chat.title)

                # Run heavy agent in background (always text — too long for voice)
                asyncio.create_task(
                    _run_agent(message, processor, message.text, user_id, scope, work_context, session)
                )
            else:
                sent_chunks = prepare_telegram_response(response)
                session.append(
                    scope,
                    "assistant",
                    text="\n\n".join(sent_chunks),
                    chat_id=message.chat.id,
                    chat_title=message.chat.title,
                )
                await _send_text_response(message, response)
        else:
            await message.answer("✓ Сохранено")

    except Exception as e:
        logger.exception("Dialog error")
        await message.answer("✓ Сохранено")

    logger.info("Text message processed: %d chars", len(message.text))


async def _run_agent(
    message: Message,
    processor: AgentProcessor,
    prompt: str,
    user_id: int,
    session_scope: int | str,
    work_context: bool,
    session: SessionStore,
) -> None:
    """Run heavy agent in background and send result."""
    try:
        await message.chat.do(action="typing")
        result = await asyncio.to_thread(
            processor.execute_agent,
            prompt,
            user_id,
            session_scope=session_scope,
            work_context=work_context,
        )

        if "error" in result:
            await message.answer(f"⚠️ Агент: {result['error']}", parse_mode=None)
        elif "report" in result:
            response = result["report"]
            sent_chunks = prepare_telegram_response(response)
            session.append(
                session_scope,
                "assistant",
                text=f"[agent-done] {'\n\n'.join(sent_chunks)}",
                chat_id=message.chat.id,
                chat_title=message.chat.title,
            )
            for chunk in sent_chunks:
                try:
                    await message.answer(chunk)
                except Exception:
                    await message.answer(chunk, parse_mode=None)
    except Exception as e:
        logger.exception("Agent execution error")
        await message.answer(f"⚠️ Агент упал: {e}", parse_mode=None)
