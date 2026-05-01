#!/usr/bin/env python3
"""Send one-off Todoist reminders to Telegram."""

from __future__ import annotations

import html
import json
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
SENT_STATE = PROJECT_DIR / "logs" / "todoist-reminders-sent.json"
REMINDER_PREFIX = "Напомнить:"


def load_sent_ids() -> set[str]:
    if not SENT_STATE.exists():
        return set()
    try:
        data = json.loads(SENT_STATE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return set()
    return {str(item) for item in data if item}


def save_sent_ids(sent_ids: set[str]) -> None:
    SENT_STATE.parent.mkdir(parents=True, exist_ok=True)
    SENT_STATE.write_text(
        json.dumps(sorted(sent_ids), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def due_time_utc(task) -> datetime | None:
    due = getattr(task, "due", None)
    value = getattr(due, "date", None) if due else None
    if not isinstance(value, datetime):
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def send_telegram(text: str, chat_id: str, token: str) -> None:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode(
        {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
        }
    ).encode()
    request = urllib.request.Request(url, data=data)
    with urllib.request.urlopen(request, timeout=15) as response:
        result = json.loads(response.read())
    if not result.get("ok"):
        raise RuntimeError(f"Telegram send failed: {result}")


def main() -> int:
    sys.path.insert(0, str(PROJECT_DIR / "src"))

    from d_brain.config import get_settings
    from todoist_api_python.api import TodoistAPI

    settings = get_settings()
    if not settings.todoist_api_key:
        print("TODOIST_API_KEY is not set", file=sys.stderr)
        return 1
    if not settings.telegram_bot_token or not settings.allowed_user_ids:
        print("Telegram settings are incomplete", file=sys.stderr)
        return 1

    api = TodoistAPI(settings.todoist_api_key)
    sent_ids = load_sent_ids()
    now = datetime.now(timezone.utc)
    sent_count = 0

    for page in api.get_tasks(limit=200):
        for task in page:
            task_id = str(getattr(task, "id", ""))
            content = getattr(task, "content", "") or ""
            if not task_id or task_id in sent_ids:
                continue
            if not content.casefold().startswith(REMINDER_PREFIX.casefold()):
                continue

            due_at = due_time_utc(task)
            if due_at is None or due_at > now:
                continue

            message = content[len(REMINDER_PREFIX):].strip() or content.strip()
            description = (getattr(task, "description", "") or "").strip()
            text = f"⏰ <b>Напоминание</b>\n\n{html.escape(message)}"
            if description:
                text += f"\n\n{html.escape(description)}"

            send_telegram(text, str(settings.allowed_user_ids[0]), settings.telegram_bot_token)
            sent_ids.add(task_id)
            save_sent_ids(sent_ids)
            api.complete_task(task_id)
            sent_count += 1

    save_sent_ids(sent_ids)
    if sent_count:
        print(f"Sent {sent_count} Todoist reminder(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
