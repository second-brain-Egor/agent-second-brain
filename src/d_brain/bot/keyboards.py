"""Reply keyboards for Telegram bot."""

from aiogram.types import InlineKeyboardMarkup, Message, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from d_brain.config import get_settings

CHAT_BUTTON = "💬 Обсудить"
WORK_BUTTON = "🛠 Работа"


def get_message_keyboard(message: Message) -> ReplyKeyboardMarkup:
    private = getattr(getattr(message, "chat", None), "type", "private") == "private"
    user_id = message.from_user.id if private and message.from_user else 0
    return get_main_keyboard(user_id)


def get_main_keyboard(user_id: int | None = None) -> ReplyKeyboardMarkup:
    """Main reply keyboard with common commands."""
    builder = ReplyKeyboardBuilder()
    # First row: main commands
    builder.button(text=WORK_BUTTON)
    builder.button(text="⚙️ Обработать")
    settings = get_settings()
    owner = settings.temporary_chat_user_id
    label = "📅 Неделя"
    if owner and user_id in (None, owner):
        from d_brain.services.temporary_chat import NORMAL_CHAT, TEMPORARY_CHAT, enabled
        label = NORMAL_CHAT if enabled(settings) else TEMPORARY_CHAT
    builder.button(text=label)
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
