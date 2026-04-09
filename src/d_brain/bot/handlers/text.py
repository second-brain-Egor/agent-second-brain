"""Text message handler — dialog mode by default."""

import asyncio
import logging
from datetime import datetime

from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from d_brain.bot.states import SilentState
from d_brain.bot.formatters import (
    format_plain_text_report,
    normalize_telegram_output,
    strip_internal_markers,
)
from d_brain.config import get_settings
from d_brain.services.processor import AgentProcessor
from d_brain.services.session import SessionStore
from d_brain.services.storage import VaultStorage

router = Router(name="text")
logger = logging.getLogger(__name__)


async def _send_text_response(message: Message, response: str) -> None:
    """Send a plain text response."""
    response = normalize_telegram_output(response)
    try:
        await message.answer(response)
    except Exception:
        await message.answer(response, parse_mode=None)


@router.message(SilentState.active, lambda m: m.text is not None and not m.text.startswith("/"))
async def handle_text_silent(message: Message, state: FSMContext) -> None:
    """Handle text in silent mode — save only."""
    if not message.text or not message.from_user:
        return

    settings = get_settings()
    storage = VaultStorage(settings.vault_path)

    timestamp = datetime.fromtimestamp(message.date.timestamp())
    storage.append_to_daily(message.text, timestamp, "[text]")

    session = SessionStore(settings.vault_path)
    session.append(
        message.from_user.id,
        "text",
        text=message.text,
        msg_id=message.message_id,
    )

    await message.answer("✓ Сохранено")


@router.message(lambda m: m.text is not None and not m.text.startswith("/"))
async def handle_text(message: Message, state: FSMContext) -> None:
    """Handle text messages — dialog mode with auto-agent escalation."""
    if not message.text or not message.from_user:
        return

    settings = get_settings()
    storage = VaultStorage(settings.vault_path)

    timestamp = datetime.fromtimestamp(message.date.timestamp())
    storage.append_to_daily(message.text, timestamp, "[text]")

    # Log to session
    session = SessionStore(settings.vault_path)
    session.append(
        message.from_user.id,
        "text",
        text=message.text,
        msg_id=message.message_id,
    )

    # Dialog mode: respond via Claude
    await message.chat.do(action="typing")

    processor = AgentProcessor(settings.vault_path, settings.todoist_api_key)
    user_id = message.from_user.id

    try:
        result = await asyncio.to_thread(
            processor.execute_raw_prompt, message.text, user_id
        )

        if "error" in result:
            await message.answer(f"⚠️ {result['error']}", parse_mode=None)
        elif "report" in result:
            response = result["report"]

            # Auto-escalation: sonnet detected complex task
            if processor.needs_agent(response):
                brief = normalize_telegram_output(processor.strip_agent_marker(response))
                await message.answer(f"🤖 Запускаю агента...\n{brief}", parse_mode=None)
                session.append(user_id, "assistant", text=f"[agent] {brief}")

                # Run heavy agent in background (always text — too long for voice)
                asyncio.create_task(
                    _run_agent(message, processor, message.text, user_id, session)
                )
            else:
                session.append(user_id, "assistant", text=response[:500])
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
    session: SessionStore,
) -> None:
    """Run heavy agent in background and send result."""
    try:
        await message.chat.do(action="typing")
        result = await asyncio.to_thread(
            processor.execute_agent, prompt, user_id
        )

        if "error" in result:
            await message.answer(f"⚠️ Агент: {result['error']}", parse_mode=None)
        elif "report" in result:
            response = result["report"]
            clean_response = strip_internal_markers(response)
            session.append(user_id, "assistant", text=f"[agent-done] {clean_response[:500]}")
            for chunk in format_plain_text_report({"report": response}):
                await message.answer(chunk, parse_mode=None)
    except Exception as e:
        logger.exception("Agent execution error")
        await message.answer(f"⚠️ Агент упал: {e}", parse_mode=None)
