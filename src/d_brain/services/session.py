"""Session persistence service.

Stores all bot interactions in JSONL format for history and analytics.
Inspired by Clawdbot's session persistence pattern.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any


class SessionStore:
    """Persistent session storage in JSONL format.

    Each user gets their own session file at vault/.sessions/{user_id}.jsonl.
    Entries are append-only for reliability and simplicity.
    """

    def __init__(self, vault_path: Path | str) -> None:
        self.sessions_dir = Path(vault_path) / ".sessions"
        self.sessions_dir.mkdir(exist_ok=True)

    def _scope_key(self, scope_id: int | str) -> str:
        if isinstance(scope_id, int):
            return str(scope_id)
        safe = str(scope_id).strip().replace("/", "_").replace("\\", "_")
        return safe or "unknown"

    def _get_session_file(self, scope_id: int | str) -> Path:
        return self.sessions_dir / f"{self._scope_key(scope_id)}.jsonl"

    def append(self, scope_id: int | str, entry_type: str, **data: Any) -> None:
        """Append entry to user's session file.

        Args:
            scope_id: Telegram user ID or chat scope key
            entry_type: Type of entry (voice, text, photo, forward, command, etc.)
            **data: Additional data to store (text, duration, msg_id, etc.)
        """
        entry = {
            "ts": datetime.now().astimezone().isoformat(),
            "type": entry_type,
            **data,
        }
        path = self._get_session_file(scope_id)
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def get_recent(self, scope_id: int | str, limit: int = 50) -> list[dict]:
        """Get recent session entries.

        Args:
            scope_id: Telegram user ID or chat scope key
            limit: Maximum number of entries to return

        Returns:
            List of session entries, most recent last
        """
        path = self._get_session_file(scope_id)
        if not path.exists():
            return []

        entries = []
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue  # Skip malformed lines

        return entries[-limit:]

    def get_today(self, scope_id: int | str) -> list[dict]:
        """Get today's session entries.

        Args:
            scope_id: Telegram user ID or chat scope key

        Returns:
            List of today's entries
        """
        today = datetime.now().date().isoformat()
        return [
            e
            for e in self.get_recent(scope_id, limit=200)
            if e.get("ts", "").startswith(today)
        ]

    def rotate(self, user_id: int | str, max_size: int = 1_000_000) -> None:
        """Rotate session file if it exceeds max_size bytes.

        Renames current file to {scope}.{YYYY-MM}.jsonl.bak and creates new one.
        """
        scope_key = self._scope_key(user_id)
        path = self._get_session_file(user_id)
        if not path.exists():
            return

        if path.stat().st_size <= max_size:
            return

        now = datetime.now()
        backup_name = f"{scope_key}.{now.strftime('%Y-%m')}.jsonl.bak"
        backup_path = self.sessions_dir / backup_name
        path.rename(backup_path)

    def rotate_all(self, max_size: int = 1_000_000) -> None:
        """Rotate all session files that exceed max_size."""
        for session_file in self.sessions_dir.glob("*.jsonl"):
            if session_file.suffix == ".jsonl" and not session_file.name.endswith(".bak"):
                self.rotate(session_file.stem, max_size)

    def get_stats(self, scope_id: int | str, days: int = 7) -> dict[str, int]:
        """Get usage statistics for the last N days.

        Args:
            scope_id: Telegram user ID or chat scope key
            days: Number of days to analyze

        Returns:
            Dict with counts by entry type
        """
        from datetime import timedelta

        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        entries = self.get_recent(scope_id, limit=1000)

        stats: dict[str, int] = {}
        for entry in entries:
            if entry.get("ts", "") >= cutoff:
                entry_type = entry.get("type", "unknown")
                stats[entry_type] = stats.get(entry_type, 0) + 1

        return stats
