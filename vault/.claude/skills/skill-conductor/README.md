# Skill Conductor

Architecture-first skill lifecycle: design → build → test → evaluate → package.

Most skill tools jump straight to "write SKILL.md." Conductor makes you choose the architecture first - because rewriting a wrong pattern costs more than writing it right.

## v2: Anthropic's eval engine meets architecture-first design

Anthropic [updated their skill-creator](https://claude.com/blog/improving-skill-creator-test-measure-and-refine-agent-skills) with serious eval infrastructure. We took the best of it:

**From Anthropic's skill-creator (new):**
- 3 specialized agents: **grader** (assertion checking + claim extraction), **comparator** (blind A/B testing), **analyzer** (post-hoc root cause analysis)
- Parallel eval execution with isolated contexts (no cross-contamination)
- Automated description optimization with train/test split (60/40)
- Benchmark tracking: pass rate, tokens, time with variance analysis
- HTML eval viewer with qualitative + quantitative tabs

**What Conductor adds on top:**
- **Architecture before code.** 5 patterns (Sequential, Iterative, Context-Aware, Domain Intelligence, Multi-MCP) with selection criteria. Pick wrong = rewrite everything later
- **Degrees of freedom.** Low (deterministic scripts) → Medium (pseudocode) → High (free text). Match freedom to risk tolerance
- **TDD RED before writing.** Verify the agent fails WITHOUT the skill first. If it already handles the task - you don't need a skill. Creator runs baselines in parallel with skill runs. Conductor runs baseline BEFORE you write anything
- **5-axis scoring with thresholds.** Discovery, Clarity, Efficiency, Robustness, Completeness. Each 1-10. Score 45-50 = production. Below 25 = rewrite. Not "vibe check" - numbers
- **Skill categorization.** Capability uplift (teaching something new) vs Encoded preference (sequencing known abilities). Different skills need different testing strategies

## Synthesized from

1. **[Anthropic Skill Creator](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/skill-creator)** — eval infrastructure, grader/comparator/analyzer agents, benchmark pipeline
2. **[The Complete Guide to Building Skills for Claude](https://claude.com/blog/complete-guide-to-building-skills-for-claude)** — 32 pages, 5 architecture patterns, success metrics
3. **[Superpowers / writing-skills](https://github.com/obra/superpowers/blob/main/skills/writing-skills/SKILL.md)** by Jesse Vincent — TDD approach, the "description trap" discovery
4. **[Skills Best Practices](https://github.com/mgechev/skills-best-practices)** by Minko Gechev — three-stage LLM validation, eval methodology

## 5 Modes

| Mode | What it does |
|------|-------------|
| **CREATE** | Architecture selection → TDD baseline → scaffold → write → verify → refactor |
| **EVAL** | 3-stage evaluation: Discovery (triggering) → Logic (execution) → Edge Cases (breaking) |
| **EDIT** | Problem → Signal → Fix table. Targeted improvements without breaking what works |
| **REVIEW** | Pass/fail checklist for third-party skills before you install them |
| **PACKAGE** | Validate structure + package as `.skill` for distribution |

## Architecture patterns

Choose before writing a single line:

| Pattern | Use when |
|---|---|
| Sequential workflow | Clear step-by-step process |
| Iterative refinement | Output improves with cycles |
| Context-aware selection | Same goal, different tools by context |
| Domain intelligence | Specialized knowledge beyond tool access |
| Multi-MCP coordination | Workflow spans multiple services |

## Eval infrastructure

```
                    ┌─────────┐
                    │  SKILL  │
                    └────┬────┘
                         │
              ┌──────────┼──────────┐
              │          │          │
         ┌────▼────┐ ┌──▼───┐ ┌───▼────┐
         │ Grader  │ │ A/B  │ │Analyzer│
         │         │ │Blind │ │        │
         │assertions│ │compare│ │root    │
         │+ claims │ │      │ │cause   │
         └─────────┘ └──────┘ └────────┘
              │          │          │
              └──────────┼──────────┘
                         │
                   ┌─────▼─────┐
                   │ Benchmark │
                   │ mean±std  │
                   └───────────┘
```

## Installation

```
skills/
└── skill-conductor/
    ├── SKILL.md
    ├── agents/
    │   ├── grader.md
    │   ├── comparator.md
    │   └── analyzer.md
    ├── eval-viewer/
    │   ├── generate_review.py
    │   └── viewer.html
    ├── references/
    │   ├── patterns.md
    │   └── schemas.md
    ├── assets/
    │   └── eval_review.html
    └── scripts/
        ├── init_skill.py
        ├── eval_skill.py
        ├── run_eval.py
        ├── run_loop.py
        ├── improve_description.py
        ├── aggregate_benchmark.py
        ├── generate_report.py
        ├── package_skill.py
        ├── quick_validate.py
        └── utils.py
```

**OpenClaw:** drop into `~/.openclaw/workspace/skills/`

**Claude Code:** drop into `.claude/skills/`

Auto-activates when the agent detects a skill-building task.

## Key discovery

Never put process steps in the skill description. If your description says "exports assets, generates specs, creates tasks" - the model follows the description and skips the body. Tested experimentally.

```yaml
# ✅ Good
description: Analyze design files for developer handoff. Use when user uploads .fig files.

# ❌ Bad - model follows this and ignores SKILL.md body
description: Exports Figma assets, generates specs, creates Linear tasks, posts to Slack.
```

## License

MIT
