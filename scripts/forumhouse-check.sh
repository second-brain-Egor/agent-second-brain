#!/bin/bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="$PROJECT_DIR/logs"
mkdir -p "$LOG_DIR"

REMOTE_HOST="${FORUMHOUSE_REMOTE_HOST:-barriga}"
REMOTE_DIR="${FORUMHOUSE_REMOTE_DIR:-/root/forum-harvest}"
STALE_AFTER_SECONDS="${FORUMHOUSE_STALE_AFTER_SECONDS:-10800}"

timestamp_local() {
    TZ=Europe/Moscow date '+%F %T MSK'
}

ssh_cmd=(
    sudo -u clawd
    ssh
    -o BatchMode=yes
    -o ConnectTimeout=20
    "$REMOTE_HOST"
    "FORUMHOUSE_REMOTE_DIR='$REMOTE_DIR' STALE_AFTER_SECONDS='$STALE_AFTER_SECONDS' bash -s"
)

remote_report="$(
    "${ssh_cmd[@]}" <<'EOF'
set -euo pipefail

cd "$FORUMHOUSE_REMOTE_DIR"

python3 - <<'PY'
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

remote_dir = Path(os.environ["FORUMHOUSE_REMOTE_DIR"])
stale_after = int(os.environ["STALE_AFTER_SECONDS"])
log_path = remote_dir / "scrape.log"
progress_path = remote_dir / "progress.json"
run_state_path = remote_dir / "runtime" / "run_state.json"

now = datetime.now(timezone.utc)

def read_json(path: Path):
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None

def parse_log_timestamp(path: Path):
    if not path.exists():
        return None
    pattern = re.compile(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})")
    with path.open("r", encoding="utf-8", errors="ignore") as fh:
        lines = fh.readlines()[-200:]
    for line in reversed(lines):
        match = pattern.search(line)
        if match:
            return datetime.strptime(match.group(1), "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
    return None

progress = read_json(progress_path) or {}
run_state = read_json(run_state_path) or {}

pgrep = subprocess.run(
    ["pgrep", "-af", "python.*(scrape.py|server_sync.py)"],
    capture_output=True,
    text=True,
)
process_lines = [line.strip() for line in pgrep.stdout.splitlines() if line.strip()]

du = subprocess.run(
    ["du", "-sb", str(remote_dir)],
    capture_output=True,
    text=True,
)
folder_size_bytes = None
if du.returncode == 0 and du.stdout.strip():
    first_field = du.stdout.split()[0]
    try:
        folder_size_bytes = int(first_field)
    except ValueError:
        folder_size_bytes = None

log_dt = parse_log_timestamp(log_path)
log_age = int((now - log_dt).total_seconds()) if log_dt else None

status = "ok"
reasons = []
if not process_lines:
    status = "warn"
    reasons.append("процесс не найден")
if log_age is None:
    status = "warn"
    reasons.append("не найден штамп времени в scrape.log")
elif log_age > stale_after:
    status = "warn"
    reasons.append(f"лог не обновлялся {log_age // 60} мин")

report = {
    "status": status,
    "reasons": reasons,
    "remote_dir": str(remote_dir),
    "folder_size_bytes": folder_size_bytes,
    "process_count": len(process_lines),
    "processes": process_lines[:5],
    "scraped_threads": len(progress.get("scraped_threads", [])),
    "completed_forums": len(progress.get("completed_forums", [])),
    "active_thread": progress.get("active_thread") if isinstance(progress.get("active_thread"), dict) else None,
    "run_state_status": run_state.get("status"),
    "run_state_phase": run_state.get("phase"),
    "run_state_updated_at": run_state.get("updated_at"),
    "log_updated_at": log_dt.isoformat() if log_dt else None,
    "log_age_seconds": log_age,
}

print(json.dumps(report, ensure_ascii=False))
PY
EOF
)"

REMOTE_REPORT="$remote_report" python3 - <<'PY'
import json
import os
from datetime import datetime, timezone

report = json.loads(os.environ["REMOTE_REPORT"])

def fmt_size(size_bytes):
    if size_bytes is None:
        return "n/a"
    units = ["Б", "КиБ", "МиБ", "ГиБ", "ТиБ"]
    size = float(size_bytes)
    unit = units[0]
    for next_unit in units[1:]:
        if size < 1024:
            break
        size /= 1024
        unit = next_unit
    precision = 0 if unit == "Б" else 2
    return f"{size:.{precision}f} {unit}"

def fmt_age(seconds):
    if seconds is None:
        return "n/a"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes} мин"
    hours = minutes // 60
    rem = minutes % 60
    return f"{hours} ч {rem} мин"

stamp = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
reasons = "; ".join(report["reasons"]) if report["reasons"] else "признаков застоя нет"
procs = " | ".join(report["processes"]) if report["processes"] else "нет"

print(f"[{stamp}] Forumhouse check: {report['status'].upper()}")
print(f"remote_dir={report['remote_dir']}")
print(
    "folder_size="
    f"bytes:{report['folder_size_bytes'] if report['folder_size_bytes'] is not None else 'n/a'} "
    f"human:{fmt_size(report['folder_size_bytes'])}"
)
print(f"process_count={report['process_count']}")
print(f"processes={procs}")
print(
    "progress="
    f"scraped_threads:{report['scraped_threads']} "
    f"completed_forums:{report['completed_forums']}"
)
active = report.get("active_thread") or {}
if active:
    print(
        "active_thread="
        f"forum_id:{active.get('forum_id', 'n/a')} "
        f"thread_id:{active.get('thread_id', 'n/a')} "
        f"page:{active.get('saved_pages', 'n/a')}/{active.get('expected_pages', 'n/a')} "
        f"posts:{active.get('posts_count', 'n/a')} "
        f"updated_at:{active.get('updated_at', 'n/a')}"
    )
print(
    "run_state="
    f"status:{report['run_state_status'] or 'n/a'} "
    f"phase:{report['run_state_phase'] or 'n/a'} "
    f"updated_at:{report['run_state_updated_at'] or 'n/a'}"
)
print(
    "log="
    f"updated_at:{report['log_updated_at'] or 'n/a'} "
    f"age:{fmt_age(report['log_age_seconds'])}"
)
print(f"summary={reasons}")
PY
