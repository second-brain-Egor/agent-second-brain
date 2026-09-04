#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="$PROJECT_DIR/.env"
STATE_FILE="${FORUMHOUSE_CHECK_STATE_FILE:-$PROJECT_DIR/logs/forumhouse-check.state.json}"
REMOTE_HOST="${FORUMHOUSE_REMOTE_HOST:-barriga}"
REMOTE_DIR="${FORUMHOUSE_REMOTE_DIR:-/root/forum-harvest}"
STALE_AFTER_SECONDS="${FORUMHOUSE_STALE_AFTER_SECONDS:-10800}"
WARN_FREE_BYTES="${FORUMHOUSE_WARN_FREE_BYTES:-5368709120}"
CRITICAL_FREE_BYTES="${FORUMHOUSE_CRITICAL_FREE_BYTES:-3221225472}"

mkdir -p "$PROJECT_DIR/logs"
if [ -f "$ENV_FILE" ]; then
    set -a
    # shellcheck disable=SC1090
    . "$ENV_FILE"
    set +a
fi

CHAT_ID="${ADMIN_USER_IDS:-${ALLOWED_USER_IDS:-}}"
CHAT_ID="${CHAT_ID//[\[\]\" ]/}"
CHAT_ID="${CHAT_ID%%,*}"

notify() {
    [ "${FORUMHOUSE_CHECK_NO_NOTIFY:-0}" != "1" ] || return 0
    [ -n "${TELEGRAM_BOT_TOKEN:-}" ] || { echo "ERROR: TELEGRAM_BOT_TOKEN не задан" >&2; return 1; }
    [ -n "$CHAT_ID" ] || { echo "ERROR: Telegram chat id не задан" >&2; return 1; }
    printf '%s' "$1" | "$PROJECT_DIR/.venv/bin/python" \
        "$PROJECT_DIR/scripts/send_telegram_message.py" \
        --token "$TELEGRAM_BOT_TOKEN" --chat-id "$CHAT_ID"
}

set +e
REMOTE_REPORT="$(ssh -o BatchMode=yes -o ConnectTimeout=20 "$REMOTE_HOST" \
    "FORUMHOUSE_REMOTE_DIR='$REMOTE_DIR' STALE_AFTER_SECONDS='$STALE_AFTER_SECONDS' bash -s" <<'EOF'
set -euo pipefail
cd "$FORUMHOUSE_REMOTE_DIR"
python3 - <<'PY'
import json, os, re, subprocess
from datetime import datetime, timezone
from pathlib import Path

root = Path(os.environ["FORUMHOUSE_REMOTE_DIR"])
stale_after = int(os.environ["STALE_AFTER_SECONDS"])
now = datetime.now(timezone.utc)

def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

def parse_dt(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")).astimezone(timezone.utc)
    except Exception:
        return None

progress = read_json(root / "progress.json")
run_state = read_json(root / "runtime/run_state.json")
summary = read_json(root / "runtime/summary.json")
last_error = read_json(root / "runtime/last_error.json")

ps = subprocess.run(["ps", "-eo", "pid=,args="], capture_output=True, text=True, check=True)
processes = []
for line in ps.stdout.splitlines():
    if re.search(r"(?:^|/)python(?:3(?:\.\d+)?)?\s+.*(?:scrape\.py|server_sync\.py)(?:\s|$)", line):
        processes.append(line.strip())

df = subprocess.run(["df", "-B1", "--output=size,used,avail,pcent", str(root)], capture_output=True, text=True, check=True)
fields = df.stdout.splitlines()[-1].split()
disk_total, disk_used, disk_free = map(int, fields[:3])
disk_percent = int(fields[3].rstrip("%"))
du = subprocess.run(["du", "-sb", str(root)], capture_output=True, text=True)
folder_size = int(du.stdout.split()[0]) if du.returncode == 0 and du.stdout.strip() else None

timestamps = []
for value in (progress.get("updated_at"), run_state.get("updated_at"), summary.get("updated_at"),
              (progress.get("active_thread") or {}).get("updated_at") if isinstance(progress.get("active_thread"), dict) else None):
    parsed = parse_dt(value)
    if parsed:
        timestamps.append(parsed)
for path in (root / "scrape.log", root / "runtime/server_sync.out"):
    if path.exists():
        timestamps.append(datetime.fromtimestamp(path.stat().st_mtime, timezone.utc))
last_activity = max(timestamps) if timestamps else None
activity_age = int((now - last_activity).total_seconds()) if last_activity else None

totals = summary.get("totals") or {}
reasons = []
if not processes:
    reasons.append("процесс загрузки не найден")
elif activity_age is None:
    reasons.append("не удалось определить время последней активности")
elif activity_age > stale_after:
    reasons.append(f"нет активности {activity_age // 60} мин")

print(json.dumps({"status": "warn" if reasons else "ok", "reasons": reasons,
    "processes": processes[:5], "process_count": len(processes), "disk_total": disk_total,
    "disk_used": disk_used, "disk_free": disk_free, "disk_percent": disk_percent,
    "folder_size": folder_size, "last_activity": last_activity.isoformat() if last_activity else None,
    "activity_age": activity_age, "run_state": run_state, "last_error": last_error,
    "totals": totals}, ensure_ascii=False))
PY
EOF
)"
SSH_RC=$?
set -e

if [ "$SSH_RC" -ne 0 ] || [ -z "$REMOTE_REPORT" ]; then
    REMOTE_REPORT="{\"status\":\"error\",\"reasons\":[\"не удалось подключиться к серверу (код $SSH_RC)\"]}"
fi

EVALUATION="$(REMOTE_REPORT="$REMOTE_REPORT" STATE_FILE="$STATE_FILE" \
    WARN_FREE_BYTES="$WARN_FREE_BYTES" CRITICAL_FREE_BYTES="$CRITICAL_FREE_BYTES" \
    "$PROJECT_DIR/.venv/bin/python" - <<'PY'
import json, os
from datetime import datetime, timezone
from pathlib import Path

report = json.loads(os.environ["REMOTE_REPORT"])
state_path = Path(os.environ["STATE_FILE"])
try:
    old = json.loads(state_path.read_text(encoding="utf-8"))
except Exception:
    old = {}

def gib(n): return "неизвестно" if n is None else f"{n / 1024**3:.2f} ГБ"

free = report.get("disk_free")
warn = int(os.environ["WARN_FREE_BYTES"])
critical = int(os.environ["CRITICAL_FREE_BYTES"])
alerts = []
if report.get("status") in {"warn", "error"}: alerts.append("stopped")
if free is not None and free <= critical: alerts.append("disk-critical")
elif free is not None and free <= warn: alerts.append("disk-warning")

fingerprint = ",".join(alerts)
old_fingerprint = old.get("fingerprint", "")
message = ""
if fingerprint and fingerprint != old_fingerprint:
    parts = []
    if "stopped" in alerts:
        reason = "; ".join(report.get("reasons") or ["неизвестная причина"])
        parts.append(f"⛔️ Загрузка Forumhouse остановилась или зависла.\n\nПричина контроля: {reason}.")
    if "disk-critical" in alerts:
        parts.append(f"🔴 На Барыге осталось {gib(free)}. Это критический уровень: загрузку нужно остановить на границе текущей темы и перенести данные на компьютер.")
    elif "disk-warning" in alerts:
        parts.append(f"⚠️ На Барыге осталось {gib(free)}. Свободное место подходит к критическому уровню 3 ГБ — пора подготовить перенос данных.")
    message = "\n\n".join(parts)
elif not fingerprint and old_fingerprint:
    message = f"✅ Контроль Forumhouse снова в норме. Процесс работает, свободно {gib(free)}."

stored_fingerprint = f"pending:{fingerprint}" if message else fingerprint
state_path.write_text(json.dumps({"updated_at": datetime.now(timezone.utc).isoformat(),
    "fingerprint": stored_fingerprint, "report": report}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"message": message, "report": report, "fingerprint": fingerprint}, ensure_ascii=False))
PY
)"

MESSAGE="$(EVALUATION="$EVALUATION" "$PROJECT_DIR/.venv/bin/python" -c 'import json,os; print(json.loads(os.environ["EVALUATION"])["message"])')"
REPORT_LINE="$(EVALUATION="$EVALUATION" "$PROJECT_DIR/.venv/bin/python" -c 'import json,os; print(json.dumps(json.loads(os.environ["EVALUATION"])["report"], ensure_ascii=False))')"
printf '[%s] %s\n' "$(TZ=Europe/Moscow date '+%F %T MSK')" "$REPORT_LINE"
if [ -n "$MESSAGE" ]; then
    notify "$MESSAGE"
    EVALUATION="$EVALUATION" STATE_FILE="$STATE_FILE" "$PROJECT_DIR/.venv/bin/python" - <<'PY'
import json, os
from pathlib import Path

evaluation = json.loads(os.environ["EVALUATION"])
path = Path(os.environ["STATE_FILE"])
state = json.loads(path.read_text(encoding="utf-8"))
state["fingerprint"] = evaluation["fingerprint"]
path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
PY
fi
