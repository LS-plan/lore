# Architecture Decision Record (ADR) Format

Decisions are recorded in `.lore/decisions/` using a lightweight ADR format.

## When to Create a Decision

Only create a decision record when ALL three conditions are met:
1. The decision is **hard to reverse** once implemented
2. The outcome would **surprise a reasonable teammate** who wasn't in the room
3. There's a **real trade-off** (not an obvious best choice)

## Template

```markdown
# NNNN — Decision Title

**Date**: YYYY-MM-DD
**Status**: proposed / accepted / deprecated / superseded by NNNN
**Deciders**: [who was involved]

## Context
What situation or problem prompted this decision?

## Decision
What did we decide to do?

## Consequences
What are the trade-offs? What becomes easier? What becomes harder?

## Alternatives Considered
What other options were evaluated and why were they rejected?
```

## Numbering

Decisions are numbered sequentially: `0001-use-docker-device-isolation.md`, `0002-volume-mount-over-bake.md`.
