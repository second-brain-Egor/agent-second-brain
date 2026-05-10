"""Text message handler — dialog mode by default."""

import asyncio
import logging
from datetime import datetime
from pathlib import Path

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
from d_brain.bot.typing_indicator import keep_typing
from d_brain.services.evening_reminder import maybe_evening_reminder
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

    # Команда удаления последнего файла («удали», «выброси», «не нужен», «убери»).
    # Только для файлов внутри vault/attachments/ — для безопасности.
    import re
    delete_pattern = re.compile(
        r"\b(удал|выброс|не\s*нужн|убери|снеси|стери|стер[еи]ть)\w*",
        re.IGNORECASE,
    )
    if delete_pattern.search(message.text):
        recent = session.get_recent(scope, limit=10)
        for entry in reversed(recent[:-1]):
            if entry.get("type") in ("text", "voice", "assistant"):
                continue
            if entry.get("type") in ("file", "photo"):
                rel = entry.get("path") or ""
                if rel and rel.startswith("attachments/"):
                    abs_path = (settings.vault_path / rel).resolve()
                    vault_abs = settings.vault_path.resolve()
                    try:
                        abs_path.relative_to(vault_abs / "attachments")
                    except ValueError:
                        await message.answer(
                            "⚠️ Удалить можно только файлы из attachments/. Этот файл не там.",
                            parse_mode=None,
                        )
                        return
                    if abs_path.exists():
                        abs_path.unlink()
                        from d_brain.services.storage import VaultStorage as _VS  # alias
                        # Лог в change-log
                        try:
                            cl = settings.vault_path / "memory" / "change-log.md"
                            cl.parent.mkdir(parents=True, exist_ok=True)
                            with cl.open("a", encoding="utf-8") as f:
                                from datetime import datetime as _dt
                                f.write(
                                    f"\n{_dt.now().strftime('%Y-%m-%d %H:%M')} | Удалён файл `{rel}` | "
                                    f"По команде пользователя в чате\n"
                                )
                        except Exception:
                            logger.exception("change-log write failed")
                        await message.answer(
                            f"🗑️ Удалил `{Path(rel).name}`",
                            parse_mode=None,
                        )
                        return
                    await message.answer(
                        f"⚠️ Файл уже удалён или не найден на диске: `{rel}`",
                        parse_mode=None,
                    )
                    return
                break
            break

    # Если последнее событие в сессии — присланный файл (без обработки),
    # а текущий текст похож на просьбу обработать его → запускаем
    # document-QA flow (как если бы caption был при отправке).
    from d_brain.bot.handlers.document import QA_TRIGGERS, _answer_document
    if QA_TRIGGERS.search(message.text):
        recent = session.get_recent(scope, limit=5)
        # Идём с конца, ищем последний file (но не дальше нашего же только что записанного text)
        for entry in reversed(recent[:-1]):  # без только что добавленного text
            etype = entry.get("type")
            if etype == "file":
                file_relpath = entry.get("path")
                file_text = entry.get("text") or ""
                file_name = Path(file_relpath).name if file_relpath else "document.md"
                if file_relpath and file_text:
                    await message.answer(
                        f"📄 Обрабатываю «{file_name}» по твоей команде. ⏳ 1–3 минуты…",
                        parse_mode=None,
                    )
                    asyncio.create_task(
                        _answer_document(
                            bot=message.bot,
                            message=message,
                            filename=file_name,
                            file_text=file_text,
                            instructions=message.text,
                            storage=storage,
                            timestamp=timestamp,
                        )
                    )
                    return
                break  # нашли file без preview — не сможем обработать
            if etype in ("text", "voice", "assistant"):
                # между файлом и нашим текстом было ещё что-то — не считаем "следом за файлом"
                break

    # Dialog mode: respond via active LLM backend
    processor = AgentProcessor(settings.vault_path, settings.todoist_api_key)
    user_id = message.from_user.id

    try:
        # 2026-05-10: classifier/pending/brief disabled — pure Opus chat, no two-model dance.
        # If returning to Sonnet+gatekeeper architecture, flip this back to ai_backend == "claude".
        if False:
            # Check pending action first: user may be confirming/cancelling a previous question.
            pending = processor.get_pending_action(scope)
            if pending:
                decision = await asyncio.to_thread(
                    processor.classify_pending_response, message.text, pending["brief"]
                )
                if decision == "confirm":
                    processor.clear_pending_action(scope)
                    await message.answer("🟢 Принял", parse_mode=None)
                    session.append(scope, "assistant", text="🟢 Принял", chat_id=message.chat.id, chat_title=message.chat.title)
                    asyncio.create_task(
                        _run_agent(message, processor, pending["original_prompt"], user_id, scope, work_context, session)
                    )
                    logger.info("Text message processed (pending confirmed → Opus)")
                    return
                if decision == "cancel":
                    processor.clear_pending_action(scope)
                    await message.answer("🔴 Отменил", parse_mode=None)
                    session.append(scope, "assistant", text="🔴 Отменил", chat_id=message.chat.id, chat_title=message.chat.title)
                    logger.info("Text message processed (pending cancelled)")
                    return
                processor.clear_pending_action(scope)

            # Pre-classify (LLM with last 20 session entries). Heavy → ask confirmation, store pending.
            async with keep_typing(message.chat):
                weight = await asyncio.to_thread(processor.classify_message_weight, message.text, scope)
                if weight == "heavy":
                    brief_raw = await asyncio.to_thread(processor.generate_brief, message.text, scope)
            if weight == "heavy":
                brief = normalize_telegram_output(brief_raw)
                processor.set_pending_action(scope, message.text, brief)
                await message.answer(brief, parse_mode=None)
                session.append(scope, "assistant", text=f"[pending] {brief}", chat_id=message.chat.id, chat_title=message.chat.title)
                logger.info("Text message processed (heavy → pending confirmation): %d chars", len(message.text))
                return

        async with keep_typing(message.chat):
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
                await message.answer(brief, parse_mode=None)
                session.append(scope, "assistant", text=f"[agent] {brief}", chat_id=message.chat.id, chat_title=message.chat.title)

                # Run heavy agent in background (always text — too long for voice)
                asyncio.create_task(
                    _run_agent(message, processor, message.text, user_id, scope, work_context, session)
                )
            else:
                reminder = maybe_evening_reminder(settings.vault_path)
                if reminder:
                    response = f"{response}\n\n{reminder}"
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
        err = str(e) or type(e).__name__
        msg = "⚠️ Не получилось ответить (таймаут или ошибка LLM). Запрос сохранён, попробуй ещё раз через минуту."
        if "TimeoutExpired" in err or "timed out" in err.lower():
            msg = "⏱ Sonnet не уложился в 90 секунд (rate limit Claude Max или API лагает). Сохранил, попробуй переформулировать короче или подожди минуту."
        await message.answer(msg, parse_mode=None)

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
        async with keep_typing(message.chat):
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
