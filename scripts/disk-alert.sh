#!/bin/bash
# Алерт о заполнении диска в Telegram админу. Без LLM — анти-бан правила не задевает.
# Cron: каждые 30 минут. Шлёт при заполнении >= THRESHOLD, повторяет не чаще раза в 6 часов,
# при выходе за CRITICAL — каждый запуск.
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="$PROJECT_DIR/.env"
STATE_FILE="$PROJECT_DIR/logs/disk-alert.state"
THRESHOLD=90
CRITICAL=95
REPEAT_SECONDS=$((6 * 3600))

[ -f "$ENV_FILE" ] || exit 0
set -a; . "$ENV_FILE"; set +a
[ -n "${TELEGRAM_BOT_TOKEN:-}" ] || exit 0
ADMIN_ID="${ADMIN_USER_IDS%%,*}"
[ -n "$ADMIN_ID" ] || exit 0

USAGE=$(df --output=pcent / | tail -1 | tr -dc '0-9')
AVAIL=$(df -h --output=avail / | tail -1 | tr -d ' ')

if [ "$USAGE" -lt "$THRESHOLD" ]; then
    rm -f "$STATE_FILE"
    exit 0
fi

NOW=$(date +%s)
LAST_SENT=0
[ -f "$STATE_FILE" ] && LAST_SENT=$(cat "$STATE_FILE" 2>/dev/null || echo 0)

if [ "$USAGE" -lt "$CRITICAL" ] && [ $((NOW - LAST_SENT)) -lt "$REPEAT_SECONDS" ]; then
    exit 0
fi

TEXT="⚠️ Диск сервера заполнен на ${USAGE}% (свободно ${AVAIL}).

Крупнейшие потребители: /root/forum-harvest (растёт ~4 ГБ/сутки), /root/trading/analysis. Подробности: «правка second brain/2026-06-11.md»."

curl -s --max-time 15 "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
    -d chat_id="${ADMIN_ID}" \
    --data-urlencode text="${TEXT}" >/dev/null \
    && echo "$NOW" > "$STATE_FILE" \
    && echo "$(date '+%Y-%m-%d %H:%M:%S') sent alert: ${USAGE}%"
