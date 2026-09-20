#!/bin/bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="$PROJECT_DIR/logs"
LOCK_FILE="$LOG_DIR/forumhouse-check.lock"
MAX_DELAY_SECONDS="${FORUMHOUSE_CHECK_MAX_DELAY_SECONDS:-18000}"

mkdir -p "$LOG_DIR"

exec 202>"$LOCK_FILE"
flock -n 202 || exit 0

# Do not check twice on the day the schedule changes or cron is restarted.
STATE_FILE="${FORUMHOUSE_CHECK_STATE_FILE:-$LOG_DIR/forumhouse-check.state.json}"
if "$PROJECT_DIR/.venv/bin/python" - "$STATE_FILE" <<'PY'
import json, sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

try:
    state = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    stamp = datetime.fromisoformat(state["updated_at"])
    tz = ZoneInfo("Europe/Moscow")
    checked_today = stamp.astimezone(tz).date() == datetime.now(tz).date()
    delivered = not state.get("fingerprint", "").startswith("pending:")
except (OSError, ValueError, KeyError, TypeError):
    checked_today = delivered = False
sys.exit(0 if checked_today and delivered else 1)
PY
then
    exit 0
fi

delay=$(( RANDOM % (MAX_DELAY_SECONDS + 1) ))
printf '[%s] Forumhouse randomized check: delay=%ss\n' \
    "$(TZ=Europe/Moscow date '+%F %T MSK')" "$delay"
sleep "$delay"

exec /bin/bash "$PROJECT_DIR/scripts/forumhouse-check.sh"
