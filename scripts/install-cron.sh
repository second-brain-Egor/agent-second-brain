#!/bin/bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
CRON_TMP="$(mktemp)"
PATH_LINE="PATH=$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin"
DAILY_SCHEDULE="${DAILY_CRON_SCHEDULE:-*/5 * * * *}"
WEEKLY_SCHEDULE="${WEEKLY_CRON_SCHEDULE:-0 18 * * 0}"
FORUMHOUSE_CHECK_SCHEDULE="${FORUMHOUSE_CHECK_SCHEDULE:-0 */2 * * *}"
TODOIST_REMINDERS_SCHEDULE="${TODOIST_REMINDERS_SCHEDULE:-* * * * *}"
NATE_HERK_CHECK_SCHEDULE="${NATE_HERK_CHECK_SCHEDULE:-0 4 * * *}"
PYTHON_BIN="$PROJECT_DIR/.venv/bin/python"

crontab -l 2>/dev/null \
    | sed '/# >>> agent-second-brain >>>/,/# <<< agent-second-brain <<</d' \
    | grep -v '^PATH=/home/egor/.local/bin:/usr/local/bin:/usr/bin:/bin$' >"$CRON_TMP" || true

{
    echo "$PATH_LINE"
    echo "# >>> agent-second-brain >>>"
    echo "@reboot cd $PROJECT_DIR && /bin/bash $PROJECT_DIR/scripts/run-bot.sh"
    echo "$DAILY_SCHEDULE cd $PROJECT_DIR && /bin/bash $PROJECT_DIR/scripts/process-randomized.sh >>$PROJECT_DIR/logs/process.log 2>&1"
    echo "$WEEKLY_SCHEDULE cd $PROJECT_DIR && /bin/bash $PROJECT_DIR/scripts/weekly.sh"
    echo "$FORUMHOUSE_CHECK_SCHEDULE cd $PROJECT_DIR && /bin/bash $PROJECT_DIR/scripts/forumhouse-check-randomized.sh >>$PROJECT_DIR/logs/forumhouse-check.log 2>&1"
    echo "$TODOIST_REMINDERS_SCHEDULE cd $PROJECT_DIR && $PYTHON_BIN $PROJECT_DIR/scripts/todoist-reminders.py >>$PROJECT_DIR/logs/todoist-reminders.log 2>&1"
    echo "$NATE_HERK_CHECK_SCHEDULE cd $PROJECT_DIR && /bin/bash $PROJECT_DIR/scripts/nate-herk-check.sh >>'$PROJECT_DIR/vault/projects/Nate Herk/logs/cron.log' 2>&1"
    echo "# <<< agent-second-brain <<<"
} >>"$CRON_TMP"

crontab "$CRON_TMP"
rm -f "$CRON_TMP"

echo "Cron automation installed:"
echo "  @reboot  bot startup"
echo "  $DAILY_SCHEDULE  randomized daily processing check (runs once between 00:00 and 05:00 Moscow)"
echo "  $WEEKLY_SCHEDULE  weekly digest"
echo "  $FORUMHOUSE_CHECK_SCHEDULE  forumhouse check with random delay up to 30 minutes"
echo "  $TODOIST_REMINDERS_SCHEDULE  one-off Todoist reminders to Telegram"
echo "  $NATE_HERK_CHECK_SCHEDULE  Nate Herk channel check (07:00 Moscow)"
