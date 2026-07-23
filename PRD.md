# GitHubAI Product Requirements Document

## 0. WHY

**North Star**: Every repository ships with an AI staff engineer. GitHubAI makes Claude Code a first-class participant in the whole SDLC — triage, implementation, review, merging, maintenance, releases — installable in any repo in one command.

**KFI (Key Focus Indicator)**: share of routine SDLC events (new issues triaged, minor PRs merged, maintenance filed, releases drafted) handled end-to-end by Claude without a human touching them, while humans retain the authorization points that matter.

**Why now**: v0.x proved the demand but carried a Django/React/Postgres/Celery stack and a bespoke OpenAI pipeline — heavy to host, impossible to adopt casually. GitHub Actions plus `claude-code-action` plus Claude Code OAuth tokens make the entire product expressible as workflows: zero servers, per-repo trust, adoption measured in minutes.

## 1. MVP (Minimum Viable Promise)

1. **As a maintainer**, I run one install command and my repo gains issue triage, label-gated implementation, PR review, an auto-merge lane, weekly maintenance, and release drafting — all authenticated by my `CLAUDE_CODE_OAUTH_TOKEN`.
2. **As a maintainer**, I declare my repo's type and purpose in `.github/githubai.yml` and Claude's behavior follows standards appropriate to that type (a library is reviewed like a library, a webapp like a webapp).
3. **As a contributor**, my issue gets triaged in minutes: classified, deduplicated, and — when it's under-specified — met with precise clarifying questions.
4. **As a maintainer**, applying `claude:implement` to an issue produces a tested PR that closes it; applying `claude:auto-merge` to a minor PR (or letting dependabot open one) gets a safety verdict and, when low-risk and green, an automatic merge.
5. **As an org owner**, I can route events through a GitHub App relay instead of per-repo event stubs, without changing the trust model (repos keep their own OAuth token).

All P0 except story 5 (P1, shipped as scaffolding). Deferred: see OOS.

## 2. UX

The product's UI is GitHub itself. The user-visible surface is exactly: labels (`claude:*` as the control plane), Claude's comments (triage summaries, review verdicts, merge verdicts, health reports), PRs and releases it creates, and one config file. The installer is the only CLI moment, and `@claude` mentions are the escape hatch to interactive mode everywhere.

```text
issue opened ──▶ triage comment + labels
      │  claude:implement (human)
      ▼
tested PR ──▶ review verdict + inline findings
      │  claude:auto-merge (human or bot author)
      ▼
safety verdict ──▶ approve + auto-merge (waits for required checks)

weekly ──▶ maintenance issues + health report        tag push ──▶ release notes
```

## 3. API (what consumers program against)

| Surface | Contract |
|---------|----------|
| `setup/install.sh` | flags: `--profile`, `--ref`, `--source`, `--app`, `--labels`, `--force`, `--dry-run` |
| Reusable workflows | `bamr87/githubai/.github/workflows/claude-{triage,implement,review,auto-merge,maintenance,release}.yml@ref` + `claude.yml`; inputs per file; secrets `CLAUDE_CODE_OAUTH_TOKEN` / `ANTHROPIC_API_KEY` |
| `actions/load-config` | input `config_path`; outputs `config`, `type`, `model`, `max_turns`, `*_enabled`, `prompt_context` |
| `.github/githubai.yml` | schema in [docs/configuration.md](docs/configuration.md); merged over `profiles/_base.yml` ← `profiles/<type>.yml` |
| Labels | `claude:implement`, `claude:auto-merge`, `claude:review`, `claude:skip` (inputs); `claude:triaged`, `claude:in-progress`, `claude:needs-human` (outputs) |
| Dispatch types (app mode) | `githubai-{triage,implement,review,auto-merge,maintenance}` with `client_payload.{issue_number,pr_number,tasks}` |

Compatibility rule: all of the above are public API; renames and removals are breaking changes requiring a major version.

## 4. Architecture invariants

- **OAuth-first**: every Claude invocation prefers `CLAUDE_CODE_OAUTH_TOKEN`; `ANTHROPIC_API_KEY` is a fallback, never the default.
- **Actions are the execution substrate** in both modes; the app relay only routes events. AI never runs outside the repo's own CI context.
- **Humans hold authorization**: implementation requires a maintainer-applied label; auto-merge requires label or trusted-bot authorship, a read-only structured verdict, and GitHub's own required checks; Claude never force-merges or approves outside the auto-merge lane.
- **Untrusted content is data**: issue/PR bodies are read via `gh` as analysis input, never interpolated into shell or treated as instructions; every automation prompt says so explicitly.
- **Config over code**: behavior differences between repos live in profiles + `githubai.yml`, not in forked workflows.

## 5. Milestones

- **M1 (this rebuild)** — framework + template + installer + app scaffolding; dogfooding on this repo.
- **M2** — tagged `v1` releases; stubs pin by default; adoption in 3+ real repos of different types; prompt tuning from field results.
- **M3** — hosted GitHubAI App: multi-tenant relay with per-org config, activity dashboard, marketplace listing; org-level policy (e.g. central auto-merge rules).
- **M4** — fleet intelligence: cross-repo health rollups, org-wide maintenance campaigns, standards drift detection across an organization.

## 6. OOS (Out of Scope)

- Hosting or proxying model calls; storing user code or tokens outside GitHub.
- A web UI beyond GitHub (the v0 chat/dashboard is intentionally gone).
- Support for non-Claude models (the framework is Claude Code-native by design).
- Auto-merging anything Claude rates above low risk, regardless of configuration.
