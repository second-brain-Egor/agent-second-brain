"""Offline regressions for browser-first reading and explicit access refusals."""

from __future__ import annotations

import importlib.util
import sys
from contextlib import nullcontext
from pathlib import Path
from unittest.mock import MagicMock

import httpx
import pytest

from direct_web import browser, fetch
from direct_web.responses import PageReadError, looks_blocked, validate_response

ROOT = Path(__file__).resolve().parents[1]
URL = "https://example.test/document"
PROXY = "socks5://127.0.0.1:19080"
ARTICLE = (
    "<html><head><title>Настройка Cloudflare</title></head><body><article>"
    "Это обычная статья про Cloudflare, captcha и способы защиты сайта. "
    "Текст документа доступен читателю без проверки.</article></body></html>"
)
CHALLENGE = (
    "<html><head><title>Just a moment...</title></head><body>"
    '<form id="challenge-form">Checking your browser</form></body></html>'
)
ELEC_CHALLENGE_TEXT = (
    "Проверяем, что запрос отправил человек.\n"
    "Подождите несколько секунд…\n"
    "Проверка не пройдена. Попробуйте ещё раз.\n"
    "Проверка пройдена, открываем страницу…\n"
    "Для проверки нужен включённый JavaScript."
)
ELEC_CHALLENGE = (
    "<html><head><title>elec.ru</title></head><body>"
    + "".join(f"<p>{line}</p>" for line in ELEC_CHALLENGE_TEXT.splitlines())
    + "</body></html>"
)


def test_article_mentions_do_not_count_as_a_block():
    assert not looks_blocked(ARTICLE)
    assert validate_response(200, ARTICLE, URL) is None


def test_http_status_reference_article_is_not_a_refusal():
    html = ARTICLE.replace("Настройка Cloudflare", "403 Forbidden - HTTP | MDN")
    assert not looks_blocked(html)
    assert validate_response(200, html, URL) is None


def test_article_with_cloudflare_code_example_is_not_a_refusal():
    html = ARTICLE.replace(
        "</article>",
        '<pre><code>const path = "/cdn-cgi/challenge-platform/"; '
        'const marker = "cf-chl-example";</code></pre></article>',
    )
    assert not looks_blocked(html)
    assert validate_response(200, html, URL) is None


@pytest.mark.parametrize("html", [ELEC_CHALLENGE_TEXT, ELEC_CHALLENGE])
def test_elec_visitor_check_with_http_200_is_not_material(html):
    assert looks_blocked(html)
    with pytest.raises(PageReadError) as error:
        validate_response(200, html, URL)
    assert error.value.status_code == 200
    assert "проверку посетителя" in error.value.reason


def test_elec_check_ignores_script_and_style_size():
    html = ELEC_CHALLENGE.replace(
        "</body>", "<script>" + "padding;" * 1000 + "</script></body>"
    )
    assert looks_blocked(html)


@pytest.mark.parametrize("tag", ["script", "style", "pre", "code", "blockquote", "q"])
def test_article_with_elec_check_example_stays_readable(tag):
    html = ARTICLE.replace(
        "</article>", f"<{tag}>{ELEC_CHALLENGE_TEXT}</{tag}></article>"
    )
    assert not looks_blocked(html)
    assert validate_response(200, html, URL) is None


@pytest.mark.parametrize("quotes", [("«", "»"), ('"', '"'), ("“", "”")])
def test_quoted_elec_check_is_not_an_active_gate(quotes):
    html = f"<p>{quotes[0]}{ELEC_CHALLENGE_TEXT}{quotes[1]}</p>"
    assert not looks_blocked(html)


def test_article_explaining_elec_check_without_quote_markup_stays_readable():
    html = "<article>" + ELEC_CHALLENGE_TEXT + " Это пример страницы защиты.</article>"
    assert not looks_blocked(html)


def test_javascript_requirement_alone_is_not_a_visitor_check():
    html = "<p>Для проверки нужен включённый JavaScript.</p>"
    assert not looks_blocked(html)
    assert validate_response(200, html, URL) is None


def test_extracted_elec_gate_is_rejected_despite_extra_html_text(monkeypatch):
    html = ELEC_CHALLENGE.replace(
        "</body>",
        '<div style="display:none">Посторонние скрытые служебные слова.</div>'
        "</body>",
    )
    assert not looks_blocked(html)
    extractor = MagicMock(return_value=ELEC_CHALLENGE_TEXT)
    monkeypatch.setattr(fetch.trafilatura, "extract", extractor)

    with pytest.raises(PageReadError) as error:
        fetch.extract_text(html, URL)

    assert error.value.status_code == 200
    assert "проверку посетителя" in error.value.reason
    extractor.assert_called_once()


def test_extracted_cloudflare_example_is_not_checked_as_html(monkeypatch):
    example = (
        'const path = "/cdn-cgi/challenge-platform/"; '
        'const marker = "cf-chl-example";'
    )
    html = ARTICLE.replace("</article>", f"<pre>{example}</pre></article>")
    monkeypatch.setattr(fetch.trafilatura, "extract", lambda *_args, **_kwargs: example)

    assert fetch.extract_text(html, URL) == example


@pytest.mark.parametrize("tag", ["pre", "code", "blockquote", "q"])
def test_extracted_elec_example_does_not_become_active_after_markup_is_lost(
    monkeypatch, tag
):
    html = ARTICLE.replace(
        "</article>", f"<{tag}>{ELEC_CHALLENGE_TEXT}</{tag}></article>"
    )
    monkeypatch.setattr(
        fetch.trafilatura, "extract", lambda *_args, **_kwargs: ELEC_CHALLENGE_TEXT
    )

    assert fetch.extract_text(html, URL) == ELEC_CHALLENGE_TEXT


def test_extracted_elec_quote_does_not_become_active_after_quotes_are_lost(
    monkeypatch,
):
    html = f"<p>«{ELEC_CHALLENGE_TEXT}»</p>"
    monkeypatch.setattr(
        fetch.trafilatura, "extract", lambda *_args, **_kwargs: ELEC_CHALLENGE_TEXT
    )

    assert fetch.extract_text(html, URL) == ELEC_CHALLENGE_TEXT


def test_nginx_forbidden_is_not_described_as_a_visitor_check():
    html = "<html><head><title>403 Forbidden</title></head><body>nginx</body></html>"
    with pytest.raises(PageReadError) as error:
        validate_response(403, html, URL)
    assert error.value.status_code == 403
    assert "проверку посетителя" not in error.value.reason
    assert "проверка посетителя" not in error.value.reason


def test_long_challenge_is_still_a_block():
    html = CHALLENGE.replace("</body>", " " * 20_000 + "</body>")
    assert looks_blocked(html)
    with pytest.raises(PageReadError):
        validate_response(200, html, URL)


@pytest.mark.parametrize("status", [401, 403, 404, 429, 500])
def test_http_error_status_is_not_success(status):
    with pytest.raises(PageReadError) as error:
        validate_response(status, ARTICLE, URL)
    assert error.value.status_code == status
    assert error.value.url == URL


def test_challenge_with_success_status_is_not_a_document():
    with pytest.raises(PageReadError):
        validate_response(200, CHALLENGE, URL)


def test_challenge_header_is_not_a_successful_document():
    with pytest.raises(PageReadError):
        validate_response(200, "<html>Проверка</html>", URL,
                          {"cf-mitigated": "challenge"})


@pytest.mark.parametrize(
    ("status", "html"),
    [(403, ARTICLE), (404, ARTICLE), (200, CHALLENGE), (200, ELEC_CHALLENGE)],
)
def test_http_reader_rejects_error_before_extracting(monkeypatch, status, html):
    response = httpx.Response(status, text=html, request=httpx.Request("GET", URL))
    client = MagicMock()
    client.__enter__.return_value.get.return_value = response
    monkeypatch.setattr(fetch.httpx, "Client", lambda **_: client)
    extract = MagicMock(side_effect=AssertionError("Refusal must not be extracted"))
    browser_reader = MagicMock(side_effect=AssertionError("No browser fallback"))
    monkeypatch.setattr(fetch, "extract_text", extract)
    monkeypatch.setattr(fetch, "fetch_with_browser", browser_reader)

    with pytest.raises(PageReadError):
        fetch.fetch_with_httpx(URL)

    extract.assert_not_called()
    browser_reader.assert_not_called()
    client.__exit__.assert_called_once()


def test_http_reader_extracts_a_real_document(monkeypatch):
    response = httpx.Response(200, text=ARTICLE, request=httpx.Request("GET", URL))
    client = MagicMock()
    client.__enter__.return_value.get.return_value = response
    monkeypatch.setattr(fetch.httpx, "Client", lambda **_: client)
    extract = MagicMock(return_value="Содержимое документа")
    monkeypatch.setattr(fetch, "extract_text", extract)

    assert fetch.fetch_with_httpx(URL) == "Содержимое документа"
    extract.assert_called_once_with(ARTICLE, URL)


def test_http_reader_uses_explicit_proxy(monkeypatch):
    response = httpx.Response(200, text=ARTICLE, request=httpx.Request("GET", URL))
    client_factory = MagicMock()
    client_factory.return_value.__enter__.return_value.get.return_value = response
    monkeypatch.setattr(fetch.httpx, "Client", client_factory)
    monkeypatch.setattr(fetch, "extract_text", lambda *_: "Документ")

    assert fetch.fetch_with_httpx(URL, proxy=PROXY) == "Документ"
    assert client_factory.call_args.kwargs["proxy"] == PROXY
    assert client_factory.call_args.kwargs["trust_env"] is False


def test_browser_reader_forwards_explicit_proxy(monkeypatch):
    html_reader = MagicMock(return_value=ARTICLE)
    monkeypatch.setattr(fetch, "fetch_html", html_reader)
    monkeypatch.setattr(fetch, "extract_text", lambda *_: "Документ")

    assert fetch.fetch_with_browser(URL, proxy=PROXY) == "Документ"
    html_reader.assert_called_once_with(URL, 30, proxy=PROXY)


@pytest.mark.parametrize(
    "proxy",
    [
        "socks5://private:secret-value@127.0.0.1:19080",
        "http://private:secret-value@127.0.0.1:19080",
        "ftp://127.0.0.1:19080",
        "socks5://127.0.0.1",
        "http://127.0.0.1:70000",
        "http://127.0.0.1:0",
        "http://127.0.0.1:19080/path",
        "http://127.0.0.1:19080?secret-value",
        "http://127.0.0.1:19080\n",
    ],
)
def test_invalid_proxy_is_rejected_before_request(monkeypatch, proxy):
    client_factory = MagicMock()
    html_reader = MagicMock()
    monkeypatch.setattr(fetch.httpx, "Client", client_factory)
    monkeypatch.setattr(fetch, "fetch_html", html_reader)

    for reader in (fetch.fetch_with_httpx, fetch.fetch_with_browser):
        with pytest.raises(ValueError) as error:
            reader(URL, proxy=proxy)
        assert "secret-value" not in str(error.value)

    client_factory.assert_not_called()
    html_reader.assert_not_called()


@pytest.fixture
def cli(monkeypatch):
    # Importing the command must not re-exec pytest because of its proxy env.
    monkeypatch.setenv("D_BRAIN_DIRECT_WEB", "1")
    spec = importlib.util.spec_from_file_location(
        "web_fetch_under_test", ROOT / "scripts" / "web_fetch.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("options", [[], ["--browser"]])
def test_cli_browser_mode_makes_one_browser_request(cli, monkeypatch, capsys, options):
    browser_reader = MagicMock(return_value="Прочитанная страница")
    http_reader = MagicMock(side_effect=AssertionError("HTTP must not run first"))
    monkeypatch.setattr(cli, "fetch_with_browser", browser_reader)
    monkeypatch.setattr(cli, "fetch_with_httpx", http_reader)
    monkeypatch.setattr(sys, "argv", ["web_fetch.py", URL, *options])

    assert cli.main() == 0
    assert capsys.readouterr().out.strip() == "Прочитанная страница"
    browser_reader.assert_called_once_with(URL)
    http_reader.assert_not_called()


def test_cli_http_mode_makes_only_http_request(cli, monkeypatch, capsys):
    browser_reader = MagicMock(side_effect=AssertionError("No browser fallback"))
    http_reader = MagicMock(return_value="Страница через HTTP")
    monkeypatch.setattr(cli, "fetch_with_browser", browser_reader)
    monkeypatch.setattr(cli, "fetch_with_httpx", http_reader)
    monkeypatch.setattr(sys, "argv", ["web_fetch.py", URL, "--http"])

    assert cli.main() == 0
    assert capsys.readouterr().out.strip() == "Страница через HTTP"
    http_reader.assert_called_once_with(URL)
    browser_reader.assert_not_called()


@pytest.mark.parametrize("options", [[], ["--http"]])
def test_cli_forwards_explicit_proxy(cli, monkeypatch, options):
    browser_reader = MagicMock(return_value="Документ")
    http_reader = MagicMock(return_value="Документ")
    monkeypatch.setattr(cli, "fetch_with_browser", browser_reader)
    monkeypatch.setattr(cli, "fetch_with_httpx", http_reader)
    monkeypatch.setattr(sys, "argv", ["web_fetch.py", URL, *options, "--proxy", PROXY])

    assert cli.main() == 0
    selected = http_reader if options else browser_reader
    unused = browser_reader if options else http_reader
    selected.assert_called_once_with(URL, proxy=PROXY)
    unused.assert_not_called()


def test_cli_rejects_proxy_credentials_without_printing_them(cli, monkeypatch, capsys):
    reader = MagicMock()
    monkeypatch.setattr(cli, "fetch_with_browser", reader)
    monkeypatch.setattr(
        sys,
        "argv",
        ["web_fetch.py", URL, "--proxy", "http://private:secret-value@localhost:80"],
    )

    with pytest.raises(SystemExit) as error:
        cli.main()

    assert error.value.code == 2
    assert "secret-value" not in capsys.readouterr().err
    reader.assert_not_called()


@pytest.mark.parametrize("options", [[], ["--http"]])
@pytest.mark.parametrize("proxy_options", [[], ["--proxy", PROXY]])
def test_cli_refusal_does_not_switch_readers(
    cli, monkeypatch, capsys, options, proxy_options
):
    refusal = PageReadError(URL, "Доступ запрещён", status_code=403)
    browser_reader = MagicMock(side_effect=refusal)
    http_reader = MagicMock(side_effect=refusal)
    monkeypatch.setattr(cli, "fetch_with_browser", browser_reader)
    monkeypatch.setattr(cli, "fetch_with_httpx", http_reader)
    monkeypatch.setattr(sys, "argv", ["web_fetch.py", URL, *options, *proxy_options])

    with pytest.raises(PageReadError):
        cli.main()

    assert capsys.readouterr().out == ""
    assert browser_reader.call_count == (0 if options else 1)
    assert http_reader.call_count == (1 if options else 0)


@pytest.fixture
def browser_session(monkeypatch, tmp_path):
    import playwright.sync_api

    monkeypatch.setattr(browser, "PROFILE_DIR", tmp_path / "profile")
    monkeypatch.setattr(browser, "DOWNLOADS_DIR", tmp_path / "downloads")
    monkeypatch.setattr(browser, "_profile_lock", nullcontext)

    runtime = MagicMock()
    context = runtime.chromium.launch_persistent_context.return_value
    page = context.new_page.return_value
    page.url = URL
    page.content.return_value = ARTICLE
    response = MagicMock()
    response.status = 200
    response.url = URL
    response.headers = {"content-type": "text/html"}
    response.all_headers.return_value = response.headers
    response.frame = page.main_frame
    response.request.frame = page.main_frame
    response.request.is_navigation_request.return_value = True
    response.request.resource_type = "document"

    def emit_response(value):
        for call in page.on.call_args_list:
            if call.args[0] == "response":
                call.args[1](value)

    def navigate(*_args, **_kwargs):
        emit_response(response)
        return response

    page.goto.side_effect = navigate
    manager = MagicMock()
    manager.__enter__.return_value = runtime
    monkeypatch.setattr(playwright.sync_api, "sync_playwright", lambda: manager)
    return context, page, response, emit_response


def test_browser_returns_document_and_closes_context(browser_session):
    context, _, _, _ = browser_session
    assert browser.fetch_html(URL) == ARTICLE
    context.close.assert_called_once()


def test_browser_default_route_stays_direct(browser_session):
    import playwright.sync_api

    assert browser.fetch_html(URL) == ARTICLE
    runtime = playwright.sync_api.sync_playwright().__enter__.return_value
    options = runtime.chromium.launch_persistent_context.call_args.kwargs
    assert "proxy" not in options
    assert "--proxy-server=direct://" in options["args"]
    assert options["user_data_dir"] == browser.PROFILE_DIR


@pytest.mark.parametrize("status", [200, 403])
def test_browser_proxy_uses_isolated_profile_and_closes_it(browser_session, status):
    import playwright.sync_api

    context, _, response, _ = browser_session
    response.status = status
    if status == 200:
        assert browser.fetch_html(URL, proxy=PROXY) == ARTICLE
    else:
        with pytest.raises(PageReadError):
            browser.fetch_html(URL, proxy=PROXY)

    runtime = playwright.sync_api.sync_playwright().__enter__.return_value
    launcher = runtime.chromium.launch_persistent_context
    options = launcher.call_args.kwargs
    assert options["proxy"] == {"server": PROXY}
    assert not any(arg.startswith("--proxy-") for arg in options["args"])
    assert options["user_data_dir"] != browser.PROFILE_DIR
    assert not options["user_data_dir"].exists()
    launcher.assert_called_once()
    context.close.assert_called_once()


@pytest.mark.parametrize(
    ("status", "html"),
    [(403, ARTICLE), (404, ARTICLE), (200, CHALLENGE), (200, ELEC_CHALLENGE)],
)
def test_browser_refusal_closes_context(browser_session, status, html):
    context, page, response, _ = browser_session
    response.status = status
    page.content.return_value = html

    with pytest.raises(PageReadError):
        browser.fetch_html(URL)

    context.close.assert_called_once()


@pytest.mark.parametrize("failure_stage", ["goto", "content"])
def test_browser_exception_closes_context(browser_session, failure_stage):
    context, page, _, _ = browser_session
    getattr(page, failure_stage).side_effect = RuntimeError("Ошибка чтения")

    with pytest.raises(RuntimeError, match="Ошибка чтения"):
        browser.fetch_html(URL)

    context.close.assert_called_once()


def test_browser_checks_document_loaded_after_javascript(browser_session):
    context, page, response, emit_response = browser_session
    final_response = MagicMock()
    final_response.status = 403
    final_response.url = URL
    final_response.headers = {}
    final_response.all_headers.return_value = {}
    final_response.frame = page.main_frame
    final_response.request.frame = page.main_frame
    final_response.request.is_navigation_request.return_value = True
    final_response.request.resource_type = "document"
    page.wait_for_timeout.side_effect = lambda *_: emit_response(final_response)
    assert response.status == 200

    with pytest.raises(PageReadError) as error:
        browser.fetch_html(URL)

    assert error.value.status_code == 403
    context.close.assert_called_once()
