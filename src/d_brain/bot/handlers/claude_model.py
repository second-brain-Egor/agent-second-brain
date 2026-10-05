"""Direct Claude selection; model choice belongs to Work and Discuss."""
import getpass
from pathlib import Path

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

router = Router(name="claude_model")
PENDING_SWITCH_PATH = Path(f"/tmp/d-brain-pending-model-switch-{getpass.getuser()}.json")


@router.message(F.text.in_({"🧠 Claude", "🧠 Claude ✓"}))
async def btn_claude_model(message: Message, state: FSMContext) -> None:
    from d_brain.bot.handlers.buttons import select_provider
    await select_provider(message, state, "claude")


@router.callback_query(F.data.startswith("claude_model:"))
async def obsolete_model_menu(callback: CallbackQuery) -> None:
    await callback.answer("Модель выбирается кнопками Работа и Обсудить.")
    if callback.message is not None:
        await callback.message.edit_reply_markup(reply_markup=None)
