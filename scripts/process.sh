#!/bin/bash
set -e

exec 200>/tmp/d-brain-heavy.lock
flock -n 200 || { echo "Another heavy process is running, skip"; exit 0; }

export PATH="$HOME/.local/bin:$HOME/.nvm/versions/node/$(ls "$HOME/.nvm/versions/node/" 2>/dev/null | tail -1)/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VAULT_DIR="$PROJECT_DIR/vault"
ENV_FILE="$PROJECT_DIR/.env"

if [ -f "$ENV_FILE" ]; then
    export $(grep -v '^#' "$ENV_FILE" | xargs)
fi

if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "ERROR: TELEGRAM_BOT_TOKEN not set"
    exit 1
fi

export TZ="${TZ:-UTC}"
export PROJECT_DIR

SKILLS_ROOT="$VAULT_DIR/.codex/skills"
if [ ! -d "$SKILLS_ROOT" ]; then
    SKILLS_ROOT="$VAULT_DIR/.claude/skills"
fi

TODAY=$(date +%Y-%m-%d)
CHAT_ID="${ALLOWED_USER_IDS//[\[\]]/}"

echo "=== d-brain processing for $TODAY ==="

DAILY_FILE="$VAULT_DIR/daily/$TODAY.md"
HANDOFF_FILE="$VAULT_DIR/.session/handoff.md"
GRAPH_FILE="$VAULT_DIR/.graph/vault-graph.json"

if [ ! -f "$DAILY_FILE" ]; then
    echo "ORIENT: daily/$TODAY.md not found - creating empty file"
    mkdir -p "$VAULT_DIR/daily"
    echo "# $TODAY" > "$DAILY_FILE"
fi

DAILY_SIZE=$(wc -c < "$DAILY_FILE" 2>/dev/null || echo "0")
if [ "$DAILY_SIZE" -lt 50 ]; then
    echo "ORIENT: daily/$TODAY.md is empty ($DAILY_SIZE bytes) - skipping AI processing"
    cd "$VAULT_DIR"
    uv run "$SKILLS_ROOT/graph-builder/scripts/analyze.py" || echo "Graph rebuild failed (non-critical)"
    cd "$PROJECT_DIR"
    git add -A
    git commit -m "chore: process daily $TODAY" || true
    git push || true
    echo "=== Done (empty daily, graph-only) ==="
    exit 0
fi

if [ ! -f "$HANDOFF_FILE" ]; then
    echo "ORIENT: handoff.md not found - creating stub"
    mkdir -p "$VAULT_DIR/.session"
    echo -e "---\nupdated: $(date -Iseconds)\n---\n\n## Last Session\n(none)\n\n## Observations" > "$HANDOFF_FILE"
fi

if [ -f "$GRAPH_FILE" ]; then
    GRAPH_AGE=$(( ($(date +%s) - $(stat -c %Y "$GRAPH_FILE" 2>/dev/null || stat -f %m "$GRAPH_FILE" 2>/dev/null || echo 0)) / 86400 ))
    if [ "$GRAPH_AGE" -gt 7 ]; then
        echo "ORIENT: vault-graph.json is $GRAPH_AGE days old (>7)"
    fi
fi

echo "ORIENT: daily=$DAILY_SIZE bytes, handoff=OK, graph=OK"

REPORT=$(cd "$PROJECT_DIR" && uv run python - <<'PY'
from datetime import date

from d_brain.config import get_settings
from d_brain.services.processor import AgentProcessor

settings = get_settings()
result = AgentProcessor(settings.vault_path, settings.todoist_api_key).process_daily(date.today())

if "error" in result:
    raise SystemExit(result["error"])

print(result.get("report", ""))
PY
)

echo "=== AI output ==="
echo "$REPORT"
echo "================="

REPORT_CLEAN=$(echo "$REPORT" | sed '/<!--/,/-->/d')

echo "=== Rebuilding vault graph ==="
cd "$VAULT_DIR"
uv run "$SKILLS_ROOT/graph-builder/scripts/analyze.py" || echo "Graph rebuild failed (non-critical)"

echo "=== RAG indexing ==="
uv run python3 -c "from d_brain.services.memory_rag import index_daily; print(f'Indexed {index_daily(\"$VAULT_DIR\")} facts')" || echo "RAG indexing failed (non-critical)"

echo "=== Memory decay ==="
uv run "$SKILLS_ROOT/agent-memory/scripts/memory-engine.py" decay . || echo "Memory decay failed (non-critical)"
cd "$PROJECT_DIR"

git add -A
git commit -m "chore: process daily $TODAY" || true
git pull --rebase origin main || true
git push || true

if [ -n "$REPORT_CLEAN" ] && [ -n "$CHAT_ID" ]; then
    echo "=== Sending to Telegram ==="
    RESULT=$(curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
        -d "chat_id=$CHAT_ID" \
        -d "text=$REPORT_CLEAN" \
        -d "parse_mode=HTML")

    if echo "$RESULT" | grep -q '"ok":false'; then
        echo "HTML failed: $RESULT"
        curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
            -d "chat_id=$CHAT_ID" \
            -d "text=$REPORT_CLEAN"
    fi
fi

echo "=== Done ==="
