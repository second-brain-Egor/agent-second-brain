"""Учёт расхода по запросам."""
import json
import os
import sys
from pathlib import Path

from d_brain.services import usage
from d_brain.services.execution import Execution, execution_context, run_bounded

CLAUDE_STREAM = "\n".join(json.dumps(event) for event in [
    {"type": "system", "subtype": "init", "model": "claude-opus-5-5"},
    {"type": "assistant", "message": {"id": "m1"}},
    {"type": "result", "result": "Ответ", "is_error": False, "duration_ms": 12500, "num_turns": 3,
     "total_cost_usd": 0.42, "permission_denials": [{"tool_name": "Bash"}],
     "usage": {"input_tokens": 5, "cache_read_input_tokens": 1000, "cache_creation_input_tokens": 200,
               "output_tokens": 300, "output_tokens_details": {"thinking_tokens": 250}}},
])


def test_claude_summary():
    line = usage.summarize(["claude", "-p", "--model", "opus", "--effort", "xhigh"], CLAUDE_STREAM, "claude")
    assert line == {"backend": "claude", "model": "claude-opus-5-5", "effort": "xhigh", "seconds": 12.5,
                    "steps": 3, "input": 5, "cache_read": 1000, "cache_write": 200, "output": 300,
                    "thinking": 250, "cost_usd": 0.42, "ok": True, "denied": 1}


def test_codex_summary():
    stream = "\n".join(json.dumps(event) for event in [
        {"type": "item.completed", "item": {"type": "command_execution"}},
        {"type": "item.completed", "item": {"type": "agent_message", "text": "Ответ"}},
        {"type": "turn.completed", "usage": {"input_tokens": 1000, "cached_input_tokens": 900,
                                             "output_tokens": 50, "reasoning_output_tokens": 20}},
    ])
    line = usage.summarize(["codex", "exec", "--model", "gpt-6-astra", "-c", 'model_reasoning_effort="max"'],
                           stream, "codex")
    assert line["effort"] == "max" and line["steps"] == 2
    assert (line["input"], line["cache_read"], line["output"], line["thinking"]) == (100, 900, 50, 20)


def test_no_final_event_no_line():
    assert usage.summarize(["claude"], '{"type":"assistant"}', "claude") is None


def fake_cli(tmp_path, stream):
    script = tmp_path / "cli.py"
    script.write_text(f"import sys\nsys.stdin.read()\nprint({stream!r})\n")
    return [sys.executable, str(script), "--model", "opus", "--effort", "max"]


def test_run_bounded_appends_one_line(tmp_path):
    execution = Execution(tmp_path, request="промпт\n=== USER MESSAGE ===\nСколько весит аппарат?")
    with execution_context(execution):
        run_bounded(fake_cli(tmp_path, CLAUDE_STREAM), input="", cwd=tmp_path, env=os.environ.copy(),
                    backend="claude")
    lines = (tmp_path / usage.USAGE_LOG).read_text().splitlines()
    assert len(lines) == 1
    line = json.loads(lines[0])
    assert line["request"] == "Сколько весит аппарат?" and line["output"] == 300
    assert execution.data["denials"] == [{"tool_name": "Bash"}]


def test_temporary_chat_leaves_no_usage_line(tmp_path):
    execution = Execution(tmp_path, request="тайна", persistent=False)
    with execution_context(execution):
        run_bounded(fake_cli(tmp_path, CLAUDE_STREAM), input="", cwd=tmp_path, env=os.environ.copy(),
                    backend="claude")
    assert not (tmp_path / usage.USAGE_LOG).exists()


def test_usage_report(tmp_path):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
    import usage_report

    rows = [{"time": "2026-10-11T09:00:00+03:00", "model": "claude-opus-5-5", "effort": effort,
             "seconds": 10, "steps": 2, "output": 100, "thinking": 50, "cost_usd": 0.5, "ok": True}
            for effort in ("xhigh", "xhigh", "max")]
    text = usage_report.report(rows, 7)
    assert "3 запросов" in text and "мышление xhigh: 2 запросов" in text and "мышление max: 1" in text
