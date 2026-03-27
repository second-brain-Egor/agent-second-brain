#!/bin/bash
# Читает последние 50 строк из самого свежего session-файла
SESSION_DIR="$(cd "$(dirname "$0")/.." && pwd)/vault/.sessions"
LATEST=$(ls -t "$SESSION_DIR"/*.jsonl 2>/dev/null | head -1)
if [ -n "$LATEST" ]; then
    tail -50 "$LATEST"
else
    echo "No session files found"
fi
