#!/usr/bin/env python3
"""Collect raw YouTube data into a project folder."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import os
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib import request, parse

from PIL import Image


DEFAULT_CHANNEL_URL = "https://www.youtube.com/@suroviplotnik/videos"
DEFAULT_OUTPUT_DIR = Path("vault/projects/dacha/Суровый Плотник")
REPO_ROOT = Path(__file__).resolve().parents[4]
YTDLP = shutil.which("yt-dlp") or str(REPO_ROOT / ".venv" / "bin" / "yt-dlp")
STATE_FILE_NAME = "download-state.json"
JOURNAL_FILE_NAME = "download-journal.md"
VIDEO_SUFFIXES = {".mp4", ".mov", ".mkv", ".avi", ".webm", ".m4v"}


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def run_binary(command: list[str]) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        command,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def slugify(value: str, fallback: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^\wа-яА-ЯёЁ]+", "-", value, flags=re.UNICODE)
    value = re.sub(r"-+", "-", value).strip("-")
    return value[:90] or fallback


def resolve_repo_path(value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else REPO_ROOT / path


def is_video_file(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in VIDEO_SUFFIXES


def load_local_videos(local_input: str | Path, limit: int | None = None) -> list[dict[str, Any]]:
    source = resolve_repo_path(local_input)
    if is_video_file(source):
        files = [source]
    elif source.is_dir():
        files = sorted(path for path in source.iterdir() if is_video_file(path))
    else:
        raise FileNotFoundError(f"Local video source not found: {source}")

    if limit:
        files = files[:limit]

    entries: list[dict[str, Any]] = []
    for path in files:
        entries.append(
            {
                "id": path.stem,
                "title": path.stem,
                "local_path": str(path),
                "source_type": "local",
            }
        )
    return entries


def ffprobe_metadata(video_file: Path) -> dict[str, Any]:
    result = run(
        [
            "ffprobe",
            "-v",
            "error",
            "-print_format",
            "json",
            "-show_format",
            "-show_streams",
            str(video_file),
        ]
    )
    return json.loads(result.stdout)


def duration_string(seconds: float | int | None) -> str:
    if seconds is None:
        return ""
    total = int(float(seconds))
    hours, rem = divmod(total, 3600)
    minutes, secs = divmod(rem, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def load_flat_playlist(channel_url: str, limit: int) -> list[dict[str, Any]]:
    result = run(
        [
            YTDLP,
            "--flat-playlist",
            "--playlist-items",
            f"1-{limit}",
            "-j",
            "--no-warnings",
            channel_url,
        ]
    )
    return [json.loads(line) for line in result.stdout.splitlines() if line.strip()]


def clean_vtt(text: str) -> str:
    lines: list[str] = []
    previous = ""
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if (
            not line
            or line == "WEBVTT"
            or line.startswith("Kind:")
            or line.startswith("Language:")
            or "-->" in line
            or re.fullmatch(r"\d+", line)
        ):
            continue
        line = re.sub(r"<[^>]+>", "", line)
        line = re.sub(r"\s+", " ", line).strip()
        if line and line != previous:
            lines.append(line)
            previous = line
    return "\n".join(lines).strip() + "\n" if lines else ""


def write_markdown_card(video_dir: Path, metadata: dict[str, Any]) -> None:
    title = metadata.get("title") or "Без названия"
    url = metadata.get("webpage_url") or metadata.get("original_url") or ""
    channel = metadata.get("channel") or metadata.get("uploader") or "Суровый Плотник"
    upload_date = metadata.get("upload_date") or ""
    duration = metadata.get("duration_string") or metadata.get("duration") or ""

    lines = [
        f"# {title}",
        "",
        f"Ссылка: {url}",
        f"Источник: {channel}",
        f"Дата: {upload_date}",
        f"Длительность: {duration}",
        "",
    ]
    (video_dir / "metadata.md").write_text("\n".join(lines), encoding="utf-8")


def write_local_metadata(video_dir: Path, video_file: Path, metadata: dict[str, Any]) -> None:
    format_data = metadata.get("format") or {}
    duration = format_data.get("duration")
    payload = {
        "id": video_file.stem,
        "title": video_file.stem,
        "source_type": "local",
        "local_path": str(video_file),
        "webpage_url": "",
        "original_url": str(video_file),
        "channel": "Локальный файл",
        "upload_date": "",
        "duration": float(duration) if duration else None,
        "duration_string": duration_string(float(duration)) if duration else "",
        "size_bytes": int(format_data.get("size") or video_file.stat().st_size),
        "ffprobe": metadata,
    }
    (video_dir / "metadata.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_markdown_card(video_dir, payload)
    (video_dir / "description.md").write_text("Локальный видеофайл. Описания из внешнего источника нет.\n", encoding="utf-8")
    write_comments(video_dir, [])


def write_comments(video_dir: Path, comments: list[dict[str, Any]]) -> None:
    (video_dir / "comments.json").write_text(
        json.dumps(comments, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    blocks: list[str] = ["# Комментарии", ""]
    for comment in comments:
        author = comment.get("author") or "Без автора"
        text = (comment.get("text") or "").strip()
        if not text:
            continue
        blocks.extend([f"## {author}", "", text, ""])

    (video_dir / "comments.md").write_text("\n".join(blocks).strip() + "\n", encoding="utf-8")


def utc_now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def load_state(output_dir: Path) -> dict[str, Any]:
    state_path = output_dir / STATE_FILE_NAME
    if not state_path.exists():
        return {"version": 1, "videos": {}}
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"version": 1, "videos": {}}
    if not isinstance(state, dict):
        return {"version": 1, "videos": {}}
    videos = state.get("videos")
    if not isinstance(videos, dict):
        state["videos"] = {}
    state.setdefault("version", 1)
    return state


def save_state(output_dir: Path, state: dict[str, Any]) -> None:
    state["updated_at"] = utc_now()
    state_path = output_dir / STATE_FILE_NAME
    tmp_path = state_path.with_suffix(".tmp")
    tmp_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp_path.replace(state_path)


def video_key(entry: dict[str, Any], fallback: str) -> str:
    return str(entry.get("id") or entry.get("url") or entry.get("webpage_url") or fallback)


def find_existing_video_dir(videos_dir: Path, video_id: str, title: str, index: int) -> Path | None:
    if not videos_dir.exists():
        return None

    for path in sorted(videos_dir.iterdir()):
        if not path.is_dir():
            continue
        metadata = read_metadata(path)
        if metadata.get("id") == video_id:
            return path

    slug = slugify(title, video_id)
    prefix = f"{index:03d}-"
    for path in sorted(videos_dir.iterdir()):
        if path.is_dir() and path.name.startswith(prefix) and path.name.endswith(slug):
            return path

    return None


def count_frames(video_dir: Path) -> int:
    return len(list((video_dir / "frames").glob("frame-*.jpg")))


def count_deduped_frames(video_dir: Path) -> int:
    deduped_dir = video_dir / "frames-deduped"
    return len(list(deduped_dir.glob("frame-*.jpg"))) if deduped_dir.exists() else 0


def is_video_complete(video_dir: Path, with_frames: bool) -> bool:
    required_files = [
        video_dir / "metadata.json",
        video_dir / "metadata.md",
        video_dir / "description.md",
        video_dir / "comments.json",
        video_dir / "comments.md",
    ]
    if any(not path.exists() for path in required_files):
        return False
    if with_frames and count_frames(video_dir) == 0:
        return False
    return True


def is_local_video_complete(video_dir: Path, with_frames: bool, with_transcript: bool) -> bool:
    required_files = [
        video_dir / "metadata.json",
        video_dir / "metadata.md",
        video_dir / "description.md",
        video_dir / "comments.json",
        video_dir / "comments.md",
    ]
    if any(not path.exists() for path in required_files):
        return False
    if with_frames:
        if count_frames(video_dir) == 0:
            return False
        if count_deduped_frames(video_dir) == 0:
            return False
    if with_transcript and not (video_dir / "transcript.md").exists():
        return False
    return True


def video_record(video_dir: Path, status: str, with_frames: bool, error: str | None = None) -> dict[str, Any]:
    metadata = read_metadata(video_dir)
    record: dict[str, Any] = {
        "status": status,
        "folder": str(video_dir.relative_to(REPO_ROOT) if video_dir.is_relative_to(REPO_ROOT) else video_dir),
        "title": metadata.get("title") or video_dir.name,
        "url": metadata.get("webpage_url") or metadata.get("original_url") or "",
        "upload_date": metadata.get("upload_date") or "",
        "comments": count_comments(video_dir),
        "frames": count_frames(video_dir),
        "deduped_frames": count_deduped_frames(video_dir),
        "description": (video_dir / "description.md").exists(),
        "transcript": (video_dir / "transcript.md").exists(),
        "frames_required": with_frames,
        "updated_at": utc_now(),
    }
    if error:
        record["error"] = error
    return record


def should_skip_video(
    entry: dict[str, Any],
    index: int,
    videos_dir: Path,
    state: dict[str, Any],
    with_frames: bool,
) -> tuple[bool, Path | None, str]:
    key = video_key(entry, f"video-{index:03d}")
    title = entry.get("title") or key
    existing_dir = find_existing_video_dir(videos_dir, key, title, index)
    state_record = state.get("videos", {}).get(key, {})

    if existing_dir and is_video_complete(existing_dir, with_frames):
        state["videos"][key] = {
            **video_record(existing_dir, "complete", with_frames),
            "completed_at": state_record.get("completed_at") or utc_now(),
        }
        return True, existing_dir, key

    return False, existing_dir, key


def move_sidecar_files(work_dir: Path, video_dir: Path) -> None:
    subtitles_dir = video_dir / "subtitles"
    subtitles_dir.mkdir(exist_ok=True)

    for file_path in work_dir.iterdir():
        if file_path.suffix == ".json":
            data = json.loads(file_path.read_text(encoding="utf-8"))
            target = "comments.json" if file_path.name.endswith(".comments.json") else "metadata.json"
            (video_dir / target).write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            if target == "metadata.json":
                write_markdown_card(video_dir, data)
                description = data.get("description") or ""
                (video_dir / "description.md").write_text(description.strip() + "\n", encoding="utf-8")
                comments = data.get("comments") or []
                if comments:
                    write_comments(video_dir, comments)

        elif file_path.suffix == ".vtt":
            target = subtitles_dir / file_path.name
            shutil.move(str(file_path), target)
            transcript = clean_vtt(target.read_text(encoding="utf-8", errors="ignore"))
            if transcript:
                (video_dir / "transcript.md").write_text(transcript, encoding="utf-8")


def download_video(video_url: str, work_dir: Path) -> Path:
    video_template = str(work_dir / "video.%(ext)s")
    run(
        [
            YTDLP,
            "-f",
            "bv*[height<=720][ext=mp4]+ba[ext=m4a]/b[height<=720][ext=mp4]/best[height<=720]",
            "--merge-output-format",
            "mp4",
            "--no-warnings",
            "-o",
            video_template,
            video_url,
        ]
    )
    candidates = sorted(work_dir.glob("video.*"))
    if not candidates:
        raise FileNotFoundError("yt-dlp did not create a video file")
    return candidates[0]


def extract_unique_frames(video_file: Path, frames_dir: Path, scene_threshold: float) -> None:
    frames_dir.mkdir(exist_ok=True)
    for old_frame in frames_dir.glob("frame-*.jpg"):
        old_frame.unlink()

    # Scene detection keeps visually changed frames and skips near-duplicates.
    run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(video_file),
            "-vf",
            f"select='gt(scene,{scene_threshold})',scale='min(1280,iw)':-2",
            "-vsync",
            "vfr",
            "-q:v",
            "3",
            str(frames_dir / "frame-%05d.jpg"),
        ]
    )

    frame_count = len(list(frames_dir.glob("frame-*.jpg")))
    (frames_dir / "README.md").write_text(
        "\n".join(
            [
                "# Кадры",
                "",
                f"Режим: уникальные кадры по смене сцены",
                f"Порог отличия: {scene_threshold}",
                f"Кадров сохранено: {frame_count}",
                "",
            ]
        ),
        encoding="utf-8",
    )


def image_hash(path: Path, size: int = 8) -> int:
    image = Image.open(path).convert("L").resize((size, size))
    pixels = list(image.getdata())
    avg = sum(pixels) / len(pixels)
    value = 0
    for index, pixel in enumerate(pixels):
        if pixel >= avg:
            value |= 1 << index
    return value


def hamming_distance(left: int, right: int) -> int:
    return (left ^ right).bit_count()


def dedupe_frames(frames_dir: Path, deduped_dir: Path, threshold: int) -> int:
    deduped_dir.mkdir(exist_ok=True)
    for old_frame in deduped_dir.glob("frame-*.jpg"):
        old_frame.unlink()

    kept_hashes: list[int] = []
    kept = 0
    for frame in sorted(frames_dir.glob("frame-*.jpg")):
        frame_hash = image_hash(frame)
        if any(hamming_distance(frame_hash, known_hash) <= threshold for known_hash in kept_hashes[-20:]):
            continue
        kept_hashes.append(frame_hash)
        kept += 1
        shutil.copy2(frame, deduped_dir / f"frame-{kept:05d}.jpg")

    total = len(list(frames_dir.glob("frame-*.jpg")))
    (deduped_dir / "README.md").write_text(
        "\n".join(
            [
                "# Кадры после дедупликации",
                "",
                "Режим: сравнение похожих кадров по perceptual hash",
                f"Порог похожести: {threshold}",
                f"Исходных кадров: {total}",
                f"Оставлено кадров: {kept}",
                f"Удалено дублей: {total - kept}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return kept


def extract_audio(video_file: Path, audio_file: Path) -> None:
    audio_file.parent.mkdir(exist_ok=True)
    run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(video_file),
            "-vn",
            "-ac",
            "1",
            "-ar",
            "16000",
            "-b:a",
            "64k",
            str(audio_file),
        ]
    )


def transcribe_audio_deepgram(audio_file: Path) -> dict[str, Any]:
    api_key = os.environ.get("DEEPGRAM_API_KEY")
    if not api_key:
        raise RuntimeError("DEEPGRAM_API_KEY is not set")

    params = parse.urlencode(
        {
            "model": "nova-3",
            "language": "ru",
            "punctuate": "true",
            "smart_format": "true",
            "paragraphs": "true",
            "utterances": "true",
        }
    )
    req = request.Request(
        f"https://api.deepgram.com/v1/listen?{params}",
        data=audio_file.read_bytes(),
        headers={
            "Authorization": f"Token {api_key}",
            "Content-Type": "audio/mpeg",
        },
        method="POST",
    )
    with request.urlopen(req, timeout=1800) as response:
        return json.loads(response.read().decode("utf-8"))


def format_transcript(response: dict[str, Any]) -> str:
    results = response.get("results") or {}
    channels = results.get("channels") or []
    if not channels:
        return ""
    alternatives = channels[0].get("alternatives") or []
    if not alternatives:
        return ""
    alternative = alternatives[0]
    paragraphs = (((alternative.get("paragraphs") or {}).get("paragraphs")) or [])
    if paragraphs:
        blocks = []
        for paragraph in paragraphs:
            start = paragraph.get("start")
            text = " ".join(sentence.get("text", "") for sentence in paragraph.get("sentences", [])).strip()
            if text:
                prefix = f"[{duration_string(start)}] " if start is not None else ""
                blocks.append(prefix + text)
        return "\n\n".join(blocks).strip() + "\n"
    transcript = (alternative.get("transcript") or "").strip()
    return transcript + "\n" if transcript else ""


def write_transcript(video_dir: Path, video_file: Path) -> None:
    audio_file = video_dir / "_work" / "audio.mp3"
    extract_audio(video_file, audio_file)
    response = transcribe_audio_deepgram(audio_file)
    (video_dir / "transcript.json").write_text(
        json.dumps(response, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    text = format_transcript(response)
    (video_dir / "transcript.md").write_text(text or "Транскрибация не вернула текст.\n", encoding="utf-8")


def count_comments(video_dir: Path) -> int:
    comments_path = video_dir / "comments.json"
    if not comments_path.exists():
        return 0
    try:
        data = json.loads(comments_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return 0
    return len(data) if isinstance(data, list) else 0


def read_metadata(video_dir: Path) -> dict[str, Any]:
    metadata_path = video_dir / "metadata.json"
    if not metadata_path.exists():
        return {}
    try:
        data = json.loads(metadata_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def generate_summary(output_dir: Path) -> None:
    videos_dir = output_dir / "videos"
    video_dirs = sorted(path for path in videos_dir.iterdir() if path.is_dir()) if videos_dir.exists() else []

    lines: list[str] = [
        "# Сводка по видео",
        "",
        f"Папка: {output_dir.name}",
        f"Роликов в выгрузке: {len(video_dirs)}",
        "",
        "## Состав выгрузки",
        "",
    ]

    total_comments = 0
    total_frames = 0

    for video_dir in video_dirs:
        metadata = read_metadata(video_dir)
        title = metadata.get("title") or video_dir.name
        url = metadata.get("webpage_url") or metadata.get("original_url") or ""
        upload_date = metadata.get("upload_date") or ""
        duration = metadata.get("duration_string") or metadata.get("duration") or ""
        comments_count = count_comments(video_dir)
        frames_count = len(list((video_dir / "frames").glob("frame-*.jpg")))
        deduped_frames_count = count_deduped_frames(video_dir)
        has_description = (video_dir / "description.md").exists()
        has_transcript = (video_dir / "transcript.md").exists()

        total_comments += comments_count
        total_frames += frames_count

        lines.extend(
            [
                f"### {video_dir.name}",
                "",
                f"Название: {title}",
                f"Ссылка: {url}",
                f"Дата: {upload_date}",
                f"Длительность: {duration}",
                f"Описание: {'есть' if has_description else 'нет'}",
                f"Комментарии: {comments_count}",
                f"Транскрипт: {'есть' if has_transcript else 'нет'}",
                f"Кадры: {frames_count}",
                f"Кадры после дедупликации: {deduped_frames_count}",
                "",
            ]
        )

    lines.extend(
        [
            "## Итого",
            "",
            f"Роликов: {len(video_dirs)}",
            f"Комментариев: {total_comments}",
            f"Кадров: {total_frames}",
            "",
        ]
    )

    (output_dir / "summary.md").write_text("\n".join(lines), encoding="utf-8")


def generate_download_journal(output_dir: Path, state: dict[str, Any] | None = None) -> None:
    videos_dir = output_dir / "videos"
    video_dirs = sorted(path for path in videos_dir.iterdir() if path.is_dir()) if videos_dir.exists() else []
    state = state or load_state(output_dir)
    records = state.get("videos", {})

    lines: list[str] = [
        "# Журнал скачанных видео",
        "",
        f"Обновлено: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"Всего видео в папке: {len(video_dirs)}",
        f"Записей в журнале: {len(records)}",
        "",
    ]

    for video_dir in video_dirs:
        metadata = read_metadata(video_dir)
        video_id = metadata.get("id") or video_dir.name
        record = records.get(video_id, {})
        title = metadata.get("title") or video_dir.name
        url = metadata.get("webpage_url") or metadata.get("original_url") or ""
        upload_date = metadata.get("upload_date") or ""
        comments_count = count_comments(video_dir)
        frames_count = len(list((video_dir / "frames").glob("frame-*.jpg")))
        has_description = (video_dir / "description.md").exists()
        has_transcript = (video_dir / "transcript.md").exists()
        status = record.get("status") or ("complete" if is_video_complete(video_dir, frames_count > 0) else "partial")

        lines.extend(
            [
                f"## {video_dir.name}",
                "",
                f"Статус: {status}",
                f"Название: {title}",
                f"Ссылка: {url}",
                f"Дата видео: {upload_date}",
                f"Описание: {'есть' if has_description else 'нет'}",
                f"Комментарии: {comments_count}",
                f"Транскрипт: {'есть' if has_transcript else 'нет'}",
                f"Кадры: {frames_count}",
                f"Обновлено: {record.get('updated_at') or ''}",
                "",
            ]
        )

    (output_dir / JOURNAL_FILE_NAME).write_text("\n".join(lines), encoding="utf-8")


def collect_video(
    entry: dict[str, Any],
    index: int,
    videos_dir: Path,
    with_frames: bool,
    keep_video: bool,
    scene_threshold: float,
    sub_langs: str,
    with_subs: bool,
) -> None:
    video_id = entry.get("id") or f"video-{index:03d}"
    title = entry.get("title") or video_id
    video_url = entry.get("url") or entry.get("webpage_url") or f"https://www.youtube.com/watch?v={video_id}"
    if video_url.startswith("/"):
        video_url = f"https://www.youtube.com{video_url}"

    video_dir = videos_dir / f"{index:03d}-{slugify(title, video_id)}"
    work_dir = video_dir / "_work"
    frames_dir = video_dir / "frames"
    video_dir.mkdir(parents=True, exist_ok=True)
    work_dir.mkdir(exist_ok=True)

    output_template = str(work_dir / "%(id)s.%(ext)s")
    command = [
        YTDLP,
        "--skip-download",
        "--write-info-json",
        "--write-comments",
        "--no-warnings",
        "-o",
        output_template,
        video_url,
    ]
    if with_subs:
        command[2:2] = [
            "--write-sub",
            "--write-auto-sub",
            "--sub-lang",
            sub_langs,
            "--sub-format",
            "vtt",
        ]
    run(command)
    move_sidecar_files(work_dir, video_dir)

    if with_frames:
        frames_dir.mkdir(exist_ok=True)
        video_file = download_video(video_url, work_dir)
        extract_unique_frames(video_file, frames_dir, scene_threshold)
        if keep_video:
            target_video = video_dir / video_file.name
            shutil.move(str(video_file), target_video)

    shutil.rmtree(work_dir, ignore_errors=True)


def collect_local_video(
    entry: dict[str, Any],
    index: int,
    videos_dir: Path,
    with_frames: bool,
    with_transcript: bool,
    keep_video: bool,
    scene_threshold: float,
    dedupe_threshold: int,
) -> Path:
    source_file = Path(entry["local_path"])
    video_id = entry.get("id") or source_file.stem
    title = entry.get("title") or source_file.stem
    video_dir = videos_dir / f"{index:03d}-{slugify(title, video_id)}"
    work_dir = video_dir / "_work"
    frames_dir = video_dir / "frames"
    deduped_dir = video_dir / "frames-deduped"
    video_dir.mkdir(parents=True, exist_ok=True)
    work_dir.mkdir(exist_ok=True)

    write_local_metadata(video_dir, source_file, ffprobe_metadata(source_file))

    if with_transcript:
        write_transcript(video_dir, source_file)

    if with_frames:
        extract_unique_frames(source_file, frames_dir, scene_threshold)
        dedupe_frames(frames_dir, deduped_dir, dedupe_threshold)

    if keep_video:
        target_video = video_dir / source_file.name
        if source_file.resolve() != target_video.resolve():
            shutil.copy2(source_file, target_video)

    shutil.rmtree(work_dir, ignore_errors=True)
    return video_dir


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default=DEFAULT_CHANNEL_URL, help="YouTube channel or playlist URL")
    parser.add_argument("--local-input", help="Local video file or folder with video files")
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Project folder where videos, logs and source files are stored",
    )
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--frames", action="store_true")
    parser.add_argument("--transcribe", action="store_true")
    parser.add_argument("--keep-video", action="store_true")
    parser.add_argument("--scene-threshold", type=float, default=0.18)
    parser.add_argument("--dedupe-threshold", type=int, default=4)
    parser.add_argument("--sub-langs", default="ru,en")
    parser.add_argument("--no-subs", action="store_true")
    args = parser.parse_args()

    output_dir = resolve_repo_path(args.output)
    videos_dir = output_dir / "videos"
    logs_dir = output_dir / "logs"
    videos_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    entries = load_local_videos(args.local_input, args.limit) if args.local_input else load_flat_playlist(args.url, args.limit)
    state = load_state(output_dir)
    errors: list[str] = []
    for index, entry in enumerate(entries, start=1):
        if entry.get("source_type") == "local":
            key = video_key(entry, f"video-{index:03d}")
            existing_dir = videos_dir / f"{index:03d}-{slugify(entry.get('title') or key, key)}"
            if is_local_video_complete(existing_dir, args.frames, args.transcribe):
                print(f"skip: {entry.get('title') or key}", flush=True)
                state["videos"][key] = {
                    **video_record(existing_dir, "complete", args.frames),
                    "completed_at": state.get("videos", {}).get(key, {}).get("completed_at") or utc_now(),
                }
                save_state(output_dir, state)
                continue
            try:
                video_dir = collect_local_video(
                    entry,
                    index,
                    videos_dir,
                    args.frames,
                    args.transcribe,
                    args.keep_video,
                    args.scene_threshold,
                    args.dedupe_threshold,
                )
                state["videos"][key] = {
                    **video_record(video_dir, "complete", args.frames),
                    "completed_at": utc_now(),
                }
                save_state(output_dir, state)
            except Exception as exc:
                error_text = str(exc)
                errors.append(f"{index}: {entry.get('title') or entry.get('id')} — {error_text}")
                if existing_dir.exists():
                    state["videos"][key] = video_record(existing_dir, "error", args.frames, error_text)
                    save_state(output_dir, state)
            continue

        skip, existing_dir, key = should_skip_video(entry, index, videos_dir, state, args.frames)
        if skip:
            print(f"skip: {entry.get('title') or key}", flush=True)
            save_state(output_dir, state)
            continue
        try:
            collect_video(
                entry,
                index,
                videos_dir,
                args.frames,
                args.keep_video,
                args.scene_threshold,
                args.sub_langs,
                not args.no_subs,
            )
            video_dir = find_existing_video_dir(
                videos_dir,
                key,
                entry.get("title") or key,
                index,
            )
            if video_dir:
                state["videos"][key] = {
                    **video_record(video_dir, "complete", args.frames),
                    "completed_at": utc_now(),
                }
                save_state(output_dir, state)
        except subprocess.CalledProcessError as exc:
            error_text = exc.stderr.strip()
            errors.append(f"{index}: {entry.get('title') or entry.get('id')} — {error_text}")
            if existing_dir:
                state["videos"][key] = video_record(existing_dir, "error", args.frames, error_text)
                save_state(output_dir, state)

    generate_summary(output_dir)
    generate_download_journal(output_dir, state)

    if errors:
        (logs_dir / "last-errors.log").write_text("\n\n".join(errors) + "\n", encoding="utf-8")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
