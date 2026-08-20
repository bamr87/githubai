# Marketplace listing

What is built, what a listing still requires, and the decisions that are deliberately still open. The relay code is listing-ready; publishing is a business decision, not an engineering one.

## Built

- **Public App manifest** — [`manifest.json`](manifest.json) declares `"public": true`, a `setup_url` that lands new installations on the relay's post-install page, and least-privilege permissions (`contents: write` only because `repository_dispatch` requires it; `issues` and `pull_requests` are read-only because the relay never writes to them).
- **Installation lifecycle** — `installation` and `installation_repositories` events create, update, suspend, unsuspend, and delete tenant records, so an install or uninstall is reflected immediately rather than inferred.
- **Plan handling** — `marketplace_purchase` deliveries (`purchased`, `changed`, `cancelled`) record the plan slug against every installation of the purchasing account; cancellation returns the account to `free`.
- **Per-tenant isolation** — every query is scoped by installation id, and the dashboard only ever reads the ids in the visitor's signed session. `test/index.test.js` asserts a session for one installation cannot see another's activity.
- **Abuse limits** — a per-installation dispatch ceiling (`RATE_LIMIT_PER_MINUTE`, default 60) with refused deliveries recorded rather than dropped.
- **Data disclosure** — [DATA-HANDLING.md](DATA-HANDLING.md) is the verifiable inventory a privacy policy can be written from.

## Required before listing

1. **A published privacy policy and terms of service at stable URLs.** GitHub requires both. Base the privacy policy on DATA-HANDLING.md and have it reviewed; do not publish that file as the policy itself.
2. **A support URL** with a real response path — a GitHub Discussions category or a support email.
3. **Verified publisher status** for the organization that owns the App, which GitHub requires before a listing can charge money.
4. **A pricing decision.** The plan slug is already recorded per account, but nothing in the relay enforces plan limits yet: `RATE_LIMIT_PER_MINUTE` is global, not per plan. Enforcing tiers means gating on `installation.plan` in the webhook pipeline — a small change, deliberately deferred until pricing exists.
5. **Marketplace webhook configuration.** Marketplace events are configured on the *listing*, not on the App's event subscriptions. Point the listing's webhook URL at the same `/webhook` endpoint; the relay already handles the payloads.
6. **A statement about what Claude usage costs.** GitHubAI never bills for model usage and never proxies it — each customer brings their own Claude Code subscription or Anthropic API key. Say so on the listing, prominently, or the pricing will be misread.

## Open decisions

- **Single-tenant or multi-tenant hosting.** The code runs either way. A public listing implies one shared deployment; some customers will want their own.
- **What a paid tier would actually buy**, given the relay does no AI work: longer retention, higher dispatch ceilings, org-wide policy reporting, and priority support are the plausible axes.
- **Whether to list at all.** Self-hosting the relay is ten minutes of `wrangler` and costs nothing on Cloudflare's free tier. A listing buys reach and convenience, not capability.

## Non-goals

Listing must not change the trust model. Claude keeps running in the customer's own Actions with the customer's own token, the relay keeps holding no code and no credentials, and no plan may unlock automation that bypasses the authorization gates in [docs/security.md](../docs/security.md).
