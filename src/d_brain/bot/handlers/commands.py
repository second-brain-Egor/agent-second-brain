"""Command handlers for /start, /help, /status, /silent, /chat."""

from datetime import date

from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from d_brain.bot.keyboards import get_main_keyboard
from d_brain.bot.states import SilentState
from d_brain.config import get_settings
from d_brain.services.session import SessionStore
from d_brain.services.storage import VaultStorage

router = Router(name="commands")


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    """Handle /start command."""
    await message.answer(
        "<b>d-brain</b> - твой голосовой дневник\n\n"
        "Отправляй мне:\n"
        "🎤 Голосовые сообщения\n"
        "💬 Текст\n"
        "📷 Фото\n"
        "↩️ Пересланные сообщения\n\n"
        "Всё будет сохранено и обработано.\n\n"
        "<b>Команды:</b>\n"
        "/status - статус сегодняшнего дня\n"
        "/process - обработать записи\n"
        "/do - выполнить произвольный запрос\n"
        "/weekly - недельный дайджест\n"
        "/silent - тихий режим (только сохранение)\n"
        "/chat - вернуться в диалог\n"
        "/voice - включить/выключить голосовые ответы\n"
        "/help - справка",
        reply_markup=get_main_keyboard(),
    )


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    """Handle /help command."""
    await message.answer(
        "<b>Как использовать d-brain:</b>\n\n"
        "1. Отправь голосовое — я транскрибирую и сохраню\n"
        "2. Отправь текст — сохраню как есть\n"
        "3. Отправь фото — сохраню в attachments\n"
        "4. Перешли сообщение — сохраню с источником\n\n"
        "Вечером используй /process для обработки:\n"
        "Мысли → Obsidian, Задачи → Todoist\n\n"
        "<b>Команды:</b>\n"
        "/status - сколько записей сегодня\n"
        "/process - обработать записи\n"
        "/do - выполнить произвольный запрос\n"
        "/weekly - недельный дайджест\n"
        "/voice - включить/выключить голосовые ответы\n\n"
        "<i>Пример: /do перенеси просроченные задачи на понедельник</i>"
    )


@router.message(Command("status"))
async def cmd_status(message: Message) -> None:
    """Handle /status command."""
    user_id = message.from_user.id if message.from_user else 0
    settings = get_settings()
    storage = VaultStorage(settings.vault_path)

    # Log command
    session = SessionStore(settings.vault_path)
    session.append(user_id, "command", cmd="/status")

    today = date.today()
    content = storage.read_daily(today)

    if not content:
        await message.answer(f"📅 <b>{today}</b>\n\nЗаписей пока нет.")
        return

    lines = content.strip().split("\n")
    entries = [line for line in lines if line.startswith("## ")]

    voice_count = sum(1 for e in entries if "[voice]" in e)
    text_count = sum(1 for e in entries if "[text]" in e)
    photo_count = sum(1 for e in entries if "[photo]" in e)
    forward_count = sum(1 for e in entries if "[forward from:" in e)

    total = len(entries)

    # Get weekly stats from session
    week_stats = ""
    stats = session.get_stats(user_id, days=7)
    if stats:
        week_stats = "\n\n<b>За 7 дней:</b>"
        for entry_type, count in sorted(stats.items()):
            week_stats += f"\n• {entry_type}: {count}"

    await message.answer(
        f"📅 <b>{today}</b>\n\n"
        f"Всего записей: <b>{total}</b>\n"
        f"- 🎤 Голосовых: {voice_count}\n"
        f"- 💬 Текстовых: {text_count}\n"
        f"- 📷 Фото: {photo_count}\n"
        f"- ↩️ Пересланных: {forward_count}"
        f"{week_stats}"
    )


@router.message(Command("silent"))
async def cmd_silent(message: Message, state: FSMContext) -> None:
    """Switch to silent mode — save only, no AI responses."""
    await state.set_state(SilentState.active)
    await message.answer(
        "🔇 <b>Тихий режим</b>\n\n"
        "Сообщения сохраняются, но AI не отвечает.\n"
        "Для возврата в диалог: /chat"
    )


@router.message(Command("chat"))
async def cmd_chat(message: Message, state: FSMContext) -> None:
    """Switch back to dialog mode."""
    # Save voice_mode preference before clearing state
    data = await state.get_data()
    voice_mode = data.get("voice_mode", False)
    await state.clear()
    if voice_mode:
        await state.update_data(voice_mode=True)
    await message.answer(
        "💬 <b>Диалоговый режим</b>\n\n"
        "AI отвечает на каждое сообщение."
    )


@router.message(Command("voice"), StateFilter("*"))
async def cmd_voice(message: Message, state: FSMContext) -> None:
    """Toggle voice reply mode on/off."""
    data = await state.get_data()
    if data.get("voice_mode", False):
        await state.update_data(voice_mode=False)
        await message.answer(
            "🔇 <b>Голосовые ответы выключены</b>\n\n"
            "Бот отвечает текстом.\n"
            "/voice — включить снова"
        )
    else:
        await state.update_data(voice_mode=True)
        await message.answer(
            "🔊 <b>Голосовые ответы включены</b>\n\n"
            "Бот будет отвечать голосом (edge-tts).\n"
            "/voice — выключить"
        )
