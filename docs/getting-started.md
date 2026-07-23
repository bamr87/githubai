# Getting started

Adopting GitHubAI takes one command, two credentials steps, and one config edit. You need: a repo you maintain, the [GitHub CLI](https://cli.github.com/) authenticated, and a Claude subscription (or an Anthropic API key as fallback).

## 1. Install the framework files

From your repo's root:

```bash
curl -fsSL https://raw.githubusercontent.com/bamr87/githubai/main/setup/install.sh | bash -s -- --labels
```

This detects your repo type, writes thin workflow stubs to `.github/workflows/` (they call this repo's reusable workflows — your copy stays small), a starter `.github/githubai.yml`, a starter `CLAUDE.md`, and (with `--labels`) the label taxonomy. Nothing existing is overwritten without `--force`; `--dry-run` previews. Pin to a release with `--ref <tag>` once tags exist, and pick the type explicitly with `--profile library|webapp|service|cli|github-action|docs|data|template` if detection guesses wrong.

## 2. Authenticate — Claude Code OAuth by default

```bash
claude setup-token                        # from Claude Code; prints an OAuth token
gh secret set CLAUDE_CODE_OAUTH_TOKEN     # paste it
```

Every workflow uses `CLAUDE_CODE_OAUTH_TOKEN` first and falls back to an `ANTHROPIC_API_KEY` secret only when the OAuth token is absent. Organizations: set it once as an org secret and every adopted repo inherits it.

Then install the [Claude GitHub App](https://github.com/apps/claude) on the repo — `claude-code-action` uses it for branch, comment, and PR operations.

## 3. Tell Claude what your repo is

Edit `.github/githubai.yml`: confirm `repo.type`, and write a real `repo.purpose` — one sharp sentence. Claude reads it in every triage, review, and maintenance run; specific purpose in, specific judgment out. Set `standards.test_command` so implemented PRs arrive tested. Commit and push everything.

## 4. Watch it work

- **Open an issue** → the triage workflow labels it, checks for duplicates, asks clarifying questions if needed, and marks it `claude:triaged`.
- **Apply `claude:implement`** to a triaged issue → Claude builds it on a `claude/` branch and opens a PR that closes the issue, with test evidence in the body.
- **Open any PR** (or mark ready) → Claude reviews it against your repo type's standards with inline findings and a verdict comment. Label `claude:review` re-runs it.
- **Label a minor PR `claude:auto-merge`** (or wait for dependabot) → the safety gate evaluates read-only; low-risk verdicts get approved and auto-merged once your required checks pass. Off by default — enable `automation.auto_merge` in config after reading [security.md](security.md).
- **Weekly** → maintenance files capped, deduplicated issues (docs drift, TODOs, dependency report) and keeps a "Repo health report" issue current.
- **Push a `v*` tag** → categorized release notes appear as a draft release.
- **Mention `@claude`** in any issue or PR comment for interactive help; label anything `claude:skip` to keep automation away from it.

## Uninstalling / pausing

Delete the stub workflows (and labels) to uninstall; set `automation.<area>.enabled: false` in `githubai.yml` to pause one lane while keeping the files; `claude:skip` excludes individual items.
