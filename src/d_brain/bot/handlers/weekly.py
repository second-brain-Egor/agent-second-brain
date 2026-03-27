"""Weekly digest command handler."""

import asyncio
import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from d_brain.bot.formatters import format_process_report
from d_brain.config import get_settings
from d_brain.services.git import VaultGit
from d_brain.services.processor import ClaudeProcessor

router = Router(name="weekly")
logger = logging.getLogger(__name__)


@router.message(Command("weekly"))
async def cmd_weekly(message: Message) -> None:
    """Handle /weekly command - generate weekly digest."""
    user_id = message.from_user.id if message.from_user else "unknown"
    logger.info("Weekly digest triggered by user %s", user_id)

    status_msg = await message.answer("⏳ Генерирую недельный дайджест...")

    settings = get_settings()
    processor = ClaudeProcessor(settings.vault_path, settings.todoist_api_key)
    git = VaultGit(settings.vault_path)

    async def run_with_progress() -> dict:
        task = asyncio.create_task(
            asyncio.to_thread(processor.generate_weekly)
        )

        elapsed = 0
        while not task.done():
            await asyncio.sleep(30)
            elapsed += 30
            if not task.done():
                try:
                    await status_msg.edit_text(
                        f"⏳ Генерирую дайджест... ({elapsed // 60}m {elapsed % 60}s)"
                    )
                except Exception:
                    pass

        return await task

    report = await run_with_progress()

    # Commit any changes (weekly goal updates, etc)
    if "error" not in report:
        await asyncio.to_thread(git.commit_and_push, "chore: weekly digest")

    messages = format_process_report(report)
    if messages:
        try:
            await status_msg.edit_text(messages[0])
        except Exception:
            await status_msg.edit_text(messages[0], parse_mode=None)
        for msg in messages[1:]:
            try:
                await message.answer(msg)
            except Exception:
                await message.answer(msg, parse_mode=None)
