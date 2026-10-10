#!/usr/bin/env python
"""Weekly digest script - generates and sends to Telegram."""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramNetworkError

from d_brain.bot.formatters import format_process_report

from d_brain.config import get_settings
from d_brain.services.git import VaultGit
from d_brain.services.processor import AgentProcessor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)



async def _send_with_retry(bot: Bot, chat_id: int, text: str, attempts: int = 3) -> None:
    """Retry network failures: TLS to api.telegram.org intermittently drops."""
    for attempt in range(1, attempts + 1):
        try:
            await bot.send_message(chat_id=chat_id, text=text)
            return
        except TelegramNetworkError:
            if attempt == attempts:
                raise
            logger.warning("Telegram send failed, retry %s/%s", attempt, attempts - 1)
            await asyncio.sleep(10 * attempt)

async def main() -> None:
    """Generate weekly digest and send to Telegram."""
    settings = get_settings()
    processor = AgentProcessor(settings.vault_path, settings.todoist_api_key)
    git = VaultGit(settings.vault_path)

    logger.info("Starting weekly digest generation...")

    result = processor.generate_weekly()

    if "error" in result:
        report = f"Error: {result['error']}"
        logger.error("Weekly digest failed: %s", result["error"])
    else:
        report = result.get("report", "No output")
        logger.info("Weekly digest generated successfully")
        # Commit any changes
        git.commit_and_push("chore: weekly digest")

    # Send to Telegram
    bot = Bot(
        token=settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    try:
        user_id = settings.allowed_user_ids[0] if settings.allowed_user_ids else None
        if not user_id:
            logger.error("No allowed user IDs configured")
            return

        try:
            await _send_with_retry(bot, user_id, report)
        except TelegramNetworkError:
            raise
        except Exception:
            # Fallback: send without HTML parsing
            messages = format_process_report({"report": report})
            for chunk in messages:
                await _send_with_retry(bot, user_id, chunk)

        logger.info("Weekly digest sent to user %s", user_id)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
