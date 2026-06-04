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
