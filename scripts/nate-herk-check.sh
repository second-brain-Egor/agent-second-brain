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
trap 'rm -f "$BEFORE" "$AFTER"' EXIT
state_folders | sort -u >"$BEFORE"

if ! "$PROJECT_DIR/.venv/bin/python" "$COLLECTOR" \
    --url "https://youtube.com/@nateherk/videos" \
    --output "$OUTPUT_DIR" \
    --limit 50 \
    --only-new \
    --frames \
    --keep-video \
    --sub-langs "en"; then
  notify "⚠️ Nate Herk: проверка завершилась с ошибкой. Новые ролики могли обработаться не полностью."
  exit 1
fi

state_folders | sort -u >"$AFTER"
mapfile -t NEW_FOLDERS < <(comm -13 "$BEFORE" "$AFTER")

if [ "${#NEW_FOLDERS[@]}" -eq 0 ]; then
  notify "📺 Nate Herk: новых роликов нет."
  exit 0
fi

DOWNLOADED=0
PREPARED=0
ANALYZED=0
for folder in "${NEW_FOLDERS[@]}"; do
  [ -n "$(find "$PROJECT_DIR/$folder" -maxdepth 1 -type f \
    \( -name '*.mp4' -o -name '*.webm' -o -name '*.mkv' \) -print -quit 2>/dev/null)" ] \
    && DOWNLOADED=$((DOWNLOADED + 1))
  [ -s "$PROJECT_DIR/$folder/transcript.md" ] && [ -d "$PROJECT_DIR/$folder/frames" ] \
    && PREPARED=$((PREPARED + 1))
  [ -s "$PROJECT_DIR/$folder/analysis.md" ] && ANALYZED=$((ANALYZED + 1))
done

notify "📺 Nate Herk: найдено новых роликов — ${#NEW_FOLDERS[@]}.

Скачано видео: $DOWNLOADED.
Подготовлены транскрипции и отобранные кадры: $PREPARED.
Готовы аналитические карточки: $ANALYZED."
