"""Regression checks for processing all entries since the previous run."""

import importlib.util
import os
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path
from unittest.mock import Mock

import pytest


ROOT = Path(__file__).resolve().parents[1]


def load_service(name):
    path = ROOT / "src" / "d_brain" / "services" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"pending_test_{name}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


processor_module = load_service("processor")
storage_module = load_service("storage")
TODAY = date(2026, 9, 18)
MARKER = "\n---\nprocessed: 2026-09-15T20:00:00+03:00\nthoughts: 1\ntasks: 0\n---\n"


@pytest.fixture
def processor(tmp_path, monkeypatch):
    instance = object.__new__(processor_module.AgentProcessor)
    instance.project_path = tmp_path
    instance.vault_path = tmp_path / "vault"
    (instance.vault_path / "daily").mkdir(parents=True)
    monkeypatch.setattr(instance, "_load_skill_content", lambda: "")
    monkeypatch.setattr(instance, "_load_todoist_reference", lambda: "")
    monkeypatch.setattr(instance, "_prime_context_cache", lambda: None)
    monkeypatch.setattr("d_brain.services.wiki.refresh_wiki", lambda _: None)
    monkeypatch.setattr(instance, "_run_agent", Mock(return_value="Готово"))
    return instance


def daily(processor, day, text):
    path = processor.vault_path / "daily" / f"{day}.md"
    path.write_text(f"# {day}\n{text}", encoding="utf-8")
    return path


def test_multiple_days_and_tail_after_last_marker(processor):
    daily(processor, "2026-09-01", "Старые необработанные записи")
    daily(processor, "2026-09-15", "Уже обработано" + MARKER + "Свежая запись")
    daily(processor, "2026-09-16", "Запись за следующий день")
    daily(processor, "2026-09-17", "")
    daily(processor, "2026-09-18", "Сегодняшняя запись")
    result = processor.process_pending(TODAY)
    assert result["days"] == ["2026-09-15", "2026-09-16", "2026-09-18"]
    assert processor._run_agent.call_count == 1
    prompt = processor._run_agent.call_args.args[1]
    assert "Свежая запись" in prompt
    assert "Запись за следующий день" in prompt
    assert "Сегодняшняя запись" in prompt
    assert "Старые необработанные записи" not in prompt
    assert "Уже обработано" not in prompt
    assert processor.pending_days(TODAY) == [date(2026, 9, 1)]


def test_backlog_is_processed_when_today_is_missing_or_empty(processor):
    daily(processor, "2026-09-15", "Ранее обработано" + MARKER)
    daily(processor, "2026-09-16", "Необработанная запись")
    assert processor.pending_days(TODAY) == [date(2026, 9, 16)]
    daily(processor, "2026-09-18", "")
    assert processor.process_pending(TODAY)["days"] == ["2026-09-16"]


def test_marker_older_than_two_weeks_and_short_entry(processor):
    daily(processor, "2026-08-01", "Прежнее" + MARKER + "Да")
    daily(processor, "2026-09-17", "Новая запись")
    assert processor.process_pending(TODAY)["days"] == ["2026-08-01", "2026-09-17"]


def test_no_markers_does_not_discard_older_days(processor):
    daily(processor, "2026-07-01", "Необработанный старый день")
    daily(processor, "2026-09-18", "Новый день")
    daily(processor, "2026-09-19", "Будущий день")
    daily(processor, "README", "Служебный файл")
    assert processor.pending_days(TODAY) == [date(2026, 7, 1), TODAY]


def test_html_marker_is_recognized(processor):
    daily(processor, "2026-09-17", "Старое\n<!-- ✓ processed -->\n<!-- timestamp: old -->\nНовое")
    processor.process_pending(TODAY)
    prompt = processor._run_agent.call_args.args[1]
    assert "Новое" in prompt
    assert "Старое" not in prompt
    assert processor.pending_days(TODAY) == []


def test_repeated_run_does_not_call_model_again(processor):
    daily(processor, "2026-09-18", "Запись")
    assert processor.process_pending(TODAY)["processed_entries"] == 1
    result = processor.process_pending(TODAY)
    assert result["days"] == []
    assert result["processed_entries"] == 0
    assert processor._run_agent.call_count == 1


def test_failure_keeps_failed_and_later_days_pending(processor):
    daily(processor, "2026-09-15", "Обработано" + MARKER + "Новая запись")
    for day in ["2026-09-16", "2026-09-17"]:
        daily(processor, day, "Запись")
    processor._run_agent.side_effect = RuntimeError("test failure")
    result = processor.process_pending(TODAY)
    assert "error" in result
    assert result["days"] == []
    assert processor.pending_days(TODAY) == [
        date(2026, 9, 15), date(2026, 9, 16), date(2026, 9, 17)
    ]


def test_new_messages_during_processing_are_preserved(processor):
    path = daily(processor, "2026-09-18", "Исходная запись")
    storage = storage_module.VaultStorage(processor.vault_path)

    def run(*args, **kwargs):
        storage.append_to_daily("Пришло во время обработки", datetime(2026, 9, 18, 22), "[text]")
        return "Готово"

    processor._run_agent.side_effect = run
    processor.process_pending(TODAY)
    assert "Исходная запись" in path.read_text()
    tail = processor._daily_unprocessed_tail(TODAY)
    assert "Пришло во время обработки" in tail
    assert "Исходная запись" not in tail
    processor._run_agent.side_effect = None
    processor.process_pending(TODAY)
    assert processor.pending_days(TODAY) == []


def test_new_tail_on_earlier_day_is_not_skipped(processor):
    old_day = date(2026, 9, 17)
    path = daily(processor, old_day.isoformat(), "Обработано" + MARKER + "Первая запись")
    daily(processor, "2026-09-18", "Сегодняшняя запись")

    def run(*args, **kwargs):
        with path.open("a") as handle:
            handle.write("\nПоздняя запись\n")
        return "Готово"

    processor._run_agent.side_effect = run
    assert processor.process_pending(TODAY)["days"] == ["2026-09-17", "2026-09-18"]
    assert processor._run_agent.call_count == 1
    assert processor.pending_days(TODAY) == [old_day]


def test_empty_model_result_does_not_mark_entries(processor):
    daily(processor, "2026-09-18", "Запись")
    processor._run_agent.return_value = ""
    assert "error" in processor.process_pending(TODAY)
    assert processor.pending_days(TODAY) == [TODAY]


def test_changed_snapshot_is_not_marked(processor):
    path = daily(processor, "2026-09-18", "Исходный текст")

    def run(*args, **kwargs):
        path.write_text("Исправленный текст")
        return "Готово"

    processor._run_agent.side_effect = run
    assert "error" in processor.process_pending(TODAY)
    assert processor.pending_days(TODAY) == [TODAY]
    assert "processed:" not in path.read_text()


@pytest.mark.parametrize("pending_count", [0, 1])
def test_scheduled_run_uses_backlog_even_with_empty_today(tmp_path, pending_count):
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    script = (ROOT / "scripts" / "process.sh").read_text()
    lines = script.splitlines()
    for index, line in enumerate(lines):
        if line.startswith("export PATH="):
            lines[index] = f'export PATH="{fake_bin}:$PATH"'
        if line.startswith("exec 200>"):
            lines[index] = f'exec 200>"{tmp_path}/process.lock"'
    (scripts / "process.sh").write_text("\n".join(lines) + "\n")
    ran = tmp_path / "processed"
    uv = fake_bin / "uv"
    uv.write_text(
        f"#!{sys.executable}\n"
        "import sys\nfrom pathlib import Path\n"
        "source = sys.stdin.read() if sys.argv[-1] == '-' else ''\n"
        f"if 'print(len(' in source: print({pending_count})\n"
        "elif 'result = AgentProcessor' in source:\n"
        f"    Path({str(ran)!r}).touch()\n"
        "    print('Готово')\n"
    )
    uv.chmod(0o755)
    git = fake_bin / "git"
    git.write_text("#!/bin/sh\nexit 0\n")
    git.chmod(0o755)
    result = subprocess.run(
        ["bash", str(scripts / "process.sh")], cwd=tmp_path,
        env={**os.environ, "TELEGRAM_BOT_TOKEN": "fake-token", "ALLOWED_USER_IDS": ""},
        capture_output=True, text=True, timeout=10,
    )
    assert result.returncode == 0, result.stderr
    assert ran.exists() == bool(pending_count)


def test_latest_processing_marker_excludes_older_archive(processor):
    daily(processor, "2026-05-08", "Майская запись")
    daily(processor, "2026-06-19", "Июньская запись")
    daily(processor, "2026-07-29", "Июльская запись")
    today_path = daily(processor, "2026-09-18", "Сегодня уже обработано" + MARKER)
    today_snapshot = today_path.read_text()
    result = processor.process_pending(TODAY)
    assert result["days"] == []
    assert processor._run_agent.call_count == 0
    assert today_path.read_text() == today_snapshot
    assert processor.pending_days(TODAY) == [
        date(2026, 5, 8), date(2026, 6, 19), date(2026, 7, 29)
    ]
    processor.process_pending(TODAY)
    assert processor._run_agent.call_count == 0


def test_telegram_button_processes_one_interval_with_one_model_call(processor):
    daily(processor, "2026-05-08", "Старая запись")
    daily(processor, "2026-09-14", "Обработано" + MARKER)
    for day in ["2026-09-15", "2026-09-16", "2026-09-17", "2026-09-18"]:
        daily(processor, day, f"Запись {day}")

    execution = processor_module.Execution(
        processor.project_path,
        scope="test",
        request="Обработать",
        origin="bot",
    )
    with processor_module.execution_context(execution):
        result = processor.process_pending(TODAY)

    assert result["days"] == ["2026-09-15", "2026-09-16", "2026-09-17", "2026-09-18"]
    assert processor._run_agent.call_count == 1
    assert execution.data["backlog_total"] == 5
    assert execution.data["model_call_limit"] == 1
    assert date(2026, 5, 8) in processor.pending_days(TODAY)


def test_old_partial_tail_is_outside_the_latest_processing_interval(processor):
    daily(processor, "2026-05-08", "Прежняя запись" + MARKER + "Позднее дополнение")
    daily(processor, "2026-09-18", "Сегодня обработано" + MARKER)
    assert processor.process_pending(TODAY)["days"] == []
    assert processor._run_agent.call_count == 0
    assert processor.pending_days(TODAY) == [date(2026, 5, 8)]


def test_failed_interval_can_resume_as_one_batch(processor):
    daily(processor, "2026-09-16", "Обработано" + MARKER + "Первая запись")
    daily(processor, "2026-09-17", "Вторая запись")
    daily(processor, "2026-09-18", "Третья запись")
    processor._run_agent.side_effect = RuntimeError("test failure")
    result = processor.process_pending(TODAY)
    assert "error" in result
    assert result["days"] == []
    assert processor.pending_days(TODAY) == [
        date(2026, 9, 16), date(2026, 9, 17), date(2026, 9, 18)
    ]
    processor._run_agent.side_effect = None
    assert processor.process_pending(TODAY)["days"] == [
        "2026-09-16", "2026-09-17", "2026-09-18"
    ]
    assert processor._run_agent.call_count == 2
    assert processor.pending_days(TODAY) == []
