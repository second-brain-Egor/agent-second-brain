"""
Heartbeat: проверяет память, цели, дедлайны и отправляет напоминания в Telegram.
Запускается cron каждые 30 мин с 8 до 22.
"""

import json
import os
import sys
import urllib.parse
import urllib.request

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
ALLOWED_USER_IDS = os.environ.get("ALLOWED_USER_IDS", "[]")


def get_chat_id() -> str:
    """Extract chat ID from ALLOWED_USER_IDS."""
    return ALLOWED_USER_IDS.strip("[]").strip()


def run_agent() -> str:
    """Run the local OpenAI-backed agent to check for reminders."""
    from datetime import date

    sys.path.insert(0, os.path.join(PROJECT_DIR, "src"))

    from d_brain.config import get_settings
    from d_brain.services.processor import AgentProcessor

    today = date.today().isoformat()

    prompt = f"""Сегодня {today}. Ты — heartbeat-агент.

Проверь:
1. memory/facts.md — недавние события, требующие действий
2. goals/3-weekly.md — прогресс по недельным целям
3. Задачи в Todoist, связанные с сегодня и завтра

Если есть что-то важное — верни краткое напоминание в формате Telegram HTML.
Если нечего напоминать — верни ТОЛЬКО слово "SKIP" (без ничего другого).

Формат: <b>заголовок</b>, списки через \\n• пункт.
Допустимые теги: <b>, <i>, <code>.
Максимум 500 символов.
Ничего не меняй в файлах и не создавай задачи."""

    try:
        settings = get_settings()
        processor = AgentProcessor(settings.vault_path, settings.todoist_api_key)
        result = processor.execute_prompt(prompt, user_id=0)
        return result.get("report", "").strip() if "error" not in result else ""
    except Exception as e:
        print(f"Agent error: {e}", file=sys.stderr)
        return ""


def send_telegram(text: str, chat_id: str) -> None:
    """Send message via Telegram Bot API."""
    if not TELEGRAM_TOKEN or not chat_id:
        print("Missing TELEGRAM_TOKEN or chat_id", file=sys.stderr)
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
    }).encode()

    try:
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
            if not result.get("ok"):
                # Retry without HTML
                data = urllib.parse.urlencode({
                    "chat_id": chat_id,
                    "text": text,
                }).encode()
                req = urllib.request.Request(url, data=data)
                urllib.request.urlopen(req, timeout=10)
    except Exception as e:
        print(f"Telegram error: {e}", file=sys.stderr)


def main() -> None:
    chat_id = get_chat_id()
    if not chat_id:
        print("No chat_id configured", file=sys.stderr)
        sys.exit(1)

    output = run_agent()

    if not output or output.strip().upper() == "SKIP":
        print("Nothing to report")
        return

    send_telegram(output, chat_id)
    print(f"Sent heartbeat ({len(output)} chars)")


if __name__ == "__main__":
    main()
