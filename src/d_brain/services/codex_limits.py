"""Свежий недельный лимит подписки через локальный Codex, без запуска модели."""
from __future__ import annotations

import asyncio
import contextlib
import json
import math
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

REQUEST_TIMEOUT = 30
WEEK_MINUTES = 7 * 24 * 60


class CodexLimitsError(RuntimeError):
    """Понятная пользователю ошибка без внутренних ответов и учётных данных."""


def parse_weekly_limits(payload: dict) -> str:
    """Неделя может находиться в любом из двух окон; другие лимиты не подходят."""
    buckets = payload.get("rateLimitsByLimitId")
    limits = buckets.get("codex") if isinstance(buckets, dict) else None
    if limits is None:
        limits = payload.get("rateLimits")
    if not isinstance(limits, dict) or limits.get("limitId") not in (None, "codex"):
        raise CodexLimitsError("Codex не вернул недельный лимит подписки.")
    for name in ("primary", "secondary"):
        window = limits.get(name)
        if not isinstance(window, dict) or window.get("windowDurationMins") != WEEK_MINUTES:
            continue
        used, reset = window.get("usedPercent"), window.get("resetsAt")
        if (type(used) not in (int, float) or not math.isfinite(used) or not 0 <= used <= 100
                or type(reset) not in (int, float) or not math.isfinite(reset) or reset <= 0):
            raise CodexLimitsError("Codex вернул неполные данные недельного лимита.")
        try:
            resets_at = datetime.fromtimestamp(reset, ZoneInfo("Europe/Moscow"))
        except (OverflowError, OSError, ValueError) as error:
            raise CodexLimitsError("Codex вернул неверное время сброса лимита.") from error
        remaining = f"{100 - used:g}".replace(".", ",")
        return (f"📊 Недельный лимит Codex: осталось <b>{remaining}%</b>.\n\n"
                f"Сброс — <b>{resets_at:%d.%m.%Y в %H:%M} по Москве</b>.")
    raise CodexLimitsError("Codex не вернул недельный лимит подписки.")


async def read_weekly_limits(codex_bin: str, project: Path) -> str:
    """Каждое нажатие читает актуальный статус аккаунта через app-server stdio."""
    process = None

    async def send(message: dict) -> None:
        process.stdin.write((json.dumps(message) + "\n").encode())
        await process.stdin.drain()

    async def response(request_id: int) -> dict:
        while line := await process.stdout.readline():
            message = json.loads(line)
            if not isinstance(message, dict) or message.get("id") != request_id:
                continue
            if "error" in message:
                raise CodexLimitsError("Codex отклонил запрос лимита. Свежие данные не получены.")
            result = message.get("result")
            if not isinstance(result, dict):
                break
            return result
        raise CodexLimitsError("Codex не вернул ответ о лимите.")

    try:
        async with asyncio.timeout(REQUEST_TIMEOUT):
            process = await asyncio.create_subprocess_exec(
                codex_bin, "app-server", "--listen", "stdio://", cwd=project,
                stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.DEVNULL,
            )
            await send({"id": 1, "method": "initialize", "params": {
                "clientInfo": {"name": "second_brain_limits", "version": "1.0.0"},
            }})
            await response(1)
            await send({"method": "initialized"})
            await send({"id": 2, "method": "account/rateLimits/read"})
            return parse_weekly_limits(await response(2))
    except TimeoutError as error:
        raise CodexLimitsError("Codex не ответил за 30 секунд. Попробуй нажать кнопку ещё раз.") from error
    except OSError as error:
        raise CodexLimitsError("Не удалось обратиться к Codex для проверки лимита.") from error
    except (ValueError, TypeError) as error:
        raise CodexLimitsError("Codex вернул непонятный ответ о лимите.") from error
    finally:
        if process is not None:
            if process.returncode is None:
                with contextlib.suppress(ProcessLookupError):
                    process.terminate()
                try:
                    await asyncio.wait_for(process.wait(), 3)
                except TimeoutError:
                    with contextlib.suppress(ProcessLookupError):
                        process.kill()
                    await process.wait()
