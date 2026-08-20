# GitHubAI as a GitHub App

Two ways to run GitHubAI. **Actions-only mode is the default** and needs nothing from this directory: the installer drops per-event workflow stubs into each repo and GitHub Actions does the rest. **App mode** exists for org-scale rollouts — one installation surface instead of per-repo stubs, org-wide routing policy, and one place to see what the automation did across every repository.

What app mode does *not* change is the trust model. Claude still runs only inside each repository's own Actions run, with that repository's own `CLAUDE_CODE_OAUTH_TOKEN`. The relay's App token is used for exactly one thing: firing `repository_dispatch`.

## How app mode works

```text
GitHub event ──▶ GitHubAI App webhook ──▶ relay (Cloudflare Worker + D1)
                                            │  verify HMAC signature
                                            │  drop duplicate deliveries
                                            │  apply org policy + rate limit
                                            │  mint installation token
                                            ▼
                              repository_dispatch (githubai-*)
                                            ▼
                        .github/workflows/claude-dispatch.yml
                                            ▼
                    same reusable claude-*.yml workflows as Actions mode
```

## What the relay is and is not

| It does | It never does |
|---------|---------------|
| Verify webhook signatures and deduplicate deliveries | Run Claude, or call any model API |
| Decide which dispatch type an event maps to | Read repository code, issue bodies, or PR diffs |
| Read org policy from your own `.github` repository | Store your Claude Code OAuth token, or any user token |
| Record what it routed, and why, for 30 days | Write to your repositories beyond `repository_dispatch` |
| Mint short-lived installation tokens per request | Hold long-lived credentials for your account |

Full disclosure of stored data: [DATA-HANDLING.md](DATA-HANDLING.md).

## Event routing

Routing mirrors Actions mode exactly, including the opt-outs. That matters more than it sounds: a reusable workflow reached through `repository_dispatch` has no issue or PR in its event context, so it *cannot* re-check `claude:skip` or draft status the way it does for direct events. The relay applies those gates itself ([`src/routing.js`](relay/src/routing.js)), and `test/routing.test.js` asserts the parity.

| Webhook | Condition | Dispatch type |
|---------|-----------|---------------|
| `issues` | opened / reopened, human author | `githubai-triage` |
| `issues` | labeled `claude:implement` | `githubai-implement` |
| `pull_request` | opened / ready_for_review (same-repo, non-draft) | `githubai-review` |
| `pull_request` | opened by dependabot / renovate | `githubai-auto-merge` |
| `pull_request` | labeled `claude:auto-merge` / `claude:review` | `githubai-auto-merge` / `githubai-review` |
| any | subject carries `claude:skip` | ignored |
| any | fork PR, draft PR, or bot-authored issue | ignored |
| `installation`, `installation_repositories` | any | tenant record maintained |
| anything else | — | ignored, with the reason recorded |

`githubai-maintenance` is routed by the dispatch workflow but never emitted by the relay: maintenance is cron-driven inside each repo.

## Org policy

Organizations can narrow routing from one file — `.github/githubai-org.yml` in the org's `.github` repository, in the same schema repositories already use. Start from [`template/githubai-org.yml`](../template/githubai-org.yml).

```yaml
org:
  enabled: true
  repos:
    exclude: ["legacy-*"]
automation:
  auto_merge:
    enabled: false     # no repository in this org enters the auto-merge lane
```

Policy is **subtractive**: it can stop the relay dispatching, never make a repository do something its own config disables, and never change who may authorize work. If the file fails to parse, the last version that parsed keeps applying and the error surfaces on the dashboard — a typo cannot silently unlock automation an org had turned off. The `.github` repository must be included in the installation, or the relay cannot read the file and treats the org as unrestricted.

## Dashboard

Signing in with GitHub at the relay's root shows, for installations you administer: which repositories are covered, whether org policy loaded, and every delivery the relay handled with its outcome — dispatched, ignored, blocked by policy, rate limited, or failed. It is read-only and deliberately narrow. GitHubAI's PRD puts "a web UI beyond GitHub" out of scope and that still holds; this answers the one question a router owes its operators — *what did you do with my events, and why* — and nothing else.

Sessions are HMAC-signed cookies holding your login and the installation ids you were entitled to at sign-in. The GitHub user token used to look those ids up is discarded immediately and never stored.

## Setup

1. **Create the App.** Use GitHub's [App Manifest flow](https://docs.github.com/en/apps/sharing-github-apps/registering-a-github-app-from-a-manifest) with [`manifest.json`](manifest.json) (replace the three `YOUR-RELAY` URLs first), or let the relay generate it: set `SETUP_TOKEN` and open `/manifest/new?token=…`. Registering manually works too — match the permissions (`contents: write`, `issues: read`, `pull_requests: read`, `metadata: read`) and events (`issues`, `pull_request`, `installation`, `installation_repositories`). Set `"public": false` in the manifest if the App is for your org only.
2. **Deploy the relay.** [`OPERATIONS.md`](OPERATIONS.md) has the runbook: create the D1 database, apply `schema.sql`, set the secrets, `wrangler deploy`, then point the App's webhook URL at `https://<worker>/webhook`.
3. **Install the App** on the org or selected repositories. Include the `.github` repository if you want org policy.
4. **Add the dispatch workflow** to each repo: `setup/install.sh --app` installs `claude-dispatch.yml` alongside the config. Keep `claude.yml` for `@claude` mentions, `claude-maintenance.yml` for its cron, and `claude-release.yml` for tag pushes — schedules and tag events do not route through the relay.
5. **Secrets stay per-repo/org**: `CLAUDE_CODE_OAUTH_TOKEN` (or `ANTHROPIC_API_KEY` fallback) exactly as in Actions-only mode. One org-level Actions secret covers every repository.

## Development

```bash
cd app/relay
npm test          # node --test, no dependencies, no Cloudflare account needed
npm run dev       # wrangler dev (in-memory store when no D1 binding is bound)
npm run deploy
```

The relay has no build step and no npm dependencies. Tests run against the same modules the Worker imports, with an in-memory store and a fake GitHub client; [`test/`](relay/test/) covers routing parity, policy evaluation, session and signature handling, tenant isolation, and the full webhook pipeline. `tests/test_app.py` in the framework's Python suite additionally checks that the relay's dispatch types stay in sync with `template/workflows/claude-dispatch.yml`.

One consequence of running in a zero-dependency Worker: org policy is parsed by [`src/yaml.js`](relay/src/yaml.js), a deliberately small YAML subset that throws on anything it cannot represent faithfully (anchors, aliases, merge keys, tags, multi-document streams). Its test suite parses this framework's own config files and asserts the results match what `actions/load-config` gets from PyYAML.

## Marketplace

Listing prerequisites, the plan model, and what still has to be decided before publishing: [MARKETPLACE.md](MARKETPLACE.md).
