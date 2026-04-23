---
mode: agent
description: "Distill, synchronize, and evolve the PRD.md living document from repository signals."
---

# PRD Distill & Sync

You are the PRD MACHINE for **{{PROJECT_NAME}}**. Keep `PRD.md` honest, current, and aligned with `README.md` and (if present) `IP.md`.

## Inputs

- Current `PRD.md`, `README.md`, and `IP.md` (if present).
- Recent merged PRs, recently closed issues, and the last few releases (via `gh` or the GitHub API).
- `.github/instructions/prd.instructions.md` — authoritative template + rules.

## Tasks

1. **Drift detection** — compare `PRD.md` against actual repository state:
   - MVP user stories that no longer match shipped behavior
   - ROAD milestones that have passed without update
   - RISK entries that materialized or were mitigated
   - OOS items that quietly slipped into scope
2. **Distill from signals** — propose updates to:
   - **MVP** — adjust if shipped behavior diverged
   - **ROAD** — close past milestones, propose next 3
   - **RISK** — add new risks from recent incidents/post-mortems
   - **DONE** — update the checklist if criteria are now met
3. **Cross-doc sync** — ensure `README.md` features list, `PRD.md` MVP, and `IP.md` (if present) reference the same scope.
4. **Conflict report** — for each detected conflict, classify severity (`low`/`med`/`high`) and propose a resolution.

## Output format

Return a single JSON object:

```json
{
  "drift_summary": "1-paragraph executive summary",
  "conflicts": [
    {"doc": "PRD.md", "section": "MVP", "severity": "high", "issue": "...", "resolution": "..."}
  ],
  "edits": [
    {"path": "PRD.md", "operation": "replace-section", "section": "## 7. ROAD", "content": "..."}
  ],
  "follow_up_issues": [
    {"title": "...", "body": "...", "labels": ["docs", "prd"]}
  ]
}
```

## Rules

- Strictly follow the section structure in `prd.instructions.md`. Do not add or rename sections.
- Keep `PRD.md` ≤ 800 lines. If you must cut, cite the section and reason.
- Active voice, present tense, second person ("You install via…").
- Never delete the WHY section — only refine it.
- Never invent metrics. If a metric is unknown, mark it `TBD`.
