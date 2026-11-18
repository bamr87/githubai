# ADR 0003 — Org policy is subtractive and keeps the last document that parsed

> In app mode, org policy can only stop an event from reaching a repository, and a policy file that fails to fetch or parse keeps enforcing the last version that parsed.

- **Status**: accepted
- **Date**: 2026-08-19
- **Deciders**: the maintainer (bamr87); recorded after the fact on 2026-11-15 from the shipped code and docs (#137)
- **Related**: #110 (hosted multi-tenant relay); PRD § 3 (org policy is "subtractive only") and § 4 "Humans hold authorization"; [`app/relay/src/policy.js`](../../app/relay/src/policy.js); [docs/configuration.md](../configuration.md) (the org-policy layer); tests `app/relay/test/policy.test.js`, `tests/test_app.py::test_org_policy_template_uses_the_repo_config_schema` and `tests/test_app.py::test_org_policy_areas_cover_every_relay_dispatch_type`

## Context

The hosted relay routes webhooks for many organizations, and each needs a way to restrict where Claude runs: turn the whole org off, limit routing to an include or exclude list of repositories, or switch off an automation area. That policy is applied at the routing layer, before any repository's own workflows run. It must not become a second place that can turn automation on, and a broken policy file must not change what is enforced.

## Decision

1. **Policy lives in the customer's repository.** The relay reads `.github/githubai-org.yml` from the organization's own `.github` repository and only caches it (300 seconds, 60 after an error). It uses the same schema as a repository's `githubai.yml`, so no customer has settings they cannot see and revert in git.
2. **Policy is subtractive only.** `evaluatePolicy` in `app/relay/src/policy.js` either lets an event through unchanged or returns `allowed: false` with a reason. Nothing in the policy layer may enable an area a repository disabled, bypass an authorization gate, or change who may authorize work. Every dispatch still lands in the repository's own workflows, which re-check its config, labels and permissions. The org layer is evaluated in the relay at routing time and is not part of the config merge chain ([ADR 0005](0005-layered-config-merge.md)).
3. **The last known good document wins.** A missing file means no restrictions. A file that fails to fetch or parse does not unlock what the previous version locked: the last successfully parsed document keeps applying, and the error is surfaced in the activity log and the dashboard.

`app/relay/test/policy.test.js` enforces both rules ("policy is subtractive: enabled: true never forces a lane on" and "a broken policy keeps the last good document instead of failing open"); the two `tests/test_app.py` cases keep the policy schema and its areas in step with the repository config schema and the relay's dispatch types.

## Consequences

**Positive**

- A repository's effective behaviour is still exactly what `load_config.py --print` shows; org policy only decides whether the event arrives.
- A typo in the policy file neither silently unlocks a restriction nor takes the whole org offline.

**Negative**

- An organization cannot use policy to turn a lane on across its repositories; each repository opts in through its own config.
- A policy that has never parsed has no last good version, so an unreadable file on the first fetch means no restrictions.

## Alternatives considered

- **Store org configuration in the relay** — customers would have settings they cannot see and revert in git, and "config over code" would stop holding across the tenant boundary.
- **Fail open on a broken policy file** — a typo would become a silent policy bypass.
- **Fail closed on a broken policy file** — a typo would become an org-wide outage.

## Supersedes / Superseded by

- Supersedes: none
- Superseded by: none
