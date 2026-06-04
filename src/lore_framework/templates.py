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

**On startup**: Read `.lore/INDEX.md`. Match your current task against listed keywords.
Only load deeper files (experiences, domain knowledge) if they're relevant to your task.

**After completing a task**: If you discovered a new verified pattern or pitfall:
1. Write it to `.lore/experiences/<id>.md` using the experience format
2. Update `.lore/experiences/INDEX.md` and `.lore/INDEX.md`

**Loop protection**: If the same experience has been loaded 2 times in this session
without resolving the issue, stop and ask the user for guidance.

**Write rules**:
- Exploration phase: write freely, mark `reviewed: false` for generated entries
- Development phase: unverified observations go to `.lore/runs/` only
- Never set `reviewed: true` on your own generated entries
- Max 5 experiences loaded per task
```
""",
    "_adapters/codex.md": """\
# Codex Adapter

Add the following to your project's `AGENTS.md`:

```markdown
## Project Experience (Lore)

This project uses Lore for engineering experience management.

On startup: Read `.lore/INDEX.md`. Match your current task against listed keywords.
Only load deeper files if relevant.

After task: Write verified findings to `.lore/experiences/`, update indexes.

Loop protection: Same experience loaded 2x without resolution → stop, ask user.
Write rules: Development phase requires verification evidence for new experiences.
Max 5 experiences per task.
```
""",
    "_adapters/cursor.md": """\
# Cursor Adapter

Add the following to `.cursor/rules`:

```
## Project Experience (Lore)

This project uses Lore (.lore/) for engineering experience management.
On startup, read .lore/INDEX.md and match task keywords.
Load relevant experiences from .lore/experiences/ as needed.
After verified work, update experiences and indexes.
Loop protection: same experience 2x without resolution → ask user.
```
""",
    "_adapters/gemini.md": """\
# Gemini Adapter

For Google Gemini / AI Studio projects, add this to your project instructions or `.gemini/` configuration:

```
This project uses Lore (.lore/) for engineering experience management.
Read .lore/INDEX.md at the start of each task.
Match task keywords against experience triggers.
Load relevant experiences on demand.
Write verified findings back to .lore/experiences/ and update indexes.
```
""",
}


def load_all_templates() -> dict[str, str]:
    return dict(TEMPLATES)
