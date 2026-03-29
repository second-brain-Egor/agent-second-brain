"""Handlers for reading Telegram channels via user account (Telethon)."""

import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from d_brain.bot.states import TgConnectState
from d_brain.config import get_settings
from d_brain.services.telegram_reader import TelegramReader

logger = logging.getLogger(__name__)
router = Router(name="channel")

_reader: TelegramReader | None = None


def _get_reader() -> TelegramReader:
    global _reader
    if _reader is None:
        settings = get_settings()
        if not settings.telegram_api_id or not settings.telegram_api_hash:
            raise RuntimeError(
                "TELEGRAM_API_ID и TELEGRAM_API_HASH не заданы в .env\n"
                "Получи их на https://my.telegram.org"
            )
        sessions_path = settings.vault_path / ".sessions"
        sessions_path.mkdir(parents=True, exist_ok=True)
        _reader = TelegramReader(settings.telegram_api_id, settings.telegram_api_hash, sessions_path)
    return _reader


@router.message(Command("tg_connect"))
async def cmd_tg_connect(message: Message, state: FSMContext) -> None:
    """Start Telegram user account authorization."""
    try:
        reader = _get_reader()
    except RuntimeError as e:
        await message.answer(f"❌ {e}")
        return

    if await reader.is_authorized():
        await message.answer("✅ Уже авторизован. Используй /read для чтения каналов.")
        return

    await state.set_state(TgConnectState.waiting_phone)
    await message.answer(
        "📱 Введи номер телефона в формате +79001234567\n"
        "(тот, на который зарегистрирован Telegram)"
    )


@router.message(TgConnectState.waiting_phone)
async def handle_tg_phone(message: Message, state: FSMContext) -> None:
    """Handle phone number input."""
    phone = (message.text or "").strip()
    if not phone.startswith("+"):
        await message.answer("❌ Формат: +79001234567")
        return

    try:
        reader = _get_reader()
        await reader.send_code(phone)
        await state.update_data(phone=phone)
        await state.set_state(TgConnectState.waiting_code)
        await message.answer(
            f"📨 Код отправлен на {phone}\nВведи код из Telegram:"
        )
    except Exception as e:
        logger.exception("Error sending code")
        await message.answer(f"❌ Ошибка: {e}")
        await state.clear()


@router.message(TgConnectState.waiting_code)
async def handle_tg_code(message: Message, state: FSMContext) -> None:
    """Handle auth code input."""
    code = (message.text or "").strip().replace(" ", "")
    try:
        reader = _get_reader()
        await reader.sign_in(code)
        await state.clear()
        await message.answer(
            "✅ Авторизация прошла успешно!\n\n"
            "Теперь можешь читать каналы:\n"
            "<code>/read @channel 20</code>"
        )
    except Exception as e:
        err = str(e)
        if "2FA" in err or "password" in err.lower():
            await state.set_state(TgConnectState.waiting_password)
            await message.answer("🔐 Введи пароль двухфакторной аутентификации:")
        else:
            logger.exception("Sign-in error")
            await message.answer(f"❌ Ошибка: {e}")
            await state.clear()


@router.message(TgConnectState.waiting_password)
async def handle_tg_password(message: Message, state: FSMContext) -> None:
    """Handle 2FA password."""
    password = message.text or ""
    try:
        reader = _get_reader()
        await reader.sign_in("", password=password)
        await state.clear()
        await message.answer("✅ Авторизован (2FA). Используй /read для чтения каналов.")
    except Exception as e:
        logger.exception("2FA error")
        await message.answer(f"❌ Ошибка: {e}")
        await state.clear()


@router.message(Command("read"))
async def cmd_read_channel(message: Message) -> None:
    """Read last N messages from a channel. Usage: /read @channel [N]"""
    args = (message.text or "").split()[1:]
    if not args:
        await message.answer(
            "Использование: <code>/read @channel [количество]</code>\n"
            "Пример: <code>/read @durov 10</code>"
        )
        return

    channel = args[0]
    limit = 10
    if len(args) > 1:
        try:
            limit = int(args[1])
        except ValueError:
            pass

    status_msg = await message.answer(f"⏳ Читаю {channel}...")

    try:
        reader = _get_reader()
        messages = await reader.get_messages(channel, limit=limit)
    except RuntimeError as e:
        await status_msg.edit_text(f"❌ {e}")
        return
    except Exception as e:
        logger.exception("Error reading channel")
        await status_msg.edit_text(f"❌ Ошибка: {e}")
        return

    if not messages:
        await status_msg.edit_text(f"В {channel} нет сообщений.")
        return

    lines = [f"<b>📢 {channel}</b> — последние {len(messages)} сообщений:\n"]
    for msg in messages:
        header = f"[{msg['date']}]"
        if msg["sender"]:
            header += f" @{msg['sender']}"
        if msg["fwd_from"]:
            header += f" (fwd: {msg['fwd_from']})"
        text = (msg["text"] or "").strip()
        if len(text) > 300:
            text = text[:300] + "…"
        if text:
            lines.append(f"{header}\n{text}\n")

    result = "\n".join(lines)
    # Split if too long
    if len(result) > 4000:
        result = result[:4000] + "\n…(обрезано)"

    await status_msg.edit_text(result)


@router.message(Command("tg_status"))
async def cmd_tg_status(message: Message) -> None:
    """Check Telethon auth status."""
    try:
        reader = _get_reader()
        authorized = await reader.is_authorized()
        if authorized:
            me = await reader.client.get_me()
            name = getattr(me, "first_name", "") or ""
            username = getattr(me, "username", "") or ""
            await message.answer(
                f"✅ Авторизован как {name}"
                + (f" (@{username})" if username else "")
            )
        else:
            await message.answer("❌ Не авторизован. Используй /tg_connect")
    except RuntimeError as e:
        await message.answer(f"❌ {e}")
