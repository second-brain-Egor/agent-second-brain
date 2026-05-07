# Второй Мозг — Claude симка

Корневой конфиг Claude Code. Подхватывается автоматически при `claude --print` в этой директории.

---

## Главный регламент — общий для обеих симок

`GLOBAL_RULES.md` содержит весь свод: режимы ответа, стиль общения, оформление Telegram, запрещённые фразы, эксплуатация системы, проверки Барыги, **политика записи новых правил (раздел 6)**. Действует одинаково для Codex и для Claude.

@GLOBAL_RULES.md

## Принцип экономии контекста

Не загружай в системный промпт всё подряд. **Читай через Read только то, что прямо нужно для ответа на текущий запрос.** Это тот же режим, в котором работал Codex.

В частности:
- `vault/memory/user.md` (10 KB) — профиль пользователя. Прочитай если запрос личный/контекстный.
- `vault/memory/soul.md` (15 KB) — паттерны поведения, что работает / что бесит. Прочитай при первой реплике сессии или когда нужно свериться со стилем.
- `vault/memory/facts.md` (16 KB, RAG-индекс) — ключевые факты. **Не читай целиком.** Используй `memory_rag.search(query)` — дешевле в десятки раз.
- `vault/memory/change-log.md` (20 KB) — историческая хронология. Читай только если нужен ретроспективный контекст.
- `Скиллы/telegram-formatting/SKILL.md` (8 KB) — детальные правила Telegram-оформления. Базовые правила формы уже в `GLOBAL_RULES.md` (раздел 4). Полные читай при сложных ответах с карточками/подборками.
- `vault/.claude/rules/telegram-report.md` — формат HTML-отчёта обработки дня. Читай только перед `/process`.
- `vault/thoughts/learnings/*.md` — каноны по узким темам (`bot-communication-rules`, `telegram-formatting-rules`, `vault-search-discipline`, `planning-horizon-rules`, `loading-vs-git-export`, `windows-network-recovery-after-wireguard`). Читай по триггерам темы.
- `vault/goals/{0-vision-3y,1-yearly-2026,2-monthly,3-weekly}.md` — цели разных горизонтов. Читай когда запрос про планирование/приоритеты.

После значимого изменения в vault — короткая строка в `vault/memory/system-log.md`:
```
YYYY-MM-DD HH:MM | event | claude | OK
```

## ⚠️ АНТИБАН (только при `AI_BACKEND=claude`)

Anthropic TOS запрещает «automated or non-human means» через подписку:
- НЕ создавай новые cron / systemd timers / heartbeat-скрипты с Claude.
- Существующие `process-randomized.sh` и `weekly.sh` имеют guard на `AI_BACKEND=claude` — **не убирай**.
- Cron без LLM (`todoist-reminders.py`, `forumhouse-check-randomized.sh`, `@reboot run-bot.sh`) работают всегда.
- Обработка дня и недели на Claude — только по кнопкам «⚙️ Обработать», «📅 Неделя».

При `AI_BACKEND=codex` ограничение снимается автоматически.

## Архитектура «телефон + симки»

- Активная симка определяется `AI_BACKEND` в `.env`.
- `vault/.claude/` — мастер. `vault/.codex/{rules,docs,agents,skills}` — симлинки на `.claude/*`. Один источник правил для обеих симок.
- Точки входа: `CLAUDE.md` (этот файл) и `GLOBAL_RULES.md` (для Codex). Содержательно идентичны — `CLAUDE.md` импортирует `GLOBAL_RULES.md` через `@`.
- Переключение симок: кнопка «🤖 Модель» в боте (только админ).

## Структура vault (для ориентации)

`daily/  memory/  goals/  projects/  thoughts/{ideas,reflections,projects,learnings}  summaries/  MOC/  attachments/  references/  templates/  blog/  reports/  .claude/  .codex/  .session/  .sessions/  .data/`

CRM/business/contacts папок нет. Клиенты/проекты — в `projects/{name}/` или `thoughts/projects/`.

## Скиллы и агенты

- `vault/.claude/skills/` — главный `dbrain-processor` (загружается кодом напрямую через `_load_skill_content`); остальные 9 (todoist-ai, graph-builder, vault-health, agent-memory, web-search, video-processor, skill-creator/builder/conductor) — по триггерам.
- `vault/.claude/agents/` — goal-aligner, inbox-processor, note-organizer, weekly-digest.
- `vault/.claude/rules/` — communication-style, daily-format, goals-format, governance, obsidian-markdown, security, telegram-report, thoughts-format, weekly-reflection.
- `Скиллы/` (корень) — локальные скиллы (`telegram-formatting` обязательный для Telegram, `baryga-access` для SSH к root).

## Терминал → vault (по ходу сессии)

Значимые действия — в `vault/daily/YYYY-MM-DD.md` сразу:
```
## HH:MM [text]
Описание
```

## Две директории сессий (НЕ ПУТАТЬ)

- `vault/.sessions/` (мн.ч.) — JSONL логи Telegram (SessionStore).
- `vault/.session/` (ед.ч.) — handoff/capture/execute пайплайна обработки.

## Что НЕ делать

- НЕ редактировать `vault/.codex/{rules,docs,agents,skills}` напрямую — это симлинки на `.claude/`, правка идёт в обе симки. Хочешь править — правь `vault/.claude/<file>`.
- НЕ удалять Claude-код в `processor.py` (`_tool_*`, `_dispatch_tool`, `_tool_schemas`).
- НЕ создавать `vault/MEMORY.md` если его нет — используй `vault/memory/{user,soul,facts}.md`.
- НЕ показывать `.env` или API-ключи в ответах.
- НЕ обрезать ответы — разбивай на несколько сообщений.
- НЕ грузить большие файлы в контекст «на всякий случай» — читай через Read только нужное.
- НЕ записывать одно и то же правило в файлы конкретной симки — пиши только в общие места согласно `GLOBAL_RULES.md` раздел 6.
