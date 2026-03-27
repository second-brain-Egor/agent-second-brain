"""Voice message handler — dialog mode by default."""

import asyncio
import logging
from datetime import datetime

from aiogram import Bot, Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from d_brain.bot.states import SilentState
from d_brain.config import get_settings
from d_brain.services.processor import ClaudeProcessor
from d_brain.services.session import SessionStore
from d_brain.services.storage import VaultStorage
from d_brain.services.transcription import DeepgramTranscriber

router = Router(name="voice")
logger = logging.getLogger(__name__)


async def _transcribe_voice(message: Message, bot: Bot) -> str | None:
    """Transcribe voice message, return text or None."""
    settings = get_settings()
    transcriber = DeepgramTranscriber(settings.deepgram_api_key)

    file = await bot.get_file(message.voice.file_id)
    if not file.file_path:
        return None

    file_bytes = await bot.download_file(file.file_path)
    if not file_bytes:
        return None

    return await transcriber.transcribe(file_bytes.read())


@router.message(SilentState.active, lambda m: m.voice is not None)
async def handle_voice_silent(message: Message, bot: Bot, state: FSMContext) -> None:
    """Handle voice in silent mode — transcribe and save only."""
    if not message.voice or not message.from_user:
        return

    await message.chat.do(action="typing")

    try:
        transcript = await _transcribe_voice(message, bot)
        if not transcript:
            await message.answer("Could not transcribe audio")
            return

        settings = get_settings()
        storage = VaultStorage(settings.vault_path)
        timestamp = datetime.fromtimestamp(message.date.timestamp())
        storage.append_to_daily(transcript, timestamp, "[voice]")

        session = SessionStore(settings.vault_path)
        session.append(
            message.from_user.id,
            "voice",
            text=transcript,
            duration=message.voice.duration,
            msg_id=message.message_id,
        )

        await message.answer(f"🎤 {transcript}\n\n✓ Сохранено")

    except Exception as e:
        logger.exception("Error processing voice message")
        await message.answer(f"Error: {e}")


@router.message(lambda m: m.voice is not None)
async def handle_voice(message: Message, bot: Bot) -> None:
    """Handle voice messages — dialog mode (default)."""
    if not message.voice or not message.from_user:
        return

    await message.chat.do(action="typing")

    try:
        transcript = await _transcribe_voice(message, bot)
        if not transcript:
            await message.answer("Could not transcribe audio")
            return

        settings = get_settings()
        storage = VaultStorage(settings.vault_path)
        timestamp = datetime.fromtimestamp(message.date.timestamp())
        storage.append_to_daily(transcript, timestamp, "[voice]")

        session = SessionStore(settings.vault_path)
        session.append(
            message.from_user.id,
            "voice",
            text=transcript,
            duration=message.voice.duration,
            msg_id=message.message_id,
        )

        # Show transcription
        await message.answer(f"🎤 {transcript}")

        # Dialog mode: respond via Claude
        await message.chat.do(action="typing")
        processor = ClaudeProcessor(settings.vault_path, settings.todoist_api_key)
        user_id = message.from_user.id

        result = await asyncio.to_thread(
            processor.execute_raw_prompt, transcript, user_id
        )

        if "error" in result:
            await message.answer(f"⚠️ {result['error']}")
        elif "report" in result:
            response = result["report"]
            session.append(user_id, "assistant", text=response[:500])
            await message.answer(response)

    except Exception as e:
        logger.exception("Error processing voice message")
        await message.answer(f"Error: {e}")

    logger.info("Voice message processed")
