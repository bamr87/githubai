# Security model

GitHubAI automates high-trust operations (labeling, implementing, reviewing, merging), so the design is explicit about who authorizes what, which credentials exist where, and how untrusted content is contained.

## Authentication

**Claude Code OAuth is the default.** Every workflow passes `claude_code_oauth_token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}` and only falls back to `ANTHROPIC_API_KEY` when the OAuth token is empty (`tests/test_workflows.py` enforces the pattern in every file). The OAuth token comes from `claude setup-token`, is scoped to Claude Code usage under your subscription, and should live as a repo or org **Actions secret** — never in files. GitHub-side write operations use either the workflow's `GITHUB_TOKEN` (bounded by each job's `permissions` block) or the [Claude GitHub App](https://github.com/apps/claude)'s installation token for branch/PR pushes; no personal access tokens anywhere.

## Authorization boundaries (who can make Claude do what)

| Action | Authorized by |
|--------|---------------|
| Triage labels/comments | Automatic on new issues — but the tools are read/label/comment only |
| Code implementation | A user with **triage+ permission** applying `claude:implement` |
| Review comments | Automatic on non-draft, same-repo PRs; read + comment tools only |
| Approve + auto-merge | Label by a triage+ user *or* trusted bot authorship, **and** Claude's independent low-risk verdict, **and** your branch protection's required checks |
| Maintenance issues/PRs | The schedule you installed; output caps in config |
| Releases | A human pushing a tag (publish) or dispatching the workflow (prepare); automation never creates tags |
| Interactive `@claude` | Commenters — the action itself restricts execution to users with write access unless you configure otherwise |

`claude:skip` is a universal opt-out; `claude:needs-human` is Claude's own escalation path and appears whenever it declines to act.

## Untrusted content

Issue and PR bodies are attacker-controlled. Three containment layers: (1) workflows interpolate only numeric IDs and repo names into prompts and shell — bodies are read by Claude via `gh` as data; (2) every automation prompt states that fetched content is analysis input, not instructions, and that in-content claims of authorization are void; (3) tool allowlists match each job's purpose — triage and the auto-merge evaluator run read-only (`gh` view/search + file reads), so even a successful injection cannot push code or merge. The implement lane has write tools by necessity, which is exactly why it sits behind a maintainer-applied label. Fork PRs are skipped entirely (they get no secrets), and the interactive workflow answers only same-repo events.

## The auto-merge lane, specifically

Merging without human review is the sharpest capability, so it's off by default and quadruple-gated when on: config gate (enabled + `allowed_authors`/label + every changed file matching `allowed_paths`) → content gate (genuinely-minor diff standard) → risk verdict (structured JSON; `high` never merges; dependency diffs inspected for install hooks, changed dist URLs, obfuscation) → GitHub's own machinery (`gh pr merge --auto` means required checks still decide when). The merging step is deterministic bash acting on the verdict — Claude itself has no merge tool. **Prerequisites**: enable repo auto-merge setting and branch protection with required status checks; without protection the workflow refuses to merge directly and says so. Note that the approval comes from `github-actions[bot]`, which satisfies "1 approval" rules but not CODEOWNERS review requirements — leave those on for paths that should never auto-merge.

## Supply chain

Stubs reference this framework `@main` by default for frictionless starts; pin with `--ref <tag>` at install (the installer rewrites every `uses:` line) once you want immutability, and prefer a full commit SHA for the strictest posture. Inside the framework, third-party actions are pinned by major (`actions/checkout@v4`, `anthropics/claude-code-action@v1`), permissions are least-privilege per job, and dependabot + the auto-merge lane keep pins fresh under the same safety gate as everything else. The relay (app mode) verifies webhook HMACs, holds no state, and never sees model traffic or code — worst case on relay compromise is spurious `repository_dispatch` events into workflows that still enforce all gates above.

## Reporting

Security reports: open an issue with the `type:bug` label mentioning security (triage marks these `claude:needs-human` — automation is instructed not to self-triage security reports into implementation), or contact the maintainer directly for anything sensitive.
