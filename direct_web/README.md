# Прямой веб-контур

Эта директория хранит браузерный контур, который ходит в интернет напрямую с IP
сервера, без inherited proxy-переменных и без `proxychains`.

- `network.py` очищает proxy-окружение и при необходимости перезапускает Python.
- `browser.py` запускает Chromium с постоянным профилем `browser-profile/`.
- `search.py` выполняет веб-поиск через DDGS в прямом окружении.
- `fetch.py` читает страницы через HTTP, а при блокировке переключается на браузер.

Публичные команды остаются прежними:

```bash
uv run python scripts/web_search.py "запрос" --max-results 5
uv run python scripts/web_fetch.py "https://example.com"
```
