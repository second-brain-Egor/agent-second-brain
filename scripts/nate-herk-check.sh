#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="/home/egor/agent-second-brain"
OUTPUT_DIR="vault/projects/Nate Herk"
COLLECTOR="vault/projects/Скрипт для выгрузки видео/scripts/выгрузка-видео.py"
ENV_FILE="$PROJECT_DIR/.env"
STATE_FILE="$PROJECT_DIR/$OUTPUT_DIR/download-state.json"

if [ -f "$ENV_FILE" ]; then
  set -a
  # shellcheck disable=SC1090
  . "$ENV_FILE"
  set +a
fi

CHAT_ID="${ALLOWED_USER_IDS:-}"
CHAT_ID="${CHAT_ID//[\[\]\" ]/}"
CHAT_ID="${CHAT_ID%%,*}"

notify() {
  [ -n "${TELEGRAM_BOT_TOKEN:-}" ] || return 0
  [ -n "$CHAT_ID" ] || return 0
  curl -fsS --max-time 20 \
    "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
    -d "chat_id=$CHAT_ID" \
    --data-urlencode "text=$1" >/dev/null || true
}

state_folders() {
  [ -f "$STATE_FILE" ] || return 0
  "$PROJECT_DIR/.venv/bin/python" - "$STATE_FILE" <<'PY'
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
for item in data.get("videos", {}).values():
    folder = item.get("folder")
    if folder:
        print(folder)
PY
}

cd "$PROJECT_DIR"

BEFORE="$(mktemp)"
AFTER="$(mktemp)"
RUN_LOG="$(mktemp)"
trap 'rm -f "$BEFORE" "$AFTER" "$RUN_LOG"' EXIT
state_folders | sort -u >"$BEFORE"

if ! "$PROJECT_DIR/.venv/bin/python" "$COLLECTOR" \
    --url "https://youtube.com/@nateherk/videos" \
    --output "$OUTPUT_DIR" \
    --limit 50 \
    --only-new \
    --direct-network \
    --frames \
    --keep-video \
    --sub-langs "en" >"$RUN_LOG" 2>&1; then
  cat "$RUN_LOG"
  ERROR_REASON="$("$PROJECT_DIR/.venv/bin/python" - "$RUN_LOG" <<'PY'
import re
import sys

text = open(sys.argv[1], encoding="utf-8", errors="replace").read()

if re.search(r"(?:HTTP Error )?403(?: Forbidden)?", text, re.IGNORECASE):
    print("YouTube отклонил скачивание видео: ошибка 403 Forbidden.")
elif re.search(r"(?:HTTP Error )?429|Too Many Requests", text, re.IGNORECASE):
    print("YouTube временно ограничил запросы: ошибка 429 Too Many Requests.")
elif re.search(r"timed? out|timeout", text, re.IGNORECASE):
    print("Истекло время ожидания ответа от YouTube.")
elif re.search(r"Temporary failure in name resolution|Name or service not known", text, re.IGNORECASE):
    print("Не удалось разрешить адрес YouTube: ошибка сети или DNS.")
else:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    error_lines = [
        line for line in lines
        if re.search(r"\b(?:error|failed|exception)\b", line, re.IGNORECASE)
    ]
    reason = (error_lines or lines or ["Причина не указана в журнале."])[-1]
    reason = re.sub(r"\s+", " ", reason)
    print(reason[:500])
PY
)"
  notify "⚠️ Nate Herk: проверка завершилась с ошибкой.

Причина: $ERROR_REASON"
  exit 1
fi

cat "$RUN_LOG"

state_folders | sort -u >"$AFTER"
mapfile -t NEW_FOLDERS < <(comm -13 "$BEFORE" "$AFTER")

# Карточки — обязательная часть ежедневного контура. Очередь запускается после
# каждой проверки, в том числе когда остался незавершённый материал с прошлого
# запуска. Файловая блокировка в обработчике не допускает параллельных дублей.
PROCESSING_OK=1
if ! /bin/bash "$PROJECT_DIR/scripts/nate-herk-process-pending.sh"; then
  PROCESSING_OK=0
fi

if [ "${#NEW_FOLDERS[@]}" -eq 0 ]; then
  if [ "$PROCESSING_OK" -eq 1 ]; then
    notify "📺 Nate Herk — утренний отчёт

Новых роликов нет.

✅ Проверка завершена. Ошибок нет."
    exit 0
  fi
  notify "⚠️ Nate Herk: новых роликов нет, но не удалось завершить очередь аналитических карточек."
  exit 1
fi

ANALYZED=0
VIDEO_SUMMARIES=()
REPORT_DETAILS_OK=1
for folder in "${NEW_FOLDERS[@]}"; do
  if [ -s "$PROJECT_DIR/$folder/analysis.md" ]; then
    ANALYZED=$((ANALYZED + 1))
    VIDEO_SUMMARY="$("$PROJECT_DIR/.venv/bin/python" - "$PROJECT_DIR/$folder/analysis.md" <<'PY'
import re
import sys

text = open(sys.argv[1], encoding="utf-8").read()

def section(*names):
    alternatives = "|".join(re.escape(name) for name in names)
    match = re.search(
        rf"^## (?:{alternatives})\s*\n+(.*?)(?=\n## |\Z)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    if not match:
        return ""
    value = re.sub(r"\*\*([^*]+?)\*\*", r"\1", match.group(1))
    return re.sub(r"\s+", " ", value).strip()

title_match = re.search(r"^# (?:Карточка ролика:\s*)?(.+)$", text, re.MULTILINE)
title = title_match.group(1).strip() if title_match else ""
theme = section("Тема")
content = section("Краткое содержание", "Кратко")
conclusion = section("Основной вывод")

if all((title, theme, content, conclusion)):
    print(f"Название: {title}\n\nТема: {theme}\n\nСодержание: {content}\n\nОсновной вывод: {conclusion}")
PY
)"
    if [ -n "$VIDEO_SUMMARY" ]; then
      VIDEO_SUMMARIES+=("$VIDEO_SUMMARY")
    else
      REPORT_DETAILS_OK=0
    fi
  fi
done

REPORT="📺 Nate Herk — утренний отчёт

Новых роликов: ${#NEW_FOLDERS[@]}."

if [ "${#VIDEO_SUMMARIES[@]}" -gt 0 ]; then
  for summary in "${VIDEO_SUMMARIES[@]}"; do
    REPORT+=$'\n\n'"$summary"
  done
fi

if [ "$PROCESSING_OK" -eq 1 ] && [ "$REPORT_DETAILS_OK" -eq 1 ] \
    && [ "$ANALYZED" -eq "${#NEW_FOLDERS[@]}" ]; then
  REPORT+=$'\n\n✅ Обработка полностью завершена. Ошибок нет.'
else
  REPORT+=$'\n\n⚠️ Обработка завершена не полностью.'
  [ "$ANALYZED" -lt "${#NEW_FOLDERS[@]}" ] \
    && REPORT+=$'\n'"Не готовы аналитические карточки: $((${#NEW_FOLDERS[@]} - ANALYZED))."
  [ "$REPORT_DETAILS_OK" -eq 0 ] \
    && REPORT+=$'\nНе удалось сформировать обязательное содержание отчёта из карточки.'
  [ "$PROCESSING_OK" -eq 0 ] \
    && REPORT+=$'\nОчередь обработки завершилась с ошибкой.'
fi

notify "$REPORT"

[ "$PROCESSING_OK" -eq 1 ] \
  && [ "$REPORT_DETAILS_OK" -eq 1 ] \
  && [ "$ANALYZED" -eq "${#NEW_FOLDERS[@]}" ] \
  || exit 1
