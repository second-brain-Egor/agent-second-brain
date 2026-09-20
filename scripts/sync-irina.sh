#!/bin/bash
# Общие файлы в обе стороны, без удаления. По умолчанию только проверка.
# --apply применяет изменения с резервными копиями; конфликты останавливают запись.
set -euo pipefail
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
exec sudo -n python3 "$PROJECT_DIR/scripts/sync-assistants.py" "$@"
