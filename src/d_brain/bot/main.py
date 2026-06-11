"""Telegram bot initialization and polling."""

import logging
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Update

from d_brain.config import Settings

logger = logging.getLogger(__name__)


def create_bot(settings: Settings) -> Bot:
    """Create and configure the Telegram bot."""
    return Bot(
        token=settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


def create_dispatcher() -> Dispatcher:
    """Create and configure the dispatcher with routers."""
    from d_brain.bot.handlers import ask, backend, buttons, channel, claude_model, commands, do, document, forward, photo, process, text, voice, web, weekly

    # Use memory storage for FSM (required for /do command state)
    dp = Dispatcher(storage=MemoryStorage())

    # Register routers - ORDER MATTERS
    dp.include_router(commands.router)
    dp.include_router(ask.router)
    dp.include_router(channel.router)  # Telegram user account reader
    dp.include_router(process.router)
    dp.include_router(weekly.router)
    dp.include_router(do.router)  # Before voice/text to catch FSM state
    dp.include_router(backend.router)  # 🤖 Модель: backend switcher (button + callbacks)
    dp.include_router(claude_model.router)  # 🧠 Claude: Opus/Sonnet/Fable switcher
    dp.include_router(buttons.router)  # Reply keyboard buttons
    dp.include_router(web.router)  # Веб-поиск fast-path (/web + интент) — до text catch-all
    dp.include_router(document.router)
    dp.include_router(voice.router)
    dp.include_router(photo.router)
    dp.include_router(forward.router)
    dp.include_router(text.router)  # Must be last (catch-all for text)
    return dp


MiddlewareHandler = Callable[[Update, dict[str, Any]], Awaitable[Any]]
MiddlewareType = Callable[[MiddlewareHandler, Update, dict[str, Any]], Awaitable[Any]]


def create_auth_middleware(settings: Settings) -> MiddlewareType:
    """Create middleware to check user authorization."""

    async def auth_middleware(
        handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: dict[str, Any],
    ) -> Any:
        user = None
        if event.message:
            user = event.message.from_user
        elif event.callback_query:
            user = event.callback_query.from_user

        # If no users allowed and not allow_all_users -> deny everyone
        if not settings.allowed_user_ids:
            logger.warning("Access denied: no allowed_user_ids configured and allow_all_users is False")
            return None

        # Check if user is in allowed list
        if user and user.id not in settings.allowed_user_ids:
            logger.warning("Unauthorized access attempt from user %s", user.id)
            return None

        return await handler(event, data)

    return auth_middleware


async def _announce_pending_switch(bot: Bot, marker_path, default_label: str) -> None:
    """If a pending switch marker exists, notify the chat and remove it."""
    import json

    if not marker_path.exists():
        return
    try:
        data = json.loads(marker_path.read_text(encoding="utf-8"))
        chat_id = int(data["chat_id"])
        label = str(data.get("label") or default_label)
        await bot.send_message(chat_id, f"✅ Готово, теперь на <b>{label}</b>.")
    except Exception:
        logger.exception("Failed to announce switch from %s", marker_path)
    finally:
        try:
            marker_path.unlink()
        except OSError:
            pass


async def _announce_pending_switches(bot: Bot) -> None:
    """Announce any pending model and/or backend switches after restart."""
    from d_brain.bot.handlers.claude_model import PENDING_SWITCH_PATH as MODEL_PATH
    from d_brain.bot.handlers.backend import PENDING_SWITCH_PATH as BACKEND_PATH

    await _announce_pending_switch(bot, BACKEND_PATH, "Claude")
    await _announce_pending_switch(bot, MODEL_PATH, "Claude")


async def run_bot(settings: Settings) -> None:
    """Run the bot with polling."""
    if not settings.allowed_user_ids:
        raise RuntimeError("ALLOWED_USER_IDS is empty; bot startup refused")

    if settings.allow_all_users:
        raise RuntimeError("ALLOW_ALL_USERS is enabled; bot startup refused")

    # Rotate large session files on startup
    from d_brain.services.session import SessionStore
    SessionStore(settings.vault_path).rotate_all()

    bot = create_bot(settings)
    dp = create_dispatcher()

    # Always filter updates by allowed Telegram user IDs.
    dp.update.middleware(create_auth_middleware(settings))

    await _announce_pending_switches(bot)

    logger.info("Starting bot polling...")
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()
