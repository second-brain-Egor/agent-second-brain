"""Direct HTTP/browser page reader."""

from __future__ import annotations

import httpx
import trafilatura

from .browser import USER_AGENT, fetch_html, validate_proxy
from .responses import (  # noqa: F401
    PageReadError,
    has_human_check_prompt,
    looks_blocked,
    looks_like_human_check,
    validate_response,
)


def extract_text(html: str, url: str) -> str:
    text = trafilatura.extract(
        html,
        url=url,
        include_comments=False,
        include_tables=True,
    )
    result = text or html
    if looks_like_human_check(result) and has_human_check_prompt(html):
        raise PageReadError(
            url,
            "сайт вернул проверку посетителя вместо страницы; материал не прочитан",
            200,
        )
    return result


def fetch_with_httpx(
    url: str, timeout: int = 20, *, proxy: str | None = None
) -> str:
    proxy = validate_proxy(proxy)
    with httpx.Client(
        follow_redirects=True,
        timeout=timeout,
        trust_env=False,
        proxy=proxy,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        },
    ) as client:
        try:
            response = client.get(url)
        except httpx.TimeoutException as exc:
            raise PageReadError(
                url, f"сайт не ответил HTTP-клиенту за {timeout} секунд"
            ) from exc
        except httpx.RequestError as exc:
            raise PageReadError(url, "не удалось установить соединение с сайтом") from exc
        html = response.text
        validate_response(
            response.status_code, html, str(response.url), response.headers
        )
    return extract_text(html, url)


def fetch_with_browser(
    url: str, timeout: int = 30, *, proxy: str | None = None
) -> str:
    proxy = validate_proxy(proxy)
    html = fetch_html(url, timeout, proxy=proxy) if proxy else fetch_html(url, timeout)
    return extract_text(html, url)
