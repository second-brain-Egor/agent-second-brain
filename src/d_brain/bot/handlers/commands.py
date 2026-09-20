"""Command handlers for /start, /help, /restart, /silent, /chat."""

import asyncio
import shlex

from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from d_brain.bot.keyboards import get_main_keyboard
from d_brain.bot.states import SilentState
from d_brain.config import Settings, get_settings
from d_brain.services.session import SessionStore

router = Router(name="commands")


def _is_admin(user_id: int, settings: Settings) -> bool:
    """Return True when the user can run admin commands."""
    return user_id in settings.admin_user_ids


async def _run_admin_command(command: str, timeout: int = 30) -> tuple[int, str, str]:
    """Execute configured admin command and collect output."""
    args = shlex.split(command)
    if not args:
        return 2, "", "empty command"

    try:
        proc = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
    except OSError as exc:
        return 127, "", str(exc)
    try:
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except TimeoutError:
        proc.kill()
        await proc.wait()
        return 124, "", "timeout"

    return (
        proc.returncode or 0,
        stdout.decode("utf-8", errors="replace").strip(),
        stderr.decode("utf-8", errors="replace").strip(),
    )


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    """Handle /start command."""
    await message.answer(
        "<b>Твой помощник</b> — записи, вопросы и дела\n\n"
        "Отправляй мне:\n"
        "🎤 Голосовые сообщения\n"
        "💬 Текст\n"
        "📷 Фото\n"
        "↩️ Пересланные сообщения\n\n"
        "Всё будет сохранено и обработано.\n\n"
        "<b>Команды:</b>\n"
        "/ask - ответить на вопрос по запросу\n"
        "/stop - остановить текущую задачу\n"
        "/tasks - состояние задачи без обращения к модели\n"
        "/process - обработать записи\n"
        "/do - выполнить произвольный запрос\n"
        "/weekly - недельный дайджест\n"
        "/restart - перезапустить бота (для администратора)\n"
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
        "<b>Как пользоваться помощником:</b>\n\n"
        "1. Отправь голосовое — я транскрибирую и сохраню\n"
        "2. Отправь текст — сохраню как есть\n"
        "3. Отправь фото — сохраню во вложения\n"
        "4. Перешли сообщение — сохраню с источником\n\n"
        "Записи обрабатываются автоматически. Для ручного запуска — /process:\n"
        "Мысли → Obsidian, Задачи → Todoist\n\n"
        "<b>Команды:</b>\n"
        "/ask - ответить на вопрос по запросу\n"
        "/stop - остановить текущую задачу\n"
        "/tasks - состояние задачи без обращения к модели\n"
        "/process - обработать записи\n"
        "/do - выполнить произвольный запрос\n"
        "/weekly - недельный дайджест\n"
        "/restart - перезапустить бота (для администратора)\n"
        "/voice - включить/выключить голосовые ответы\n\n"
        "<i>Пример: /do перенеси просроченные задачи на понедельник</i>",
        reply_markup=get_main_keyboard(),
    )


@router.message(Command("restart"))
async def cmd_restart(message: Message) -> None:
    """Handle /restart command for bot restart."""
    user_id = message.from_user.id if message.from_user else 0
    settings = get_settings()
    session = SessionStore(settings.vault_path)
    session.append(user_id, "command", cmd="/restart")

    if not _is_admin(user_id, settings):
        await message.answer("⛔ Команда доступна только администратору.")
        return

    restart_command = settings.admin_restart_command.strip()
    if not restart_command:
        await message.answer(
            "⚠️ Перезапуск не настроен.\n\n"
            "Нужно задать `ADMIN_RESTART_COMMAND` в `.env`."
        )
        return

    await message.answer("🔄 Команда перезапуска отправлена. Бот вернётся через несколько секунд.")
    asyncio.create_task(_run_admin_command(restart_command, timeout=10))


@router.message(Command("silent"))
async def cmd_silent(message: Message, state: FSMContext) -> None:
    """Switch to silent mode — save only, no AI responses."""
    await state.set_state(SilentState.active)
    await message.answer(
        "🔇 <b>Тихий режим</b>\n\n"
        "Сообщения сохраняются, но помощник не отвечает.\n"
        "Для возврата в диалог: /chat",
        reply_markup=get_main_keyboard(),
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
        "Помощник отвечает на каждое сообщение.",
        reply_markup=get_main_keyboard(),
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
            "/voice — включить снова",
            reply_markup=get_main_keyboard(),
        )
    else:
        await state.update_data(voice_mode=True)
        await message.answer(
            "🔊 <b>Голосовые ответы включены</b>\n\n"
            "Бот будет отвечать голосом (edge-tts).\n"
            "/voice — выключить",
            reply_markup=get_main_keyboard(),
        )
