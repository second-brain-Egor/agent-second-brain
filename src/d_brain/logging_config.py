"""Application logging configuration, including a persistent error journal."""

from __future__ import annotations

import json
import logging
import re
from datetime import UTC, datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any


_SECRET_PATTERNS = (
    re.compile(r"(?i)(bot\d{6,}):[A-Za-z0-9_-]{20,}"),
    re.compile(r"(?i)(api[_ -]?key|token|secret|password)(\s*[=:]\s*)\S+"),
)


def _redact(value: str) -> str:
    """Remove common secret shapes before they reach the persistent journal."""
    result = value
    for pattern in _SECRET_PATTERNS:
        if pattern.groups == 1:
            result = pattern.sub(r"\1:[СКРЫТО]", result)
        else:
            result = pattern.sub(r"\1\2[СКРЫТО]", result)
    return result


class JsonErrorFormatter(logging.Formatter):
    """Write one machine-readable error event per line."""

    def format(self, record: logging.LogRecord) -> str:
        event: dict[str, Any] = {
            "time": datetime.fromtimestamp(record.created, UTC).isoformat(),
            "level": record.levelname,
            "source": record.name,
            "message": _redact(record.getMessage()),
        }
        if record.exc_info:
            event["exception"] = _redact(self.formatException(record.exc_info))
        if record.stack_info:
            event["stack"] = _redact(self.formatStack(record.stack_info))
        return json.dumps(event, ensure_ascii=False)


def configure_logging(
    error_log_path: Path,
    *,
    max_bytes: int = 5 * 1024 * 1024,
    backup_count: int = 5,
) -> None:
    """Configure console output and a rotating JSONL journal for errors."""
    error_log_path.parent.mkdir(parents=True, exist_ok=True)

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.handlers.clear()

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )

    errors = RotatingFileHandler(
        error_log_path,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    errors.setLevel(logging.ERROR)
    errors.setFormatter(JsonErrorFormatter())

    root.addHandler(console)
    root.addHandler(errors)
