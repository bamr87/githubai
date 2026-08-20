# Relay operations runbook

Everything needed to stand up, run, and troubleshoot the GitHubAI hosted relay. The relay is a single Cloudflare Worker with one D1 database and no build step.

## Prerequisites

- A Cloudflare account with Workers and D1 enabled, and `wrangler` authenticated (`npx wrangler login`).
- A GitHub App — created from [`manifest.json`](manifest.json), from the relay's `/manifest/new` flow, or by hand with the permissions and events listed in [README.md](README.md#setup).
- Node 20+ if you want to run the test suite locally.

## First deploy

```bash
cd app/relay

# 1. Database
npx wrangler d1 create githubai              # copy the returned database_id into wrangler.toml
npx wrangler d1 execute githubai --remote --file=schema.sql

# 2. Secrets (each prompts for the value)
npx wrangler secret put GITHUB_APP_ID          # numeric App ID
npx wrangler secret put GITHUB_APP_PRIVATE_KEY # PKCS#8 PEM — see below
npx wrangler secret put WEBHOOK_SECRET         # the App's webhook secret
npx wrangler secret put SESSION_SECRET         # 32+ random chars: openssl rand -hex 32
npx wrangler secret put GITHUB_CLIENT_ID       # optional: dashboard sign-in
npx wrangler secret put GITHUB_CLIENT_SECRET   # optional: dashboard sign-in

# 3. Ship it
npx wrangler deploy
```

GitHub hands you a **PKCS#1** private key (`BEGIN RSA PRIVATE KEY`); WebCrypto only imports **PKCS#8**. Convert once and store the result:

```bash
openssl pkcs8 -topk8 -nocrypt -in your-app.private-key.pem -out app-pkcs8.pem
```

The relay refuses to start signing with a PKCS#1 key and says exactly this in the error, so a wrong key shows up as a clear message rather than a cryptic WebCrypto failure.

Finally, point the App's webhook URL at `https://<worker>.workers.dev/webhook` and verify with **Redeliver** on any ping in the App's Advanced tab.

## Configuration reference

| Name | Kind | Required | Purpose |
|------|------|----------|---------|
| `GITHUB_APP_ID` | secret | yes | Identifies the App when minting installation tokens |
| `GITHUB_APP_PRIVATE_KEY` | secret | yes | PKCS#8 PEM used to sign the App JWT |
| `WEBHOOK_SECRET` | secret | yes | HMAC key for verifying deliveries |
| `SESSION_SECRET` | secret | dashboard | Signs session cookies and OAuth state; 16 chars minimum, 32+ recommended |
| `GITHUB_CLIENT_ID` / `GITHUB_CLIENT_SECRET` | secret | dashboard | App OAuth credentials for sign-in |
| `SETUP_TOKEN` | secret | no | Enables `/manifest/new`; the route 404s when unset |
| `DB` | D1 binding | yes | Tenant records, activity, policy cache |
| `RATE_LIMIT_PER_MINUTE` | var | no | Dispatches per installation per minute (default 60) |
| `POLICY_TTL_SECONDS` | var | no | Org policy cache lifetime (default 300) |
| `APP_INSTALL_URL` | var | no | Install link shown on the signed-out landing page |
| `MANIFEST_ORG` | var | no | Targets `/manifest/new` at an org rather than a user account |

Without a `DB` binding the relay falls back to an in-memory store scoped to one isolate. That is fine for `wrangler dev` and is what the tests use; in production it would silently lose deduplication, rate limiting, and policy caching, so `/health` reports `database: false` to make the situation visible.

## Endpoints

| Path | Method | Auth | Purpose |
|------|--------|------|---------|
| `/webhook` | POST | HMAC signature | The only endpoint GitHub calls |
| `/health` | GET | none | Configuration presence and row counts; 503 when misconfigured |
| `/` and `/dashboard` | GET | session cookie | Landing page, or the activity dashboard |
| `/login`, `/oauth/callback`, `/logout` | GET | — | Dashboard sign-in via GitHub App user-to-server OAuth |
| `/api/installations`, `/api/activity` | GET | session cookie | JSON behind the same entitlement check as the dashboard |
| `/setup` | GET | none | Post-install landing page GitHub redirects to |
| `/manifest/new`, `/manifest/callback` | GET | `SETUP_TOKEN` | Self-service App registration; disabled unless the token is set |

`/health` never returns a secret's value — only whether each one is present.

## Monitoring

- `npx wrangler tail` streams live logs; unhandled errors log the path and stack while the response stays a bare `internal error`.
- `/health` is the endpoint to point an uptime check at. It returns 503 when `GITHUB_APP_ID`, `GITHUB_APP_PRIVATE_KEY`, or `WEBHOOK_SECRET` is missing, or when the database is unreachable.
- The App's **Advanced → Recent Deliveries** tab is the authority on what GitHub sent. The relay's dashboard is the authority on what happened next.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Deliveries show 401 | `WEBHOOK_SECRET` differs from the App's | Reset the secret in App settings, `wrangler secret put` the same value |
| Deliveries show 502 | Installation token or dispatch call failed | Check the activity row's detail; usually the App lacks `contents: write` on that repo, or the installation was removed |
| Deliveries show 429 | One installation exceeded the per-minute ceiling | Raise `RATE_LIMIT_PER_MINUTE`, or find the loop that is generating events |
| 202 but nothing runs | The repo has no `claude-dispatch.yml` | `setup/install.sh --app` in that repository |
| Dispatched but the workflow no-ops | The repo's own `githubai.yml` disables that lane, or the workflow's gate rejected it | Check the repo's Actions run, not the relay |
| Org policy has no effect | The `.github` repo is not in the installation, or the file is at the wrong path | Add the repo to the installation; the path is `.github/githubai-org.yml` |
| Dashboard shows no installations | The session predates the installation | Sign out and back in; entitlement is a snapshot taken at sign-in |
| Policy shows an error pill | The file no longer parses | The last good version is still being enforced; fix the YAML and it reloads within a minute |

## Retention and deletion

A nightly cron (`17 4 * * *`) deletes activity rows and delivery ids older than 30 days. Uninstalling the App deletes that installation's record, repository list, cached policy, and rate-limit counter immediately; activity rows age out on the normal schedule. To purge a tenant on request:

```bash
npx wrangler d1 execute githubai --remote \
  --command "DELETE FROM activity WHERE installation_id = <id>;"
```

## Upgrades

`wrangler deploy` is the whole upgrade path. Schema changes are additive `CREATE TABLE IF NOT EXISTS` statements in `schema.sql`; re-running it against an existing database is safe. Run `npm test` before deploying — it needs no Cloudflare account and covers routing, policy, sessions, tenant isolation, and the webhook pipeline.
