import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).parents[1]
COLLECTOR = ROOT / "scripts/video_collector.py"
SPEC = importlib.util.spec_from_file_location("video_collector", COLLECTOR)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_original_subtitles_preferred_but_manual_preserved():
    metadata = {"automatic_captions": {"en": [], "en-orig": []}}
    assert MODULE.subtitle_languages(metadata, "en,ru") == "en-orig,ru"
    metadata["subtitles"] = {"en": [{}]}
    assert MODULE.subtitle_languages(metadata, "en") == "en"
    assert MODULE.subtitle_languages({}, "en") == "en"


@pytest.mark.parametrize("failures", [1, 2, 3])
def test_rate_limit_retries_are_bounded(monkeypatch, failures):
    calls, sleeps = [], []

    def run(command):
        calls.append(command)
        if len(calls) <= failures:
            raise subprocess.CalledProcessError(
                1, command, stderr="HTTP Error 429: Too Many Requests"
            )
        return "ok"

    monkeypatch.setattr(MODULE, "run", run)
    monkeypatch.setattr(MODULE.time, "sleep", sleeps.append)
    if failures == 3:
        with pytest.raises(subprocess.CalledProcessError):
            MODULE.run_subtitles(["yt-dlp"])
    else:
        assert MODULE.run_subtitles(["yt-dlp"]) == "ok"
    assert len(calls) == min(failures + 1, 3)
    assert sleeps == [30, 60][:min(failures, 2)]


def test_non_rate_limit_is_not_retried(monkeypatch):
    def run(command):
        raise subprocess.CalledProcessError(1, command, stderr="HTTP Error 403")

    def unexpected_sleep(_):
        pytest.fail("non-429 error must not enter the rate limit retry loop")

    monkeypatch.setattr(MODULE, "run", run)
    monkeypatch.setattr(MODULE.time, "sleep", unexpected_sleep)
    with pytest.raises(subprocess.CalledProcessError):
        MODULE.run_subtitles(["yt-dlp"])


def test_pending_video_is_not_lost_behind_newer_completed_video():
    entries = [{"id": key} for key in ("new", "done", "failed", "old")]
    state = {"videos": {
        "done": {"status": "complete"},
        "failed": {"status": "error"},
        "outside": {"status": "error", "url": "https://example.test/outside"},
    }}
    selected = MODULE.new_and_pending_entries(entries, state)
    assert [entry["id"] for entry in selected] == ["new", "failed", "outside"]
    assert selected[-1]["url"] == "https://example.test/outside"


def test_subtitle_failure_keeps_metadata_and_error_state(tmp_path, monkeypatch, capsys):
    output = tmp_path / "project"
    entry = {"id": "new-video", "title": "New video", "url": "https://example.test/video"}
    monkeypatch.setattr(MODULE, "load_flat_playlist", lambda *_: [entry])
    monkeypatch.setattr(sys, "argv", [str(COLLECTOR), "--output", str(output)])

    def run(command):
        template = command[command.index("-o") + 1]
        metadata_file = Path(template.replace("%(id)s", entry["id"]).replace("%(ext)s", "info.json"))
        metadata_file.write_text(json.dumps({
            **entry, "description": "Description", "webpage_url": entry["url"],
            "comments": [], "automatic_captions": {"en-orig": []},
        }))

    def fail_subtitles(command):
        raise subprocess.CalledProcessError(1, command, stderr="HTTP Error 429: Too Many Requests")

    monkeypatch.setattr(MODULE, "run", run)
    monkeypatch.setattr(MODULE, "run_subtitles", fail_subtitles)
    with pytest.raises(SystemExit) as error:
        MODULE.main()
    assert error.value.code == 1
    state = json.loads((output / "download-state.json").read_text())
    record = state["videos"][entry["id"]]
    folder = Path(record["folder"])
    assert record["status"] == "error"
    assert record["url"] == entry["url"]
    assert (folder / "metadata.json").is_file()
    assert json.loads((folder / "comments.json").read_text()) == []
    assert not MODULE.is_video_complete(folder, False, True)
    assert "429" in (output / "logs/last-errors.log").read_text()
    assert "429" in capsys.readouterr().out


def test_missing_subtitles_cannot_be_marked_complete(tmp_path, monkeypatch):
    folder = tmp_path / "videos/001-test"
    folder.mkdir(parents=True)
    (folder / "metadata.json").write_text(json.dumps({"id": "test"}))
    for name in ("metadata.md", "description.md", "comments.json", "comments.md"):
        (folder / name).write_text("[]")
    monkeypatch.setattr(MODULE, "run_subtitles", lambda _: None)
    with pytest.raises(RuntimeError, match="Не получен текст субтитров"):
        MODULE.collect_video(
            {"id": "test"}, 1, folder.parent, False, False, 0.18, "en", True, folder
        )


def test_retry_reuses_folder_when_playlist_position_changes(tmp_path):
    videos = tmp_path / "videos"
    folder = videos / "002-original-title"
    folder.mkdir(parents=True)
    state = {"videos": {"failed": {"status": "error", "folder": str(folder)}}}
    skip, existing, key = MODULE.should_skip_video(
        {"id": "failed", "title": "New title"}, 1, videos, state, False
    )
    assert not skip
    assert existing == folder
    assert key == "failed"


def test_interrupted_frame_extraction_is_not_complete(tmp_path):
    for name in ("metadata.json", "metadata.md", "description.md", "comments.json", "comments.md", "transcript.md"):
        (tmp_path / name).write_text("data")
    frames = tmp_path / "frames"
    frames.mkdir()
    (frames / "frame-00001.jpg").write_bytes(b"image")
    assert not MODULE.is_video_complete(tmp_path, True, True)
    (frames / "README.md").write_text("Extraction finished")
    assert MODULE.is_video_complete(tmp_path, True, True)
    assert not MODULE.is_video_complete(tmp_path, True, True, True)
    (tmp_path / "video.mp4").write_bytes(b"video")
    assert MODULE.is_video_complete(tmp_path, True, True, True)


@pytest.mark.skipif(not (ROOT / "scripts/nate-herk-check.sh").exists(), reason="Личный проект не настроен в этом экземпляре")
def test_check_runs_pending_queue_even_when_collection_fails(tmp_path):
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    python = tmp_path / ".venv/bin/python"
    python.parent.mkdir(parents=True)
    python.symlink_to(sys.executable)
    collector = tmp_path / "vault/projects/Скрипт для выгрузки видео/scripts/выгрузка-видео.py"
    collector.parent.mkdir(parents=True)
    collector.write_text('print("HTTP Error 429: Too Many Requests")\nraise SystemExit(1)\n')
    check = scripts / "nate-herk-check.sh"
    check.write_text((ROOT / "scripts/nate-herk-check.sh").read_text().replace(str(ROOT), str(tmp_path)))
    (scripts / "nate-herk-process-pending.sh").write_text('touch queue-ran\n')
    # Временный сбой повторяется до конца окна; нулевое окно сразу его исчерпывает.
    result = subprocess.run(
        ["bash", str(check), "--no-notify"], capture_output=True, text=True,
        cwd=tmp_path, timeout=10,
        env={**os.environ, "NATE_HERK_RETRY_WINDOW_SECONDS": "0"},
    )
    assert result.returncode == 1, result.stderr
    assert (tmp_path / "queue-ran").exists()
    assert "YouTube временно ограничил запросы (код 429)" in result.stdout
    assert "Ошибок нет" not in result.stdout


CARD = """# Карточка ролика: {title}
## Тема
Тема.
## Краткое содержание
{summary}
## Основной вывод
Вывод.
"""


def _nate_check_project(tmp_path, sender_ok=True):
    """Проект Nate Herk с двумя скачанными роликами, у которых есть карточки."""
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    python = tmp_path / ".venv/bin/python"
    python.parent.mkdir(parents=True)
    python.symlink_to(sys.executable)
    collector = tmp_path / "vault/projects/Скрипт для выгрузки видео/scripts/выгрузка-видео.py"
    collector.parent.mkdir(parents=True)
    collector.write_text('print("new videos: 0")\n')
    check = scripts / "nate-herk-check.sh"
    check.write_text((ROOT / "scripts/nate-herk-check.sh").read_text().replace(str(ROOT), str(tmp_path)))
    (scripts / "nate_herk_report.py").write_text((ROOT / "scripts/nate_herk_report.py").read_text())
    (scripts / "nate-herk-process-pending.sh").write_text("touch queue-ran\n")
    (scripts / "send_telegram_message.py").write_text(
        "import sys\n"
        f"open({str(tmp_path / 'sent.txt')!r}, 'a').write(sys.stdin.read() + '\\n---\\n')\n"
        + ("" if sender_ok else "raise SystemExit(1)\n")
    )
    (tmp_path / ".env").write_text("TELEGRAM_BOT_TOKEN=test\nALLOWED_USER_IDS=[1]\n")
    project = tmp_path / "vault/projects/Nate Herk"
    videos = {}
    for key, title in (("old", "Старый ролик"), ("one", "Первый ролик"), ("two", "Второй ролик")):
        folder = f"vault/projects/Nate Herk/videos/{key}"
        (tmp_path / folder).mkdir(parents=True)
        (tmp_path / folder / "analysis.md").write_text(CARD.format(title=title, summary=f"О чём {key}."))
        videos[key] = {"status": "complete", "folder": folder}
    (project / "download-state.json").write_text(json.dumps({"videos": videos}))
    return project


def _run_check(tmp_path, *args):
    return subprocess.run(
        ["bash", str(tmp_path / "scripts/nate-herk-check.sh"), *args],
        capture_output=True, text=True, cwd=tmp_path, timeout=20,
    )


@pytest.mark.skipif(not (ROOT / "scripts/nate-herk-check.sh").exists(), reason="Личный проект не настроен в этом экземпляре")
def test_check_reports_videos_left_unreported_by_interrupted_run(tmp_path):
    # Прошлый запуск скачал ролики и оборвался до отправки отчёта: в списке
    # отправленных их нет, хотя в состоянии загрузки они уже «complete».
    project = _nate_check_project(tmp_path)
    reported = project / "reported-folders.txt"
    reported.write_text("vault/projects/Nate Herk/videos/old\n")
    result = _run_check(tmp_path, "--no-notify")
    assert result.returncode == 0, result.stderr
    assert "Новых роликов: 2." in result.stdout
    assert "Первый ролик" in result.stdout and "Второй ролик" in result.stdout
    assert "Новых роликов нет" not in result.stdout
    # Пробный прогон ничего не отправлял, значит и не отмечает ролики отправленными.
    assert reported.read_text() == "vault/projects/Nate Herk/videos/old\n"


@pytest.mark.skipif(not (ROOT / "scripts/nate-herk-check.sh").exists(), reason="Личный проект не настроен в этом экземпляре")
def test_check_marks_videos_reported_only_after_successful_send(tmp_path):
    project = _nate_check_project(tmp_path, sender_ok=False)
    reported = project / "reported-folders.txt"
    reported.write_text("vault/projects/Nate Herk/videos/old\n")
    failed = _run_check(tmp_path)
    assert failed.returncode != 0
    assert reported.read_text() == "vault/projects/Nate Herk/videos/old\n"

    (tmp_path / "scripts/send_telegram_message.py").write_text(
        "import sys\n"
        f"open({str(tmp_path / 'sent.txt')!r}, 'a').write(sys.stdin.read() + '\\n---\\n')\n"
    )
    sent = _run_check(tmp_path)
    assert sent.returncode == 0, sent.stderr
    text = (tmp_path / "sent.txt").read_text()
    assert "Новых роликов: 2." in text and "Первый ролик" in text and "Второй ролик" in text
    assert set(reported.read_text().splitlines()) == {
        "vault/projects/Nate Herk/videos/old",
        "vault/projects/Nate Herk/videos/one",
        "vault/projects/Nate Herk/videos/two",
    }

    (tmp_path / "sent.txt").unlink()
    again = _run_check(tmp_path)
    assert again.returncode == 0, again.stderr
    assert "Новых роликов нет" in (tmp_path / "sent.txt").read_text()


@pytest.mark.skipif(not (ROOT / "scripts/nate-herk-check.sh").exists(), reason="Личный проект не настроен в этом экземпляре")
def test_check_first_run_treats_downloaded_videos_as_reported(tmp_path):
    project = _nate_check_project(tmp_path)
    result = _run_check(tmp_path, "--no-notify")
    assert result.returncode == 0, result.stderr
    assert "Новых роликов нет" in result.stdout
    assert len((project / "reported-folders.txt").read_text().splitlines()) == 3


@pytest.mark.skipif(not (ROOT / "scripts/nate-herk-check.sh").exists(), reason="Личный проект не настроен в этом экземпляре")
def test_check_keeps_video_without_card_unreported(tmp_path):
    project = _nate_check_project(tmp_path)
    (tmp_path / "vault/projects/Nate Herk/videos/two/analysis.md").unlink()
    reported = project / "reported-folders.txt"
    reported.write_text("vault/projects/Nate Herk/videos/old\n")
    result = _run_check(tmp_path)
    assert result.returncode == 1
    text = (tmp_path / "sent.txt").read_text()
    assert "Новых роликов: 2." in text and "Не готовы аналитические карточки: 1." in text
    assert set(reported.read_text().splitlines()) == {
        "vault/projects/Nate Herk/videos/old",
        "vault/projects/Nate Herk/videos/one",
    }


@pytest.mark.skipif(not (ROOT / "scripts/nate-herk-process-pending.sh").exists(), reason="Личный проект не настроен в этом экземпляре")
def test_worker_does_not_analyze_missing_sources(tmp_path):
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    project = tmp_path / "vault/projects/Nate Herk"
    (project / "videos/001-incomplete").mkdir(parents=True)
    worker = scripts / "worker.sh"
    worker.write_text((ROOT / "scripts/nate-herk-process-pending.sh").read_text().replace(str(ROOT), str(tmp_path)))
    result = subprocess.run(["bash", str(worker)], capture_output=True, text=True, timeout=10)
    assert result.returncode == 1
    assert "WAITING_FOR_SOURCES" in (project / "logs/analysis-worker.log").read_text()
    assert "codex" not in result.stderr
