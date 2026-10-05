"""Button handlers for reply keyboard."""

import logging
import os
from pathlib import Path

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from d_brain.bot.handlers.backend import _replace_env_value, _replace_env_values
from d_brain.bot.keyboards import (
    CHAT_BUTTON_LABELS, CODEX_CHAT_MODEL, CODEX_MODE_EFFORT, CODEX_WORK_MODEL,
    WORK_BUTTON_LABELS, get_message_keyboard, CLAUDE_WORK_MODEL, CLAUDE_CHAT_MODEL,
)
from d_brain.config import get_settings

router = Router(name="buttons")
logger = logging.getLogger(__name__)


@router.message(F.text.in_(WORK_BUTTON_LABELS))
async def btn_work(message: Message, state: FSMContext) -> None:
    """Select Astra max on Codex; retain the Claude effort selector."""
    await _set_effort(message, state, "xhigh", "очень высокий", "🛠",
                      CODEX_WORK_MODEL, "GPT-6 Astra")


@router.message(F.text == "⚙️ Обработать")
async def btn_process(message: Message) -> None:
    """Handle Process button."""
    from d_brain.bot.handlers.process import cmd_process

    await cmd_process(message)


@router.message(F.text == "📅 Неделя")
async def btn_weekly(message: Message) -> None:
    """Handle Weekly button."""
    from d_brain.bot.handlers.weekly import cmd_weekly

    await cmd_weekly(message)


@router.message(F.text.in_(CHAT_BUTTON_LABELS))
async def btn_chat(message: Message, state: FSMContext) -> None:
    """Select Sol max on Codex without calling a model."""
    await _set_effort(message, state, "max", "максимальный", "💬",
                      CODEX_CHAT_MODEL, "GPT-6.1 Sol")


async def _set_effort(
    message: Message, state: FSMContext, effort: str, label: str, icon: str,
    codex_model: str, model_label: str,
) -> None:
    settings = get_settings()
    if message.from_user is None or message.from_user.id not in settings.admin_user_ids:
        await message.answer("Менять уровень мышления может только администратор.")
        return
    if settings.ai_backend == "claude":
        model = CLAUDE_WORK_MODEL if effort == "xhigh" else CLAUDE_CHAT_MODEL
        values = dict.fromkeys(("CLAUDE_MODEL", "CLAUDE_MODEL_CHAT", "CLAUDE_MODEL_AGENT"), model)
        values["CLAUDE_EFFORT"] = effort
        confirmation = f"{icon} Включил {'Opus 5.5' if effort == 'xhigh' else 'Sonnet 5.5'}."
    else:
        values = {
            "CODEX_MODEL": codex_model,
            "CODEX_MODEL_CHAT": codex_model,
            "CODEX_MODEL_AGENT": codex_model,
            "CODEX_REASONING_EFFORT": CODEX_MODE_EFFORT,
        }
        confirmation = f"{icon} Включил {model_label}, уровень мышления — максимальный (max)."
    try:
        _replace_env_values(values)
    except OSError:
        logger.exception("Failed to persist model selection")
        await message.answer("Не удалось сохранить режим. Настройка не изменена.")
        return
    os.environ.update(values)
    await state.set_state(None)
    await message.answer(
        confirmation,
        reply_markup=get_message_keyboard(message),
    )


@router.message(F.text == "❓ Помощь")
async def btn_help(message: Message) -> None:
    """Handle Help button."""
    from d_brain.bot.handlers.commands import cmd_help

    await cmd_help(message)


@router.message(F.text.in_({"🤖 Codex", "🤖 Codex ✓"}))
async def btn_codex(message: Message, state: FSMContext) -> None:
    await select_provider(message, state, "codex")


async def select_provider(message: Message, state: FSMContext, provider: str) -> None:
    settings = get_settings()
    if message.from_user is None or message.from_user.id not in settings.admin_user_ids:
        await message.answer("Менять модель может только администратор.")
        return
    work = (settings.claude_effort == "xhigh" if settings.ai_backend == "claude"
            else (settings.codex_model_chat.strip() or settings.codex_model) == CODEX_WORK_MODEL)
    if provider == "claude":
        from d_brain.bot.handlers.backend import _probe_claude_auth
        model = CLAUDE_WORK_MODEL if work else CLAUDE_CHAT_MODEL
        effort = "xhigh" if work else "max"
        ok, error = await _probe_claude_auth(model=model, effort=effort)
        if not ok:
            await message.answer(f"Claude недоступен. Модель не изменена.\n{error}")
            return
        values = dict.fromkeys(("CLAUDE_MODEL", "CLAUDE_MODEL_CHAT", "CLAUDE_MODEL_AGENT"), model)
        values["CLAUDE_EFFORT"] = effort
    else:
        if not (Path.home() / ".codex" / "auth.json").exists():
            await message.answer("Codex не авторизован. Модель не изменена.")
            return
        model = CODEX_WORK_MODEL if work else CODEX_CHAT_MODEL
        values = dict.fromkeys(("CODEX_MODEL", "CODEX_MODEL_CHAT", "CODEX_MODEL_AGENT"), model)
        values["CODEX_REASONING_EFFORT"] = CODEX_MODE_EFFORT
    values["AI_BACKEND"] = provider
    try:
        _replace_env_values(values)
    except OSError:
        logger.exception("Failed to persist provider selection")
        await message.answer("Не удалось сохранить модель. Настройка не изменена.")
        return
    os.environ.update(values)
    await state.set_state(None)
    await message.answer(f"Переключился на {'Claude' if provider == 'claude' else 'Codex'}.",
                         reply_markup=get_message_keyboard(message))
