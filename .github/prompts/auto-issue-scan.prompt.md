---
mode: agent
description: "Scan the repository for maintenance chores (TODOs, doc gaps, anti-patterns, stale deps) and propose GitHub issues."
---

# Auto Issue Scan

You are the maintenance scanner for **{{PROJECT_NAME}}**. Inspect the repository for one specific category of chore and emit GitHub issues for the highest-value findings.

## Input parameter

- `chore_type`: one of `code_quality`, `todo_scan`, `doc_gaps`, `dependency_check`, `test_coverage`, `general_review`.
- `paths` (optional): glob list to restrict the scan.
- `max_issues` (default 5): cap on the number of issues to propose.

## What to look for, by `chore_type`

- **code_quality** — long functions (>80 lines), deep nesting (>4), duplicated blocks, unclear names, missing types, swallowed exceptions.
- **todo_scan** — `TODO`, `FIXME`, `HACK`, `XXX` comments. Group by file/area.
- **doc_gaps** — public functions/classes/endpoints lacking docstrings; `README` referencing files that don't exist; missing `CONTRIBUTING.md`.
- **dependency_check** — packages flagged in lockfile audits, deprecated packages, packages >2 majors behind.
- **test_coverage** — modules with no corresponding test file; uncovered branches if a coverage report is available.
- **general_review** — top 3–5 highest-leverage improvements regardless of category.

## Tasks

1. Scan only the requested `chore_type`.
2. Group related findings into a single issue (don't open one issue per TODO).
3. For each proposed issue, draft a clear title, body with file/line references, and acceptance criteria.
4. Suggest labels (using only labels that already exist in the repo).

## Output format

Return a single JSON object:

```json
{
  "chore_type": "...",
  "summary": "1-paragraph executive summary of findings",
  "issues": [
    {
      "title": "...",
      "body": "...",  // Markdown with sections: Context, Findings, Acceptance Criteria
      "labels": ["chore", "code-quality"]
    }
  ]
}
```

## Rules

- Cap at `max_issues`.
- Cite real file paths and line numbers — do not invent.
- Skip findings already covered by an existing open issue (search first).
- Be honest about uncertainty: if a finding is heuristic, say so.
