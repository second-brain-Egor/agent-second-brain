"""Legacy reminder helper kept for compatibility."""

from pathlib import Path


def check_process_reminder(vault_path: str | Path) -> str | None:
    """Automatic nudges are disabled unless explicitly reintroduced later."""
    del vault_path
    return None
