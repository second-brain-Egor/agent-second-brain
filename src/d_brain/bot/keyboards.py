"""Reply keyboards for Telegram bot."""

from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from d_brain.config import get_settings

CHAT_BUTTON = "💬 Обсудить"
WORK_BUTTON = "🛠 Работа"


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Main reply keyboard with common commands."""
    builder = ReplyKeyboardBuilder()
    # First row: main commands
    builder.button(text=WORK_BUTTON)
    builder.button(text="⚙️ Обработать")
    builder.button(text="📅 Неделя")
    # Second row: conversation mode and model selectors.
    builder.button(text=CHAT_BUTTON)
    builder.button(text="🤖 Модель")
    builder.button(text="🧠 Claude")
    if get_settings().show_help_button:
        builder.button(text="❓ Помощь")
    builder.adjust(3, 3)
    # Let Telegram collapse the custom keyboard normally on Android.
    return builder.as_markup(resize_keyboard=True, is_persistent=False)


def get_backend_inline_keyboard(current: str) -> InlineKeyboardMarkup:
    """Inline keyboard for switching active AI backend (Claude/Codex)."""
    builder = InlineKeyboardBuilder()
    claude_label = "✅ Claude" if current == "claude" else "Claude"
    codex_label = "✅ Codex" if current == "codex" else "Codex"
    builder.button(text=claude_label, callback_data="backend:claude")
    builder.button(text=codex_label, callback_data="backend:codex")
    builder.adjust(2)
    return builder.as_markup()


def get_claude_model_inline_keyboard(current: str) -> InlineKeyboardMarkup:
    """Inline keyboard for switching Claude model (Opus/Sonnet/Fable)."""
    builder = InlineKeyboardBuilder()
    options = [("opus", "Opus"), ("sonnet", "Sonnet"), ("fable", "Fable")]
    for value, label in options:
        text = f"✅ {label}" if current == value else label
        builder.button(text=text, callback_data=f"claude_model:{value}")
    builder.adjust(3)
    return builder.as_markup()
