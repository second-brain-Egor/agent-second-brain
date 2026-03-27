"""Text message handler — dialog mode by default."""

import asyncio
import logging
from datetime import datetime

from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from d_brain.bot.states import SilentState
from d_brain.config import get_settings
from d_brain.services.processor import ClaudeProcessor
from d_brain.services.session import SessionStore
from d_brain.services.storage import VaultStorage

router = Router(name="text")
logger = logging.getLogger(__name__)


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
async def handle_text(message: Message) -> None:
    """Handle text messages — dialog mode (default)."""
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

    processor = ClaudeProcessor(settings.vault_path, settings.todoist_api_key)
    user_id = message.from_user.id

    try:
        result = await asyncio.to_thread(
            processor.execute_raw_prompt, message.text, user_id
        )

        if "error" in result:
            await message.answer(f"⚠️ {result['error']}")
        elif "report" in result:
            response = result["report"]
            # Save assistant response to session
            session.append(user_id, "assistant", text=response[:500])
            await message.answer(response)
        else:
            await message.answer("✓ Сохранено")

    except Exception as e:
        logger.exception("Dialog error")
        await message.answer("✓ Сохранено")

    logger.info("Text message processed: %d chars", len(message.text))
