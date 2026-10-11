"""Расход по запросам: одна строка на каждый вызов модели в vault/.data/usage.jsonl.

Сводка по моделям и уровням мышления — `uv run python scripts/usage_report.py`.
Стоимость у Claude — цена по прайсу API (`total_cost_usd`): подписка столько не списывает,
но для сравнения уровней между собой она годится.
"""
from __future__ import annotations

import json
import logging
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)

USAGE_LOG = Path("vault") / ".data" / "usage.jsonl"
MOSCOW = ZoneInfo("Europe/Moscow")


def _option(cmd: list[str], name: str) -> str:
    try:
        return str(cmd[cmd.index(name) + 1])
    except (ValueError, IndexError):
        return ""


def _codex_effort(cmd: list[str]) -> str:
    for part in cmd:
        if str(part).startswith("model_reasoning_effort="):
            return str(part).split("=", 1)[1].strip('"')
    return ""


def summarize(cmd: list[str], output: str, backend: str) -> dict | None:
    """Tokens, steps and time of one CLI call; None if the stream has no final event."""
    record: dict = {"backend": backend, "model": _option(cmd, "--model"),
                    "effort": _option(cmd, "--effort") if backend == "claude" else _codex_effort(cmd)}
    final = None
    steps = 0
    for line in output.splitlines():
        if not line.startswith("{"):
            continue
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if not isinstance(event, dict):
            continue
        kind = event.get("type")
        if backend == "claude" and kind == "system" and event.get("subtype") == "init":
            record["model"] = event.get("model") or record["model"]
        elif backend == "claude" and kind == "result":
            final = event
        elif backend == "codex" and kind == "turn.completed":
            final = event
        elif backend == "codex" and kind == "item.completed":
            steps += 1
    if final is None:
        return None
    usage = final.get("usage") or {}
    if backend == "claude":
        details = usage.get("output_tokens_details") or {}
        record.update(
            seconds=round((final.get("duration_ms") or 0) / 1000, 1),
            steps=final.get("num_turns"),
            input=usage.get("input_tokens", 0),
            cache_read=usage.get("cache_read_input_tokens", 0),
            cache_write=usage.get("cache_creation_input_tokens", 0),
            output=usage.get("output_tokens", 0),
            thinking=details.get("thinking_tokens", 0),
            cost_usd=final.get("total_cost_usd"),
            ok=not final.get("is_error"),
            denied=len(final.get("permission_denials") or []),
        )
    else:
        cached = usage.get("cached_input_tokens", 0)
        record.update(
            steps=steps,
            input=max(0, usage.get("input_tokens", 0) - cached),
            cache_read=cached,
            cache_write=usage.get("cache_write_input_tokens", 0),
            output=usage.get("output_tokens", 0),
            thinking=usage.get("reasoning_output_tokens", 0),
            ok=True,
        )
    return record


def record(project: Path, cmd: list[str], output: str, backend: str, execution,
           seconds: float, returncode: int) -> None:
    """Append one line; never breaks the request itself."""
    try:
        if not execution.persistent:
            return  # временный чат: никаких следов на диске
        line = summarize([str(part) for part in cmd], output, backend)
        if line is None:
            return
        line.setdefault("seconds", round(seconds, 1))
        if returncode:
            line["ok"] = False
        request = str(execution.data.get("request") or "")
        request = " ".join(re.split(r"=== USER MESSAGES? ===", request)[-1].split())
        line = {
            "time": datetime.now(MOSCOW).isoformat(timespec="seconds"),
            "origin": execution.data.get("origin", ""),
            "scope": execution.data.get("scope", ""),
            "task": execution.id,
            **line,
            "request": request[-160:],
        }
        path = Path(project) / USAGE_LOG
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as log:
            log.write(json.dumps(line, ensure_ascii=False) + "\n")
    except Exception:
        logger.warning("Не удалось записать расход запроса", exc_info=True)
