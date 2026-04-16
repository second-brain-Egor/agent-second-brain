"""Handler for /ask command in group chats."""

import asyncio
import logging

from aiogram import Bot, Router
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from d_brain.bot.chat_context import get_session_scope, is_work_chat
from d_brain.bot.formatters import (
    format_plain_text_report,
    normalize_telegram_output,
    prepare_plain_text_response,
)
from d_brain.bot.states import AskCommandState
from d_brain.config import get_settings
from d_brain.services.processor import AgentProcessor
from d_brain.services.session import SessionStore
from d_brain.services.transcription import DeepgramTranscriber

router = Router(name="ask")
logger = logging.getLogger(__name__)


async def _send_text_response(message: Message, response: str) -> None:
    """Send a plain text response."""
    for chunk in prepare_plain_text_response(response):
        try:
            await message.answer(chunk)
        except Exception:
            await message.answer(chunk, parse_mode=None)


@router.message(Command("ask"))
async def cmd_ask(message: Message, command: CommandObject, state: FSMContext) -> None:
    """Handle /ask command for explicit group replies."""
    if command.args:
        await process_ask(message, command.args)
        return

    await state.set_state(AskCommandState.waiting_for_input)
    await message.answer("Напиши следующим сообщением вопрос или пришли голосовое.")


@router.message(AskCommandState.waiting_for_input)
async def handle_ask_input(message: Message, bot: Bot, state: FSMContext) -> None:
    """Handle voice/text input after /ask command."""
    await state.clear()
    prompt = None

    if message.voice:
        await message.chat.do(action="typing")
        settings = get_settings()
        transcriber = DeepgramTranscriber(settings.deepgram_api_key)

        try:
            file = await bot.get_file(message.voice.file_id)
            if not file.file_path:
                await message.answer("Не удалось скачать голосовое.")
                return

            file_bytes = await bot.download_file(file.file_path)
            if not file_bytes:
                await message.answer("Не удалось скачать голосовое.")
                return

            prompt = await transcriber.transcribe(file_bytes.read())
        except Exception as exc:
            logger.exception("Failed to transcribe voice for /ask")
            await message.answer(f"Не удалось распознать голосовое: {exc}", parse_mode=None)
            return

        if not prompt:
            await message.answer("Не удалось распознать речь.")
            return

    elif message.text:
        prompt = message.text

    else:
        await message.answer("Отправь текст или голосовое сообщение.")
        return

    await process_ask(message, prompt)


async def process_ask(message: Message, prompt: str) -> None:
    """Process an explicit /ask request."""
    settings = get_settings()
    processor = AgentProcessor(settings.vault_path, settings.todoist_api_key)
    session = SessionStore(settings.vault_path)
    session_scope = get_session_scope(message)
    work_context = is_work_chat(message, settings)
    user_id = message.from_user.id if message.from_user else 0

    await message.chat.do(action="typing")

    try:
        result = await asyncio.to_thread(
            processor.execute_raw_prompt,
            prompt,
            user_id,
            session_scope=session_scope,
            work_context=work_context,
        )

        if "error" in result:
            await message.answer(f"⚠️ {result['error']}", parse_mode=None)
            return

        response = result.get("report")
        if not response:
            await message.answer("Не получилось собрать ответ.", parse_mode=None)
            return

        if processor.needs_agent(response):
            brief = normalize_telegram_output(processor.strip_agent_marker(response))
            await message.answer(f"Запускаю агента.\n{brief}", parse_mode=None)
            session.append(
                session_scope,
                "assistant",
                text=f"[agent] {brief}",
                chat_id=message.chat.id,
                chat_title=message.chat.title,
            )
            asyncio.create_task(
                _run_ask_agent(message, processor, prompt, user_id, session_scope, work_context, session)
            )
            return

        sent_chunks = prepare_plain_text_response(response)
        session.append(
            session_scope,
            "assistant",
            text="\n\n".join(sent_chunks),
            chat_id=message.chat.id,
            chat_title=message.chat.title,
        )
        await _send_text_response(message, response)
    except Exception:
        logger.exception("Ask command failed")
        await message.answer("Не получилось обработать запрос.", parse_mode=None)


async def _run_ask_agent(
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
            return

        response = result.get("report")
        if not response:
            await message.answer("Не получилось собрать ответ агента.", parse_mode=None)
            return

        sent_chunks = format_plain_text_report({"report": response})
        session.append(
            session_scope,
            "assistant",
            text=f"[agent-done] {'\n\n'.join(sent_chunks)}",
            chat_id=message.chat.id,
            chat_title=message.chat.title,
        )
        for chunk in sent_chunks:
            await message.answer(chunk, parse_mode=None)
    except Exception as exc:
        logger.exception("Ask agent execution error")
        await message.answer(f"⚠️ Агент упал: {exc}", parse_mode=None)
