"""One-time deployment: drain the current reply before restarting its own bot."""

import json
from pathlib import Path
import re
import subprocess
import sys
import time

request_pid = int(sys.argv[1])
request_start = sys.argv[2]
service = "d-brain-bot"
root = Path("/home/egor/agent-second-brain")
log = root / "logs/bot.log"
status = Path(__file__).with_name("restart-status.json")
cgroup = Path("/sys/fs/cgroup/system.slice/d-brain-bot.service/cgroup.procs")


def record(state, **details):
    status.write_text(json.dumps({"state": state, **details}, ensure_ascii=False) + "\n")
    print(state, flush=True)


def same_process(pid, started):
    try:
        return Path(f"/proc/{pid}/stat").read_text().split()[21] == started
    except FileNotFoundError:
        return False


def main_pid():
    return subprocess.check_output(
        ["systemctl", "show", service, "-p", "MainPID", "--value"], text=True
    ).strip()


def running_model():
    for pid in cgroup.read_text().split():
        try:
            name = Path(f"/proc/{pid}/comm").read_text().strip()
        except FileNotFoundError:
            continue
        if name in {"codex", "claude", "node", "codex-code-mode"}:
            return True
    return False


try:
    old_pid = main_pid()
    record("waiting_for_reply", old_pid=old_pid)
    offset = log.stat().st_size
    while True:
        observed_offset = log.stat().st_size
        if not same_process(request_pid, request_start):
            break
        offset = observed_offset
        time.sleep(0.2)
    # The handler writes this only after its Telegram answer has completed.
    while True:
        with log.open() as stream:
            stream.seek(offset)
            tail = stream.read()
        if re.search(r"aiogram.event - INFO - Update id=\d+ is handled", tail):
            break
        time.sleep(0.2)
    while running_model():
        time.sleep(0.5)
    if main_pid() != old_pid:
        raise RuntimeError("Bot was restarted concurrently; deployment needs inspection")
    record("restarting", old_pid=old_pid)
    offset = log.stat().st_size
    subprocess.run(["systemctl", "restart", service], check=True)
    for _ in range(60):
        with log.open() as stream:
            stream.seek(offset)
            tail = stream.read()
        active = subprocess.run(["systemctl", "is-active", "--quiet", service]).returncode == 0
        if active and main_pid() != old_pid and "Run polling for bot" in tail:
            record("verified", old_pid=old_pid, new_pid=main_pid())
            break
        time.sleep(1)
    else:
        raise RuntimeError("Restart did not reach Telegram polling")
except Exception as error:
    record("failed", error=str(error))
    raise
