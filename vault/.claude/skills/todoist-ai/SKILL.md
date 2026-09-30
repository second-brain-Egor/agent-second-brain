---
type: note
description: Todoist integration via Python SDK todoist-api-python (NOT mcp-cli)
last_accessed: 2026-05-07
relevance: 0.98
tier: active
name: todoist-ai
depends_on: []
---

# todoist-ai

Интеграция с Todoist через **Python SDK `todoist-api-python`**.

## КРИТИЧНО

**В этом проекте НЕ используется `mcp-cli`. Не пытайся его звать.**

Вместо этого работа с Todoist идёт через официальный Python SDK `todoist-api-python` — он уже установлен в `.venv` и API-ключ читается из `.env` (переменная `TODOIST_API_KEY`).

Реализованные методы — в `src/d_brain/services/processor.py`:
- `_tool_todoist_get_projects()` — получить список проектов
- `_tool_todoist_search_tasks(query, limit=20)` — найти активные задачи по тексту
- `_tool_todoist_get_completed_tasks(since_iso, until_iso, limit=50)` — выполненные задачи в окне
- `_tool_todoist_add_task(content, due_string=..., priority=..., labels=..., project_id=...)` — создать задачу
- `_tool_todoist_update_task(task_id, content=..., due_string=..., priority=..., labels=...)` — изменить задачу
- `_tool_todoist_complete_task(task_id)` — закрыть задачу

## Как вызывать SDK напрямую (из Bash/скрипта/скилла)

Если нужно дёрнуть Todoist быстро прямо из терминала — используй `.venv/bin/python -c "..."` с автоподгрузкой `.env`. **Важно:** `get_projects()`, `filter_tasks()`, `get_tasks()` возвращают **paginated iterator** — нужно итерироваться двумя циклами, либо flatten через list-comprehension `[x for page in iter for x in page]`.

```bash
cd /home/egor/agent-second-brain && \
  .venv/bin/python -c "
import os
from dotenv import load_dotenv; load_dotenv('.env')
from todoist_api_python.api import TodoistAPI
api = TodoistAPI(os.environ['TODOIST_API_KEY'])
"
```

### Задачи на сегодня (workload check)

```bash
.venv/bin/python -c "
import os
from dotenv import load_dotenv; load_dotenv('.env')
from todoist_api_python.api import TodoistAPI
api = TodoistAPI(os.environ['TODOIST_API_KEY'])
tasks = [t for page in api.filter_tasks(query='today') for t in page]
print(f'today: {len(tasks)} tasks')
for t in tasks:
    due = t.due.string if t.due else '-'
    print(f'  p{t.priority} | {t.content[:60]} | due={due}')
"
```

### Найти задачи по слову

```bash
.venv/bin/python -c "
import os
from dotenv import load_dotenv; load_dotenv('.env')
from todoist_api_python.api import TodoistAPI
api = TodoistAPI(os.environ['TODOIST_API_KEY'])
tasks = [t for page in api.filter_tasks(query='search: timberframe') for t in page]
for t in tasks[:10]:
    print(f'{t.id} | {t.content}')
"
```

### Создать задачу

```bash
.venv/bin/python -c "
import os
from dotenv import load_dotenv; load_dotenv('.env')
from todoist_api_python.api import TodoistAPI
api = TodoistAPI(os.environ['TODOIST_API_KEY'])
t = api.add_task(content='Перезвонить клиенту по бане', due_string='завтра 10:00', priority=2)
print(f'Created: {t.id} | {t.content}')
"
```

### Закрыть задачу

```bash
.venv/bin/python -c "
import os
from dotenv import load_dotenv; load_dotenv('.env')
from todoist_api_python.api import TodoistAPI
api = TodoistAPI(os.environ['TODOIST_API_KEY'])
ok = api.complete_task('1234567890')
print('done' if ok else 'failed')
"
```

### Получить проекты

```bash
.venv/bin/python -c "
import os
from dotenv import load_dotenv; load_dotenv('.env')
from todoist_api_python.api import TodoistAPI
api = TodoistAPI(os.environ['TODOIST_API_KEY'])
projects = [p for page in api.get_projects() for p in page]
for p in projects:
    print(f'{p.id} | {p.name}')
"
```

### Синтаксис фильтров `filter_tasks(query=...)`

В Todoist API свой DSL для фильтров:
- `today` — все задачи на сегодня
- `tomorrow`, `next 7 days`, `7 days`, `no date`
- `overdue` — просроченные
- `p1`, `p2`, `p3`, `p4` — по приоритету (UI-нумерация)
- `@label_name` — по метке
- `#project_name` — в конкретном проекте
- `search: keyword` — по содержимому
- Комбинирование: `today & p1`, `(today | overdue) & @work`

Полная справка: https://todoist.com/help/articles/introduction-to-filters

## Приоритеты

- `1` = p4 (без приоритета, default)
- `2` = p3 (medium)
- `3` = p2 (high)
- `4` = p1 (highest)

⚠️ **Внимание на инверсию:** в SDK число `4` = высший приоритет, в UI Todoist это `p1`. Не путать.

## Алгоритм при ошибках

**СНАЧАЛА ВЫЗОВИ КОМАНДУ. ПОТОМ ДУМАЙ.**

1. Запусти команду через `.venv/bin/python -c "..."`.
2. Получил ответ → продолжай.
3. Ошибка (`401`, `403`, `network error`) → проверь `TODOIST_API_KEY` в `.env`, попробуй ещё раз.
4. 3 ошибки подряд → покажи пользователю точный текст ошибки, не выдумывай «Todoist недоступен».

**Запрещено:**
- ❌ «mcp-cli не установлен / Todoist недоступен» — это **неправда**, у нас Python SDK.
- ❌ Решать что не работает БЕЗ вызова команды.
- ❌ Просить пользователя «добавь задачу вручную».

**Обязательно:**
- ✅ Вызвать команду через `.venv/bin/python -c "..."`.
- ✅ При сетевой ошибке — retry 2-3 раза.
- ✅ Показать `task ID` если задача создана.

## Когда использовать этот скилл

- Создать / обновить / завершить задачу в Todoist.
- Проверить загрузку дня или недели.
- Найти задачу по тексту, проекту, label.
- Работа с recurring tasks (`due_string='every weekday'`, `'every monday'` и т.п.).

## Документация SDK

- PyPI: https://pypi.org/project/todoist-api-python/
- GitHub: https://github.com/Doist/todoist-api-python
- Полный список методов API: `import todoist_api_python.api; help(todoist_api_python.api.TodoistAPI)`

## Relevant Skills

- [[vault/.claude/skills/dbrain-processor/SKILL|dbrain-processor]] — ежедневная обработка записей (создаёт задачи в Todoist по результатам classification)
