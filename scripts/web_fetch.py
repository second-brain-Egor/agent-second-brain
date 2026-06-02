#!/usr/bin/env python3
"""Fetch and extract readable text from a web page."""

from __future__ import annotations

import argparse
import sys

import httpx
import trafilatura

BLOCKED_INDICATORS = [
    "enable javascript",
    "please enable",
    "access denied",
    "cloudflare",
    "ddos protection",
    "checking your browser",
    "robot or human",
    "captcha",
]


def fetch_with_httpx(url: str, timeout: int = 20) -> str | None:
    with httpx.Client(
        follow_redirects=True,
        timeout=timeout,
        headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        },
    ) as client:
        response = client.get(url)
        response.raise_for_status()
        html = response.text

    lower = html.lower()
    if any(ind in lower for ind in BLOCKED_INDICATORS) and len(html) < 5000:
        return None  # likely blocked

    text = trafilatura.extract(
        html,
        url=url,
        include_comments=False,
        include_tables=True,
    )
    return text or html


def fetch_with_playwright(url: str, timeout: int = 30) -> str:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="ru-RU",
        )
        page = context.new_page()
        page.goto(url, timeout=timeout * 1000, wait_until="domcontentloaded")
        page.wait_for_timeout(2000)
        html = page.content()
        browser.close()

    text = trafilatura.extract(
        html,
        url=url,
        include_comments=False,
        include_tables=True,
    )
    return text or html


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch a web page and extract text.")
    parser.add_argument("url", help="Page URL.")
    parser.add_argument("--max-chars", type=int, default=12000)
    parser.add_argument("--browser", action="store_true", help="Force Playwright mode.")
    args = parser.parse_args()

    max_chars = min(max(args.max_chars, 1000), 50000)

    if args.browser:
        text = fetch_with_playwright(args.url)
    else:
        text = fetch_with_httpx(args.url)
        if text is None:
            print("HTTP заблокирован, переключаюсь на браузер...", file=sys.stderr)
            text = fetch_with_playwright(args.url)

    print(text[:max_chars].strip())
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Ошибка чтения страницы: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
