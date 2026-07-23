# Migrating from GitHubAI v0.x

Through v0.5.3, GitHubAI was a self-hosted Django + React + Celery + Postgres application with an OpenAI-based issue pipeline. The v1 rebuild replaced it with the GitHub-native, Claude Code-powered framework this repo now contains: no hosting, OAuth-first auth, adoption by installer instead of deployment. The last application-stack release is preserved in git history at tag/commit `v0.5.3` (`ad024a8`) — check that out if you need the old stack.

## Feature map

| v0.x (Django app) | v1 successor |
|-------------------|--------------|
| AI sub-issue generation from parent issues (`create_issue` command, `ai-assist` label) | Triage + `claude:implement` lane — Claude turns the issue into an actual PR, not more issues ([workflows](workflows.md)) |
| Auto-issue generation: code quality, TODO scan, doc gaps, dependency checks | `claude-maintenance.yml` scheduled tasks: `todo_sweep`, `docs_drift`, `dependency_report`, `health_report` |
| Feedback form + REST API creating formatted issues | GitHub issue forms (`.github/ISSUE_TEMPLATE/`) + automatic triage |
| README-update issues (`README-update` label) | `docs_drift` maintenance task (`auto_fix_docs: true` turns findings into PRs) |
| PRD MACHINE document sync / conflict detection | `docs_drift` + repo-type docs expectations in [profiles](../profiles/) |
| AI chat interface (React) + team-lead dashboard | `@claude` mentions in issues/PRs (interactive workflow) + Claude Code locally |
| Semantic versioning service + versioning workflow | `claude-release.yml` prepare mode (version bump PRs) + publish mode (release notes) |
| Multi-provider AI abstraction (OpenAI/XAI/Anthropic) | Claude Code-native by design; model choice via `claude.model` in config |
| Django admin, response caching, API logs | Gone on purpose — GitHub is the UI; Actions logs are the audit trail |
| Docker/Celery/Postgres/nginx infra | Nothing to host |

## Migration steps

1. Decommission any running v0 deployment (nothing in v1 talks to it).
2. Remove v0 workflow files if you had copied them (`openai-issue-processing.yml`, `auto-doc-generator.yml`, `versioning.yml`) and the `OPENAI_API_KEY`/`XAI_API_KEY` secrets.
3. Follow [getting-started.md](getting-started.md) — install, set `CLAUDE_CODE_OAUTH_TOKEN`, configure `githubai.yml`.
4. Labels: v0's `ai-assist` and `README-update` have no effect anymore; the installer's `--labels` creates the new taxonomy.

Data note: v0 stored issues/templates/logs in Postgres. None of it is needed by v1 (GitHub already holds the issues themselves); export anything you want to keep before decommissioning.
