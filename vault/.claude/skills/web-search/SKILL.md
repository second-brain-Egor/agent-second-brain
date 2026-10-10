---
description: Веб-поиск через scripts/web_search.py (DuckDuckGo, регион ru-ru)
name: web-search
model: default
scope: global
depends_on: []
triggers:
  - найди информацию
  - поищи в интернете
  - что такое
---

# Web Search

Единственный путь поиска — готовый скрипт (DuckDuckGo, регион ru-ru уже настроен):

```bash
uv run python scripts/web_search.py "запрос" --max-results 5
```

Прочитать страницу по URL:

```bash
uv run python scripts/web_fetch.py "https://example.com"
```

## Правила

- НЕ использовать встроенные веб-инструменты CLI — только эти скрипты.
- В Telegram у пользователя есть быстрый путь: команда `/web запрос` или фраза
  «найди в интернете …» — обрабатывается ботом напрямую (handlers/web.py),
  без полного чат-пайплайна.
- Tavily удалён 2026-06-11: ключа TAVILY_API_KEY нет, ветка была мёртвой.
