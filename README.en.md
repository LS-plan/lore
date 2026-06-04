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

### Step 4: Start Working

`lore init` automatically detects platform config files in your project root (`CLAUDE.md`, `AGENTS.md`, `.cursorrules`, `.gemini/`) and injects the adapter snippet. **No manual copying needed.**

If the config file doesn't exist at init time, create it later and run:

```bash
lore inject    # Manually inject adapter snippet
```

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
lore suggest --task "xxx"     # FHQ-Treap + keyword hybrid retrieval
lore gc                       # Clean up expired runs/ + TTL auto-expiry
lore gc --dry-run             # Preview cleanup without deleting
lore turnoff                  # Disable Lore processing (current project)
lore turnon                   # Re-enable Lore processing
lore inject                   # Re-inject adapter snippet into platform config
lore list                     # List all registered Lore projects
lore list --global            # Aggregated statistics across all projects
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

## FHQ-Treap Intelligent Retrieval Engine

v0.3 introduces an FHQ-Treap (Split-Merge Treap) based experience scoring and retrieval system.

### Scoring Formula (Ant Colony Pheromone Inspired)

```
score = base_impact × (1 - decay_rate)^days_unused × (log₂(use_count + 1) + 1)
```

| Parameter | Value | Description |
|-----------|-------|-------------|
| `base_impact` | critical=10, high=7, medium=4, low=1 | Base weight |
| `decay_rate` | 0.02 | Daily decay coefficient |
| `use_count` | Historical usage count | Frequency bonus (logarithmic) |

### Three-Layer Architecture

Scores determine which layer an experience belongs to:

| Layer | Score Threshold | Behavior |
|-------|----------------|----------|
| **L1 (Hot)** | > 5.0 | Summary always in INDEX, full file loaded on keyword match |
| **L2 (Warm)** | 1.0 ~ 5.0 | Only loaded when task keywords match triggers |
| **L3 (Cold)** | < 1.0 | Normally skipped, only recalled via mutation |

### Hybrid Retrieval

```
final_score = α × keyword_relevance + (1 - α) × normalized_treap_score
```

- `keyword_relevance`: Jaccard similarity between task description and triggers
- `α = 0.6`: Keyword weight dominates

### Mutation Mechanism (Ant Colony Mutation)

Each retrieval has ε = 5% probability to randomly recall an experience from L3/archived, preventing useful but low-frequency experiences from being permanently forgotten. Similar to random exploration (mutation) in ant colony algorithms, avoiding local optima.

### `[Lore]` Response Prefix

When an agent loads any Lore experience, it prefixes the response with `[Lore]` so the user knows project experience influenced the decision.

### Toggle Control

```bash
lore turnoff    # Disable Lore processing
lore turnon     # Re-enable
```

---

## Global Project Management

Lore maintains a global registry at `~/.lore/` that tracks all projects using Lore.

```bash
lore list                     # List all projects
lore list --global            # Aggregated stats: total experiences, layer distribution, per-project details
```

Projects are automatically registered during `lore init`.

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
| **Structured dedup** | Check trigger similarity before writing; > 70% → merge, don't create new |
| **Traceable compression** | Keep `source_run` field when promoting from `runs/` to `experiences/` |
| **TTL auto-forgetting** | 90 days unused → stale, 180 days → archived, critical exempt |
| **Mutation recall** | 5% chance to recall archived/L3 experience (prevents permanent forgetting) |
| **Toggle control** | `lore turnoff` / `lore turnon` to disable/enable Lore processing |

---

## Docs

- [Experience File Format](docs/experience-format.md) — Frontmatter fields, body structure, lifecycle rules
- [Architecture Decision Record Format](docs/decision-format.md) — When to create an ADR, template, numbering

## License

MIT
