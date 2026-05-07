"""Telegram typing indicator that survives long-running tasks.

Telegram sends 'typing' action which auto-expires after ~5 seconds. For LLM
calls that take 20-60 seconds we need to re-send the action periodically.
"""

from __future__ import annotations

import asyncio
import contextlib
import logging
from collections.abc import AsyncIterator

from aiogram.types import Chat

logger = logging.getLogger(__name__)


@contextlib.asynccontextmanager
async def keep_typing(chat: Chat, action: str = "typing", interval: float = 4.0) -> AsyncIterator[None]:
    """Async context manager that keeps a chat action visible until the block exits.

    Usage:
        async with keep_typing(message.chat):
            response = await asyncio.to_thread(processor.do_heavy_work, ...)
    """
    stop = asyncio.Event()

    async def _loop() -> None:
        try:
            while not stop.is_set():
                try:
                    await chat.do(action=action)
                except Exception:
                    logger.debug("send_chat_action failed (non-critical)", exc_info=True)
                try:
                    await asyncio.wait_for(stop.wait(), timeout=interval)
                except TimeoutError:
                    continue
        except asyncio.CancelledError:
            pass

    task = asyncio.create_task(_loop())
    try:
        yield
    finally:
        stop.set()
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError, Exception):
            await task
