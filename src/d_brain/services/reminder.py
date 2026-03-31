"""Smart reminder helper — checks if daily processing was done."""

import os
from datetime import datetime, date
from pathlib import Path

# Track if reminder was already shown this session
_reminder_shown_today: str = ""


def check_process_reminder(vault_path: str | Path) -> str | None:
    """Check if it's after 20:00 and daily processing wasn't done.
    
    Returns reminder text or None.
    Shows reminder only once per day per session.
    """
    global _reminder_shown_today
    
    tz_name = os.environ.get("TZ", "UTC")
    try:
        from zoneinfo import ZoneInfo
        now = datetime.now(ZoneInfo(tz_name))
    except Exception:
        now = datetime.now()
    
    today_str = now.strftime("%Y-%m-%d")
    
    # Only remind after 20:00
    if now.hour < 20:
        return None
    
    # Only remind once per day
    if _reminder_shown_today == today_str:
        return None
    
    # Check if daily was processed
    daily_file = Path(vault_path) / "daily" / f"{today_str}.md"
    if daily_file.exists():
        content = daily_file.read_text(errors="ignore")
        if "[processed]" in content or "[summary]" in content:
            return None
    
    _reminder_shown_today = today_str
    return "\n\n💡 День не обработан. Нажми «Обработать» когда будешь готов."
