# Второй Мозг — Лог проекта

Источник правды о текущем состоянии. AI-ассистент (Codex или Claude Code) читает его в начале сессии, чтобы не переделывать уже сделанное и не действовать по устаревшим предположениям.

---

## ПРАВИЛА ДЛЯ AI-АССИСТЕНТА

1. **В начале сессии** по теме «Второй Мозг» — прочитай этот файл первым.
2. **В конце сессии**, если были изменения — обнови соответствующие секции.
3. **Формат записи в журнал изменений:** дата, что изменено, почему.
4. **Не пропускай обновления.** Это потеря контекста для следующих сессий.

---

## Текущее состояние

| Параметр | Значение |
|----------|----------|
| Активная симка | **Claude** (`vault/.claude/`, через подписку Claude Max) |
| Модель | sonnet (Claude Code CLI `claude -p` через subprocess) |
| Спящая симка | Codex (`vault/.codex/`) — готова к активации, после `codex login` |
| Подписка | **Codex Pro** (OpenAI) для бота + **Claude Max** (Anthropic) для Claude Code на сервере |
| API ключи | Не используются. Авторизация локальная: `codex login` |
| VPS текущий | 185.23.35.88, пользователь `egor` |
| VPS прошлый | 37.233.84.178 (удалён) |
| Путь проекта | `/home/egor/agent-second-brain/` |
| Bot username | `@Mozg02_bot` |
| GitHub | `second-brain-Egor/agent-second-brain` (приватный) |
| Telegram бот | aiogram |
| Транскрипция голоса | Deepgram nova-3 |
| Tasks | Todoist через `mcp-cli` |
| RAG | SQLite FTS5 (`vault/.data/memory.db`) |
| TTS | Edge-TTS |
| Каналы | Telethon (отдельная фича) |

---

## История архитектурных решений

### 2026-03-31 — Анти-бан архитектура (УСТАРЕЛО)

**Контекст эпохи Claude Pro:** Anthropic TOS запрещает «automated or non-human means». Heartbeat и ночная обработка по cron могли вызвать бан.

**Тогдашнее решение:** убрать всю автоматику — ни cron, ни systemd timers, ни heartbeat. Обработка только по кнопке.

**СТАТУС: УСТАРЕЛО** после переезда на Codex (см. ниже).

### 2026-04~ — Переезд с Claude на Codex

**Причина:** удобство автоматики, цена, отсутствие TOS-ограничений на cron.

**Что изменилось:**
- Активная симка: Claude → Codex.
- Cron вернулся (process-randomized, weekly, todoist-reminders, forumhouse-check, @reboot run-bot).
- Главный конфиг в корне: `CLAUDE.md` → `GLOBAL_RULES.md`.
- `processor.py` переписан под `codex exec` через subprocess.
- Память разделена в `vault/memory/{user,soul,facts,change-log,system-log}.md`.

**Что не доделано на момент переезда (известный долг):**
- Папка `vault/.codex/` физически отсутствовала, был только fallback в коде на `vault/.claude/`.
- Скиллы остались в Claude-формате — Codex их подхватывал плохо.
- Чистого `AI_BACKEND=codex|claude` переключателя в `.env` не было.
- Чистых `CodexAdapter` / `ClaudeAdapter` в коде не было.

→ Бот «работал на 10% от задумки»: каркас живой, начинка не подгружается.

### 2026-05-07 — Переезд на новый VPS + Этап 2 (Codex-симка)

**Причина:** старый VPS удалён.

**Этап 1 (чистый перенос):**
- Архив `agent-second-brain.tar.gz` (3.4 ГБ, ~26 257 файлов) распакован под пользователя `egor`.
- Установлены: Python 3.12, uv (через pipx — `curl|sh` блокируется sandbox), Node 20, ffmpeg, Codex CLI 0.128.0.
- `uv sync`, систему пакетов проверены.
- `.gitignore` дополнен (`.pytest_cache/`, `.ruff_cache/`, `vault/.sessions/`, `logs/`, `.session/`, `.sessions/`, `.data/`, `.github_user`, `*.bak`).
- `logs/*` и `vault/.sessions/*.jsonl` сняты с трекинга git (staged для коммита).
- systemd-юнит `d-brain-bot.service` установлен и enabled (но не запущен).
- cron установлен (5 задач).
- Все `*.sh` сделаны исполняемыми.

**Этап 2 (Codex-симка как активная):**
- Создана структура `vault/.codex/{skills,agents,rules,docs}/`.
- `rules/` (9 файлов) и `docs/` (2 файла) скопированы 1:1 из `vault/.claude/`.
- 10 скиллов: `dbrain-processor` переписан с нуля под Codex и реальный vault (выкинуты блоки про `business/`, `business/crm/`, `contacts/`, `projects/clients/`, `projects/leads/` — этих папок нет). Остальные 9 скиллов (agent-memory, graph-builder, skill-builder, skill-conductor, skill-creator, todoist-ai, vault-health, video-processor, web-search) — зеркальное копирование 1:1.
- 4 агента (goal-aligner, inbox-processor, note-organizer, weekly-digest) — зеркальное копирование 1:1.
- Создан `vault/.codex/CODEX.md` — корневой конфиг симки (зеркало `vault/.claude/CLAUDE.md`, без устаревшего антибана).
- Добавлена переменная `AI_BACKEND` в `config.py` и `.env` (значение `codex`). Полные адаптеры Codex/Claude — задача на будущее.

**Эффект:** при следующей обработке `_load_skill_content()` в `processor.py` найдёт `vault/.codex/skills/dbrain-processor/SKILL.md` (вместо fallback на Claude) и Codex получит инструкции в актуальном формате под реальный vault.

---

## Известные проблемы и долги

### Блокеры для запуска бота
- **`codex login` не выполнен** на новом VPS — `~/.codex/` пустая. Пользователь делает сам.

### Блокеры для бэкапа в GitHub
- **GitHub PAT отсутствует** в `.env` и `~/.git-credentials`. Создать и прописать.
- **Утечка в git history:** `vault/.sessions/*.jsonl` (диалоги с ботом) и `logs/*` запушены в репо в прошлом. Сейчас сняты с индекса, но в истории остаются. Очистка — отдельная задача через `git filter-branch` или BFG.

### Архитектурный долг (отложено)
- Полные `CodexAdapter` / `ClaudeAdapter` в коде — `processor.py` пока жёстко на Codex, переменная `AI_BACKEND` есть, но ветвление по ней не реализовано.
- Если симка снова станет Claude — `processor.py` потребует доработки.

### Не критично
- SSH к серверу «Барыга» не настроен — `forumhouse-check.sh` будет падать каждые 2 часа в `logs/forumhouse-check.log`. На основной бот не влияет.
- `CLAUDE.md` в корне проекта отсутствует. Codex его не использует. При будущем переключении на Claude-симку придётся создать.

---

## Ключевые решения

1. **Замысел «телефон + симки»**: одна база (`vault/`, код, инфра), две сменные симки (Codex активная, Claude спящая).
2. **Ничего не удалять** из Claude-симки и Claude-кода в `processor.py` (`_tool_*`, `_dispatch_tool`, `_tool_schemas`) — это спящая симка, не мёртвый код.
3. **Структура vault**: business/contacts/projects/clients не создавались специально. Если в будущем потребуется CRM — Егор сам создаст и попросит обновить инструкции скиллов.
4. **subprocess через `codex exec`**, не API.
5. **`.sessions/` (JSONL бота) ≠ `.session/` (пайплайн)** — две разные директории.
6. **`vault/memory/MEMORY.md`** — обновлять только если файл существует, не создавать новый.
7. **mcp-cli для Todoist** — всегда, не прямые MCP tools.
8. **Cron вернулся** на Codex-эпохе (TOS OpenAI разрешает автоматику через подписку).

---

## Бэклог (отложенные улучшения)

- [ ] Полные `CodexAdapter` / `ClaudeAdapter` с ветвлением по `AI_BACKEND`
- [ ] Чистка git history от утёкших `.sessions/`/`logs/`
- [ ] SSH-конфиг для сервера «Барыга»
- [ ] Создать `CLAUDE.md` в корне (когда понадобится Claude-симка)
- [ ] Perplexity API
- [ ] Календарь / Email через MCP
- [ ] Dashboard / UI
- [ ] sentence-transformers для семантического RAG
- [ ] Claude Code Channels

---

## Журнал изменений

| Дата | Изменение | Причина |
|------|-----------|---------|
| 2026-03-27 | Создан проект на форке Шимы | Стартовая база |
| 2026-03-29 | Замечания тестировщика — 4 критических + 4 средних | Стабилизация |
| 2026-03-31 | Анти-бан архитектура — убрана автоматика | TOS Anthropic |
| ~2026-04 | Переезд на Codex CLI | Удобство, цена, нет TOS-ограничений на cron |
| 2026-05-06 | Старый VPS удалён, начало переезда на новый | — |
| 2026-05-07 | Этап 1: чистый перенос на новый VPS (185.23.35.88) | Восстановление |
| 2026-05-07 | Этап 2: создание Codex-симки `vault/.codex/`, переписан `dbrain-processor`, добавлен `AI_BACKEND` | Закрытие долга «10% от задумки» |
| 2026-05-07 | Этап 2.9: реализован `_run_claude_exec` в `processor.py`, активная симка переключена на **Claude** (`AI_BACKEND=claude`). Добавлен anti-ban guard в `process-randomized.sh` и `weekly.sh` (выходят при `AI_BACKEND=claude`). Codex остаётся доступным — для активации поменять `AI_BACKEND` в `.env` обратно на `codex` (после `codex login`). | Бот работает на подписке Claude Max до момента когда настроен Codex login |
# 2026-09-02 — отчёт Nate Herk превысил лимит Telegram

- Утренняя проверка нашла и полностью обработала новые ролики, но итоговый отчёт не был доставлен: Telegram вернул ошибку 400 из-за превышения лимита 4096 символов.
- Автоматическая запись об этой ошибке в журнале отсутствовала; инцидент добавлен вручную.
- Отправка отчётов Nate Herk переведена на безопасное разбиение по абзацам на сообщения до 3800 символов. Ошибка отправки больше не подавляется и завершает запуск с ненулевым кодом.
