import importlib.util
from pathlib import Path


module_path = Path(__file__).parents[1] / "scripts" / "send_telegram_message.py"
spec = importlib.util.spec_from_file_location("send_telegram_message", module_path)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
split_message = module.split_message


def test_short_message_is_not_split() -> None:
    assert split_message("Первый абзац.\n\nВторой абзац.") == [
        "Первый абзац.\n\nВторой абзац."
    ]


def test_long_report_is_split_below_telegram_limit() -> None:
    report = "\n\n".join(["Раздел " + ("текст " * 900)] * 3)
    chunks = split_message(report)

    assert len(chunks) > 1
    assert all(len(chunk) <= 3800 for chunk in chunks)
    normalized_chunks = "".join(chunks).replace(" ", "").replace("\n", "")
    normalized_report = report.replace(" ", "").replace("\n", "")
    assert normalized_chunks == normalized_report
