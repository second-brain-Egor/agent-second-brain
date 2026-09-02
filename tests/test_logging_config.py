import json
import logging

from d_brain.logging_config import configure_logging


def test_error_journal_records_only_errors_and_traceback(tmp_path):
    path = tmp_path / "logs" / "errors.jsonl"
    configure_logging(path, max_bytes=10_000, backup_count=1)
    logger = logging.getLogger("test.component")

    logger.info("routine status")
    try:
        raise ValueError("broken input")
    except ValueError:
        logger.exception("processing failed")

    events = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    assert len(events) == 1
    assert events[0]["level"] == "ERROR"
    assert events[0]["source"] == "test.component"
    assert events[0]["message"] == "processing failed"
    assert "ValueError: broken input" in events[0]["exception"]


def test_error_journal_redacts_secrets(tmp_path):
    path = tmp_path / "errors.jsonl"
    configure_logging(path)

    logging.getLogger("test.secrets").error("token=very-secret-value")

    raw = path.read_text(encoding="utf-8")
    assert "very-secret-value" not in raw
    assert "[СКРЫТО]" in raw
