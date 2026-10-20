# SCHEMA — __SEED_NAME__

<!-- seed-kernel v__SEED_KERNEL_VERSION__ · planted __SEED_PLANTED__ from __SEED_PLANTED_FROM__ -->
<!-- Seeded by the AI-Seed planter (plant --schema); kernel-managed — `plant . --update` re-renders it. Edit the kernel template upstream, not this installed copy. -->

This is the Pyramid Schema for **__SEED_NAME__** (`__SEED_REPO__`).
A Pyramid Schema is a machine-readable directory contract: one entry per significant path, stating what lives there, who owns it, and how it fits the whole.
Lint with `schema_lint.py` from [bamr87/SCHEMA](https://github.com/bamr87/SCHEMA).

## Root

| Path | Kind | Owner | Purpose |
|---|---|---|---|
| `README.md` | file | user | Front door — visitors and bots start here |
| `CONCEPT.md` | file | user | Genome: vision, capabilities, architecture, tick log (§8) |
| `CLAUDE.md` | file | user | Agent guidance: stack, commands, guardrails |
| `SCHEMA.md` | file | kernel | This file — directory contract (Pyramid Schema); refreshed by `plant --update` |
| `.seed/` | dir | seed | AI-Seed kernel artefacts: manifest, tools, telemetry, kill-switch |
| `.github/` | dir | platform | CI/CD workflows and GitHub-specific config |

## .seed/

| Path | Kind | Owner | Purpose |
|---|---|---|---|
| `.seed/seed.yml` | file | user | Manifest: identity, policy, guardrails, auth (schema: seed-manifest/v1) |
| `.seed/pause.yml` | file | user | Kill-switch: `paused: true` halts all loops |
| `.seed/tools/seed.py` | file | kernel | Vendored planter/checker — parity-checked in CI |
| `.seed/telemetry/evolution.jsonl` | file | kernel | Append-only ledger of tick machine records |
| `.seed/telemetry/README.md` | file | kernel | Telemetry schema reference |

## .github/workflows/

| Path | Kind | Owner | Purpose |
|---|---|---|---|
| `.github/workflows/seed-germinate.yml` | file | kernel | One-shot germination pass (human-triggered) |
| `.github/workflows/seed-grow.yml` | file | kernel | Scheduled grow loop (plan→build→verify) |
| `.github/workflows/seed-evolve.yml` | file | kernel | Issue lane: `seed:approved` label → implementation draft PR |
| `.github/workflows/seed-steward.yml` | file | kernel | @claude mention handler |
| `.github/workflows/seed-verify.yml` | file | kernel | Structural gate: schema, parity, tests (CI) |

## Contracts

Machine hand-off contracts whose schema must not change without a version bump:

| Contract | Schema | Append-only? |
|---|---|---|
| `.seed/telemetry/evolution.jsonl` | `seed-telemetry/v1` (JSONL) | Yes |
| `.seed/seed.yml` | `seed-manifest/v1` (YAML) | No — human-editable |
