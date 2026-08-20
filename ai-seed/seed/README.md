# seed/ — the plantable kernel

This directory is the product: the file set that turns any repository into a self-growing, AI-native project wired to Claude Code OAuth. `seed/kernel/` is stamped into targets by the planter (`tools/seed.py plant`); `seed/garden/` is the optional hub layer for orchestrating many planted repos. The design is documented in [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) and every mechanism's production provenance in [docs/PATTERNS.md](../docs/PATTERNS.md).

## Layout

| Path | Purpose |
|---|---|
| `VERSION` | Kernel version, embedded into planted files and checked by `seed.py check` |
| `kernel/CONCEPT.md` | Template for the target's genome: §1–§7 concept, §8 Evolution Log (tick clock) |
| `kernel/CLAUDE.md` | Template for the target's agent contract: guardrails, conventions, quarantine |
| `kernel/.seed/seed.yml` | Manifest template: identity, model tiers, cadence, gates, auth contract, guardrails |
| `kernel/.seed/pause.yml` | The repo-local kill switch |
| `kernel/.seed/telemetry/README.md` | The `seed-telemetry/v1` ledger contract |
| `kernel/.github/workflows/seed-germinate.yml` | One-time initial build from CONCEPT.md (manual two-key dispatch) |
| `kernel/.github/workflows/seed-grow.yml` | The increment loop (default OFF; plan → build → verify → draft PR) |
| `kernel/.github/workflows/seed-evolve.yml` | The issue-driven lane (default OFF; `seed:approved` → implementation draft PR) |
| `kernel/.github/workflows/seed-tend.yml` | The board lane (default OFF; review CI → repair → merge the provably green → dispatch approved issues). The only lane permitted to merge |
| `kernel/.github/workflows/seed-steward.yml` | The @claude mention handler |
| `kernel/.github/workflows/seed-verify.yml` | Structural CI gate (`seed.py check`) |
| `garden/garden.yml` | Roster template for a hub orchestrating many planted repos |
| `garden/garden-orchestrate.yml` | The daily conductor: stalest-first dispatch, stateless, default OFF |

Templates carry `__SEED_*__` placeholders; the planter substitutes them from the target's identity at plant time and can re-render later (`plant <dir> --update`). The planter also vendors itself into the target at `.seed/tools/seed.py`, so every planted repo can verify itself and plant onward — that is pollination.

## Planting a repo

```bash
# 1. Plant (into a fresh clone or an empty directory; idempotent, resumable)
python3 tools/seed.py plant ../my-project --repo owner/my-project

# 2. Fill in the concept
$EDITOR ../my-project/CONCEPT.md          # §1–§5 minimum — germination reads this

# 3. Commit, push, then configure GitHub (a human does this; the planter never will)
#    Secrets:   CLAUDE_CODE_OAUTH_TOKEN (from `claude setup-token`), optional
#               ANTHROPIC_API_KEY (fallback), SEED_PAT (fine-grained PAT:
#               contents+pull-requests+actions write — makes CI fire on seed PRs)
#    Variables: SEED_GROW_ENABLED=true when you are ready for autonomous growth;
#               SEED_EVOLVE_ENABLED=true to enable the issue lane
#    Labels:    seed:request, seed:approved, seed:hold — the issue lane's state
#               machine. seed-evolve.yml never fires without seed:approved existing.
#    Branch protection on the default branch: require PRs + the seed-verify check

# 4. Germinate (Actions → seed-germinate → Run workflow → retype the seed name)
# 5. Review the draft PR, merge, and let it grow — one tick, one increment, one PR
```

## Editing the kernel

The kernel is the framework's public contract — edit with the same care as a released API:

- ai-seed itself is planted with this kernel (`kernel.strict: true`), so `seed-verify.yml` here fails when the kernel and this repo's installed copies drift. After editing a kernel workflow, re-render the installation: `python3 tools/seed.py plant . --update`.
- Never weaken a guardrail (default-OFF gates, kill-switch honor, PR-only publish, workflows-unwritable, fail-loud, and the `policy.merge` hard stops). Tightening is welcome.
- Merging stays in `seed-tend.yml` alone. If a lane needs work merged, it hands the PR to the board — it does not grow its own merge step.
- Every mechanism must trace to a production precedent — extend [docs/PATTERNS.md](../docs/PATTERNS.md) in the same PR.
- Bump `VERSION` on any behavior change; planted repos record the kernel version they were stamped from.
