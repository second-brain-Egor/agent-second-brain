"""
Heartbeat: проверяет память, цели, дедлайны и отправляет напоминания в Telegram.
Запускается cron каждые 30 мин с 8 до 22.
"""

import json
import os
import subprocess
import sys
import urllib.request
import urllib.parse

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MCP_CONFIG = os.path.join(PROJECT_DIR, "mcp-config.json")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
ALLOWED_USER_IDS = os.environ.get("ALLOWED_USER_IDS", "[]")


def get_chat_id() -> str:
    """Extract chat ID from ALLOWED_USER_IDS."""
    return ALLOWED_USER_IDS.strip("[]").strip()


def run_claude() -> str:
    """Run Claude to check for reminders."""
    from datetime import date
    today = date.today().isoformat()

    prompt = f"""Сегодня {today}. Ты — heartbeat-агент.

Проверь:
1. memory/facts.md — недавние события, требующие действий
2. goals/3-weekly.md — прогресс по недельным целям
3. Задачи в Todoist с дедлайном сегодня/завтра (вызови mcp__todoist__get-tasks)

Если есть что-то важное — верни краткое напоминание в формате Telegram HTML.
Если нечего напоминать — верни ТОЛЬКО слово "SKIP" (без ничего другого).

Формат: <b>заголовок</b>, списки через \\n• пункт.
Допустимые теги: <b>, <i>, <code>.
Максимум 500 символов."""

    env = os.environ.copy()
    env["MCP_TIMEOUT"] = "30000"

    try:
        result = subprocess.run(
            [
                "flock", "-n", "/tmp/claude-heavy.lock",
                "claude",
                "--print",
                "--dangerously-skip-permissions",
                "--mcp-config", MCP_CONFIG,
                "-p", prompt,
            ],
            cwd=os.path.join(PROJECT_DIR, "vault"),
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
            env=env,
        )
        return result.stdout.strip() if result.returncode == 0 else ""
    except Exception as e:
        print(f"Claude error: {e}", file=sys.stderr)
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

    output = run_claude()

    if not output or output.strip().upper() == "SKIP":
        print("Nothing to report")
        return

    send_telegram(output, chat_id)
    print(f"Sent heartbeat ({len(output)} chars)")


if __name__ == "__main__":
    main()
