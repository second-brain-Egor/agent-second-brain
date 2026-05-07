"""Reply keyboards for Telegram bot."""

from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Main reply keyboard with common commands."""
    builder = ReplyKeyboardBuilder()
    # First row: main commands
    builder.button(text="📊 Статус")
    builder.button(text="⚙️ Обработать")
    builder.button(text="📅 Неделя")
    # Second row: additional
    builder.button(text="✨ Запрос")
    builder.button(text="🤖 Модель")
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
