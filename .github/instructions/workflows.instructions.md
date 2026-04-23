---
applyTo: ".github/workflows/**,.github/actions/**"
---

# Workflow Instructions

Conventions for GitHub Actions workflows in **{{PROJECT_NAME}}**.

## Structure

- One concern per workflow. Don't combine PR review + scheduled scans + releases in one file.
- Reusable workflows live in `.github/workflows/` and use `on: workflow_call`. Name them `agentic-*.yml` or `reusable-*.yml`.
- Caller examples live in `examples/workflows/`.

## Permissions

- **Always** declare `permissions:` at the workflow or job level. Default to least privilege:

  ```yaml
  permissions:
    contents: read
  ```

- Add specific scopes only where needed (`issues: write`, `pull-requests: write`, `models: read`).
- Never use the implicit default token permissions.

## Pinning

- Pin actions to a tagged major version (`@v4`) at minimum; commit SHA preferred for third-party actions.
- Never use `@main` or `@master`.

## Secrets & inputs

- Workflows that accept external input (issue body, PR title, comment) must treat it as untrusted.
- Never interpolate `${{ github.event.* }}` user-controlled fields into a `run:` script. Pass via `env:` instead.
- `pull_request_target` requires extreme care — do not check out and execute PR code with elevated tokens.

## Concurrency

- Add a `concurrency:` block on long-running or release workflows so a new push cancels the old run:

  ```yaml
  concurrency:
    group: ${{ github.workflow }}-${{ github.ref }}
    cancel-in-progress: true
  ```

## Outputs & artifacts

- Reusable workflows expose typed `outputs:` rather than writing files.
- Use `actions/upload-artifact@v4` for files that need to survive the job.

## Testing

- Lint workflow YAML in CI (`actionlint` or equivalent).
- For new reusable workflows, include a tiny caller in `examples/workflows/` that exercises it on this repo.
