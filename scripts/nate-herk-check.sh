#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="/home/egor/agent-second-brain"
OUTPUT_DIR="vault/projects/Nate Herk"
COLLECTOR="vault/projects/Скрипт для выгрузки видео/scripts/выгрузка-видео.py"

cd "$PROJECT_DIR"
exec "$PROJECT_DIR/.venv/bin/python" "$COLLECTOR" \
  --url "https://youtube.com/@nateherk/videos" \
  --output "$OUTPUT_DIR" \
  --limit 50 \
  --only-new \
  --frames \
  --keep-video \
  --sub-langs "en"
