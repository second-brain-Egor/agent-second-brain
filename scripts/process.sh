#!/bin/bash
set -e

exec 200>"/tmp/d-brain-heavy-${USER:-$(whoami)}.lock"
flock -n 200 || { echo "Another heavy process is running, skip"; exit 0; }

export PATH="$HOME/.local/bin:$HOME/.nvm/versions/node/$(ls "$HOME/.nvm/versions/node/" 2>/dev/null | tail -1)/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VAULT_DIR="$PROJECT_DIR/vault"
ENV_FILE="$PROJECT_DIR/.env"

if [ -f "$ENV_FILE" ]; then
    while IFS= read -r line || [ -n "$line" ]; do
        case "$line" in
            ''|\#*) continue ;;
            *=*)
                key="${line%%=*}"
                value="${line#*=}"
                key="${key#export }"
                export "$key=$value"
                ;;
        esac
    done < "$ENV_FILE"
fi

if [ -z "${TELEGRAM_BOT_TOKEN:-}" ]; then
    echo "ERROR: TELEGRAM_BOT_TOKEN not set"
    exit 1
fi

export AI_BACKEND="${PROCESS_BACKEND:-${AI_BACKEND:-codex}}"
export TZ="${TZ:-UTC}"
export PROJECT_DIR

SKILLS_ROOT="$VAULT_DIR/.codex/skills"
if [ ! -d "$SKILLS_ROOT" ]; then
    SKILLS_ROOT="$VAULT_DIR/.claude/skills"
fi

TODAY=$(date +%Y-%m-%d)
CHAT_ID="${ALLOWED_USER_IDS:-}"
CHAT_ID="${CHAT_ID//[\[\]]/}"

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
PENDING_COUNT=$(cd "$PROJECT_DIR" && uv run python - <<'PY'
from datetime import date
from d_brain.config import get_settings
from d_brain.services.processor import AgentProcessor

settings = get_settings()
print(len(AgentProcessor(settings.vault_path, settings.todoist_api_key).pending_days(date.today())))
PY
)
if [ "$PENDING_COUNT" -eq 0 ]; then
    echo "ORIENT: no unprocessed entries - skipping AI processing"
    cd "$VAULT_DIR"
    uv run "$SKILLS_ROOT/graph-builder/scripts/analyze.py" || echo "Graph rebuild failed (non-critical)"
    cd "$PROJECT_DIR"
    echo "=== Refreshing wiki index ==="
    uv run python -m d_brain.services.wiki || echo "Wiki refresh failed (non-critical)"
    echo "=== RAG indexing ==="
    uv run python3 -c "from d_brain.services.memory_rag import index_daily; print(f'Indexed {index_daily(\"$VAULT_DIR\")} facts')" || echo "RAG indexing failed (non-critical)"
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
result = AgentProcessor(settings.vault_path, settings.todoist_api_key).process_pending(date.today())

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
mkdir -p .graph
uv run "$SKILLS_ROOT/graph-builder/scripts/analyze.py" || echo "Graph report failed (non-critical)"
uv run "$SKILLS_ROOT/graph-builder/scripts/analyze.py" "$VAULT_DIR" --json > .graph/vault-graph.json 2>/dev/null || echo "Graph JSON dump failed (non-critical)"
cd "$PROJECT_DIR"

echo "=== Regenerating sub-MOCs (business + projects) ==="
uv run "$SKILLS_ROOT/vault-health/scripts/generate_moc.py" || echo "MOC regeneration failed (non-critical)"

echo "=== Regenerating thoughts/summaries MOCs ==="
uv run "$SKILLS_ROOT/vault-health/scripts/generate_thoughts_moc.py" || echo "Thoughts MOC regeneration failed (non-critical)"

echo "=== Refreshing wiki index ==="
uv run python -m d_brain.services.wiki || echo "Wiki refresh failed (non-critical)"

echo "=== RAG indexing ==="
uv run python3 -c "from d_brain.services.memory_rag import index_daily; print(f'Indexed {index_daily(\"$VAULT_DIR\")} facts')" || echo "RAG indexing failed (non-critical)"

echo "=== Memory decay ==="
uv run "$SKILLS_ROOT/agent-memory/scripts/memory-engine.py" decay "$VAULT_DIR" || echo "Memory decay failed (non-critical)"

# process_pending marks only the snapshots actually processed, for every day.
NOW_ISO=$(date -Iseconds)

echo "=== Updating handoff.md ==="
uv run python3 - <<PY
import re
from pathlib import Path
p = Path("$HANDOFF_FILE")
if p.exists():
    content = p.read_text(encoding="utf-8")
    # Update last_accessed in frontmatter (date only)
    new_fm = re.sub(r"^last_accessed:\s*.*\$", "last_accessed: $TODAY", content, count=1, flags=re.M)
    # Update or add updated (ISO timestamp)
    if re.search(r"^updated:\s*", new_fm, flags=re.M):
        new_fm = re.sub(r"^updated:\s*.*\$", "updated: $NOW_ISO", new_fm, count=1, flags=re.M)
    elif new_fm.startswith("---"):
        new_fm = re.sub(r"^---\n", f"---\nupdated: $NOW_ISO\n", new_fm, count=1)
    else:
        new_fm = f"---\nupdated: $NOW_ISO\n---\n\n" + new_fm
    # Update or append Last Session block
    last_session_block = f"## Last Session\nProcessed daily $TODAY at $NOW_ISO\n"
    if "## Last Session" in new_fm:
        new_fm = re.sub(r"## Last Session.*?(?=\n## |\Z)", last_session_block, new_fm, count=1, flags=re.S)
    else:
        new_fm = new_fm.rstrip() + f"\n\n{last_session_block}\n"
    p.write_text(new_fm, encoding="utf-8")
    print(f"handoff updated: {p}")
PY

git add -A
git commit -m "chore: process daily $TODAY" || true
git pull --rebase origin main || true
git push || true

if [ -n "$REPORT_CLEAN" ] && [ -n "$CHAT_ID" ]; then
    echo "=== Sending to Telegram ==="
    REPORT_CLEAN="$REPORT_CLEAN" CHAT_ID="$CHAT_ID" uv run python - <<'PY'
import asyncio
import os

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from d_brain.bot.formatters import format_process_report

async def send_report():
    # Reports spanning several days can exceed Telegram's single-message limit.
    async with Bot(token=os.environ["TELEGRAM_BOT_TOKEN"]) as bot:
        for text in format_process_report({"report": os.environ["REPORT_CLEAN"]}):
            try:
                await bot.send_message(os.environ["CHAT_ID"], text, parse_mode="HTML")
            except TelegramBadRequest:
                await bot.send_message(os.environ["CHAT_ID"], text)

asyncio.run(send_report())
PY
fi

echo "=== Done ==="
