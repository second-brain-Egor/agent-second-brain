"""Validate page responses without treating access-denial pages as content."""

from __future__ import annotations

import re
from collections.abc import Mapping
from html import unescape
from html.parser import HTMLParser
from urllib.parse import urlsplit, urlunsplit


def public_url(url: str) -> str:
    """Keep page addresses in errors free of credentials, queries and fragments."""
    parts = urlsplit(url)
    host = parts.netloc.rsplit("@", 1)[-1]
    return urlunsplit((parts.scheme, host, parts.path, "", ""))


class PageReadError(RuntimeError):
    """A failed page read, with a safe address and an actionable Russian reason."""

    def __init__(
        self, url: str, reason: str, status_code: int | None = None
    ) -> None:
        self.url = public_url(url)
        self.reason = reason
        self.status_code = status_code
        status = f"HTTP {status_code}; " if status_code is not None else ""
        super().__init__(f"{self.url}: {status}{reason}")


class _GateTextParser(HTMLParser):
    """Read interstitial text while ignoring source examples and quotations."""

    _ignored_tags = {
        "head", "script", "style", "pre", "code", "blockquote", "q", "template"
    }

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.ignored: list[str] = []

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        if tag in self._ignored_tags:
            self.ignored.append(tag)

    def handle_endtag(self, tag: str) -> None:
        if tag in self.ignored:
            index = len(self.ignored) - 1 - self.ignored[::-1].index(tag)
            del self.ignored[index:]

    def handle_data(self, data: str) -> None:
        if not self.ignored:
            self.parts.append(data)


_HUMAN_CHECK_PROMPT = "проверяем, что запрос отправил человек"


def _human_check_text(html: str) -> str:
    parser = _GateTextParser()
    parser.feed(html)
    text = " ".join(" ".join(parser.parts).lower().split())
    return re.sub(r'«[^»]*»|“[^”]*”|"[^"]*"', " ", text)


def has_human_check_prompt(html: str) -> bool:
    """Require the observed prompt outside source examples and quotations."""
    return _HUMAN_CHECK_PROMPT in _human_check_text(html)


def looks_like_human_check(html: str) -> bool:
    """Recognize the observed short visitor gate in HTML or extracted text."""
    text = _human_check_text(html)
    if len(text) > 600:
        return False
    phrases = (
        _HUMAN_CHECK_PROMPT,
        "подождите несколько секунд",
        "проверка не пройдена. попробуйте ещё раз",
        "проверка пройдена, открываем страницу",
        "для проверки нужен включённый javascript",
    )
    if phrases[0] not in text or sum(phrase in text for phrase in phrases) < 3:
        return False
    for phrase in phrases:
        text = text.replace(phrase, "")
    # Keep this match narrow: an article's explanatory text must remain readable.
    return not re.sub(r"[\W_]+", "", text)


def looks_blocked(html: str) -> bool:
    """Recognize interstitials, rather than mentions of protection in articles."""
    match = re.search(r"<title\b[^>]*>(.*?)</title\s*>", html, re.I | re.S)
    title = unescape(re.sub(r"<[^>]*>", "", match[1])) if match else ""
    title = " ".join(title.lower().split())
    if re.fullmatch(
        r"^(?:just a moment|attention required|access denied|request blocked|"
        r"403(?: forbidden)?|forbidden|checking your browser|robot or human|"
        r"captcha|доступ (?:ограничен|запрещ[её]н)|проверка браузера|"
        r"проверка безопасности)[\s.!…]*(?:[|:—–-]\s*cloudflare)?",
        title,
    ):
        return True
    lower = re.sub(
        r"<(pre|code)\b[^>]*>.*?</\1\s*>", "", html, flags=re.I | re.S
    ).lower()
    return looks_like_human_check(html) or (
        "/cdn-cgi/challenge-platform/" in lower
        and ("cf-chl-" in lower or "challenge-form" in lower)
    )


def validate_response(
    status: int,
    html: str,
    url: str,
    headers: Mapping[str, str] | None = None,
) -> None:
    """Reject errors and challenges even when the server labels them HTTP 200."""
    headers = {key.lower(): value for key, value in (headers or {}).items()}
    if headers.get("cf-mitigated", "").lower() == "challenge":
        raise PageReadError(
            url,
            "сайт вернул проверку посетителя вместо страницы; материал не прочитан",
            status,
        )
    if status == 403:
        raise PageReadError(
            url, "сайт отказал в доступе; материал не прочитан", status
        )
    if status == 401:
        raise PageReadError(url, "для чтения сайт требует авторизацию", status)
    if status == 429:
        raise PageReadError(url, "сайт ограничил частоту запросов", status)
    if not 200 <= status < 300:
        raise PageReadError(url, "сайт не вернул запрошенную страницу", status)
    if looks_blocked(html):
        raise PageReadError(
            url,
            "сайт вернул отказ или проверку посетителя вместо материала",
            status,
        )
    if not html.strip():
        raise PageReadError(url, "сайт вернул пустой ответ", status)
