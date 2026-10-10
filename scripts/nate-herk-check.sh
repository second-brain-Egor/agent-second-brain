#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="/home/egor/agent-second-brain"
OUTPUT_DIR="vault/projects/Nate Herk"
COLLECTOR="vault/projects/Скрипт для выгрузки видео/scripts/выгрузка-видео.py"
ENV_FILE="$PROJECT_DIR/.env"
STATE_FILE="$PROJECT_DIR/$OUTPUT_DIR/download-state.json"
NO_NOTIFY=0
if [ "${1:-}" = "--no-notify" ]; then
  NO_NOTIFY=1
elif [ "$#" -gt 0 ]; then
  echo "Использование: $0 [--no-notify]" >&2
  exit 2
fi

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
  if [ "$NO_NOTIFY" -eq 1 ]; then
    printf '%s\n' "$1"
    return 0
  fi
  [ -n "${TELEGRAM_BOT_TOKEN:-}" ] || return 0
  [ -n "$CHAT_ID" ] || return 0
  printf '%s' "$1" | "$PROJECT_DIR/.venv/bin/python" \
    "$PROJECT_DIR/scripts/send_telegram_message.py" \
    --token "$TELEGRAM_BOT_TOKEN" \
    --chat-id "$CHAT_ID"
}

state_folders() {
  [ -f "$STATE_FILE" ] || return 0
  "$PROJECT_DIR/.venv/bin/python" - "$STATE_FILE" <<'PY'
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
for item in data.get("videos", {}).values():
    folder = item.get("folder")
    if folder and item.get("status") == "complete":
        print(folder)
PY
}

cd "$PROJECT_DIR"

# Повторная попытка в тот же день может длиться часами: не даём второму запуску
# (ручному или следующему утреннему) работать параллельно с первым.
mkdir -p "$PROJECT_DIR/$OUTPUT_DIR/logs"
exec 8>"$PROJECT_DIR/$OUTPUT_DIR/logs/.check.lock"
if ! flock -n 8; then
  printf '%s Проверка уже выполняется, второй запуск пропущен\n' "$(date -Is)"
  exit 0
fi

# Правило Егора от 9 октября 2026: временную блокировку YouTube не откладывать
# до следующего утра, а повторять, пока ролики не скачаются. Окно короче суток,
# чтобы попытки закончились до следующей утренней проверки.
RETRY_INTERVAL_SECONDS="${NATE_HERK_RETRY_INTERVAL_SECONDS:-1800}"
RETRY_WINDOW_SECONDS="${NATE_HERK_RETRY_WINDOW_SECONDS:-79200}"

collect() {
  "$PROJECT_DIR/.venv/bin/python" "$COLLECTOR" \
    --url "https://youtube.com/@nateherk/videos" \
    --output "$OUTPUT_DIR" \
    --limit 50 \
    --only-new \
    --direct-network \
    --frames \
    --keep-video \
    --sub-langs "en"
}

# Печатает две строки: вид сбоя (temporary/other) и причину по-русски.
classify_error() {
  "$PROJECT_DIR/.venv/bin/python" - "$1" <<'PY'
import re
import sys

text = open(sys.argv[1], encoding="utf-8", errors="replace").read()

checks = (
    (r"Sign in to confirm|not a bot",
     "YouTube потребовал подтвердить, что качает не робот: адрес сервера временно заблокирован."),
    (r"(?:HTTP Error )?403(?: Forbidden)?", "YouTube отклонил скачивание видео (код 403)."),
    (r"(?:HTTP Error )?429|Too Many Requests", "YouTube временно ограничил запросы (код 429)."),
    (r"timed? out|timeout", "Истекло время ожидания ответа от YouTube."),
    (r"Temporary failure in name resolution|Name or service not known",
     "Не удалось разрешить адрес YouTube: ошибка сети или DNS."),
    (r"Connection (?:reset|refused|aborted)|Network is unreachable|Remote end closed"
     r"|IncompleteRead|HTTP Error 5\d\d|Unable to download (?:webpage|API page)",
     "Связь с YouTube оборвалась."),
)
for pattern, reason in checks:
    if re.search(pattern, text, re.IGNORECASE):
        print("temporary")
        print(reason)
        raise SystemExit(0)

lines = [line.strip() for line in text.splitlines() if line.strip()]
error_lines = [
    line for line in lines
    if re.search(r"\b(?:error|failed|exception)\b", line, re.IGNORECASE)
]
reason = (error_lines or lines or ["Причина не указана в журнале."])[-1]
reason = re.sub(r"\s+", " ", reason)
print("other")
print(reason[:500])
PY
}

BEFORE="$(mktemp)"
AFTER="$(mktemp)"
RUN_LOG="$(mktemp)"
trap 'rm -f "$BEFORE" "$AFTER" "$RUN_LOG"' EXIT
state_folders | sort -u >"$BEFORE"
COLLECTION_OK=1
ERROR_REASON=""
RETRY_EXHAUSTED=0
RETRY_NOTICE_SENT=0
ATTEMPT=0
START_TS="$(date +%s)"

while :; do
  ATTEMPT=$((ATTEMPT + 1))
  printf '%s Проверка канала (попытка %d)\n' "$(date -Is)" "$ATTEMPT"
  if collect >"$RUN_LOG" 2>&1; then
    COLLECTION_OK=1
    ERROR_REASON=""
    cat "$RUN_LOG"
    break
  fi
  cat "$RUN_LOG"
  COLLECTION_OK=0
  mapfile -t ERROR_INFO < <(classify_error "$RUN_LOG")
  ERROR_KIND="${ERROR_INFO[0]:-other}"
  ERROR_REASON="${ERROR_INFO[1]:-Причина не указана в журнале.}"
  [ "$ERROR_KIND" = "temporary" ] || break
  if [ $(( $(date +%s) + RETRY_INTERVAL_SECONDS - START_TS )) -gt "$RETRY_WINDOW_SECONDS" ]; then
    RETRY_EXHAUSTED=1
    break
  fi
  if [ "$RETRY_NOTICE_SENT" -eq 0 ]; then
    notify "⏳ Nate Herk: YouTube временно не даёт скачать ролики.

Причина: $ERROR_REASON

Не откладываю на завтра: пробую снова каждые $((RETRY_INTERVAL_SECONDS / 60)) минут и пришлю отчёт, как только скачаю." || true
    RETRY_NOTICE_SENT=1
  fi
  printf '%s Временный сбой, повтор через %d с\n' "$(date -Is)" "$RETRY_INTERVAL_SECONDS"
  sleep "$RETRY_INTERVAL_SECONDS"
done

RETRY_NOTE=""
if [ "$RETRY_EXHAUSTED" -eq 1 ]; then
  RETRY_NOTE="Блокировка не снялась за $(( ( $(date +%s) - START_TS ) / 3600 )) ч повторов (попыток: $ATTEMPT). Утренняя проверка продолжит с этого места."
fi

REPORT_TITLE="📺 Nate Herk — утренний отчёт"
[ "$ATTEMPT" -gt 1 ] && REPORT_TITLE="📺 Nate Herk — отчёт после повторной загрузки"

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
  if [ "$COLLECTION_OK" -eq 0 ]; then
    MESSAGE="⚠️ Nate Herk: загрузка завершилась с ошибкой.

Причина: $ERROR_REASON

Незавершённые материалы сохранены для повторной обработки."
    [ -n "$RETRY_NOTE" ] && MESSAGE+=$'\n\n'"$RETRY_NOTE"
    notify "$MESSAGE"
    exit 1
  fi
  if [ "$PROCESSING_OK" -eq 1 ]; then
    notify "$REPORT_TITLE

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
    VIDEO_SUMMARY="$("$PROJECT_DIR/.venv/bin/python" \
      "$PROJECT_DIR/scripts/nate_herk_report.py" \
      "$PROJECT_DIR/$folder/analysis.md" 2>>"$RUN_LOG" || true)"
    if [ -n "$VIDEO_SUMMARY" ]; then
      VIDEO_SUMMARIES+=("$VIDEO_SUMMARY")
    else
      REPORT_DETAILS_OK=0
    fi
  fi
done

REPORT="$REPORT_TITLE

Новых роликов: ${#NEW_FOLDERS[@]}."

if [ "${#VIDEO_SUMMARIES[@]}" -gt 0 ]; then
  for summary in "${VIDEO_SUMMARIES[@]}"; do
    REPORT+=$'\n\n'"$summary"
  done
fi

if [ "$COLLECTION_OK" -eq 1 ] && [ "$PROCESSING_OK" -eq 1 ] && [ "$REPORT_DETAILS_OK" -eq 1 ] \
    && [ "$ANALYZED" -eq "${#NEW_FOLDERS[@]}" ]; then
  REPORT+=$'\n\n✅ Обработка полностью завершена. Ошибок нет.'
else
  REPORT+=$'\n\n⚠️ Обработка завершена не полностью.'
  [ "$COLLECTION_OK" -eq 0 ] \
    && REPORT+=$'\n'"Ошибка загрузки: $ERROR_REASON"
  [ -n "$RETRY_NOTE" ] \
    && REPORT+=$'\n'"$RETRY_NOTE"
  [ "$ANALYZED" -lt "${#NEW_FOLDERS[@]}" ] \
    && REPORT+=$'\n'"Не готовы аналитические карточки: $((${#NEW_FOLDERS[@]} - ANALYZED))."
  [ "$REPORT_DETAILS_OK" -eq 0 ] \
    && REPORT+=$'\nНе удалось сформировать обязательное содержание отчёта из карточки.'
  [ "$PROCESSING_OK" -eq 0 ] \
    && REPORT+=$'\nОчередь обработки завершилась с ошибкой.'
fi

notify "$REPORT"

[ "$COLLECTION_OK" -eq 1 ] \
  && [ "$PROCESSING_OK" -eq 1 ] \
  && [ "$REPORT_DETAILS_OK" -eq 1 ] \
  && [ "$ANALYZED" -eq "${#NEW_FOLDERS[@]}" ] \
  || exit 1
