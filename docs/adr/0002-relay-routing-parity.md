# ADR 0002 — Routing parity between Actions mode and app mode

> The relay applies every gate a workflow's `if:` applies to a direct event, because a `repository_dispatch` run has no issue or PR left to re-check.

- **Status**: accepted
- **Date**: 2026-08-19
- **Deciders**: the maintainer (bamr87); recorded after the fact on 2026-11-15 from the shipped code and docs (#137)
- **Related**: #110 (hosted multi-tenant relay); PRD § 4 "Routing parity between modes"; [`app/relay/src/routing.js`](../../app/relay/src/routing.js); tests `tests/test_app.py::test_relay_routing_mirrors_actions_mode_gating` and `app/relay/test/routing.test.js`

## Context

In Actions mode each reusable workflow skips work through its own `if:` conditions: issues labelled `claude:skip`, draft PRs, PRs from forks, and bot-authored issues. App mode reaches the same workflows through `repository_dispatch`, and a dispatched run has no issue or PR in `github.event`, so those conditions are structurally unable to fire. Left alone, app mode would be quietly more permissive than Actions mode, which is a silent privilege escalation for app-mode tenants.

## Decision

The relay re-implements exactly those gates in `app/relay/src/routing.js` before it dispatches anything: the `claude:skip` opt-out, the bot-author exclusion (with `dependabot[bot]` and `renovate[bot]` as the trusted auto-merge authors), and the fork and draft rules. `routing.js` is pure functions with no I/O, so the routing contract is unit-testable on its own. A gate added to a workflow's `if:` is added to `routing.js` in the same change. Both suites assert the parity: `app/relay/test/routing.test.js` behaviourally, and `tests/test_app.py::test_relay_routing_mirrors_actions_mode_gating` structurally.

## Consequences

**Positive**

- Installing the app does not widen what Claude may act on: app mode gates exactly like Actions mode.
- The routing contract is tested without a Cloudflare account or a live GitHub.

**Negative**

- Each gate lives in two places, a workflow `if:` and `routing.js`, and the pair must change together.
- The Python test only checks that each gate is named in `routing.js`; the Node tests are what prove the logic matches.

## Alternatives considered

- **Leave the gates to the workflows alone** — a dispatched run cannot see the issue or PR, so the gates would never fire and app mode would be laxer than Actions mode.

## Supersedes / Superseded by

- Supersedes: none
- Superseded by: none
