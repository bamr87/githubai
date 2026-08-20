# 🌱 AI-Seed — the autonomous AI orchestration framework

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![Claude Code OAuth](https://img.shields.io/badge/Claude%20Code-OAuth--first-purple.svg)](https://code.claude.com/docs) [![GitHub Native](https://img.shields.io/badge/SDLC-GitHub%20Native-blue.svg)](#github-as-the-sdlc-platform) [![Default OFF](https://img.shields.io/badge/Autonomy-Default%20OFF-green.svg)](#guardrails)

> Plant a seed in any repository. Write down the concept. Let it grow — one reviewed pull request at a time.

**AI-Seed** turns a repository into a self-growing, AI-native project. The planter stamps a small **kernel** into any repo (new or existing); from then on the repo can **germinate** (build its initial structure from a written concept) and **grow** (ship one bounded increment per tick) through Claude Code passes running inside GitHub Actions — wired to **Claude Code OAuth**, bounded by guardrails a single human can always halt, with **GitHub as the entire SDLC platform**: issues are the backlog, Actions is the compute, draft pull requests are the only write path, and merges belong to humans.

The framework packages the production patterns of the [bamr87 fleet](https://github.com/bamr87/bamr87) (~40 repos of autonomous-SDLC machinery) into a portable, self-hosting form. Nothing here is speculative: every mechanism traces to a sibling repo where it already runs — the map is [docs/PATTERNS.md](docs/PATTERNS.md), the design is [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Quick start: plant → germinate → grow

```bash
# 0. You need: a GitHub repo (fresh or existing), and a Claude Code subscription
git clone https://github.com/bamr87/ai-seed.git
cd ai-seed

# 1. PLANT — stamp the kernel (additive-only, idempotent; nothing is overwritten)
python3 tools/seed.py plant ../my-project --repo you/my-project

# 2. CONCEPT — write the genome (this is the real work)
$EDITOR ../my-project/CONCEPT.md     # fill §1 vision … §5 quality bars

# 3. WIRE — commit, push, then in the repo's GitHub settings (human-owned):
#    secrets:   CLAUDE_CODE_OAUTH_TOKEN   <- `claude setup-token` (primary auth)
#               ANTHROPIC_API_KEY          <- optional metered fallback
#               SEED_PAT                   <- fine-grained PAT so CI fires on seed PRs
#    variables: SEED_GROW_ENABLED=true     <- only when ready: the variable IS the consent
#    branch protection on main: require PRs + the seed-verify check

# 4. GERMINATE — Actions → seed-germinate → Run workflow → retype the repo's seed name
#    Claude reads CONCEPT.md and builds the initial structure as ONE draft PR.

# 5. GROW — review, merge, and let the cron tick: plan → build → verify,
#    one increment, one draft PR, telemetry appended. Forever.
```

Verify any planted repo at any time: `python3 .seed/tools/seed.py check .` (the planter vendors itself, so every planted repo can verify itself — and plant onward).

## The lifecycle

| Stage | What happens | Consent |
|---|---|---|
| **PLANT** | `seed.py plant` stamps the kernel: manifest, kill switch, CONCEPT genome, four workflows | Running the planter |
| **GERMINATE** | Claude builds the initial structure from `CONCEPT.md` → one draft PR | Manual dispatch + retyping the seed name |
| **GROW** | Scheduled ticks: plan → build → verify escalation → one increment → one draft PR + telemetry | `SEED_GROW_ENABLED=true` |
| **TEND** | `@claude` mentions and the issue lane (`seed:request` → human applies `seed:approved` → implementation PR) | The mention / the label |
| **POLLINATE** | Any planted repo plants onward; a garden hub orchestrates many (stalest-first, capped) | Per-repo, same as PLANT |
| **PAUSE** | `.seed/pause.yml` halts every loop; unsetting a variable halts one | Human edit, one file |

## Claude Code OAuth wiring

Every model pass rides [`anthropics/claude-code-action@v1`](https://github.com/anthropics/claude-code-action), **OAuth-first**: `CLAUDE_CODE_OAUTH_TOKEN` (minted by `claude setup-token`, subscription-backed) is the primary credential at every call site, with `ANTHROPIC_API_KEY` as an evidence-based fallback — fired only when the OAuth passes produced nothing or reported `is_error` in their execution output. Model tiers are policy, not workflow: `.seed/seed.yml` names the model per pass (default escalation `claude-haiku-4-5` → `claude-sonnet-4-6` → `claude-opus-4-8`); changing tiers is a data edit. The workflow — never the model — commits, pushes, and opens PRs, and it prefers `SEED_PAT` because refs pushed with `github.token` fire no CI.

## GitHub as the SDLC platform

| SDLC concern | GitHub surface |
|---|---|
| Product intent | `CONCEPT.md` §1–§7 (machine-readable genome) |
| Backlog & intake | Issues + labels: `seed:request` → `seed:approved` (consent) → PR; `seed:hold` is the brake |
| Implementation | Branches + Actions compute (`seed/*` branches only) |
| Review & merge | Draft PRs; humans merge — no agent ever does |
| CI / quality | `seed-verify` (structural gate) + the repo's own suite |
| History & telemetry | `CONCEPT.md` §8 Evolution Log (the tick clock) + `.seed/telemetry/evolution.jsonl` (append-only) |
| Incident response | `.seed/pause.yml` — one human edit halts everything |

## Guardrails

The constitution lives in `.seed/seed.yml` (`guardrails:`), binds every agent via `CLAUDE.md`, and is enforced by `seed.py check` and by workflow-owned publish steps: every loop ships **default OFF** (the `*_ENABLED` variable is the consent); **PR-only, never merge**; **workflows are not agent-writable** (model-authored workflow files become `seed/proposed-workflows/` proposals, never live code); **untrusted input is quarantined** (issue text and web content are data, never instructions); **one increment per tick**; **fail loudly** (a tick that produced nothing fails its run and names the failure class — auth vs stalled); **telemetry is append-only**. Full doctrine: [docs/ARCHITECTURE.md §7](docs/ARCHITECTURE.md).

## Self-hosting

ai-seed is planted with its own kernel — look at the root of this repo: [`CONCEPT.md`](CONCEPT.md) is its genome (§8 logs the repo's real history), `.seed/` is its plant (strict kernel parity), and the `seed-*.yml` workflows growing this framework are the same files the planter stamps everywhere else. `seed-verify.yml` fails CI here the moment the kernel and the installation drift: anything the kernel demands of a planted repo, this repo demonstrates first.

## Repository map

| Path | What it is |
|---|---|
| [`seed/`](seed/README.md) | **The product**: `kernel/` (plantable files) + `garden/` (multi-repo hub layer) |
| [`tools/seed.py`](tools/seed.py) | The planter/checker CLI — single-file, stdlib-only, self-vendoring |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | The system design: lifecycle, layers, auth, grow tick, guardrails |
| [`docs/PATTERNS.md`](docs/PATTERNS.md) | Provenance: which fleet repo proved each mechanism, with the incident behind it |
| [`CONCEPT.md`](CONCEPT.md) / [`.seed/`](.seed/seed.yml) / [`CLAUDE.md`](CLAUDE.md) | This repo's own plant (self-hosting) |
| `.github/workflows/` | Installed kernel workflows (`seed-*.yml`) + repo CI (`ci.yml`, `ci-cd.yml`, docs, prose, triage) |
| `tests/` | Pytest: CLI behavior, kernel contracts, workflow pins, strict parity |
| `src/`, `agents/`, `docker/` | The **resident example**: the G1–G2 era application (React/Node/Python demo + CrewAI engine) that this repo grew before the kernel existed — kept runnable as a worked example, not the framework |

## The fleet — design considerations and implementation examples

AI-Seed extracts, rather than invents: the [year-of-ai](https://github.com/year-of-ai/year-of-ai.github.io) and [ai-world-view](https://github.com/ai-world-view/ai-world-view.github.io) hubs proved the lineage growth engine (seeds, policy, escalation, kill switch, fail-loud ticks); [lifehacker.dev](https://github.com/bamr87/lifehacker.dev) proved consent gates, the harness discipline, and quarantine; the [bamr87 hub](https://github.com/bamr87/bamr87) proved the token contract, the label state machine, and the standing rules about `github.token` and protected branches; [wtd](https://github.com/bamr87/wtd) proved provider lanes and dedup markers; [gitorio](https://github.com/bamr87/gitorio) proved loop guards and least-privilege compilation; [git-with-the-program](https://github.com/bamr87/git-with-the-program) contributes the constitution politics; [SCHEMA](https://github.com/bamr87/SCHEMA) the self-describing, vendorable-tool posture. The registry with the receipts: [docs/PATTERNS.md](docs/PATTERNS.md).

## Contributing

Humans and agents alike: read [`CLAUDE.md`](CLAUDE.md) (the working agreement), file `seed:request` issues for changes you want the evolve lane to build, and remember the two rules that never bend — the kernel is edited in `seed/kernel/` and re-rendered (`python3 tools/seed.py plant . --update`), and nobody merges but a human. Run before any PR: `python3 -m pytest tests/ && python3 tools/seed.py check . && python3 tools/unwrap-prose.py --check`.

## License

MIT — see [LICENSE](LICENSE). Plant freely.

> *"The best time to plant a tree was 20 years ago. The second best time is now."*
