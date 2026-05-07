# Второй Мозг — Claude симка

Корневой конфиг Claude Code. Подхватывается автоматически при `claude --print` в этой директории.

---

## Главный регламент — общий для обеих симок

`GLOBAL_RULES.md` содержит весь свод правил: режимы ответа, стиль общения, оформление Telegram, запрещённые фразы, эксплуатация системы, проверки Барыги, **политика записи новых правил (раздел 6)**. Действует одинаково для Codex и для Claude.

@GLOBAL_RULES.md

## Память пользователя (общая для обеих симок)

Профиль пользователя и накопленные паттерны поведения — должны быть в каждом ответе, как у Codex.

@vault/memory/user.md
@vault/memory/soul.md

`vault/memory/facts.md` (16 KB, RAG-индекс) — читай через `memory_rag.search(query)`, **не загружай целиком**.
`vault/memory/change-log.md` (20 KB) — читай только если нужен исторический контекст.
`vault/memory/system-log.md` — пиши строку после каждого значимого действия (`YYYY-MM-DD HH:MM | event | claude | OK`).

## Telegram-оформление

Каждый ответ для Telegram — обязательно по этому скиллу.

@Скиллы/telegram-formatting/SKILL.md

Дополнительные правила формата HTML-отчёта обработки дня — `vault/.claude/rules/telegram-report.md` (читай через Read только перед `/process`).

## Контекст диалога

`vault/.sessions/*.jsonl` — это сырой лог Telegram-диалога (одна запись = одно сообщение в чат). Это не проекты и не заметки.

**Бот сам подаёт в системный промпт последние 20 записей дня** через секцию `=== TODAY SESSION === ... === END SESSION ===`. Этого хватает для обычного диалога — **по умолчанию не читай полный JSONL**, чтобы не дублировать.

**Если пользователь явно просит** «вспомни что было вчера / неделю назад / в марте», «найди в истории X», «о чём мы говорили» — конечно лезь в `vault/.sessions/<user_id>.<YYYY-MM>.jsonl`. Делай это эффективно:
1. Сначала `memory_rag.search(query)` (быстро, ищет по индексу).
2. Если RAG не нашёл нужное — открывай конкретный месячный файл `.sessions/`.
3. Большие файлы фильтруй через `grep`/`tail`/`head` (Bash), не читай целиком.

То есть свободу копать в истории у тебя никто не отнимает — просто не нужно делать это автоматически на каждое сообщение.

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

## Накопленные learnings (читай через Read по триггерам темы)

В `vault/thoughts/learnings/` лежат каноничные правила по узким темам — упомянуты в `soul.md`. **Не загружай в системный контекст**, читай через Read когда тема всплывает:

- `bot-communication-rules.md` — правила общения бота
- `telegram-formatting-rules.md` — расширенные Telegram-правила
- `vault-search-discipline.md` — правила поиска по vault
- `planning-horizon-rules.md` — горизонты планирования (длинные проекты не утаскивай в weekly)
- `loading-vs-git-export.md` — различение «загрузка Forumhouse» vs «git push»
- `windows-network-recovery-after-wireguard.md` — узкое практическое

## Структура vault (для ориентации)

```
daily/  memory/  goals/  projects/  thoughts/{ideas,reflections,projects,learnings}  summaries/  MOC/  attachments/  references/  templates/  blog/  reports/
.claude/  .codex/  .session/  .sessions/  .data/
```

CRM/business/contacts папок нет. Клиенты/проекты — в `projects/{name}/` или `thoughts/projects/`.

## Скиллы и агенты

- `vault/.claude/skills/` — главный скилл `dbrain-processor` (загружается кодом напрямую через `_load_skill_content`); остальные 9 (todoist-ai, graph-builder, vault-health, agent-memory, web-search, video-processor, skill-creator/builder/conductor) — по триггерам.
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

- `vault/.sessions/` (мн.ч.) — JSONL логи Telegram (SessionStore). **Не читай напрямую** (см. раздел про контекст диалога).
- `vault/.session/` (ед.ч.) — handoff/capture/execute пайплайна обработки.

## Что НЕ делать

- НЕ редактировать `vault/.codex/{rules,docs,agents,skills}` напрямую — это симлинки на `.claude/`, правка идёт в обе симки.
- НЕ удалять Claude-код в `processor.py` (`_tool_*`, `_dispatch_tool`, `_tool_schemas`).
- НЕ создавать `vault/MEMORY.md` если его нет — используй `vault/memory/{user,soul,facts}.md`.
- НЕ показывать `.env` или API-ключи в ответах.
- НЕ обрезать ответы — разбивай на несколько сообщений.
- По умолчанию не дублировать чтение `vault/.sessions/*.jsonl` (последние 20 уже в промпте). По явному запросу — читать можно (см. раздел про контекст диалога).
- НЕ записывать одно и то же правило в файлы конкретной симки — пиши в общие места согласно `GLOBAL_RULES.md` раздел 6.
