"""Direct HTTP/browser page reader."""

from __future__ import annotations

import httpx
import trafilatura

from .browser import USER_AGENT, fetch_html

BLOCKED_INDICATORS = [
    "enable javascript",
    "please enable",
    "access denied",
    "cloudflare",
    "ddos protection",
    "checking your browser",
    "robot or human",
    "captcha",
    "servicepipe",
    "qrator",
]


def extract_text(html: str, url: str) -> str:
    text = trafilatura.extract(
        html,
        url=url,
        include_comments=False,
        include_tables=True,
    )
    return text or html


def looks_blocked(html: str) -> bool:
    lower = html.lower()
    has_block_marker = any(indicator in lower for indicator in BLOCKED_INDICATORS)
    return has_block_marker and len(html) < 8000


def fetch_with_httpx(url: str, timeout: int = 20) -> str | None:
    with httpx.Client(
        follow_redirects=True,
        timeout=timeout,
        trust_env=False,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        },
    ) as client:
        response = client.get(url)
        response.raise_for_status()
        html = response.text

    if looks_blocked(html):
        return None
    return extract_text(html, url)


def fetch_with_browser(url: str, timeout: int = 30) -> str:
    return extract_text(fetch_html(url, timeout), url)
