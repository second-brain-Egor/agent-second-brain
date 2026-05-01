"""Voice message handler — dialog mode by default."""

import asyncio
import logging
from datetime import datetime

from aiogram import Bot, Router
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

    text = await transcriber.transcribe(file_bytes.read())
    if text:
        import re
        text = re.sub(r'(?i)\bслышь[,.]?\s*', '', text).strip()
    return text


async def _send_response(message: Message, response: str) -> None:
    """Send a formatted Telegram response."""
    for chunk in prepare_telegram_response(response):
        try:
            await message.answer(chunk)
        except Exception:
            await message.answer(chunk, parse_mode=None)


@router.message(SilentState.active, lambda m: m.voice is not None)
async def handle_voice_silent(message: Message, bot: Bot, state: FSMContext) -> None:
    """Handle voice in silent mode — transcribe and save only."""
    if not message.voice or not message.from_user:
        return

    await message.chat.do(action="typing")

    try:
        transcript = await _transcribe_voice(message, bot)
        if not transcript:
            await message.answer("Не удалось распознать аудио.")
            return

        settings = get_settings()
        storage = VaultStorage(settings.vault_path)
        scope = get_session_scope(message)
        timestamp = datetime.fromtimestamp(message.date.timestamp())
        storage.append_to_daily(transcript, timestamp, build_msg_type(message, "[voice]"))

        session = SessionStore(settings.vault_path)
        session.append(
            scope,
            "voice",
            text=transcript,
            duration=message.voice.duration,
            msg_id=message.message_id,
            chat_id=message.chat.id,
            chat_title=message.chat.title,
        )

        await message.answer(f"🎤 {transcript}\n\n✓ Сохранено")

    except Exception as e:
        logger.exception("Error processing voice message")
        await message.answer(f"Ошибка: {e}")


@router.message(lambda m: m.voice is not None)
async def handle_voice(message: Message, bot: Bot, state: FSMContext) -> None:
    """Handle voice messages — dialog mode (default)."""
    if not message.voice or not message.from_user:
        return

    await message.chat.do(action="typing")

    try:
        transcript = await _transcribe_voice(message, bot)
        if not transcript:
            await message.answer("Не удалось распознать аудио.")
            return

        settings = get_settings()
        storage = VaultStorage(settings.vault_path)
        scope = get_session_scope(message)
        timestamp = datetime.fromtimestamp(message.date.timestamp())
        storage.append_to_daily(transcript, timestamp, build_msg_type(message, "[voice]"))

        session = SessionStore(settings.vault_path)
        session.append(
            scope,
            "voice",
            text=transcript,
            duration=message.voice.duration,
            msg_id=message.message_id,
            chat_id=message.chat.id,
            chat_title=message.chat.title,
        )

        work_context = is_work_chat(message, settings)
        if work_context:
            logger.info("Saved group voice without reply in chat %s", message.chat.id)
            return

        # Dialog mode: respond via Claude
        await message.chat.do(action="typing")
        processor = AgentProcessor(settings.vault_path, settings.todoist_api_key)
        user_id = message.from_user.id

        result = await asyncio.to_thread(
            processor.execute_raw_prompt,
            transcript,
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

                asyncio.create_task(
                    _run_voice_agent(message, processor, transcript, user_id, scope, work_context, session)
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
                await _send_response(message, response)

    except Exception as e:
        logger.exception("Error processing voice message")
        await message.answer(f"Ошибка: {e}", parse_mode=None)

    logger.info("Voice message processed")


async def _run_voice_agent(
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
