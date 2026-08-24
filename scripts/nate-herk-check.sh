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

if [ "${#NEW_FOLDERS[@]}" -eq 0 ]; then
  notify "📺 Nate Herk: новых роликов нет."
  exit 0
fi

DOWNLOADED=0
PREPARED=0
ANALYZED=0
ANNOTATIONS=()
for folder in "${NEW_FOLDERS[@]}"; do
  [ -n "$(find "$PROJECT_DIR/$folder" -maxdepth 1 -type f \
    \( -name '*.mp4' -o -name '*.webm' -o -name '*.mkv' \) -print -quit 2>/dev/null)" ] \
    && DOWNLOADED=$((DOWNLOADED + 1))
  [ -s "$PROJECT_DIR/$folder/transcript.md" ] && [ -d "$PROJECT_DIR/$folder/frames" ] \
    && PREPARED=$((PREPARED + 1))
  if [ -s "$PROJECT_DIR/$folder/analysis.md" ]; then
    ANALYZED=$((ANALYZED + 1))
    ANNOTATION="$("$PROJECT_DIR/.venv/bin/python" - "$PROJECT_DIR/$folder/analysis.md" <<'PY'
import re
import sys

text = open(sys.argv[1], encoding="utf-8").read()
match = re.search(r"^## Кратко\s*\n+(.*?)(?=\n## |\Z)", text, re.MULTILINE | re.DOTALL)
if match:
    paragraph = re.sub(r"\s+", " ", match.group(1)).strip()
    sentences = re.split(r"(?<=[.!?])\s+", paragraph)
    print(" ".join(sentences[:2]))
PY
)"
    [ -n "$ANNOTATION" ] && ANNOTATIONS+=("$ANNOTATION")
  fi
done

REPORT="📺 Nate Herk: найдено новых роликов — ${#NEW_FOLDERS[@]}.

Скачано видео: $DOWNLOADED.
Подготовлены транскрипции и отобранные кадры: $PREPARED.
Готовы аналитические карточки: $ANALYZED."

if [ "${#ANNOTATIONS[@]}" -gt 0 ]; then
  REPORT+=$'\n\nО чём новые ролики:'
  for annotation in "${ANNOTATIONS[@]}"; do
    REPORT+=$'\n\n'"$annotation"
  done
fi

notify "$REPORT"
