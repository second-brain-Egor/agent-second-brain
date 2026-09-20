import importlib.util
from pathlib import Path

import pytest

from d_brain.services.processor import AgentProcessor


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "sync-assistants.py"
spec = importlib.util.spec_from_file_location("assistant_sync", SCRIPT)
sync = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync)


@pytest.mark.parametrize("changed_side", ["left", "right"])
def test_bidirectional_change_preserves_other_side(tmp_path, changed_side):
    left, right = tmp_path / "left", tmp_path / "right"
    left.mkdir()
    right.mkdir()
    for root in [left, right]:
        (root / "rules.md").write_text("original")
    baseline = {"rules.md": sync.digest(left / "rules.md")}
    changed = tmp_path / changed_side
    (changed / "rules.md").write_text("additional experience")
    changes, conflicts = sync.plan_sync(left, right, baseline)
    assert not conflicts
    assert len(changes) == 1 and changes[0][0] == changed / "rules.md"
    assert changes[0][1].read_text() == "original"


def test_missing_file_is_restored_and_conflicting_edits_are_retained(tmp_path):
    left, right = tmp_path / "left", tmp_path / "right"
    left.mkdir()
    right.mkdir()
    (left / "rules.md").write_text("retained")
    baseline = {"rules.md": sync.digest(left / "rules.md")}
    assert sync.plan_sync(left, right, baseline) == ([(left / "rules.md", right / "rules.md")], [])
    (left / "rules.md").write_text("left update")
    (right / "rules.md").write_text("right update")
    assert sync.plan_sync(left, right, baseline) == ([], ["rules.md"])


def test_shared_rules_reach_chat_and_agent_without_profile_copy(tmp_path):
    processor = object.__new__(AgentProcessor)
    processor.project_path = tmp_path
    path = tmp_path / "SHARED_ASSISTANT_RULES.md"
    path.write_text("Общее правило: проверить сохранение.")
    for read_only in [True, False]:
        assert path.read_text() in processor._build_exec_prompt("system", "request", read_only=read_only)
    path.write_text("Общее правило дополнено.")
    assert path.read_text() in processor._build_exec_prompt("system", "request", read_only=False)


def test_sync_refuses_paths_outside_instances(tmp_path):
    with pytest.raises(ValueError):
        sync.plan_sync(tmp_path / "left", tmp_path / "right", {"../.env": "hash"})


def test_unsolicited_processing_reminder_is_disabled(tmp_path, monkeypatch):
    from d_brain.services import evening_reminder

    monkeypatch.delenv("EVENING_PROCESS_REMINDER", raising=False)
    assert evening_reminder.maybe_evening_reminder(tmp_path) == ""
    assert not (tmp_path / ".session").exists()
