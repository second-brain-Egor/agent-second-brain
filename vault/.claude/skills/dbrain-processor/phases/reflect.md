---
type: note
last_accessed: 2026-03-27
relevance: 0.47
tier: cold
---
# Phase 3: REFLECT

Read execute results. Generate HTML report. Update MEMORY. Write observations. Log to daily.

## Input
- `.session/capture.json` — from Phase 1
- `.session/execute.json` — from Phase 2
- `MEMORY.md` — long-term memory
- `.session/handoff.md` — session context
- `.graph/health-history.json` — vault health trend

## Task

### 1. Generate HTML report

Use the template from SKILL.md. Include:

- ONE Big Thing (from capture.json)
- Thoughts saved (from execute.json)
- Tasks created (with IDs)
- Process goals status
- Workload by day
- Vault Health score (from latest health-history.json entry)
- Top 3 priorities
- Observations (if any)

### 2. Log actions to daily

Append to `daily/{DATE}.md`:

```markdown
## HH:MM [text]
d-brain processing

**Tasks created:** N
- "Task content" (id: XXXX, priority, due)

**Thoughts saved:** M
- [[path/to/thought|Title]] — category

**CRM updated:** K
- [[business/crm/client]] — change description
```

### 3. Evolve MEMORY.md

Check if any information from today deserves long-term memory:
- New key decisions
- Pipeline changes (new lead, closed deal, status change)
- Financial changes
- Active Context updates

Rules:
- New info REPLACES outdated (don't append duplicates)
- Only write significant changes

### 4. Capture observations (ОБЯЗАТЕЛЬНО — не пропускать)

Каждая обработка дня должна оставить хотя бы одну запись в `.session/handoff.md` под секцией `## Observations`. Это не «если что-то пошло не так», а **обязательная** запись после каждого `/process`. Если день прошёл без проблем — записать `[pattern]` про характер дня. Если возникли затыки — `[friction]`.

Формат строки строго:
```markdown
- [friction] YYYY-MM-DD: краткое описание затыка (что пошло не так, что пробовали)
- [pattern] YYYY-MM-DD: краткое описание паттерна (поведение пользователя, тема дня, нагрузка)
- [idea] YYYY-MM-DD: идея для улучшения системы из наблюдений за днём
```

Минимум одна запись за обработку. Лучше 2–3, если есть что зафиксировать.

Где записать: открыть `vault/.session/handoff.md`, найти секцию `## Observations`, **дописать новые строки в её конце** (append, не replace). Существующие записи сохранять.

Примеры (из реальных записей системы):
```
- [friction] 2026-04-08: mcp-cli не был установлен в среде — пришлось ставить вручную
- [pattern] 2026-04-16: пользователь раздражён повторами в ответах — давать конкретику с первого раза
- [pattern] 2026-04-08: долгосрочные проекты не превращать в недельные дедлайны
```

### 5. Update handoff.md (метаданные)

Кроме секции `## Observations` (см. п.4), обновить также:
- `## Last Session` — что было обработано (этот блок shell-скрипт `process.sh` уже пишет автоматически, не дублировать)
- `## Key Decisions` — если в дневнике зафиксированы важные решения, добавить сюда
- `## In Progress` — незавершённые пункты на завтра
- `## Next Steps` — что делать пользователю дальше

Каждую секцию вести в **append** режиме где это имеет смысл (Observations) или **replace** (Last Session, In Progress, Next Steps — текущее состояние).

## Output Format

Return RAW HTML report (no markdown, no code blocks). Goes directly to Telegram.

Follow the HTML template exactly:
- Only use: `<b>`, `<i>`, `<code>`, `<s>`, `<u>`, `<a>`
- NO: `<div>`, `<br>`, `<table>`, markdown syntax
- Max 4096 characters

### Vault Health section (add to report):

```html
<b>📊 Vault Health:</b> {score}/100
Orphans: {N} | Broken: {M} | Avg links: {X} | Desc: {Y}%
```

## CRITICAL

- Output is RAW HTML only
- No markdown syntax anywhere
- All HTML tags must be properly closed
