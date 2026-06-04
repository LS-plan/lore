# Lore

**Project Experience Framework** — project-level knowledge accumulation for AI agents.

Lore is a directory convention (`.lore/`) that gives AI agents a structured place to accumulate, retrieve, and retire engineering experiences within a project. It works with any LLM platform that can read files — Claude Code, Codex, Gemini, Cursor, and others.

## The Problem

AI coding agents are stateless across sessions. Every time you start a new conversation, the agent forgets:

- What bugs you've already fixed and how
- What architectural decisions you've made and why
- What domain-specific patterns this project uses
- What pitfalls to avoid

Existing solutions each cover part of this:

| Tool | What it does | What it misses |
|------|-------------|----------------|
| CLAUDE.md / AGENTS.md | Global rules | No project-specific experience, no lifecycle |
| Agent memory (auto-memory) | User preferences | Tied to agent, not project; flat structure |
| Trellis | Full workflow management | Too heavy; controls the entire dev process |
| Skills | Reusable procedures | No knowledge accumulation; no verification |

**Lore fills the gap**: project-level, verified, lifecycle-managed engineering experience.

## Quick Start

### Option 1: One-line init

```bash
# Bash / Zsh / Git Bash
curl -fsSL https://raw.githubusercontent.com/LS-plan/lore/main/scripts/init.sh | bash

# PowerShell
irm https://raw.githubusercontent.com/LS-plan/lore/main/scripts/init.ps1 | iex
```

### Option 2: Manual

```bash
git clone https://github.com/LS-plan/lore.git /tmp/lore
cp -r /tmp/lore/template/.lore .lore
rm -rf /tmp/lore
```

Then edit `.lore/identity.md` to describe your project.

### Option 3: Copy the template directory

Download the `template/.lore/` directory from this repo and place it at your project root.

## After Init

1. Edit `.lore/identity.md` — describe your project's tech stack, constraints, and current phase
2. Add a PEF injection snippet to your platform's config file (see `.lore/_adapters/`)
3. Start working — your agent will read `.lore/INDEX.md` at the start of each session

## Directory Structure

```
.lore/
├── INDEX.md              # Root index — the ONLY file agents must read on startup
├── identity.md           # Project identity: tech stack, constraints, phase
├── glossary.md           # Domain terms and definitions
├── domain/
│   ├── INDEX.md          # Domain knowledge index
│   └── <topic>.md        # Specific domain knowledge
├── experiences/
│   ├── INDEX.md          # Experience index (triggers + one-line summary)
│   └── <experience>.md   # Individual verified experiences
├── decisions/
│   └── <NNNN>-<slug>.md  # Architecture Decision Records (ADR)
├── patterns/
│   ├── INDEX.md          # Engineering patterns index
│   └── <pattern>.md      # Stable patterns (promoted from experiences)
├── runs/
│   └── <date>-<task>.yaml  # Task run logs (temporary evidence)
└── _adapters/
    ├── claude-code.md    # Snippet for CLAUDE.md
    ├── codex.md          # Snippet for AGENTS.md
    ├── cursor.md         # Snippet for .cursor/rules
    └── gemini.md         # Snippet for .gemini/
```

## How It Works

### For Agents

1. **On startup**: Read `.lore/INDEX.md` (< 80 lines). Match task keywords against section summaries.
2. **If relevant**: Drill into `experiences/INDEX.md` or `domain/INDEX.md`. Load specific files by trigger match.
3. **During work**: Apply retrieved experiences. If an experience fails twice in the same session, stop and ask the user.
4. **After work**: Record new verified findings in `experiences/`. Update indexes.

### For Humans

1. **Periodically review**: Check `experiences/` for unreviewed generated entries.
2. **Promote**: Move stable, frequently-used experiences to `patterns/`.
3. **Archive**: Mark stale experiences. Clean up `runs/` older than 30 days.
4. **Decide**: Use `decisions/` for significant architectural choices (ADR format).

## Two Phases

### Exploration Phase

Early in a project, or when an agent first encounters a codebase. Set `phase: exploration` in `identity.md`.

- Agents write freely to `domain/`, `glossary.md`, `experiences/`
- Lower verification threshold — observations are captured before they're fully validated
- Generated entries marked `reviewed: false` for later human review

### Development Phase

Project is mature with accumulated experience. Set `phase: development` in `identity.md`.

- Agents primarily read, selectively write
- New unverified observations go to `runs/` only — not directly to `experiences/`
- Experiences require verification evidence before promotion
- Lifecycle rules (stale/archive) are actively enforced

## Experience Lifecycle (PDCA)

```
Observation → runs/ (temporary, 30-day cleanup)
                ↓  [verified + reusable]
            experiences/ (active)
                ↓  [3+ uses, >80% success, human reviewed]
            patterns/ (stable engineering pattern)
                ↓  [further solidified]
            Becomes a Skill (independent of .lore/)

Reverse:
  90 days unused → status: stale
  +90 days still unused → status: archived
  Has replacement → archived immediately
  impact: critical → exempt from auto-stale
```

## Built-in Safeguards

| Safeguard | Rule |
|-----------|------|
| **Loop protection** | Same experience loaded 2x without solving the problem → stop, report to user |
| **Write gating** | Development phase: no unverified entries in `experiences/` |
| **Scope limit** | Max 5 experiences loaded per task (sorted by impact) |
| **Index consistency** | After any add/delete, indexes must be updated |
| **Self-review ban** | Agent cannot set `reviewed: true` on its own generated entries |

## Cross-Platform

Lore is just files. Any LLM that can read Markdown can use it. Platform-specific injection snippets are provided in `.lore/_adapters/` — copy the relevant one into your platform's config file.

## License

MIT
