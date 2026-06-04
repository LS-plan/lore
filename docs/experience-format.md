# Experience File Format

Each experience is a Markdown file in `.lore/experiences/` with YAML frontmatter.

## Template

```markdown
---
id: kebab-case-unique-id
triggers:
  - "symptom or situation that activates this experience"
  - "another trigger phrase"
scope: [Tag1, Tag2]
verified: YYYY-MM-DD
source: run/YYYY-MM-DD-task-name.yaml
status: active
impact: medium
usage_count: 0
last_used: null
author: generated
reviewed: false
---

# Title

## Symptom
What the user or agent observes when this experience is relevant.

## Root Cause
Why this happens.

## Solution
How to fix or handle it.

## Verification
How to confirm the solution worked.

## Boundary
When this experience does NOT apply, or edge cases to watch for.
```

## Frontmatter Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | yes | Unique kebab-case identifier |
| `triggers` | string[] | yes | Phrases that indicate this experience is relevant |
| `scope` | string[] | yes | Domain/technology tags |
| `verified` | date | yes | When this was last verified to be accurate |
| `source` | string | no | The run log that produced this experience |
| `status` | enum | yes | `active` / `stale` / `archived` |
| `impact` | enum | yes | `low` / `medium` / `high` / `critical` |
| `usage_count` | number | no | How many times this has been referenced |
| `last_used` | date | no | When this was last applied |
| `author` | enum | yes | `authored` (human-written) / `generated` (agent-produced) |
| `reviewed` | boolean | yes | Whether a human has reviewed this entry |

## Body Sections

All sections are recommended but not mandatory. At minimum, include **Symptom** and **Solution**.

- **Symptom**: Observable problem or situation
- **Root Cause**: Why it happens (understanding prevents recurrence)
- **Solution**: Concrete steps to resolve
- **Verification**: How to confirm the fix worked (critical for PDCA)
- **Boundary**: When this does NOT apply (prevents misapplication)

## Lifecycle Rules

- **New experience**: starts as `active`, `usage_count: 0`
- **After use**: increment `usage_count`, update `last_used`
- **90 days unused**: mark `status: stale`
- **180 days unused OR has replacement**: mark `status: archived`
- **impact: critical**: exempt from automatic stale marking
- **Promotion to pattern**: requires `usage_count >= 3`, success rate > 80%, `reviewed: true`
