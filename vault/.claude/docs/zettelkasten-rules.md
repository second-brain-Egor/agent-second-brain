# Zettelkasten Rules

## Directory Structure

| Folder | Purpose |
|--------|---------|
| `daily/` | Raw daily entries (YYYY-MM-DD.md) |
| `goals/` | Goal cascade (3y → yearly → monthly → weekly) |
| `thoughts/` | Processed notes by category |
| `MOC/` | Maps of Content indexes |
| `attachments/` | Photos by date |
| `business/` | Business data (CRM, network, events) |
| `projects/` | Side projects (clients, leads) |

## Graph Builder

**Purpose:** Analysis and maintenance of vault link structure.

**Architecture:**
1. `scripts/analyze.py` — deterministic vault traversal
2. `scripts/add_links.py` — batch link addition
3. Agent — semantic links for orphan files

**Usage:**
```bash
uv run vault/.claude/skills/graph-builder/scripts/analyze.py
```

**Result:**
- `vault/.graph/vault-graph.json` — JSON graph with stats
- `vault/.graph/report.md` — Human-readable report

**Domains:**
| Domain | Path | Hub |
|--------|------|-----|
| Personal | thoughts/, goals/, daily/ | memory/*.md |
| Business | business/crm/, business/network/ | business/_index.md |
| Projects | projects/clients/, projects/leads/ | projects/_index.md |

## Card Template (agent-memory)

All new vault cards follow the agent-memory template:

```yaml
---
type: crm|lead|contact|project|personal|note
description: >-
  One line — what a searcher will see in results
tags: [tag1, tag2]
status: active|draft|pending|done|inactive
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

**Rules:**
- `description` — REQUIRED. Write as a search snippet
- `tags` — REQUIRED. 2-5 tags, lowercase, hyphen-separated
- `status` ≠ `tier`: status = business status, tier = memory (automatic)
- One fact = one place (DRY). References via [[wikilinks]]

## Entry Format

```markdown
## HH:MM [type]
Content
```

Types: `[voice]`, `[text]`, `[forward from: Name]`, `[photo]`

## Goals Hierarchy

```
goals/0-vision-3y.md    → 3-year vision by life areas
goals/1-yearly-YYYY.md  → Annual goals + quarterly breakdown
goals/2-monthly.md      → Current month's top 3 priorities
goals/3-weekly.md       → This week's focus + ONE Big Thing
```

## Business Context

**Entry point:** `business/_index.md`
Search: `business/crm/{kebab-case}.md`

## Projects Context

**Entry point:** `projects/_index.md`

## Processing Workflow

3-Phase Pipeline:
1. **CAPTURE** — Read daily entries → classify → JSON
2. **EXECUTE** — Create Todoist tasks, save thoughts, update CRM → JSON
3. **REFLECT** — Generate HTML report, update memory, record observations

## Report Format

Reports use Telegram HTML:
- `<b>bold</b>` for headers
- `<i>italic</i>` for metadata
- Only allowed tags: b, i, code, pre, a

## Available Agents

| Agent | Purpose |
|-------|---------|
| `weekly-digest` | Weekly review with goal progress |
| `goal-aligner` | Check task-goal alignment |
| `note-organizer` | Organize vault, fix links |
| `inbox-processor` | GTD-style inbox processing |

## Path-Specific Rules

See `.claude/rules/` for format requirements:
- `daily-format.md` — daily files format
- `thoughts-format.md` — thought notes format
- `goals-format.md` — goals format
- `telegram-report.md` — HTML report format
- `obsidian-markdown.md` — Obsidian syntax rules
- `weekly-reflection.md` — weekly reflection template
