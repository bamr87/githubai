# Migration: Legacy Django Stack → Agentic Template

This document maps the existing Django + Celery + React implementation onto
the new `.github/`-only model.

> **Status:** Phase 1 of the refactor. The legacy Django app is **still
> present and functional** — nothing has been removed. This document is the
> roadmap for Phases 2–4.

## Service ↔ Workflow mapping

| Legacy capability | Where it lived | New surface |
| --- | --- | --- |
| AI chat (`/chat`) | `apps/core/views.py` (`ChatView`) + React `frontend/` | GitHub Copilot Chat in your IDE; configured via `.github/copilot-instructions.md` and `.github/instructions/*` |
| Prompt templates | `PromptTemplate` model + admin | `.github/prompts/*.prompt.md` (versioned by Git) |
| Sub-issue generation | `IssueService.create_sub_issue_from_template` + `python manage.py create_issue` | `agentic-track.yml` (`create-sub-issues: true`) |
| Auto-issue scans | `AutoIssueService` + `python manage.py auto_issue` | `agentic-analyze.yml` |
| Doc generation | `DocGenerationService` + `python manage.py generate_docs` | `agentic-improve.yml` (docs branch) |
| Version bumping | `VersioningService` + `python manage.py bump_version` | `agentic-improve.yml` (version branch) |
| PRD MACHINE | `PRDMachineService` + `python manage.py prd_machine` | `agentic-prd-sync.yml` |
| Feedback → issue | `POST /api/issues/issues/create-from-feedback/` | `agentic-feedback-to-issue.yml` + `feedback.yml` issue form |
| Multi-provider AI | `AIProvider`, `AIModel`, `AIProviderFactory` | `with: { model: … }` input on each reusable workflow |
| Response caching | `AIResponse` model | Removed — workflows are short-lived; cost is bounded by trigger frequency |
| Usage logs | `APILog` model | GitHub Actions run logs + the `models: read` audit trail |
| Persistent state | PostgreSQL | Repository files + Issues + Discussions |

## REST endpoints — replacement

| Endpoint | Replacement |
| --- | --- |
| `POST /api/issues/issues/create-sub-issue/` | Comment `@copilot decompose` on the parent issue, **or** trigger `agentic-track.yml` with `create-sub-issues: true` |
| `POST /api/issues/issues/create-readme-update/` | Open an `ai_assist.yml` issue with scope = README |
| `POST /api/issues/issues/create-auto-issue/` | `workflow_dispatch` of the `weekly-scan.yml` caller |
| `POST /api/issues/issues/create-from-feedback/` | Submit the `feedback.yml` issue form |
| `GET  /api/issues/templates/` | Browse `.github/prompts/` and `.github/ISSUE_TEMPLATE/` directly |
| `POST /api/chat/` | Use Copilot Chat in VS Code (with `.vscode/mcp.json` for tool access) |

## Management commands — replacement

| Command | Replacement |
| --- | --- |
| `python manage.py create_issue --repo … --parent N` | `agentic-track.yml` triggered on issue open |
| `python manage.py auto_issue --chore-type X` | `workflow_dispatch` on `weekly-scan.yml` with input `chore_type=X` |
| `python manage.py generate_docs --file F` | Edit the file, push, `agentic-improve.yml` runs |
| `python manage.py bump_version` | `agentic-improve.yml` (run-version: true) |
| `python manage.py prd_machine --distill` | `workflow_dispatch` on `prd-sync.yml` |

## Phase plan

- **Phase 1 (this PR)** — Add new `.github/` assets. Legacy untouched.
- **Phase 2** — Validate the new workflows on this repo's own PRs/issues
  for one release cycle. Address gaps in prompts.
- **Phase 3** — Add template metadata (`scripts/init-template.sh`, repo
  topic `template`, README rewrite).
- **Phase 4** — Deprecate Django app: move `apps/`, `frontend/`,
  `infra/docker/`, Celery / Postgres deps to a `legacy/` directory or a
  long-lived `legacy` branch. Update `pyproject.toml`, `pytest.ini`,
  `PRD.md`, `IP.md`.

## What you lose by migrating

- **Persistent chat history & response cache.** GitHub Actions runs are
  ephemeral. If you need history, the run logs and PR/issue comments are
  the system of record now.
- **Custom Django admin UI.** Replaced by the GitHub UI (Issues, PRs,
  Actions runs).
- **Database-driven prompt versioning.** Replaced by Git history of the
  `.github/prompts/` files.

## What you gain

- **Zero infra.** No Postgres, Redis, Celery, Nginx, Docker.
- **Portable.** Drop the `.github/` directory into any repo.
- **Native.** Uses GitHub Copilot, GitHub-hosted models,
  `actions/ai-inference`, MCP — surfaces that ship with GitHub itself.
- **Reviewable.** Every agent action becomes a PR or comment with a
  human-readable diff.
