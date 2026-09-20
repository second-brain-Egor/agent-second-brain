"""Button handlers for reply keyboard."""

import logging
import os

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from d_brain.bot.handlers.backend import _replace_env_value
from d_brain.bot.keyboards import CHAT_BUTTON, WORK_BUTTON, get_main_keyboard
from d_brain.config import get_settings

router = Router(name="buttons")
logger = logging.getLogger(__name__)


@router.message(F.text == WORK_BUTTON)
async def btn_work(message: Message, state: FSMContext) -> None:
    """Persist very high effort for subsequent messages."""
    await _set_effort(message, state, "xhigh", "очень высокий", "🛠")


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


@router.message(F.text.in_({CHAT_BUTTON, "✨ Запрос"}))
async def btn_chat(message: Message, state: FSMContext) -> None:
    """Persist medium effort for subsequent messages without calling a model."""
    await _set_effort(message, state, "medium", "средний", "💬")


async def _set_effort(
    message: Message, state: FSMContext, effort: str, label: str, icon: str,
) -> None:
    settings = get_settings()
    if message.from_user is None or message.from_user.id not in settings.admin_user_ids:
        await message.answer("Менять уровень мышления может только администратор.")
        return
    key = "CLAUDE_EFFORT" if settings.ai_backend == "claude" else "CODEX_REASONING_EFFORT"
    try:
        _replace_env_value(key, effort)
    except OSError:
        logger.exception("Failed to persist reasoning effort")
        await message.answer(f"Не удалось сохранить {label} уровень мышления. Настройка не изменена.")
        return
    os.environ[key] = effort
    await state.set_state(None)
    await message.answer(
        f"{icon} Включил {label} уровень мышления.",
        reply_markup=get_main_keyboard(),
    )


@router.message(F.text == "❓ Помощь")
async def btn_help(message: Message) -> None:
    """Handle Help button."""
    from d_brain.bot.handlers.commands import cmd_help

    await cmd_help(message)
