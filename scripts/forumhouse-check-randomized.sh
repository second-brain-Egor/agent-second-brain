#!/bin/bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="$PROJECT_DIR/logs"
LOCK_FILE="/tmp/d-brain-forumhouse-check.lock"
MAX_DELAY_SECONDS="${FORUMHOUSE_CHECK_MAX_DELAY_SECONDS:-1800}"

mkdir -p "$LOG_DIR"

exec 202>"$LOCK_FILE"
flock -n 202 || exit 0

delay=$(( RANDOM % (MAX_DELAY_SECONDS + 1) ))
printf '[%s] Forumhouse randomized check: delay=%ss\n' \
    "$(TZ=Europe/Moscow date '+%F %T MSK')" "$delay"
sleep "$delay"

exec /bin/bash "$PROJECT_DIR/scripts/forumhouse-check.sh"

