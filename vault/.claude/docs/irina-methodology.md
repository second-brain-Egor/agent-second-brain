---
type: note
last_accessed: 2026-09-20
relevance: 0.98
tier: active
---
# Zettelkasten Rules

Метод связанных заметок (Niklas Luhmann). Vault — это не свалка markdown-файлов,
а **граф знаний**: каждая заметка имеет описание, теги и связи через `[[wikilinks]]`.
Через месяц использования бот видит связи между темами, событиями и идеями, которые
ты сам забыл. Это и есть «второй мозг».

## Directory Structure

| Folder | Purpose |
|--------|---------|
| `daily/` | Raw daily entries (YYYY-MM-DD.md) |
| `goals/` | Goal cascade (3y → yearly → monthly → weekly) |
| `thoughts/` | Processed notes by category (ideas, reflections, projects, learnings) |
| `MOC/` | Maps of Content indexes (точки входа в темы) |
| `summaries/` | Дневные/недельные сводки |
| `attachments/` | Photos and files by date |
| `references/` | Внешние материалы (статьи, ссылки, кэш) |
| `templates/` | Шаблоны новых заметок |
| `memory/` | Curated long-term memory (user.md, soul.md, facts.md) |
| `blog/` | Опубликованные статьи (если ведёшь) |
| `projects/` | Активные проекты, по одной папке на проект (опционально) |

> **Доменная таксономия** добавляется по мере роста vault. Если есть бизнес-кейсы —
> заводи `business/` с подпапками; есть клиенты — `projects/clients/`. Рекомендуется
> начинать с `daily/` + `thoughts/` + `goals/`, а специализированные домены
> создавать когда накапливается материал.

## Graph Builder

**Назначение:** анализ и поддержка структуры связей между заметками.

**Архитектура:**
1. `vault/.claude/skills/graph-builder/scripts/analyze.py` — детерминированный обход
2. Агент — семантические связи для orphan-файлов
3. `vault/.claude/skills/vault-health/` — health-метрика, MOC, ремонт ссылок

**Запуск:**
```bash
uv run vault/.claude/skills/graph-builder/scripts/analyze.py
```

**Результат:**
- `vault/.graph/vault-graph.json` — JSON графа со статистикой
- `vault/.graph/report.md` — человекочитаемый отчёт

**Health-формула** (в `analyze.py`):
```
health_score = 100
    - (orphan_ratio  × 30)        # сироты — потеря знания
    - (broken_ratio  × 30)        # битые ссылки — фрагментация
    - max(0, (3 - avg_links) × 15)  # цель: 3+ ссылки на файл
    - ((1 - desc_ratio) × 10)     # покрытие description
```

**Targets:**

| Метрика | Цель | Как улучшить |
|---|---|---|
| Orphans | <10% | Скилл `graph-builder` добавляет семантические links |
| Broken links | 0 | `vault-health/scripts/fix_links.py --apply` |
| Avg links/file | ≥3 | `agent-memory` шаблон требует ссылок при создании |
| Description coverage | >80% | YAML `description:` обязателен в frontmatter |

## Card Template (agent-memory)

Все новые карточки vault следуют единому шаблону:

```yaml
---
type: note|idea|reflection|project|contact|reference
description: >-
  Одна строка — то, что увидит ищущий в результатах поиска
tags: [tag1, tag2]
status: active|draft|pending|done|inactive
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

**Правила:**
- `description` — **ОБЯЗАТЕЛЬНО**. Пиши как сниппет для поиска (одно предложение, по делу)
- `tags` — **ОБЯЗАТЕЛЬНО**. 2–5 тегов, lowercase, через дефис (`marketing-funnel`, не `MarketingFunnel`)
- `status` ≠ `tier`: status — статус сущности; tier — слой памяти (определяется automatic decay-движком)
- **Один факт = одно место (DRY).** Дублирование запрещено — связывай через `[[wikilinks]]`
- Каждая заметка должна иметь **минимум 2 связи** с другими заметками (граф, а не свалка)

## Entry Format (daily/)

```markdown
## HH:MM [type]
Содержание сообщения.
```

Типы: `[voice]`, `[text]`, `[forward from: Name]`, `[photo]`, `[document]`.

После обработки бот добавляет:
```markdown
> [!note] Vision
> {описание содержания если фото}
```
и в конце дня — маркер `<!-- ✓ processed -->` (анти-двойная обработка).

## Goals Hierarchy

```
goals/0-vision-3y.md    → видение на 3 года по областям жизни
goals/1-yearly-YYYY.md  → годовые цели + квартальный разбор
goals/2-monthly.md      → топ-3 приоритета текущего месяца
goals/3-weekly.md       → фокус недели + ONE Big Thing
```

Иерархия каскадная: weekly → monthly → yearly → vision. Бот при обработке дня
проверяет, помогает ли каждое выполненное действие текущему ONE Big Thing.

## Hubs (точки входа)

Чтобы граф был навигабельным, в каждом крупном домене делай **хаб** — `_index.md`
со списком всех заметок этого домена и кратким описанием каждой:

```markdown
# {Domain} Hub

## Active
- [[note-1]] — описание
- [[note-2]] — описание

## Archive
- [[note-3]] — описание
```

Хабы автоматически попадают в MOC через скилл `vault-health/scripts/generate_moc.py`.

## Processing Workflow

3-фазный pipeline (`dbrain-processor` SKILL):

1. **CAPTURE** — читает `daily/{сегодня}.md` → классифицирует (task/idea/reflection/note) → JSON
2. **EXECUTE** — создаёт задачи в Todoist, сохраняет мысли в `thoughts/`, обновляет хабы → JSON
3. **REFLECT** — генерирует HTML-отчёт в Telegram, обновляет `memory/`, записывает observations в `vault/.session/handoff.md`

В конце — `graph-builder/analyze.py` пересоздаёт граф, `memory_rag.py` индексирует FTS5.

## Report Format

Telegram-отчёты — RAW HTML, разрешённые теги: `<b>`, `<i>`, `<code>`, `<pre>`, `<a>`,
`<s>`, `<u>`. Markdown НЕ работает (Telegram парсит как HTML с `parse_mode="HTML"`).
Подробности — `vault/.claude/rules/telegram-report.md`.

## Available Agents

| Agent | Назначение |
|---|---|
| `weekly-digest` | Недельный отчёт с прогрессом по целям |
| `goal-aligner` | Проверка соответствия задач Todoist целям |
| `note-organizer` | Организация vault, починка ссылок, дедупликация |
| `inbox-processor` | GTD-обработка входящего |

## Path-Specific Rules

См. `vault/.claude/rules/`:
- `daily-format.md` — формат daily-заметок
- `thoughts-format.md` — формат thought-заметок
- `goals-format.md` — формат целей
- `telegram-report.md` — формат HTML-отчёта в Telegram
- `obsidian-markdown.md` — правила Obsidian-синтаксиса (wiki-links, callouts, properties)
- `weekly-reflection.md` — шаблон еженедельной рефлексии
- `governance.md` — что нельзя делать без подтверждения пользователя
- `security.md` — `.env` не показывать, prompt injection guards
- `communication-style.md` — тон, формат, язык общения

## Tools

- **Visualization:** Obsidian (видит wiki-links, граф, backlinks автоматически)
- **Indexing:** SQLite FTS5 в `vault/.data/memory.db` (RAG-поиск через `search_memory()`)
- **Sync:** GitHub через `commit_and_push` (autostash + pull-rebase)

## Origin

Метод Zettelkasten — Niklas Luhmann (немецкий социолог, 70 книг через картотеку
связанных заметок). Адаптирован для AI-эры: вместо бумажных карточек — markdown-файлы,
вместо ручной картотеки — автоматический graph-builder, который сам ищет
семантические связи между orphan-файлами.

Архитектура health-системы и типизированных связей основана на паттернах
[arscontexta](https://github.com/agenticnotetaking/arscontexta) — derivation engine
для Claude Code (Heinrich, 249 research claims из cognitive science, network theory,
Zettelkasten, agent architecture).
