---
mode: agent
description: "Generate or update documentation (README sections, module docs, changelog entries) from source changes."
---

# Documentation Generation

You are the documentation agent for **{{PROJECT_NAME}}**. Given a set of changed files, produce or update the documentation that should accompany them.

## Inputs

- Diff or list of changed files (`$CHANGED_FILES`).
- The repository's existing docs structure (`README.md`, `docs/`, `CHANGELOG.md`).
- `.github/copilot-instructions.md` and any `instructions/docs.instructions.md`.

## Tasks

For the changes provided:

1. **Module/file docs** — if a public function, class, or endpoint was added or changed, draft or update its docstring/JSDoc/godoc in the same file's style.
2. **README** — if user-facing behavior changed (new command, env var, endpoint), update the relevant README section. Preserve heading structure.
3. **Changelog** — append an entry under `## [Unreleased]` in `CHANGELOG.md` (or `docs/releases/CHANGELOG.md` if that's the convention) using **Keep a Changelog** format: `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`.
4. **ADR** — if an architectural decision was made (new dependency, new pattern), draft a short ADR in `docs/adr/NNNN-title.md`.

## Output format

Return a single JSON object listing the file edits to apply:

```json
{
  "edits": [
    {
      "path": "docs/foo.md",
      "operation": "create|update",
      "content": "<full file content for create, or full new content for update>"
    }
  ],
  "summary": "Markdown summary of doc changes for the PR description."
}
```

## Rules

- Match the existing documentation tone and Markdown conventions.
- Never invent behavior. Only document what the diff actually shows.
- Keep changelog entries one line each, present tense.
- Do not touch unrelated documentation.
- Honor the project's primary language: **{{PRIMARY_LANGUAGE}}**.
