"""Report formatters for Telegram messages."""

import html
import re
from typing import Any


# Allowed HTML tags in Telegram
ALLOWED_TAGS = {"b", "i", "code", "pre", "a", "s", "u"}


def sanitize_telegram_html(text: str) -> str:
    """Sanitize HTML for Telegram, keeping only allowed tags.

    Telegram supports: <b>, <i>, <code>, <pre>, <a>, <s>, <u>

    Args:
        text: Raw HTML text from Claude

    Returns:
        Sanitized HTML safe for Telegram
    """
    if not text:
        return ""

    # First, escape any raw < > that are not part of tags
    # This regex matches < or > not followed/preceded by tag patterns
    result = []
    i = 0
    while i < len(text):
        if text[i] == "<":
            # Check if this looks like a valid tag
            tag_match = re.match(r"</?([a-zA-Z]+)(?:\s[^>]*)?>", text[i:])
            if tag_match:
                tag_name = tag_match.group(1).lower()
                if tag_name in ALLOWED_TAGS:
                    # Keep the allowed tag
                    result.append(tag_match.group(0))
                    i += len(tag_match.group(0))
                    continue
                else:
                    # Escape disallowed tag
                    result.append("&lt;")
                    i += 1
                    continue
            else:
                # Not a valid tag pattern, escape
                result.append("&lt;")
                i += 1
                continue
        elif text[i] == ">":
            # Standalone > should be escaped
            result.append("&gt;")
            i += 1
        elif text[i] == "&":
            # Check if already escaped
            entity_match = re.match(r"&(amp|lt|gt|quot|#\d+|#x[0-9a-fA-F]+);", text[i:])
            if entity_match:
                result.append(entity_match.group(0))
                i += len(entity_match.group(0))
            else:
                result.append("&amp;")
                i += 1
        else:
            result.append(text[i])
            i += 1

    return "".join(result)


def validate_telegram_html(text: str) -> bool:
    """Validate that HTML tags are properly closed.

    Args:
        text: HTML text to validate

    Returns:
        True if valid, False otherwise
    """
    tag_stack = []
    tag_pattern = re.compile(r"<(/?)([a-zA-Z]+)(?:\s[^>]*)?>")

    for match in tag_pattern.finditer(text):
        is_closing = match.group(1) == "/"
        tag_name = match.group(2).lower()

        if tag_name not in ALLOWED_TAGS:
            continue

        if is_closing:
            if not tag_stack or tag_stack[-1] != tag_name:
                return False
            tag_stack.pop()
        else:
            tag_stack.append(tag_name)

    return len(tag_stack) == 0


def _get_open_tags(text: str) -> list[str]:
    """Get list of currently open HTML tags in text."""
    tag_pattern = re.compile(r"<(/?)([a-zA-Z]+)(?:\s[^>]*)?>")
    open_tags: list[str] = []
    for match in tag_pattern.finditer(text):
        is_closing = match.group(1) == "/"
        tag_name = match.group(2).lower()
        if tag_name not in ALLOWED_TAGS:
            continue
        if is_closing and open_tags and open_tags[-1] == tag_name:
            open_tags.pop()
        elif not is_closing:
            open_tags.append(tag_name)
    return open_tags


def split_html_messages(text: str, max_length: int = 4096) -> list[str]:
    """Split HTML text into multiple messages, keeping tags balanced.

    Args:
        text: HTML text
        max_length: Maximum length per message (Telegram limit is 4096)

    Returns:
        List of HTML messages with balanced tags
    """
    if len(text) <= max_length:
        return [text]

    messages: list[str] = []
    remaining = text

    while remaining:
        if len(remaining) <= max_length:
            messages.append(remaining)
            break

        # Find a safe cut point
        cut_point = max_length - 100  # Room for closing/opening tags

        # Don't cut in the middle of a tag
        last_open = remaining.rfind("<", 0, cut_point)
        last_close = remaining.rfind(">", 0, cut_point)
        if last_open > last_close:
            cut_point = last_open

        # Try not to cut in the middle of a word
        space_pos = remaining.rfind(" ", max(0, cut_point - 200), cut_point)
        newline_pos = remaining.rfind("\n", max(0, cut_point - 200), cut_point)
        best_break = max(space_pos, newline_pos)
        if best_break > cut_point - 200:
            cut_point = best_break

        chunk = remaining[:cut_point]
        remaining = remaining[cut_point:]

        # Close open tags at end of chunk
        open_tags = _get_open_tags(chunk)
        closing_tags = "".join(f"</{tag}>" for tag in reversed(open_tags))
        chunk += closing_tags

        # Re-open tags at start of next chunk
        opening_tags = "".join(f"<{tag}>" for tag in open_tags)
        remaining = opening_tags + remaining

        messages.append(chunk)

    return messages


def format_process_report(report: dict[str, Any]) -> list[str]:
    """Format processing report for Telegram HTML.

    The report from Claude is expected to be in HTML format.
    We sanitize it to ensure only Telegram-safe tags are used.

    Args:
        report: Processing report from ClaudeProcessor

    Returns:
        List of formatted HTML messages for Telegram
    """
    if "error" in report:
        error_msg = html.escape(str(report["error"]))
        return [f"❌ <b>Ошибка:</b> {error_msg}"]

    if "report" in report:
        raw_report = report["report"]

        # Sanitize HTML, keeping allowed tags
        sanitized = sanitize_telegram_html(raw_report)

        # Validate tag balance
        if not validate_telegram_html(sanitized):
            # Fall back to plain text if tags are broken
            return [html.escape(raw_report)]

        # Split into multiple messages if too long
        return split_html_messages(sanitized, max_length=4096)

    return ["✅ <b>Обработка завершена</b>"]


def format_error(error: str) -> str:
    """Format error message for Telegram.

    Args:
        error: Error message

    Returns:
        Formatted HTML error message
    """
    return f"❌ <b>Ошибка:</b> {html.escape(error)}"


def format_empty_daily() -> str:
    """Format message for empty daily file.

    Returns:
        Formatted HTML message
    """
    return (
        "📭 <b>Нет записей для обработки</b>\n\n"
        "<i>Добавьте голосовые сообщения или текст в течение дня</i>"
    )
