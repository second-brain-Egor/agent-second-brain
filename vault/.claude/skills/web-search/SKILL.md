---
type: note
description: DuckDuckGo для быстрых фактов, Tavily для исследований
last_accessed: 2026-03-27
relevance: 0.94
tier: active
name: web-search
model: default
scope: global
depends_on: []
triggers: 
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
