#!/bin/bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/weekly.log"
LOCK_FILE="/tmp/d-brain-weekly.lock"
ENV_FILE="$PROJECT_DIR/.env"

mkdir -p "$LOG_DIR"

export PATH="$HOME/.local/bin:$HOME/.nvm/versions/node/$(ls "$HOME/.nvm/versions/node/" 2>/dev/null | tail -1)/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

if [ -f "$ENV_FILE" ]; then
    set -a
    # shellcheck disable=SC1090
    . "$ENV_FILE"
    set +a
fi

# Vault-health maintenance — heuristic Python scripts, no LLM. Run on BOTH backends.
# Adds descriptions to new notes, connects orphans/weakly-connected to hub files,
# fixes broken wiki-links. Without this, vault accumulates orphans over time.
{
    echo "=== Vault-health maintenance $(date -Iseconds) ==="
    cd "$PROJECT_DIR/vault"
    mkdir -p .graph
    SKILLS_ROOT=".codex/skills"
    [ -d "$SKILLS_ROOT" ] || SKILLS_ROOT=".claude/skills"

    echo "[1/4] Refreshing vault-graph.json..."
    uv run "$SKILLS_ROOT/graph-builder/scripts/analyze.py" "$PROJECT_DIR/vault" --json > .graph/vault-graph.json 2>/dev/null || echo "  graph dump failed (non-critical)"

    echo "[2/4] Adding descriptions to new notes..."
    uv run "$SKILLS_ROOT/vault-health/scripts/add_descriptions.py" --apply 2>&1 || echo "  add_descriptions failed (non-critical)"

    echo "[3/4] Connecting orphan/weakly-connected notes..."
    uv run "$SKILLS_ROOT/vault-health/scripts/connect_orphans.py" --apply 2>&1 || echo "  connect_orphans failed (non-critical)"

    echo "[4/4] Fixing broken wiki-links..."
    uv run "$SKILLS_ROOT/vault-health/scripts/fix_links.py" --apply 2>&1 || echo "  fix_links failed (non-critical)"

    cd "$PROJECT_DIR"
    echo "=== Vault-health done ==="
} >>"$LOG_FILE" 2>&1

# Anti-ban guard: skip LLM-based weekly digest when Claude sim is active (Anthropic TOS).
# Vault-health above runs unconditionally — it doesn't call LLM.
if [ "${AI_BACKEND:-codex}" = "claude" ]; then
    exit 0
fi

cd "$PROJECT_DIR"
exec flock -n "$LOCK_FILE" uv run python scripts/weekly.py >>"$LOG_FILE" 2>&1
