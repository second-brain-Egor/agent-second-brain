---
name: web-search
description: DuckDuckGo для быстрых фактов, Tavily для исследований
model: default
scope: global
depends_on: []
triggers:
  - найди информацию
  - поищи в интернете
  - что такое
---

# Web Search

Два источника поиска:

## DuckDuckGo (быстрый, бесплатный)

```python
from duckduckgo_search import DDGS
results = DDGS().text("запрос", max_results=5)
for r in results:
    print(f"- {r['title']}: {r['body'][:200]}")
    print(f"  URL: {r['href']}")
```

## Tavily (глубокий, платный)

```bash
curl -s -X POST "https://api.tavily.com/search" \
  -H "Content-Type: application/json" \
  -d "{\"api_key\": \"$TAVILY_API_KEY\", \"query\": \"запрос\", \"max_results\": 5}"
```

## Правила выбора
- Простой факт → DuckDuckGo
- Глубокое исследование → Tavily
- Нет TAVILY_API_KEY в .env → только DuckDuckGo
