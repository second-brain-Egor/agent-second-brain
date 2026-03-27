"""
Фильтр prompt injection для пересланных сообщений.
Обнаруживает опасные паттерны и оборачивает данные.
"""

import re
from typing import Tuple

DANGEROUS_PATTERNS = [
    r'ignore\s+(all\s+)?previous\s+instructions',
    r'ignore\s+(all\s+)?above',
    r'you\s+are\s+now\s+',
    r'system\s*:\s*',
    r'admin\s*:\s*',
    r'sudo\s+',
    r'rm\s+-rf',
    r'DROP\s+TABLE',
    r'eval\s*\(',
    r'exec\s*\(',
    r'__import__',
    r'забудь\s+(все\s+)?предыдущие',
    r'игнорируй\s+(все\s+)?инструкции',
    r'ты\s+теперь\s+',
    r'новая\s+роль',
]


def check_injection(text: str) -> Tuple[bool, str]:
    """Проверить текст на prompt injection. Возвращает (is_safe, reason)."""
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return False, f"Обнаружен подозрительный паттерн: {pattern}"
    return True, ""


def wrap_forwarded(text: str) -> str:
    """Обернуть пересланное сообщение в безопасные маркеры."""
    is_safe, reason = check_injection(text)
    prefix = ""
    if not is_safe:
        prefix = f"⚠️ ПРЕДУПРЕЖДЕНИЕ: {reason}\n"
    return f"{prefix}[FORWARDED_DATA]\n{text}\n[/FORWARDED_DATA]"
