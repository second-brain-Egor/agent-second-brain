#!/bin/bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# Anti-ban guard: skip LLM-triggering automation when Claude sim is active.
# Anthropic TOS forbids automated calls via subscription. If AI_BACKEND=claude — exit silently.
if [ -f "$PROJECT_DIR/.env" ]; then
    AI_BACKEND_VAL="$(grep -E '^AI_BACKEND=' "$PROJECT_DIR/.env" | tail -n1 | cut -d= -f2 | tr -d '"' | tr -d "'" | tr -d '[:space:]')"
    if [ "${AI_BACKEND_VAL:-codex}" = "claude" ]; then
        exit 0
    fi
fi

STATE_DIR="$PROJECT_DIR/logs"
STATE_FILE="$STATE_DIR/process-randomized.state"
LOCK_FILE="/tmp/d-brain-process-randomized.lock"

mkdir -p "$STATE_DIR"

exec 201>"$LOCK_FILE"
flock -n 201 || exit 0

MOSCOW_TODAY="$(TZ=Europe/Moscow date +%F)"
CURRENT_HOUR="$(TZ=Europe/Moscow date +%H)"
CURRENT_MIN="$(TZ=Europe/Moscow date +%M)"
CURRENT_MINUTE=$((10#$CURRENT_HOUR * 60 + 10#$CURRENT_MIN))
WINDOW_END_MINUTE=$((5 * 60))

if [ "$CURRENT_MINUTE" -gt "$WINDOW_END_MINUTE" ]; then
    exit 0
fi

state_date=""
target_minute=""
ran_marker=""

if [ -f "$STATE_FILE" ]; then
    IFS='|' read -r state_date target_minute ran_marker < "$STATE_FILE" || true
fi

if [ "$state_date" != "$MOSCOW_TODAY" ] || [ -z "$target_minute" ]; then
    target_minute=$(( RANDOM % (WINDOW_END_MINUTE + 1) ))
    printf '%s|%s|\n' "$MOSCOW_TODAY" "$target_minute" > "$STATE_FILE"
    printf 'RANDOMIZED_PROCESS: picked %02d:%02d Moscow for %s\n' \
        $((target_minute / 60)) $((target_minute % 60)) "$MOSCOW_TODAY"
fi

if [ "$ran_marker" = "done" ]; then
    exit 0
fi

if [ "$CURRENT_MINUTE" -lt "$target_minute" ]; then
    exit 0
fi

printf '%s|%s|done\n' "$MOSCOW_TODAY" "$target_minute" > "$STATE_FILE"
printf 'RANDOMIZED_PROCESS: starting at %02d:%02d Moscow for target %02d:%02d\n' \
    $((CURRENT_MINUTE / 60)) $((CURRENT_MINUTE % 60)) \
    $((target_minute / 60)) $((target_minute % 60))

exec /bin/bash "$PROJECT_DIR/scripts/process.sh"
