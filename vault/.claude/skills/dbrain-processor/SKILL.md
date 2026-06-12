---
type: note
last_accessed: 2026-05-07
relevance: 0.47
tier: cold
---
# d-brain Processor (Codex)

Главный скилл обработки записей дня. Запускается по команде `/process` или из cron-задачи `process-randomized.sh`.

Pipeline: voice/text/forward/photo entries → классификация → задачи в Todoist + мысли в Obsidian с wiki-links → HTML-отчёт в Telegram.

## CRITICAL: Output Format

**ALWAYS return RAW HTML. No exceptions. No markdown. Ever.**

Финальный вывод идёт прямо в Telegram с `parse_mode=HTML`.

Правила:
1. ВСЕГДА возвращай HTML-отчёт — даже если все записи уже обработаны.
2. ВСЕГДА используй шаблон отчёта (см. ниже) — никакого свободного текста.
3. НИКОГДА не используй markdown-синтаксис: `**`, `##`, ` ``` `, `-`.
4. НИКОГДА не объясняй что сделано простым текстом — это идёт в HTML-отчёт.

WRONG:
```html
<b>Title</b>
```

CORRECT:
<b>Title</b>

## Todoist через mcp-cli

**ВСЕГДА используй mcp-cli для Todoist.** Не используй прямые MCP tools.

Базовые команды (детали — в `references/todoist.md`):

```bash
# Задачи на сегодня (workload check)
mcp-cli call todoist find-tasks-by-date '{"startDate": "today"}'

# Создать задачу
mcp-cli call todoist add-tasks '{"tasks": [{"content": "Task", "dueString": "tomorrow", "priority": 2}]}'

# Найти задачи по label
mcp-cli call todoist find-tasks '{"labels": ["process-goal"]}'

# Завершить задачи
mcp-cli call todoist complete-tasks '{"ids": ["task_id"]}'
```

Приоритеты: 1=p1 (highest), 2=p2 (high), 3=p3 (medium), 4=p4 (default).

### Алгоритм работы с mcp-cli

**СНАЧАЛА ВЫЗОВИ КОМАНДУ. ПОТОМ ДУМАЙ.**

```
1. ВЫЗОВИ команду
   ↓
   Получил результат? → Продолжай
   Ошибка? → Подожди, ВЫЗОВИ СНОВА
   3 ошибки подряд? → Покажи точный текст ошибки
```

**Запрещено:**
- ❌ "Todoist недоступен" без вызова команды
- ❌ "mcp-cli не работает" без вызова
- ❌ "добавь вручную"
- ❌ Решения о неработоспособности БЕЗ вызова

**Обязательно:**
- ✅ Bash-вызов команды
- ✅ 3 retry перед выводами
- ✅ Показать task ID если задача создана

## Реальная структура vault

Текущие папки vault, с которыми работаешь:

| Папка | Назначение |
|-------|------------|
| `daily/` | Дневные заметки YYYY-MM-DD.md |
| `memory/` | user.md, soul.md, facts.md, change-log.md, system-log.md, MEMORY.md |
| `goals/` | 0-vision-3y.md, 1-yearly-2026.md, 2-monthly.md, 3-weekly.md |
| `projects/` | Активные проекты, по подпапке на каждый |
| `thoughts/` | ideas/, reflections/, projects/, learnings/ |
| `summaries/` | Сводки и саммари |
| `MOC/` | Maps of Content (индексные заметки) |
| `attachments/` | Прикреплённые файлы (фото, аудио) |
| `references/` | Справочники и внешние данные |
| `templates/` | Шаблоны для новых заметок |
| `blog/` | Черновики постов |
| `reports/` | Отчёты |

CRM/business/contacts папок **нет**. Не пытайся их создавать или искать — всё, что про клиентов и активности, идёт в `projects/{name}/` или `thoughts/projects/`.

## Processing Flow

1. **Load personal context** — `goals/3-weekly.md`, `goals/2-monthly.md`, `goals/1-yearly-2026.md`.
2. **Load memory** — `memory/user.md`, `memory/soul.md`, `memory/facts.md`.
3. **Read daily** — `daily/YYYY-MM-DD.md`.
4. **Check workload** — `mcp-cli call todoist find-tasks-by-date '{"startDate": "today", "daysCount": 7}'`.
5. **Check Process Goals** — `mcp-cli call todoist find-tasks '{"labels": ["process-goal"]}'`. Если пусто или устарели — сгенерировать из goals (см. ниже).
6. **Process entries** — классифицировать каждую запись (task / idea / reflection / learning / project).
7. **Build links** — создать wiki-links между связанными заметками.
8. **Generate HTML report** — по шаблону (см. ниже).
9. **Log actions** — в `daily/YYYY-MM-DD.md` (см. ниже).
10. **Evolve MEMORY.md** — если файл существует и есть что внести.
11. **Capture observations** — friction/pattern/idea сигналы в `vault/.session/handoff.md`.

## ОБЯЗАТЕЛЬНО: Логирование в daily/

После ЛЮБЫХ изменений в vault — сразу пиши в `daily/YYYY-MM-DD.md`:

```
## HH:MM [text]
{Описание действий}

**Создано/Обновлено:**
- [[path/to/file|Name]] — описание
```

Что логировать:
- Создание файлов в `thoughts/`, `projects/`, `summaries/`
- Создание задач в Todoist (с task ID)
- Синхронизация с внешними системами
- Обновление `memory/*.md`

Пример:
```
## 14:30 [text]
Обработка ежедневных записей

**Создано задач:** 3
- "Follow-up по проекту X" (id: 8501234567, p2, завтра)
- "Подготовить материалы для встречи Y" (id: 8501234568, p2, пятница)

**Сохранено мыслей:** 1
- [[thoughts/ideas/product-launch|Product Launch]] — идея запуска
```

Зачем: audit trail + контекст для будущих обработок.

После записи — добавь строку в `memory/system-log.md`:
```
YYYY-MM-DD HH:MM | process | OK | {N tasks, M thoughts}
```

## Process Goals (детали Step 5)

ОБЯЗАТЕЛЬНО при каждом `/process`.

### 1. Проверь существующие process goals
```bash
mcp-cli call todoist find-tasks '{"labels": ["process-goal"], "limit": 20}'
```

### 2. Если process goals отсутствуют — создай

Читай goals и генерируй process commitments:

| Goal Level | Source | Process Pattern |
|------------|--------|-----------------|
| Weekly ONE Big Thing | `goals/3-weekly.md` | 2h deep work ежедневно |
| Monthly Top 3 | `goals/2-monthly.md` | 1 action/день на приоритет |
| Yearly Focus | `goals/1-yearly-2026.md` | 30 мин/день на стратегию |

Создай recurring tasks:
```bash
mcp-cli call todoist add-tasks '{"tasks": [
  {"content": "2h deep work: [ONE Big Thing]", "dueString": "every weekday at 6am", "priority": 2, "labels": ["process-goal"]},
  {"content": "1 action/день: [monthly priority]", "dueString": "every weekday", "priority": 3, "labels": ["process-goal"]},
  {"content": "30 мин стратегия", "dueString": "every day", "priority": 4, "labels": ["process-goal"]}
]}'
```

Лимит: max 5–7 активных process goals.

### 3. Если process goals есть — проверь статус

- Активные (upcoming) → ✅ показать в отчёте
- Просроченные (overdue) → ⚠️ предупредить
- Устаревшие (не связаны с текущими целями) → рекомендовать удалить

## Classification

| Тип | Куда |
|-----|------|
| task (actionable) | Todoist (детали — `references/todoist.md`) |
| 💡 idea | `thoughts/ideas/` |
| 🪞 reflection | `thoughts/reflections/` |
| 🎯 project mention | `thoughts/projects/` или `projects/{name}/` если есть активный проект |
| 📚 learning | `thoughts/learnings/` |

Детали — `references/classification.md`.

## Priority Rules

| Условие | Приоритет |
|---------|-----------|
| Deadline сегодня/завтра | p1 |
| Aligns with ONE Big Thing или monthly priority | p2 |
| Aligns with yearly goal | p3 |
| Operational, без goal alignment | p4 |

## Process Goals Preference

Создавая задачи, **предпочитай PROCESS формулировки OUTCOME-формулировкам**.

**Outcome (less effective):**
- "Закрыть сделку с X"
- "Запустить продукт"
- "Подготовить программу"

**Process (more effective):**
- "Отправить follow-up клиенту X" (actionable, controllable)
- "2h deep work на MVP" (time-bounded)
- "Показать драфт программы коллеге" (checkpoint)

Когда трансформировать:
- Запись звучит расплывчато / outcome-focused → конкретизировать в process step.
- Пользователь сказал "нужно сделать X" → создавай actionable next step, не X.
- Упомянута цель → задача движет к цели, не она сама.

Детали — `references/process-goals.md`.

## Evolve MEMORY.md

Цель: поддерживать `memory/MEMORY.md` актуальным **если файл существует**. Не добавлять, а ЭВОЛЮЦИОНИРОВАТЬ.

Если файла нет — НЕ создавай. Просто пропусти этот шаг.

### Что достойно MEMORY.md
ПИСАТЬ:
- ✅ Key decisions с impact (pivot, tool choice, architecture change)
- ✅ Финансовые изменения (контракты, оплаты, долги)
- ✅ Новые паттерны / инсайты
- ✅ Изменения в Active Context (новый ONE Big Thing, Hot Projects)
- ✅ Новые ключевые контакты с context

НЕ ПИСАТЬ:
- ❌ Ежедневные мелочи без impact
- ❌ Временные заметки (оставлять в `daily/`)
- ❌ Дубликаты
- ❌ Тривиальные задачи

### Как обновлять (evolve, не append)

Принцип: новое ЗАМЕНЯЕТ устаревшее, не добавляется рядом.

| Ситуация | Действие |
|----------|----------|
| Новое противоречит старому | ЗАМЕНИТЬ старую информацию |
| Новое дополняет старое | Добавить в существующую секцию |
| Информация устарела | Удалить или архивировать |

Используй точечные правки (Edit-стиль), а не append.

В отчёте:
```html
<b>🧠 MEMORY.md обновлён:</b>
• Active Context → Hot Projects updated
• Key Decisions → +1 новое решение
```

## Capture Observations

Записывать friction/patterns/ideas для эволюции системы.

Append в `vault/.session/handoff.md` секцию `## Observations`:
```markdown
## Observations
- [friction] YYYY-MM-DD: mcp-cli timeout 3x — retry спас, но -60s
- [pattern] YYYY-MM-DD: daily без entries 2 дня подряд
- [idea] YYYY-MM-DD: добавить process-goal "1h reading"
```

Правила:
- Одна строка на наблюдение
- Дата обязательна
- Не повторять
- Когда observations ≥10 → сигнал для system improvement session

В отчёте (если есть):
```html
<b>👁 Observations:</b>
• [friction] mcp-cli timeout 3x
```

## Entry Format

```
## HH:MM [type]
Content
```

Types: `[voice]`, `[text]`, `[forward from: Name]`, `[photo]`, `[terminal]`.

## HTML Report Template

Output RAW HTML (no markdown, no code blocks):

```
📊 <b>Обработка за {DATE}</b>

<b>🎯 Текущий фокус:</b>
{ONE_BIG_THING}

<b>📓 Сохранено мыслей:</b> {N}
• {emoji} {title} → {category}/

<b>✅ Создано задач:</b> {M}
• {task} <i>({priority}, {due})</i>

<b>📋 Process Goals:</b>
• {goal 1} → {status}
• {goal 2} → {status}
{N} активных | {M} требуют внимания
<i>Создано новых: {K}</i>

<b>📅 Загрузка на неделю:</b>
Пн: {n} | Вт: {n} | Ср: {n} | Чт: {n} | Пт: {n} | Сб: {n} | Вс: {n}

<b>⚠️ Требует внимания:</b>
• {overdue или stale goals}

<b>🔗 Новые связи:</b>
• [[Note A]] ↔ [[Note B]]

<b>⚡ Топ-3 приоритета:</b>
1. {task}
2. {task}
3. {task}

<b>📈 Прогресс:</b>
• {goal}: {%} {emoji}

<b>🧠 MEMORY.md:</b>
• {section} → {change}
<i>(если обновлено)</i>

---
<i>Обработано за {duration}</i>
```

## If Already Processed

Если все записи имеют маркер `<!-- ✓ processed -->` — статус-отчёт без re-processing:

```
📊 <b>Статус за {DATE}</b>

<b>🎯 Текущий фокус:</b>
{ONE_BIG_THING}

<b>📋 Process Goals:</b>
• {goal 1} → {status}
{N} активных | {M} требуют внимания

<b>📅 Загрузка на неделю:</b>
Пн: {n} | Вт: {n} | Ср: {n} | Чт: {n} | Пт: {n} | Сб: {n} | Вс: {n}

<b>⚠️ Требует внимания:</b>
• {overdue} просроченных
• {today} на сегодня

<b>⚡ Топ-3 приоритета:</b>
1. {task}
2. {task}
3. {task}

---
<i>Записи уже обработаны ранее</i>
```

## Allowed HTML Tags

`<b>` — bold (заголовки)
`<i>` — italic (метаданные)
`<code>` — команды, пути
`<s>` — strikethrough
`<u>` — underline
`<a href="url">text</a>` — ссылки

## FORBIDDEN in Output

- НЕ markdown: `**`, `##`, `-`, `*`, backticks
- НЕ code blocks (triple backticks)
- НЕ tables
- НЕ unsupported tags: `<div>`, `<span>`, `<br>`, `<p>`, `<table>`

Max length: 4096 characters (Telegram).

## References (читать по запросу)

- `references/about.md` — профиль пользователя, decision filters
- `references/classification.md` — правила классификации записей
- `references/todoist.md` — детали Todoist API + recurring patterns
- `references/goals.md` — alignment с целями
- `references/process-goals.md` — process vs outcome, паттерны трансформации
- `references/links.md` — построение wiki-links
- `references/rules.md` — обязательные правила обработки
- `references/report-template.md` — полная HTML-спецификация отчёта

## Phases (детальный pipeline)

- `phases/capture.md` — фаза захвата записей
- `phases/execute.md` — фаза выполнения (создание задач, заметок)
- `phases/reflect.md` — фаза рефлексии (logs, observations)
