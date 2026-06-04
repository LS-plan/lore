"""Bundled template content — embedded so pip install works without bundled files."""

TEMPLATES: dict[str, str] = {
    "INDEX.md": """\
# Project Experience Index

> Framework: Lore/1.0
> Phase: exploration
> Last updated: YYYY-MM-DD

## Project Identity
- Project: [project name]
- Tech stack: [languages / frameworks / infrastructure]
- See → identity.md

## Domain Knowledge (0 entries)
- See → domain/INDEX.md
- Keywords: [auto-populated as domain knowledge grows]

## Verified Experiences (0 entries)
- See → experiences/INDEX.md
- Keywords: —
- Last verified: — | Last added: —

## Engineering Patterns (0 entries)
- See → patterns/INDEX.md

## Decisions (0 entries)
- See → decisions/

## Glossary
- See → glossary.md | Terms: 0

---

## Agent Instructions

**On startup**: Read this file. Match your current task against the keywords and summaries above. Only drill into sub-indexes if relevant.

**After task**: If you produced a new verified finding, add it to `experiences/` and update this index.

**Loop protection**: If the same experience has been loaded 2 times in this session without resolving the issue, stop loading it. Record the failure in `runs/` and ask the user for guidance.

**Scope limit**: Load at most 5 experiences per task. If more than 5 match, prioritize by impact (critical > high > medium > low).
""",
    "identity.md": """\
# Project Identity

## Basics
- **Project**: [project name]
- **Description**: [one-line description]
- **Tech stack**: [e.g., Python / FastAPI / Docker / PostgreSQL]
- **Repository**: [e.g., https://github.com/org/repo]

## Phase
- **Current phase**: exploration  <!-- or: development -->

## Constraints
- [List any hard constraints: compliance requirements, performance budgets, etc.]

## Team
- [Who works on this project and their roles, if relevant]

## Notes
- [Any other context that helps an agent understand this project]
""",
    "glossary.md": """\
# Glossary

Domain terms used in this project. Agents should use these terms consistently and update this file when new terms are established.

| Term | Definition | Context |
|------|-----------|---------|
| — | — | — |

<!--
Add terms as you encounter domain-specific language.
Format: one row per term, with a clear definition and where it's used.
Example:
| bitstream | FPGA configuration binary loaded via JTAG or Flash | Hardware, FPGA |
| probe | yt-dlp metadata extraction without downloading | Media, download |
-->
""",
    "domain/INDEX.md": """\
# Domain Knowledge Index

| Topic | File | Summary |
|-------|------|---------|
| — | — | — |

<!--
Add entries as domain knowledge is captured.
Example:
| Deployment | deployment.md | Docker Compose architecture, volume mounts, service dependencies |
| Database | database.md | MySQL schema, migrations, character encoding requirements |
-->
""",
    "experiences/INDEX.md": """\
# Verified Experiences

| ID | Triggers | Scope | Impact | Status |
|----|----------|-------|--------|--------|
| — | — | — | — | — |

<!--
Add entries when a new experience is verified and written.
Agents match their current task against the Triggers column.

Status values: active / stale / archived
Impact values: low / medium / high / critical

Example:
| docker-volume-vs-bake | host file changes not reflected in container | Docker | medium | active |
| mysql-utf8mb4 | Chinese characters garbled, emoji storage fails | MySQL | high | active |
-->
""",
    "patterns/INDEX.md": """\
# Engineering Patterns

Stable, repeatedly-verified patterns promoted from experiences.

| ID | Description | Scope | Promoted from |
|----|------------|-------|---------------|
| — | — | — | — |

<!--
Patterns are experiences that have been used 3+ times with >80% success rate
and have been reviewed by a human. They represent established project conventions.

Example:
| upstream-sync | ZIP-based upstream import to git branch with merge | Git, deployment | experiences/upstream-zip-sync |
-->
""",
    "_adapters/claude-code.md": """\
# Claude Code Adapter

Add the following to your project's `CLAUDE.md`:

```markdown
## Project Experience (Lore)

This project uses Lore for engineering experience management.

### Startup Protocol

1. Check `.lore/.disabled` — if it exists, skip all Lore processing
2. Read `.lore/INDEX.md` — scan keywords and experience summaries
3. Match your current task against listed keywords (do NOT load all experiences)

### Response Prefix

When any Lore experience is loaded or referenced, prefix your response with `[Lore]`.
This signals to the user that project experience influenced the response.

### Layered Architecture (Progressive Disclosure)

Experiences are scored by FHQ-Treap (frequency × impact × recency). Three layers:

- **L1 (Hot)**: High-score experiences — summaries shown in INDEX, load full file on keyword match
- **L2 (Warm)**: Medium-score — only load when task keywords match triggers
- **L3 (Cold)**: Low-score or stale — normally skipped, but may be recalled via mutation

Progressive disclosure: start with INDEX summaries → if keywords match, load the full
experience file → if still unresolved, check domain/ and patterns/. Never bulk-load.

### After Task

If you discovered a new verified pattern or pitfall:
1. **Dedup check**: Compare triggers with existing experiences. If similarity > 70%, update the existing entry instead of creating a new one
2. Write to `.lore/experiences/<id>.md` with frontmatter (id, triggers, scope, impact, status, verified, author: generated, reviewed: false)
3. If promoting from `runs/`, keep `source_run` field for traceability
4. Update `.lore/experiences/INDEX.md` and `.lore/INDEX.md`

### Safeguards

- **Loop protection**: Same experience loaded 2× without resolving → stop, ask user
- **Max 5 experiences** per task (sorted by impact: critical > high > medium > low)
- **Write rules**: exploration phase → write freely; development phase → unverified goes to runs/ only
- **Self-review ban**: Never set `reviewed: true` on your own generated entries

### Toggle

User can run `lore turnoff` / `lore turnon` to disable/enable Lore processing.
```
""",
    "_adapters/codex.md": """\
# Codex Adapter

Add the following to your project's `AGENTS.md`:

```markdown
## Project Experience (Lore)

This project uses Lore for engineering experience management.

**Startup**: Check `.lore/.disabled` — if present, skip Lore. Otherwise read `.lore/INDEX.md`,
match task keywords. Prefix responses with `[Lore]` when experience is loaded.

**Layers**: L1 (hot, always in INDEX) → L2 (warm, keyword match) → L3 (cold, mutation recall).
Progressive disclosure: INDEX summary first, full file only on match. Max 5 per task.

**After task**: Dedup check triggers (>70% similarity → merge). Write verified findings to
`.lore/experiences/`, keep `source_run` if promoted from runs/. Update indexes.

**Safeguards**: Loop protection (2× same experience → stop). Development phase requires
verification. Never self-review. Toggle: `lore turnoff` / `lore turnon`.
```
""",
    "_adapters/cursor.md": """\
# Cursor Adapter

Add the following to `.cursor/rules`:

```
## Project Experience (Lore)

This project uses Lore (.lore/) for engineering experience management.

Startup: check .lore/.disabled, then read .lore/INDEX.md. Match task keywords.
Prefix responses with [Lore] when experience is loaded.
Layers: L1 hot → L2 warm (keyword match) → L3 cold (mutation recall only).
Load INDEX summary first, full files only on match. Max 5 per task.
After task: dedup check, write verified experiences, update indexes.
Loop protection: same experience 2x without resolution → ask user.
Toggle: lore turnoff / lore turnon.
```
""",
    "_adapters/gemini.md": """\
# Gemini Adapter

For Google Gemini / AI Studio projects, add this to your `.gemini/` configuration:

```
This project uses Lore (.lore/) for engineering experience management.

Startup: check .lore/.disabled, then read .lore/INDEX.md.
Match task keywords against experience triggers.
Prefix responses with [Lore] when any experience is loaded.
Three layers: L1 (hot, always visible) → L2 (warm, keyword match) → L3 (cold, mutation).
Progressive disclosure: INDEX summary → full file on match → domain/patterns if needed.
Max 5 experiences per task. Dedup before writing new experiences.
Write verified findings to .lore/experiences/ and update indexes.
Toggle: lore turnoff / lore turnon.
```
""",
}


def load_all_templates() -> dict[str, str]:
    return dict(TEMPLATES)
