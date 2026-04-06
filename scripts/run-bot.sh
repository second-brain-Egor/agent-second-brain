#!/bin/bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/bot.log"
LOCK_FILE="/tmp/d-brain-bot.lock"

mkdir -p "$LOG_DIR"

export PATH="$HOME/.local/bin:$HOME/.nvm/versions/node/$(ls "$HOME/.nvm/versions/node/" 2>/dev/null | tail -1)/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

cd "$PROJECT_DIR"
exec flock -n "$LOCK_FILE" uv run python -m d_brain >>"$LOG_FILE" 2>&1
