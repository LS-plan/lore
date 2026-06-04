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
