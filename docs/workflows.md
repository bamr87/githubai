# Workflow reference

Every automation workflow is dual-use: it runs live in this repo (dogfooding) *and* is callable via `workflow_call` — which is how installed repos consume it through their thin stubs (`template/workflows/`). All of them share these conventions: OAuth-first auth (`CLAUDE_CODE_OAUTH_TOKEN`, then `ANTHROPIC_API_KEY`), least-privilege `permissions`, `timeout-minutes`, `concurrency` groups, config loaded via `actions/load-config`, and prompts that treat issue/PR content as data — numbers are interpolated, bodies never are.

When calling any of them: `secrets: inherit` from your stub, and grant the stub's job the same permissions listed below (a reusable workflow can't exceed its caller's grants).

## claude.yml — interactive

- **Triggers**: `@claude` in issue/PR comments or reviews; issue opened/assigned containing `@claude`.
- **Permissions**: contents/PRs/issues read + `id-token: write`, `actions: read`.
- **Behavior**: whatever was asked — the action's tag mode with repo context from `CLAUDE.md`. Branch/PR writes happen through the Claude GitHub App's token, not the workflow token.

## claude-triage.yml

- **Triggers**: issues opened/reopened; `workflow_dispatch(issue_number)` for backfill; `workflow_call(issue_number?, config_path?)`.
- **Permissions**: `issues: write`, contents read, id-token write. Tools restricted to `gh issue`/`gh search`/read-only file access — triage cannot touch code.
- **Behavior**: one `type:*` + `priority:*` + `size:*` label each, dedupe search, clarifying questions, single summary comment, `claude:triaged` (+ `claude:needs-human` when a human call is needed). Chains into implementation only when `triage.auto_implement_labels` allows. Skips bot-authored issues and `claude:skip`.

## claude-implement.yml

- **Triggers**: issue labeled `claude:implement` (rename via the `trigger_label` input); dispatch/call with `issue_number`.
- **Permissions**: `contents: write`, `issues: write`, `pull-requests: write`, id-token write, actions read.
- **Behavior**: marks `claude:in-progress`, then either (a) stops with questions + `claude:needs-human` when requirements are ambiguous, or (b) implements on `claude/issue-<n>-<slug>`, runs `standards.test_command`, updates stale docs, opens a PR with `Closes #<n>` + test evidence, links it on the issue. The maintainer-applied label is the authorization boundary.

## claude-review.yml

- **Triggers**: PR opened/ready_for_review (same-repo, non-draft); label `claude:review` to (re)run, drafts included; dispatch/call with `pr_number`.
- **Permissions**: `pull-requests: write`, contents read, id-token write, actions read.
- **Behavior**: reviews diff + surrounding code against the profile's review focus; inline comments classified [blocker]/[important]/[nit]; one sticky verdict comment (includes semver classification where the repo type demands it); adds a `size:*` label; may nominate clean, path-eligible PRs with the auto-merge label. Never approves or merges. Fork PRs are skipped (no secrets in fork context).

## claude-auto-merge.yml

- **Triggers**: PR labeled `claude:auto-merge`; PRs opened by dependabot/renovate; dispatch/call with `pr_number`.
- **Permissions**: `contents: write`, `pull-requests: write`, checks read, id-token write, actions read.
- **Behavior**: two-phase by design. Phase 1: Claude, with **read-only tools**, checks the config gate (enabled + author/label + every file in `allowed_paths`), the content gate (genuinely minor changes only), risk (dependency-diff inspection; major bumps ≥ medium), and CI state — returning a structured verdict via JSON schema. Phase 2: a deterministic bash step posts the verdict comment and, only for `eligible && risk ≤ max_risk` (high never merges), approves and runs `gh pr merge --auto` — so the merge still waits for your required checks. If enabling auto-merge fails (repo setting off, no protection), it says so and leaves the PR approved but unmerged.

## claude-maintenance.yml

- **Triggers**: weekly cron (the *stub's* cron is what fires for consumers), dispatch/call with optional `tasks` subset.
- **Permissions**: contents/issues/PRs write, id-token write, actions read.
- **Behavior**: runs the enabled tasks — `docs_drift`, `todo_sweep`, `dependency_report` (manifest reading only, never installs), `stale_nudge` (max 5), `health_report` (single updatable issue). All output deduped via the `<!-- githubai:maintenance -->` marker, capped by `max_issues_per_run`, labeled `type:chore` + `claude:triaged`. Docs fixes become PRs only when `auto_fix_docs: true`; nothing ever lands on the default branch directly.

## claude-release.yml

- **Triggers**: push of `v*` tag (publish mode); dispatch/call with `bump` (prepare mode).
- **Permissions**: `contents: write`, `pull-requests: write`, id-token write.
- **Behavior**: publish = categorized release notes from the tag range → GitHub release (draft per config). Prepare = pick the semver bump from commits (or honor the input), update `VERSION`/`CHANGELOG.md` on a branch, open a `release: vX.Y.Z` PR. Tags are never created by automation — pushing the tag stays a human act.

## CI for the framework itself

`ci.yml` (pytest suite + shellcheck) and `markdown-oneline.yml` (one-paragraph-per-line prose rule) guard this repo; they are not installed into consumers.
