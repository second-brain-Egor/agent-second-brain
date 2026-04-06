#!/bin/bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

cd "$PROJECT_DIR"
/bin/bash "$PROJECT_DIR/scripts/install-cron.sh"
