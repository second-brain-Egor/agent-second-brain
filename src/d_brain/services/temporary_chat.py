"""Only the personal chat-mode flag is durable; no conversation data belongs here."""
import json
from pathlib import Path

NORMAL_CHAT = "💬 Обычный чат"
TEMPORARY_CHAT = "🕶 Временный чат"
TOGGLE_LABELS = {NORMAL_CHAT, TEMPORARY_CHAT, "📅 Неделя", "/temporary"}


def mode_path(settings) -> Path:
    return Path(settings.vault_path) / ".session" / "temporary-chat.json"


def enabled(settings) -> bool:
    if not getattr(settings, "temporary_chat_user_id", 0):
        return False
    try:
        value = json.loads(mode_path(settings).read_text())
        return value.get("enabled") is not False
    except FileNotFoundError:
        return False
    except (OSError, ValueError, AttributeError):
        # A damaged flag must never silently enable saving private messages.
        return True


def set_enabled(settings, value: bool) -> None:
    path = mode_path(settings)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps({"enabled": value}) + "\n")
    temporary.chmod(0o600)
    temporary.replace(path)
