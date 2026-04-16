"""Process command handler."""

import asyncio
import logging
from datetime import date

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from d_brain.bot.formatters import format_process_report
from d_brain.config import get_settings
from d_brain.services.git import VaultGit
from d_brain.services.memory_rag import index_daily
from d_brain.services.processor import AgentProcessor
from d_brain.services.wiki import refresh_wiki

router = Router(name="process")
logger = logging.getLogger(__name__)


@router.message(Command("process"))
async def cmd_process(message: Message) -> None:
    """Handle /process command - trigger Claude processing."""
    user_id = message.from_user.id if message.from_user else "unknown"
    logger.info("Process command triggered by user %s", user_id)

    status_msg = await message.answer("⏳ Обрабатываю... Это может занять до 10 минут.")

    settings = get_settings()
    processor = AgentProcessor(settings.vault_path, settings.todoist_api_key)
    git = VaultGit(settings.vault_path)

    # Run subprocess in thread to avoid blocking event loop
    async def process_with_progress() -> dict:
        task = asyncio.create_task(
            asyncio.to_thread(processor.process_daily, date.today())
        )

        elapsed = 0
        while not task.done():
            await asyncio.sleep(30)
            elapsed += 30
            if not task.done():
                try:
                    await status_msg.edit_text(
                        f"⏳ Обрабатываю... ({elapsed // 60}м {elapsed % 60}с)"
                    )
                except Exception:
                    pass  # Ignore edit errors

        return await task

    report = await process_with_progress()

    if "error" not in report:
        today = date.today().isoformat()
        await asyncio.to_thread(refresh_wiki, settings.vault_path)
        await asyncio.to_thread(index_daily, str(settings.vault_path))
        await asyncio.to_thread(git.commit_and_push, f"chore: process daily {today}")

    # Format and send report
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
