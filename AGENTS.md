# AGENTS.md

Canonical agent context for this repository lives in [CLAUDE.md](CLAUDE.md) — read that. It covers what the repo is, the commands to run, the hard conventions (OAuth-first auth, public API surface, untrusted-input rule, markdown style), and the sync duties between profiles, installer, templates, and docs.

## Governance

Read [`docs/constitution.md`](docs/constitution.md) before changing anything: it is the highest-precedence rule set here and wins over this file when they disagree. It changes only through a numbered record in [`docs/amendments/`](docs/amendments/), ratified by the maintainer merging the PR; agents propose, never merge. Every user-facing feature has a stable id in [`features/features.yml`](features/features.yml) with `status`, location and the PRD requirement ids it serves; the PRD's "Feature catalog" block is generated from it (`python3 <bamr87/bamr87>/tools/governance_lint.py prd-sync . --write`; check with `… check .`). Never hand-edit that block or `CHANGELOG.md`.
