"""Voice message handler — dialog mode by default."""

import asyncio
import logging
from datetime import datetime

from aiogram import Bot, Router
from aiogram.types import BufferedInputFile, Message
from aiogram.fsm.context import FSMContext

from d_brain.bot.states import SilentState
from d_brain.bot.formatters import format_process_report, normalize_telegram_output
from d_brain.config import get_settings
from d_brain.services.processor import AgentProcessor
from d_brain.services.session import SessionStore
from d_brain.services.storage import VaultStorage
from d_brain.services.transcription import DeepgramTranscriber
from d_brain.services.tts import text_to_voice
from d_brain.services.reminder import check_process_reminder

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

    text = await transcriber.transcribe(file_bytes.read())
    if text:
        import re
        text = re.sub(r'(?i)\bслышь[,.]?\s*', '', text).strip()
    return text


async def _send_response(message: Message, response: str, voice_replies: bool) -> None:
    """Send response as voice or text depending on settings."""
    response = normalize_telegram_output(response)
    if voice_replies:
        try:
            audio = await text_to_voice(response)
            await message.answer_voice(BufferedInputFile(audio, filename="response.ogg"))
            return
        except Exception:
            logger.exception("TTS failed, falling back to text")
            await message.answer("⚠️ Голосовой ответ не удался, отвечаю текстом:")
    try:
        await message.answer(response)
    except Exception:
        await message.answer(response, parse_mode=None)


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
async def handle_voice(message: Message, bot: Bot, state: FSMContext) -> None:
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

        # Dialog mode: respond via Claude
        await message.chat.do(action="typing")
        processor = AgentProcessor(settings.vault_path, settings.todoist_api_key)
        user_id = message.from_user.id
        fsm_data = await state.get_data()
        voice_mode = settings.voice_replies or fsm_data.get("voice_mode", False)

        result = await asyncio.to_thread(
            processor.execute_raw_prompt, transcript, user_id
        )

        if "error" in result:
            await message.answer(f"⚠️ {result['error']}", parse_mode=None)
        elif "report" in result:
            response = result["report"]

            # Auto-escalation: sonnet detected complex task
            if processor.needs_agent(response):
                brief = processor.strip_agent_marker(response)
                await message.answer(f"🤖 Запускаю агента...\n{brief}", parse_mode=None)
                session.append(user_id, "assistant", text=f"[agent] {brief}")

                asyncio.create_task(
                    _run_voice_agent(message, processor, transcript, user_id, session, voice_mode)
                )
            else:
                session.append(user_id, "assistant", text=response[:500])
                # Smart reminder: after 20:00 if day not processed
                reminder = check_process_reminder(settings.vault_path)
                if reminder:
                    response += reminder
                await _send_response(message, response, voice_mode)

    except Exception as e:
        logger.exception("Error processing voice message")
        await message.answer(f"Error: {e}", parse_mode=None)

    logger.info("Voice message processed")


async def _run_voice_agent(
    message: Message,
    processor: AgentProcessor,
    prompt: str,
    user_id: int,
    session: SessionStore,
    voice_replies: bool = False,
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
            session.append(user_id, "assistant", text=f"[agent-done] {response[:500]}")
            for chunk in format_process_report({"report": response}):
                try:
                    await message.answer(chunk)
                except Exception:
                    await message.answer(chunk, parse_mode=None)
    except Exception as e:
        logger.exception("Agent execution error")
        await message.answer(f"⚠️ Агент упал: {e}", parse_mode=None)
