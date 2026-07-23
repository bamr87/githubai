# Architecture

GitHubAI's architecture is the deliberate absence of one: no servers, no database, no queue — GitHub Actions is the runtime, GitHub itself is the UI and state store, and Claude Code (via `anthropics/claude-code-action@v1`) is the only compute. This page records the load-bearing decisions and why they hold.

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

**The app is a router, not a runtime.** App mode (see [app/README.md](../app/README.md)) converts webhooks to `repository_dispatch` into the same workflows. Trust stays per-repo (each repo's own OAuth secret); the relay holds no state and can be replaced without touching the framework. This is the intended growth path to the hosted GitHub App without ever moving execution out of the consumer's CI.

**Framework refs at `@main`, pinnable at install.** Stubs and internal action references default to `@main` (fresh installs track latest); the installer's `--ref` rewrites every reference for pinning. Internal `uses:` between a reusable workflow and `load-config` intentionally match refs only per-release — the tradeoff (a PR here doesn't exercise its own loader changes in-workflow) is covered by the pytest suite instead.

## What guards the framework

Structure is tested, behavior is dogfooded: `tests/` proves every workflow parses, authenticates OAuth-first, declares permissions/timeouts/concurrency, that stubs point at real workflows with sufficient permissions, that installer labels match the taxonomy, and that the loader's merge semantics hold. The live workflows on this repo prove the rest — a change that breaks triage or review breaks it here first.
