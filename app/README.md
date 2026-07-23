# GitHubAI as a GitHub App

Two ways to run GitHubAI. **Actions-only mode is the default** and needs nothing from this directory: the installer drops per-event workflow stubs into each repo and GitHub Actions does the rest. App mode exists for org-scale rollouts where you want one installation surface, centralized event routing, and a single place to evolve routing logic without touching every repo's stubs.

## How app mode works

```text
GitHub event ──▶ GitHubAI App webhook ──▶ relay (Cloudflare Worker)
                                            │  verify HMAC signature
                                            │  map event → dispatch type
                                            │  mint installation token
                                            ▼
                              repository_dispatch (githubai-*)
                                            ▼
                        .github/workflows/claude-dispatch.yml
                                            ▼
                    same reusable claude-*.yml workflows as Actions mode
```

The relay is deliberately thin: no state, no queue, no AI calls. All Claude work still happens inside the repo's own Actions runs with the repo's own `CLAUDE_CODE_OAUTH_TOKEN` secret, so app mode changes *routing*, not *trust*: the App's token is used only to fire `repository_dispatch`.

## Setup

1. **Create the App from the manifest.** Use GitHub's [App Manifest flow](https://docs.github.com/en/apps/sharing-github-apps/registering-a-github-app-from-a-manifest) with [`manifest.json`](manifest.json), or register manually with the same permissions (contents/issues/PRs write; checks/actions/metadata read) and events (issues, issue_comment, pull_request, pull_request_review, pull_request_review_comment, release).
2. **Deploy the relay.** From [`relay/`](relay/): set the three secrets (`GITHUB_APP_ID`, `GITHUB_APP_PRIVATE_KEY` as PKCS#8 — convert GitHub's download with `openssl pkcs8 -topk8 -nocrypt -in app.pem`, and `WEBHOOK_SECRET`), then `wrangler deploy`. Point the App's webhook URL at `https://<worker>/webhook`.
3. **Install the App** on the repos or the whole org.
4. **Add the dispatch workflow** to each repo: `setup/install.sh --app` installs `claude-dispatch.yml` alongside the config; the per-event stubs become optional at that point (keep `claude.yml` for `@claude` mentions, `claude-maintenance.yml` for its cron, and `claude-release.yml` for tag pushes — schedules and tag events don't route through the relay).
5. **Secrets stay per-repo/org**: `CLAUDE_CODE_OAUTH_TOKEN` (or `ANTHROPIC_API_KEY` fallback) exactly as in Actions-only mode.

## Event routing

| Webhook | Condition | Dispatch type |
|---------|-----------|---------------|
| `issues` | opened / reopened | `githubai-triage` |
| `issues` | labeled `claude:implement` | `githubai-implement` |
| `pull_request` | opened / ready_for_review (same-repo, non-draft) | `githubai-review` |
| `pull_request` | opened by dependabot/renovate | `githubai-auto-merge` |
| `pull_request` | labeled `claude:auto-merge` / `claude:review` | `githubai-auto-merge` / `githubai-review` |
| anything else | — | ignored |

## Roadmap

The relay is the seed of the hosted GitHubAI App: a multi-tenant service that adds per-org config, a dashboard over Claude's activity, and marketplace installation. That work is tracked in [PRD.md](../PRD.md); the contract that stays fixed is that repos keep their own OAuth token and the reusable workflows remain the execution substrate.
