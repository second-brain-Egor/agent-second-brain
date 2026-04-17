#!/bin/bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
CRON_TMP="$(mktemp)"
PATH_LINE="PATH=$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin"
DAILY_SCHEDULE="${DAILY_CRON_SCHEDULE:-*/5 * * * *}"
WEEKLY_SCHEDULE="${WEEKLY_CRON_SCHEDULE:-0 18 * * 0}"

crontab -l 2>/dev/null \
    | sed '/# >>> agent-second-brain >>>/,/# <<< agent-second-brain <<</d' \
    | grep -v '^PATH=/home/egor/.local/bin:/usr/local/bin:/usr/bin:/bin$' >"$CRON_TMP" || true

{
    echo "$PATH_LINE"
    echo "# >>> agent-second-brain >>>"
    echo "@reboot cd $PROJECT_DIR && /bin/bash $PROJECT_DIR/scripts/run-bot.sh"
    echo "$DAILY_SCHEDULE cd $PROJECT_DIR && /bin/bash $PROJECT_DIR/scripts/process-randomized.sh >>$PROJECT_DIR/logs/process.log 2>&1"
    echo "$WEEKLY_SCHEDULE cd $PROJECT_DIR && /bin/bash $PROJECT_DIR/scripts/weekly.sh"
    echo "*/30 8-22 * * * cd $PROJECT_DIR && $HOME/.local/bin/uv run python heartbeat/heartbeat.py >>$PROJECT_DIR/logs/heartbeat.log 2>&1"
    echo "# <<< agent-second-brain <<<"
} >>"$CRON_TMP"

crontab "$CRON_TMP"
rm -f "$CRON_TMP"

echo "Cron automation installed:"
echo "  @reboot  bot startup"
echo "  $DAILY_SCHEDULE  randomized daily processing check (runs once between 00:00 and 05:00 Moscow)"
echo "  $WEEKLY_SCHEDULE  weekly digest"
echo "  */30 8-22 * * *  heartbeat reminders"
