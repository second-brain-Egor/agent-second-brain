"""Evening reminder per v3 §7.1.

При первом сообщении после 20:00 (по таймзоне пользователя) — если
`vault/daily/{today}.md` ещё не имеет маркера `[processed]`/`[summary]`,
ответу бота добавляется строка-подсказка нажать «Обработать».

Состояние «уже напомнили сегодня» хранится в `vault/.session/last-evening-reminder.txt`
(одна строка с датой YYYY-MM-DD). Один раз за вечер, не каждое сообщение.
"""

from __future__ import annotations

import logging
import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)

EVENING_HOUR = 20
REMINDER_TEXT = "💡 День не обработан. Нажми «Обработать» когда будешь готов."
PROCESSED_MARKERS = ("[processed]", "[summary]", "<!-- ✓ processed -->")


def _state_path(vault_path: Path) -> Path:
    return vault_path / ".session" / "last-evening-reminder.txt"


def _user_tz() -> ZoneInfo:
    tz_name = (os.environ.get("TZ") or "Europe/Moscow").strip() or "Europe/Moscow"
    try:
        return ZoneInfo(tz_name)
    except Exception:
        return ZoneInfo("Europe/Moscow")


def _today_local() -> tuple[str, datetime]:
    now = datetime.now(_user_tz())
    return now.strftime("%Y-%m-%d"), now


def _is_day_processed(vault_path: Path, today: str) -> bool:
    daily = vault_path / "daily" / f"{today}.md"
    if not daily.exists():
        return False
    try:
        content = daily.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return False
    return any(marker in content for marker in PROCESSED_MARKERS)


def _already_reminded_today(vault_path: Path, today: str) -> bool:
    path = _state_path(vault_path)
    if not path.exists():
        return False
    try:
        return path.read_text(encoding="utf-8").strip() == today
    except OSError:
        return False


def _mark_reminded(vault_path: Path, today: str) -> None:
    path = _state_path(vault_path)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(today, encoding="utf-8")
    except OSError:
        logger.exception("Failed to write evening-reminder state")


def maybe_evening_reminder(vault_path: Path) -> str:
    """Возвращает строку-напоминание или пустую строку.

    Условия (все должны быть выполнены):
    1. Текущее время в TZ пользователя >= 20:00.
    2. Сегодняшний daily не помечен как обработанный.
    3. Сегодня ещё не напоминали.
    """
    today, now = _today_local()
    if now.hour < EVENING_HOUR:
        return ""
    if _is_day_processed(vault_path, today):
        return ""
    if _already_reminded_today(vault_path, today):
        return ""
    _mark_reminded(vault_path, today)
    return REMINDER_TEXT
