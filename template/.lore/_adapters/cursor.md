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
