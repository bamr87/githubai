# Architecture

GitHubAI's architecture is the deliberate absence of one: no servers, no database, no queue — GitHub Actions is the runtime, GitHub itself is the UI and state store, and Claude Code (via `anthropics/claude-code-action@v1`) is the only compute. App mode adds exactly one process to that picture, a webhook router, and the decisions below are largely about keeping it from becoming anything more. This page records what holds and why.

## The shape

```text
consumer repo                                framework repo (this one)
─────────────                                ─────────────────────────
.github/workflows/*.yml   ── workflow_call ─▶ .github/workflows/claude-*.yml
  (thin stubs, ~20 lines)                       │
.github/githubai.yml      ──── read by ──────▶ actions/load-config  ◀── profiles/*.yml
CLAUDE.md                                       │ merged config + prompt_context
                                                ▼
                                        anthropics/claude-code-action@v1
                                          (OAuth-first auth, per-lane tool allowlists)
```

## Decisions and rationale

**Reusable workflows over copied workflows.** Consumers hold ~20-line stubs; logic lives here and upgrades by ref bump. The cost is that `github.event` context and caller permissions must be reasoned about carefully — each reusable workflow re-checks its own gating `if` so a mis-wired stub fails closed, and stubs carry the permissions their called jobs need (a callee can't exceed its caller).

**One dual-use file per lane.** Each `claude-*.yml` triggers on this repo's real events *and* declares `workflow_call`. Dogfooding and the consumer path are therefore the same code — divergence is impossible, and every PR here exercises what consumers run.

**Config as layered YAML, resolved at runtime.** `_base.yml` ← `profiles/<type>.yml` ← repo `githubai.yml`, deep-merged by ~250 lines of dependency-light Python inside a composite action. The merged result reaches Claude as a rendered `prompt_context` markdown block — standards, conventions, posture, taxonomy — so prompts stay generic while behavior is repo-specific. The same block is reproducible locally (`--print`), which makes "why did Claude do that" debuggable.

**Prompts live in workflows, mirrored as commands.** Injecting the standards block requires runtime composition, so canonical prompts sit in the workflow files; `.claude/commands/` carries human-invocable equivalents for local use. The pair is kept aligned by convention (CLAUDE.md sync duty) — a known, accepted duplication.

**Structured output where automation acts on the verdict.** The auto-merge lane is the template: Claude evaluates with read-only tools and returns schema-validated JSON; deterministic bash performs the side effects. Judgment and actuation are separated so the blast radius of a bad (or manipulated) judgment is bounded by what the actuator permits.

**Labels as the control plane.** Authorization (`claude:implement`, `claude:auto-merge`), state (`claude:in-progress`, `claude:triaged`), and escalation (`claude:needs-human`, `claude:skip`) are all labels — visible, auditable, permission-gated by GitHub, and equally usable by humans and the app relay.

**The app is a router, not a runtime.** App mode (see [app/README.md](../app/README.md)) converts webhooks to `repository_dispatch` into the same workflows. Trust stays per-repo — each repo's own OAuth secret, each run in the repo's own CI — and the relay can be replaced without touching the framework. Multi-tenancy gave it the only state it has: installation records, a cache of each org's policy file, and 30 days of routing telemetry. It still holds no code, no credentials, and no model traffic, so the blast radius of a relay compromise remains "spurious `repository_dispatch` events into workflows that enforce every gate anyway".

**Routing gates live in the relay because dispatched events cannot carry them.** A reusable workflow reached through `repository_dispatch` has no issue or PR in `github.event`, so the `if:` conditions that skip `claude:skip`, drafts, forks, and bot-authored issues on direct events are structurally unable to fire. App mode would otherwise be quietly more permissive than Actions mode. The relay therefore re-implements exactly those gates in [`routing.js`](../app/relay/src/routing.js), and both suites assert the parity — the Node tests behaviorally, `tests/test_app.py` structurally.

**Org policy is subtractive, and lives in the customer's repo.** The hosted relay reads `.github/githubai-org.yml` from the org's own `.github` repository rather than storing configuration itself, which keeps "config over code" true across the tenant boundary and means no customer has settings they cannot see and revert in git. Policy can only remove: it stops events reaching repositories, never grants a repository something its own config disables. A policy file that fails to parse keeps enforcing the last version that parsed, because failing open would turn a typo into a silent policy bypass and failing closed would turn one into an org-wide outage.

**The framework ships to the runner version-matched.** Each reusable workflow checks out `bamr87/githubai` at `${{ github.job_workflow_sha || github.sha }}` into `.githubai-framework/`, uses `load-config` from that checkout, and deletes the directory before Claude runs. `job_workflow_sha` is the commit of the *called* reusable workflow, so a consumer pinning `@v1` gets the loader and profiles of exactly `v1`; on this repo's own direct events the fallback `github.sha` makes every PR exercise its own loader changes. Stubs still reference workflows `@main` by default (fresh installs track latest) and the installer's `--ref` rewrites them for pinning — but there is no ref skew between a workflow and its action, ever.

## What guards the framework

Structure is tested, behavior is dogfooded: `tests/` proves every workflow parses, authenticates OAuth-first, declares permissions/timeouts/concurrency, that stubs point at real workflows with sufficient permissions, that installer labels match the taxonomy, and that the loader's merge semantics hold. The live workflows on this repo prove the rest — a change that breaks triage or review breaks it here first.

The relay is the exception that gets real behavioral tests, because it is the one component no repository dogfoods: `app/relay/test/` runs the actual modules against an in-memory store and a fake GitHub, covering routing parity, policy evaluation and its last-known-good fallback, signature and session handling, tenant isolation, and the whole webhook pipeline. `tests/test_app.py` guards the seams between the two languages — dispatch types against the dispatch workflow, org policy areas against the config schema, and the relay's YAML subset against PyYAML on this repo's own config files.
