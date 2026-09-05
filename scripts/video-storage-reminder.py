#!/usr/bin/env python3
"""Send the weekly Telegram reminder to clean downloaded video files."""

from __future__ import annotations

import html
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
MESSAGE = (
    "🧹 <b>Напоминание</b>\n\n"
    "Проверь папки с роликами и удали ненужные видео и скриншоты, "
    "чтобы освободить место. Субтитры, тексты и разборы оставь."
)


def main() -> int:
    sys.path.insert(0, str(PROJECT_DIR / "src"))
    from d_brain.config import get_settings

    settings = get_settings()
    if not settings.telegram_bot_token or not settings.allowed_user_ids:
        print("Telegram settings are incomplete", file=sys.stderr)
        return 1

    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
    data = urllib.parse.urlencode(
        {
            "chat_id": str(settings.allowed_user_ids[0]),
            "text": html.unescape(MESSAGE),
            "parse_mode": "HTML",
        }
    ).encode()
    request = urllib.request.Request(url, data=data)
    with urllib.request.urlopen(request, timeout=15) as response:
        result = json.loads(response.read())
    if not result.get("ok"):
        raise RuntimeError(f"Telegram send failed: {result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
