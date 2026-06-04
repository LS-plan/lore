<p align="center">
  <img src="assets/lore-icon.png" width="180" alt="Lore Logo" />
</p>

<h1 align="center">Lore</h1>

<p align="center">
  <b>Project Experience Framework</b> — Let AI agents accumulate, retrieve, and retire engineering experiences within projects.
</p>

<p align="center">
  <a href="README.md">简体中文</a> | <b>English</b>
</p>

---

## Why Lore

AI coding agents are stateless across sessions. Every new conversation, the agent forgets:

- What bugs you've fixed and how
- What architectural decisions were made and why
- What engineering patterns are specific to this project
- What pitfalls to avoid

| Approach | What it does | What's missing |
|----------|-------------|----------------|
| CLAUDE.md / AGENTS.md | Global behavior rules | No project-level experience, no lifecycle |
| Agent memory (auto-memory) | User preferences | Bound to agent not project, flat structure |
| Trellis | Full workflow management | Too heavy, controls entire dev process |
| Skills | Reusable operation flows | Doesn't accumulate knowledge, no verification |

**Lore fills the gap**: project-level, verified, lifecycle-managed engineering experiences.

Lore is a directory convention (`.lore/`) that gives AI agents a structured place to manage project-level engineering experiences. It's platform-agnostic — any LLM that can read files can use it (Claude Code, Codex, Gemini, Cursor, etc.).

---

## Quick Start

### Step 1: Install CLI (Recommended)

```bash
pip install lore-framework
```

The CLI is cross-platform (Windows / macOS / Linux) with consistent behavior and incremental update support.

### Step 2: Initialize

Navigate to your project root and run:

```bash
lore init
```

The CLI auto-detects the project name from the directory. You can also specify it manually:

```bash
lore init --project my-awesome-app --phase exploration
```

<details>
<summary>Alternative: Quick init without installing CLI</summary>

```bash
# Bash / Zsh / Git Bash
curl -fsSL https://raw.githubusercontent.com/LS-plan/lore/main/scripts/init.sh | bash
```

```powershell
# PowerShell
irm https://raw.githubusercontent.com/LS-plan/lore/main/scripts/init.ps1 | iex
```

```bash
# Manual copy
git clone https://github.com/LS-plan/lore.git /tmp/lore
cp -r /tmp/lore/template/.lore .lore
rm -rf /tmp/lore
```

</details>

### Step 3: Describe Your Project

Edit `.lore/identity.md` with your project name, tech stack, and current phase:

```markdown
## Basics
- **Project**: my-awesome-app
- **Tech stack**: Python / FastAPI / Docker / PostgreSQL

## Phase
- **Current phase**: exploration
```

### Step 4: Inject into Your Agent Platform

Copy the corresponding snippet from `.lore/_adapters/` into your platform config:

| Platform | Config File | Adapter |
|----------|------------|---------|
| Claude Code | `CLAUDE.md` | `.lore/_adapters/claude-code.md` |
| Codex | `AGENTS.md` | `.lore/_adapters/codex.md` |
| Cursor | `.cursor/rules` | `.lore/_adapters/cursor.md` |
| Gemini | `.gemini/` | `.lore/_adapters/gemini.md` |

Or add this snippet directly to your project's `CLAUDE.md` (or equivalent):

```markdown
## Project Experience Framework (Lore)

This project uses Lore for engineering experience management.
On startup, read `.lore/INDEX.md` and load relevant experiences by task keywords.
After tasks, write verified experiences to `.lore/experiences/` and update the index.
Loop protection: if the same experience is loaded 2 times without resolving the issue, stop and report to user.
```

### Step 5: Start Working

Just work normally. The agent reads `.lore/INDEX.md` at the start of each session and loads relevant experiences on demand.

### Incremental Updates

For projects with the CLI installed, upgrading is simple:

```bash
pip install --upgrade lore-framework
lore update
```

`lore update` only adds new files and fields introduced in the new version — it **never overwrites your modified files** (like `identity.md`, `glossary.md`, etc.).

### Other Commands

```bash
lore stats                    # View experience statistics
lore suggest --task "xxx"     # Suggest relevant experiences (FHQ-Treap scheduling in v0.3)
lore gc                       # Clean up expired runs/ logs
lore gc --dry-run             # Preview cleanup without deleting
```

---

## Expected LLM Behavior After Installation

After installing Lore, the AI agent should exhibit the following behavior patterns:

### First Contact with a Project

- **Auto-form project understanding**: When the agent first encounters a project with `.lore/`, it defaults to reading `identity.md`, `INDEX.md`, `glossary.md`, and other files to proactively build a global understanding of the project — no extra user authorization needed for this step
- **Auto-detect project info**: Project name, tech stack, etc. should be identified from `.lore/identity.md` and the directory structure, not by repeatedly asking the user

### Executing Tasks

- **Plan first**: After the user states a request, the agent first presents a complete plan (including files involved, steps, and any matched engineering experiences), then seeks confirmation on specific details that need user input (e.g., whether to initialize git, create new directories, etc.)
- **Experience match notification**: When a task matches an existing engineering experience, reference it in the plan with a brief explanation
- **Progressive confirmation**: Confirm details incrementally until a complete understanding is formed, rather than dumping all questions at once

### Preventing Stalls

- **Proactive progression**: If several conversation rounds show little progress (e.g., repeatedly confirming the same point, or the user hasn't given clear direction), the agent should proactively ask: "Shall I proceed based on my current understanding? We can adjust later."
- **No over-engineering**: Don't obsess over details or assume hypothetical requirements. Build a working version first, iterate later

### Writing Experiences

- **Post-task reflection**: After completing a task, the agent should assess whether a reusable engineering experience was produced
- **Skip trivial operations**: One-off operations (copy edits, parameter tweaks) don't go into `experiences/`
- **Verification required**: In the development phase, new experiences must include verification methods

---

## Experience File Format

Each experience is a Markdown file under `.lore/experiences/`:

```markdown
---
id: docker-volume-vs-bake
triggers:
  - "Host file changes not reflected in container"
  - "Changes lost after docker restart"
scope: [Docker, Deployment]
verified: 2026-06-03
status: active
impact: medium
author: generated
reviewed: false
---

# Docker: volume mount vs baked image

## Symptom
Modified code files on the host, but Docker container shows no changes.

## Root Cause
Code was COPYed into the image during docker build. Host files and container files are independent copies.

## Solution
Add a volume mount in docker-compose.yml.

## Verification
Edit host file → docker compose up -d → exec into container and confirm file is updated.
```

Key fields:
- `triggers`: Match conditions — the agent uses these keywords to decide whether to load the experience
- `status`: `active` / `stale` / `archived`
- `impact`: `low` / `medium` / `high` / `critical`
- `author`: `authored` (human-written) / `generated` (agent-produced)
- `reviewed`: Whether it has been human-reviewed

Full format spec: [docs/experience-format.md](docs/experience-format.md).

---

## Directory Structure

```
.lore/
├── INDEX.md              # Root index — the only file the agent MUST read on startup
├── identity.md           # Project identity: name, tech stack, constraints, phase
├── glossary.md           # Domain glossary
├── domain/               # Domain knowledge
│   ├── INDEX.md
│   └── <topic>.md
├── experiences/          # Verified engineering experiences
│   ├── INDEX.md
│   └── <experience>.md
├── decisions/            # Architecture Decision Records (ADR)
│   └── <NNNN>-<slug>.md
├── patterns/             # Stable engineering patterns (promoted from experiences)
│   ├── INDEX.md
│   └── <pattern>.md
├── runs/                 # Task run logs (temporary evidence)
│   └── <date>-<task>.yaml
└── _adapters/            # Platform injection snippets
    ├── claude-code.md
    ├── codex.md
    ├── cursor.md
    └── gemini.md
```

| Directory | Contents | Lifecycle |
|-----------|----------|-----------|
| `identity.md` | Project tech stack, constraints, current phase | Long-term, occasional updates |
| `glossary.md` | Domain term definitions | Long-term, continuously growing |
| `domain/` | Domain knowledge (business logic, protocol details) | Long-term |
| `experiences/` | Verified engineering experiences | Medium-term, may expire |
| `decisions/` | Architecture decision records | Long-term |
| `patterns/` | Stable engineering patterns | Long-term |
| `runs/` | Task run logs | Short-term (30-day cleanup) |

---

## Two Phases

### Exploration

Early project stage, or when the agent first encounters the project. Set `phase: exploration` in `identity.md`.

- Agent proactively writes to `domain/`, `glossary.md`, `experiences/`
- Low write threshold — record valuable observations first, human review later
- Generated entries marked `reviewed: false`

### Development

Mature project with accumulated experience library. Set `phase: development` in `identity.md`.

- Agent primarily reads, selectively writes
- Unverified observations go to `runs/` only, not directly to `experiences/`
- New experiences must have verification evidence
- Lifecycle rules (expiry / archival) actively enforced

Typically switch to development after 5+ verified experiences and `domain/` covers core areas.

---

## Experience Lifecycle (PDCA)

```
Observation / Hypothesis
    ↓
runs/ (temporary run logs, 30-day cleanup)
    ↓  [verified + reusable]
experiences/ (verified, status: active)
    ↓  [3+ uses, >80% success rate, human reviewed]
patterns/ (stable engineering patterns)
    ↓  [further solidified into executable flows]
Becomes a standalone Skill

Retirement:
  90 days unused → status: stale
  Another 90 days unused → status: archived
  Superseded → directly archived
  impact: critical → exempt from auto-expiry
```

---

## Built-in Safeguards

| Mechanism | Rule |
|-----------|------|
| **Loop protection** | Same experience loaded 2 times without resolving → stop and report to user |
| **Write gating** | Development phase: unverified entries cannot enter `experiences/` |
| **Load limit** | Max 5 experiences per task (sorted by impact) |
| **Index consistency** | Index must be updated after every experience add/remove |
| **Self-review ban** | Agent cannot set `reviewed: true` on its own generated entries |

---

## Docs

- [Experience File Format](docs/experience-format.md) — Frontmatter fields, body structure, lifecycle rules
- [Architecture Decision Record Format](docs/decision-format.md) — When to create an ADR, template, numbering

## License

MIT
