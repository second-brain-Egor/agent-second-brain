import json
from datetime import datetime, timedelta, timezone
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
GIB = 1024 ** 3


@pytest.fixture
def checker(tmp_path):
    (tmp_path / "scripts").mkdir()
    (tmp_path / ".venv/bin").mkdir(parents=True)
    (tmp_path / ".venv/bin/python").symlink_to(sys.executable)
    script = tmp_path / "scripts/forumhouse-check.sh"
    shutil.copy2(ROOT / "scripts/forumhouse-check.sh", script)
    (tmp_path / ".env").write_text("TELEGRAM_BOT_TOKEN=test\nALLOWED_USER_IDS='[123]'\n")
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    ssh = fake_bin / "ssh"
    ssh.write_text('#!/bin/sh\ncat "$FAKE_REPORT"\nexit "${FAKE_SSH_RC:-0}"\n')
    ssh.chmod(0o755)
    sender = tmp_path / "scripts/send_telegram_message.py"
    sender.write_text('''import os, sys
from pathlib import Path
if os.environ.get("FAIL_SEND") == "1":
    sys.exit(1)
with Path(os.environ["SENT_MESSAGES"]).open("a") as f:
    f.write(__import__("json").dumps(sys.stdin.read(), ensure_ascii=False) + "\\n")
''')
    report = tmp_path / "report.json"
    sent = tmp_path / "sent.jsonl"
    state = tmp_path / "logs/forumhouse-check.state.json"

    def run(status="ok", free=10 * GIB, **extra):
        report.write_text(json.dumps({
            "status": status, "disk_free": free,
            "reasons": ["процесс загрузки не найден"] if status == "warn" else [],
        }))
        env = {**os.environ, "PATH": str(fake_bin) + os.pathsep + os.environ["PATH"],
               "FAKE_REPORT": str(report), "SENT_MESSAGES": str(sent), **extra}
        result = subprocess.run(["bash", str(script)], env=env, capture_output=True, text=True)
        messages = [json.loads(line) for line in sent.read_text().splitlines()] if sent.exists() else []
        return result, messages, json.loads(state.read_text()) if state.exists() else None

    return run


def test_stopped_and_disk_alerts_are_deduplicated_and_recovery_sent(checker):
    result, messages, state = checker("warn", 4 * GIB)
    assert result.returncode == 0
    assert len(messages) == 1
    assert "остановилась" in messages[0] and "4.00 ГБ" in messages[0]
    assert state["fingerprint"] == "stopped,disk-warning"
    assert len(checker("warn", 4 * GIB)[1]) == 1
    result, messages, state = checker("warn", 2 * GIB)
    assert len(messages) == 2 and "критический уровень" in messages[-1]
    assert state["fingerprint"] == "stopped,disk-critical"
    result, messages, state = checker()
    assert len(messages) == 3 and "снова в норме" in messages[-1]
    assert state["fingerprint"] == ""
    assert len(checker()[1]) == 3


def test_failed_delivery_is_retried(checker):
    result, messages, state = checker("warn", FAIL_SEND="1")
    assert result.returncode != 0 and messages == []
    assert state["fingerprint"] == "pending:stopped"
    result, messages, state = checker("warn")
    assert result.returncode == 0 and len(messages) == 1
    assert state["fingerprint"] == "stopped"


def test_dry_run_does_not_acknowledge_alert(checker):
    result, messages, state = checker("warn", FORUMHOUSE_CHECK_NO_NOTIFY="1")
    assert result.returncode == 0 and messages == [] and state is None
    assert len(checker("warn")[1]) == 1
    previous = checker("warn")[2]
    result, messages, state = checker(FORUMHOUSE_CHECK_NO_NOTIFY="1")
    assert len(messages) == 1 and state == previous
    assert len(checker()[1]) == 2


def test_ssh_failure_is_reported(checker):
    result, messages, state = checker(FAKE_SSH_RC="255")
    assert result.returncode == 0 and len(messages) == 1
    assert "не удалось подключиться" in messages[0]
    assert state["fingerprint"] == "stopped"


@pytest.mark.parametrize("days_ago,fingerprint,should_run", [
    (0, "stopped", False),
    (1, "stopped", True),
    (0, "pending:stopped", True),
])
def test_schedule_skips_only_today_with_confirmed_delivery(tmp_path, days_ago, fingerprint, should_run):
    (tmp_path / "scripts").mkdir()
    (tmp_path / "logs").mkdir()
    (tmp_path / ".venv/bin").mkdir(parents=True)
    (tmp_path / ".venv/bin/python").symlink_to(sys.executable)
    script = tmp_path / "scripts/forumhouse-check-randomized.sh"
    shutil.copy2(ROOT / "scripts/forumhouse-check-randomized.sh", script)
    marker = tmp_path / "ran"
    (tmp_path / "scripts/forumhouse-check.sh").write_text('touch "$TEST_MARKER"\n')
    (tmp_path / "logs/forumhouse-check.state.json").write_text(json.dumps({
        "updated_at": (datetime.now(timezone.utc) - timedelta(days=days_ago)).isoformat(),
        "fingerprint": fingerprint,
    }))
    result = subprocess.run(["bash", str(script)], capture_output=True, text=True, env={
        **os.environ, "FORUMHOUSE_CHECK_MAX_DELAY_SECONDS": "0", "TEST_MARKER": str(marker),
    })
    assert result.returncode == 0
    assert marker.exists() == should_run
