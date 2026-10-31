# Proposal — Seed recipes: mining feature progressions into replayable build instructions

- **Status:** proposed (design only — no code, no kernel change)
- **Date:** 2026-10-30
- **Proposed by:** agent (Grok Bot) for Amr (bamr87)
- **Affects:** ai-seed `CONCEPT.md` §2 capabilities and §3 architecture intent (proposed edit in §9 below — `CONCEPT.md` is user-owned, so a human applies it); `docs/ARCHITECTURE.md` §6 (grow tick PLAN pass input) and §12 (roadmap); `docs/PATTERNS.md` (a precedent row is required before anything lands in the kernel); githubai `docs/PRD.md` §5 M4 "fleet intelligence" (`FR-NEW` placeholder); `features/features.yml` (`AISEED-NEW` placeholder ids, numbered at merge — the catalog is still the `TODO-001` stub)
- **Counterpart:** bamr87/gitorio `packages/git-with-the-program/docs/proposals/rl-drift-learning.md` — see [Counterbalance contract](#counterbalance-contract-shared-section--identical-in-both-proposals)
- **Related:** gitorio #160 (Harness Studio on Jev), hub bamr87/bamr87#480 (prior art first), #478 (architecture research harness)

## 0. Needs assessment (hub §10.8 "Prior art first", proposed in bamr87/bamr87#480)

**Problem.** Germinate builds from a one-page `CONCEPT.md`, and grow picks "exactly ONE increment" from the concept plus repo state (ARCHITECTURE §6). Neither has a memory of *how similar features were actually built* — in this repo or across the fleet — or of the bugs that followed. Every grow pass rediscovers the path, and repeats the pitfalls.

**Need.** A structured, evidence-backed description of the intended path for a feature — what has to exist first, which steps in which order, which files and tests, what went wrong last time, and how to tell it is done — mined from real history rather than invented, and *checked by replay* before anyone trusts it.

**Who benefits.** Grow/germinate passes (better plans, fewer repair attempts), reviewers (a PR can be read against its recipe), and GWTP (an explicit "expected path" to test its drift scores against, and vice versa).

**Non-need.** Recipes do not replace `CONCEPT.md` (the genome stays the intent of record), and they are not executable codemods. They never widen what a pass may write.

## 1. Mining feature progressions

**Unit of analysis: a feature, identified by its FEAT-style id** (the `features/v1` catalog ids, e.g. `GITORIO-005`, `HUB-039`, or this repo's `AISEED-NNN` once minted). A *progression* is the ordered set of changes that introduced and then evolved that feature.

**Linking ids to changes, in decreasing confidence:**

1. `features.yml` `provenance: {introduced_in, pr, commit, issue}` — explicit, human-authored.
2. Id mentions in PR titles/bodies, commit messages, branch names (`feature/GITORIO-005-…`), and `changelog.d/` fragments (Jev).
3. Issue links: a PR that `Closes #N` where issue N carries the id or a `feature`-template field.
4. Path affinity: changes touching the feature's `link` / `docs` / `tests` paths, weighted by code-maat-style temporal coupling.
5. Unlinked: reported, never guessed (honesty rule 6).

Each link records its tier so a recipe's provenance says *how* a step was attributed.

**Bug-fix chains.** For each change in a progression, find later changes that fixed it: `fix:` Conventional Commit types, `bug`-labelled issues/PRs, reverts, and SZZ blame from the fix's deleted/modified lines back to the introducing change (refactor/whitespace filters per PySZZ). The chain `introducing change → symptom (issue/CI failure) → fix` is stored as a `pitfall` candidate.

**Phases.** Progressions are cut with the shared `phase-map/v1` (produced by GWTP from releases, tags, epics, epochs and time windows), so "step 3 happened in the v0.2 phase" means the same thing on both sides.

**Implementation shape (proposed).** An offline miner, `tools/recipe_mine.py`, outside the kernel (so `tools/seed.py` stays single-file stdlib and planted repos vendor nothing new). It may use PyDriller (see prior art) and `gh api` with read-only tokens. Output: `progressions/<FEAT-id>.json` in a recipes store (§5).

## 2. Inferring trends

From many progressions (one repo or the whole fleet via the hub's `_data/features_index.yml`), compute deterministic, explainable statistics — no learned embeddings in v1:

- **Canonical ordering.** For each feature *kind* (surface + tags, e.g. `cli`, `infra/workflow`, `ui/route`), the most common partial order of step types (schema → code → tests → docs → workflow wiring) via pairwise precedence counts; ties broken lexically for determinism.
- **Prerequisite edges.** "Feature kind X's first step depends on Y existing" when ≥ 80% of progressions show Y earlier and the first step imports/references it.
- **Co-change sets.** Files that change together with ≥ 0.5 coupling (code-maat metric) become *files touched* hints.
- **Pitfall frequency.** Bug-fix chains clustered by touched path pattern and fix type; a pitfall needs ≥ 2 independent occurrences (distinct phases) to be promoted from candidate.
- **Velocity and churn.** Steps per phase and rework ratio (lines rewritten within 30 days) — reported, never optimised.
- **Drift-adjacent signals.** Where GWTP's ledger has verdicts for the same changes, the recipe records which steps historically drew drift verdicts; this is read-only input and becomes a `known_pitfall` only after replay confirms it (§4).

Trends are labelled with sample size and phase span; anything with n < 3 is shown as an anecdote, not a trend.

## 3. The seed recipe schema (`seed-recipe/v1`)

YAML on disk, JSON Schema in the hub (see contract). Illustrative:

```yaml
schema: seed-recipe/v1
id: RCP-NEW                      # Jev placeholder, numbered at merge
version: 1
feature: GITORIO-005             # FEAT id this recipe builds (or AISEED-NEW for a new feature)
prd: [FR-NEW]                    # PRD requirement ids it satisfies
kind: infra/package-import
intent: >-
  One sentence of what the user can do when this exists, quoted from the PRD/feature
  description, never paraphrased by a model.
prerequisites:
  - feature: GITORIO-002         # must already exist
  - file: package.json
  - tool: { name: node, version: ">=22" }
steps:                           # ordered; each step is one reviewable increment
  - id: S1
    title: Import history under packages/<name>/ with full history
    files: ["packages/<name>/**"]
    tests: []
    checks: ["git log --follow packages/<name>/README.md shows upstream commits"]
    evidence: [{ change: { repo: bamr87/gitorio, pr: 136 }, link_tier: 1 }]
  - id: S2
    title: Rewire root CI to run the package's own gates
    depends_on: [S1]
    files: [".github/workflows/ci.yml"]
    tests: ["packages/<name>/tests/**"]
files_touched:                   # union, with coupling weights
  - { path: ".github/workflows/ci.yml", weight: 0.8 }
tests:
  fail_to_pass: ["tests/test_packages.py::test_package_gates_run"]
  pass_to_pass: ["tests/**"]
known_pitfalls:
  - id: PIT-1
    description: Root docs index picked up package docs and failed docs_index --check
    pattern: "docs/README.md index span includes packages/**"
    chain: [{ introduced: <sha>, symptom: "<CI run url>", fixed: <sha> }]
    occurrences: 2
acceptance_criteria:             # testable, each mapped to a check or test
  - "Package gates run in CI and are green"
  - "Hub references to the old repo URL are updated"
provenance:
  mined_from: [{ repo: bamr87/gitorio, range: "<from_sha>..<to_sha>", phase_ids: [P7] }]
  miner: { tool: recipe_mine.py, version: "0.1.0", sha256: "<hash>" }
  inputs_hash: "<sha256 of canonical inputs>"
  replay: { status: passed|failed|not-run, run: "<url>", similarity: 0.82 }
  generated_at: 2026-10-30
  cost: "API-equivalent (estimate): $0.00"
```

Rules: every step cites at least one evidence change or is marked `synthesised: true` (and synthesised steps cannot be the only step); `acceptance_criteria` must each map to a `tests` entry or a `checks` command; no author identities anywhere.

## 4. Validation by replay

A recipe is trusted only after it reproduces history (the SWE-bench / Defects4J method):

1. **Fix the start.** Check out the parent of the progression's first change into a sandbox branch `seed/replay-<recipe>-<run_id>` in a scratch clone (or a fork) — never the default branch, never pushed to `main`.
2. **Hide the future.** The replaying pass sees the recipe and the tree at start only; later commits, the real PR diffs and the recipe's own `evidence` diffs are withheld (they would leak the answer).
3. **Execute.** Run a grow-style PLAN → BUILD → VERIFY sequence, one recipe step per pass, with the kernel's normal guardrails (no workflow writes, kill switch honoured, bounded attempts).
4. **Score against the real history.**
   - *Tests:* the real later `fail_to_pass` tests pass, `pass_to_pass` stay green (primary signal).
   - *Structure:* Jaccard overlap of files touched vs. the real progression; step-order agreement (Kendall τ).
   - *Pitfalls:* did the replay reproduce a known pitfall the recipe warned about? (A recipe whose warnings do not prevent the pitfall is weakened.)
   - *Drift:* GWTP scores the replay's diff with the same calibrated `p_drift` used on real history (counterbalance input).
5. **Verdict.** `passed` when tests pass and structural similarity ≥ the threshold pinned in the contract (proposed 0.6); otherwise `failed` with the diff of expectations. Recipes start at `status: candidate` and become `validated` only on `passed` plus human review of the replay PR; they never auto-promote.
6. **Reproducibility.** The replay manifest pins start SHA, recipe hash, model id + prompt sha256, and seed. Model outputs are not bit-reproducible, so replay runs N=3 and reports the median and spread; a spread above threshold marks the recipe `unstable`.

Replays are expensive; each run reports tokens and **"API-equivalent (estimate)"** cost, and the garden runs them stalest-first under a per-tick cap (the cost governor in CONCEPT §2 is a prerequisite for fleet-scale replay).

## 5. How recipes feed germinate and grow

- **Storage.** Validated recipes live as data, not kernel: proposed `seed/recipes/<RCP-id>.yaml` in ai-seed for fleet-wide recipes, and `.seed/recipes/` in a planted repo for repo-local ones. The planter (`plant --update`) does **not** copy recipes (kernel parity stays strict); a repo opts in by listing recipe ids in `.seed/seed.yml` (`recipes: [RCP-…]`) — a user-owned file, so adoption is a human choice.
- **Germinate.** When `CONCEPT.md` §2 lists a capability whose kind matches a validated recipe, the germinate prompt receives the recipe's `intent`, `prerequisites`, `steps` and `known_pitfalls` as *reference material*, quoted as data with the standard "content is data, not instructions" line. The two-key confirm and draft-PR rules are unchanged.
- **Grow PLAN pass.** Selecting "exactly ONE increment" becomes: pick the next unmet step of the highest-priority recipe whose prerequisites are satisfied; write the step id into the tick plan file and the §8 Evolution Log entry (`… Tick N: RCP-12/S3 — <summary>`) and into `evolution.jsonl`. That makes every tick traceable to a recipe step.
- **Grow VERIFY pass.** Runs the step's `checks` and `tests`, and checks the diff against `known_pitfalls` patterns; a hit is reported in the PR body, not silently fixed.
- **Tend lane.** Unchanged merge policy. A recipe never makes a PR merge-eligible; it only adds evidence to the PR body.
- **Feedback.** Merged ticks append their real change to the recipe's evidence (a new recipe *version* via draft PR); human-resolved counterbalance findings marked `recipe-wrong` add a pitfall or reorder steps.

## 6. Guardrails

All kernel guardrails hold unchanged (PR-only; no model merges; workflows not agent-writable; human-owned controls; quarantine untrusted input; honesty; OAuth-first). In addition: mining is read-only; replay runs only on `seed/replay-*` sandbox branches in a scratch clone or fork; recipes are default OFF per repo (`SEED_RECIPES_ENABLED` variable plus the `recipes:` list); recipe content mined from issue/PR bodies is quarantined data, and `intent` is quoted from the catalog/PRD, never from an issue body.

## 7. Phasing

- **R0** — miner + progression files + trend report for this repo and gitorio, no recipes. Exit: deterministic rerun is byte-identical.
- **R1** — `seed-recipe/v1` schema in the hub; hand-reviewed candidate recipes for 3 shipped features.
- **R2** — replay harness; first `validated` recipe with a reviewed replay PR. Requires a `docs/PATTERNS.md` precedent row before kernel use.
- **R3** — PLAN-pass integration behind `SEED_RECIPES_ENABLED`; counterbalance comparator with GWTP (after the hub contract lands).
## 8. Prior-art survey and build-vs-adopt (hub §10.8, proposed in bamr87/bamr87#480)

Surveyed from published documentation and papers; versions and licences should be re-checked at implementation time. "Adopt" means use the tool or method as is; "adopt method" means reimplement a published algorithm inside our constraints (GWTP pins its runtime dependencies in ADR-0006; ai-seed tooling is single-file stdlib Python); "build" means nothing fits.

| Prior art | What it does | Fit | Call |
| --- | --- | --- | --- |
| [PyDriller](https://github.com/ishepard/pydriller) | Python git-mining: commits, modifications, metrics, per-file history | Good for AI seed's offline miner; GWTP is TypeScript and already has `src/distill/miner.ts` | **AI seed: adopt** (dev-time dependency of the recipe miner, not the kernel). **GWTP: build** (keep the existing miner; dependency pin) |
| [GitHub Linguist](https://github.com/github-linguist/linguist) | Language / generated / vendored file classification | Needed to exclude vendored and generated files from labels and recipes | **Adopt its data, not the gem**: read the forge's language stats via the API and reuse Linguist's `vendor.yml`/`generated` heuristics as a pinned list |
| [CodeScene](https://codescene.com/) / [code-maat](https://github.com/adamtornhill/code-maat) | Behavioural code analysis: hotspots, temporal coupling, change coupling | Temporal coupling is a useful recipe feature ("these files change together") | **Adopt method** (code-maat's coupling metric, open source). CodeScene itself is SaaS and identity-centric (author analyses) — **not adopted** |
| SZZ ([Śliwerski, Zimmermann, Zeller 2005](https://doi.org/10.1145/1083142.1083147)); [PySZZ](https://github.com/grosa1/pyszz), SZZ Unleashed | Trace bug-fix commits back to bug-introducing commits via blame | Core of both the reward labels (GWTP) and pitfall mining (AI seed) | **Adopt method** (B-SZZ + refactoring/whitespace filters per PySZZ's variants); use PySZZ as the reference oracle in tests |
| Architecture erosion / drift research: Perry & Wolf 1992; reflexion models ([Murphy, Notkin, Sullivan 1995](https://doi.org/10.1145/222124.222136)); [ArchUnit](https://www.archunit.org/); dependency-cruiser | Compare an intended architecture model to the extracted one | GWTP's `.program/` + nexus *is* a reflexion model; ArchUnit-style rules are its deterministic rung | **Already adopted in spirit**; cite in spec 05. No new tool |
| RLHF / reward modelling ([Christiano et al. 2017](https://arxiv.org/abs/1706.03741)); Bradley–Terry preference models | Learn a reward from human comparisons | Useful only for pairwise human labels on findings | **Adopt method, small**: Bradley–Terry over resolved findings, offline. No policy optimisation (PPO) — ruled out (§1) |
| Contextual bandits + off-policy evaluation ([Li et al. 2010](https://arxiv.org/abs/1003.0146); [Vowpal Wabbit](https://vowpalwabbit.org/); doubly-robust OPE) | Choose an arm per context; evaluate policies from logs | Exactly the knob-selection problem | **Adopt method** (grid arms + replay + bootstrap bound). VW not adopted (native dependency, overkill for a few dozen arms) |
| Probability calibration (Platt scaling; isotonic regression; [scikit-learn calibration](https://scikit-learn.org/stable/modules/calibration.html)) | Map scores to calibrated probabilities; reliability diagrams, ECE | Core of A1 | **Adopt method** (isotonic/PAV is ~40 lines, pure, deterministic). scikit-learn used only as a test oracle |
| [OpenRewrite](https://docs.openrewrite.org/) recipes | Declarative, composable, testable code-transformation recipes (YAML + visitors, before/after tests) | Closest prior art to *seed recipes*: declarative steps + preconditions + tests. But it transforms code deterministically; seed recipes describe intent for an agent | **Adopt shape, not engine**: borrow `preconditions`, composition, and before/after test conventions into `seed-recipe/v1`. Emit an OpenRewrite recipe reference when a step is a mechanical migration |
| [Semgrep](https://semgrep.dev/) / [Comby](https://comby.dev/) / codemods (jscodeshift) | Pattern match / rewrite | Good for recipe *checks* ("this pitfall pattern must not appear") | **Adopt optionally** as an acceptance-check runner in planted repos that already use it; not a kernel dependency |
| [SWE-bench](https://www.swebench.com/) / Defects4J / [BugsInPy](https://github.com/soarsmu/BugsInPy) | Benchmarks that replay real fixes from history in a sandbox and score against real tests | Exactly the *validation-by-replay* method for recipes | **Adopt method**: checkout parent SHA, apply agent work on a sandbox branch, run the real later tests (fail-to-pass / pass-to-pass) |
| [GrimoireLab / Perceval](https://chaoss.github.io/grimoirelab/) | Collect forge data (issues, PRs, reviews) at scale | Heavier than needed; identity-centric dashboards | **Not adopted**; `gh api` through each repo's adapter suffices |
| Conventional Commits / [git-cliff](https://git-cliff.org/) / release-please | Commit type parsing; changelog from history | Both repos already use Conventional Commits; `fix:` types seed bug-fix chains | **Adopt** the convention as a labelling input (already in force) |
| [TokenEconomizer](https://github.com/microsoft/TokenEconomizer) (Apache-2.0) | Coding-agent plugin: micro-skills, tool pruning, failure-loop guard; claims 18–31% lower cost on SWE-Bench | Agent passes that run again and again in the same repo | **Adopt** as-is, opt-in, pinned, shadow first; see §8.1 |
| Jev (hub numbering + fragments) | `HUB-NEW`/`FR-NEW` placeholders, `features.d/` and `changelog.d/` fragments numbered at merge | The fleet's own standard for ids in proposals | **Adopt** for every new id in this proposal |

**Net decision.** Build a small, auditable core in each repo's existing language (TypeScript in GWTP, stdlib Python in ai-seed) that reimplements published methods (SZZ, isotonic calibration, bandit replay, SWE-bench-style replay); adopt PyDriller as AI seed's offline mining library; adopt OpenRewrite's recipe *shape*; adopt Jev for numbering. No hosted service, no online RL framework.

### 8.1 TokenEconomizer (microsoft/TokenEconomizer): token-cost control for the agent loops

Added 2026-10-30 at Amr's request. Facts below were read from the repository README and LICENSE at commit `e428fc9` and the GitHub API on that date. Re-check them before implementation, because the project is about 2.5 weeks old.

**What it is.** [microsoft/TokenEconomizer](https://github.com/microsoft/TokenEconomizer) ("Experience-Driven Black-Box Cost Control for Coding Agents"; UC Berkeley + Microsoft Research; paper [arXiv 2610.22732](https://arxiv.org/abs/2610.22732)) is a **plugin, not a library**. It works with Claude Code, Codex, GitHub Copilot CLI and Pi, and opencode support is experimental. It leaves the agent unchanged and learns from earlier sessions in the same repository. It has three switchable mechanisms:
- **Micro-skills** (off by default): learns repo facts such as "run `python -m pytest`" from repeated failures and from a proposer model call every *k* = 3 sessions. It injects a fact at session start once 3 sessions confirm it and drops the fact when later sessions contradict it. The `microskills=envfacts` mode learns from failures only and makes no model calls.
- **Tool pruning** (on by default): leaves out tools that went unused (*p* = 10 prompts over at least *m* = 2 sessions, or *s* = 5 sessions). It does this through the agent's own settings, which for Claude Code is `.claude/settings.local.json`, kept out of git via `.git/info/exclude`. The `toolprune=propose` mode only proposes, and `toolprune restore` undoes it.
- **Loop guard** (on by default): when a turn repeats failures, a judge model (confidence *c* ≥ 0.7) adds at most *r* = 1 redirect note. It **never stops a turn itself**; it only tells the operator.
- Interfaces: slash commands and the `~/.tokeneconomizer/bin/te` CLI (`status`, `config`, `microskills`, `toolprune`, `doctor`). Settings use `TE_*` env vars, and `TE_DISABLE=1` turns the plugin off. State stays local in `~/.tokeneconomizer`. It needs **no API key of its own** and never handles credentials. Its own model calls go through the host agent, and they are counted in its cost reports, which use cache-aware pricing.
- Reported result (the authors' own measurement on SWE-Bench, 5 agent–model combinations): **18.4–30.9% lower mean cost**, cheaper in 30/30 repo × combination cells, Pass@1 up in 4/5. On new-repo security benchmarks it saved 6–20%. Savings are largest for **repeated sessions in the same repository**.
- Maturity: Apache-2.0. Created 2026-10-12 (MDT) and pushed daily, with about 2.1k stars. Agent support is pinned to narrow version windows (for example Claude Code 2.1.300–2.1.310, and "older versions not supported"). Research-grade, with no release tags.

**Needs assessment.** Both designs add model-calling loops: per-commit triage, epoch synthesis, recipe drafting, replay judging, and the `tend` / germinate / grow / steward passes that run Claude Code in Actions. The research review (risk 6, "cost creep") and the open `ai-seed/CONCEPT.md §2` item "Cost governor" both say cost control must exist before any scheduled run. That need has two parts:
1. **Pacing / budgets**: hard caps per run and per period (`--max-budget-usd`, the manifest budget block, `gate.budget`). TokenEconomizer does **not** do this.
2. **Waste reduction inside a loop**: re-learning the repo, unused tool definitions, and stuck loops. This is what TokenEconomizer does, and building our own would duplicate a published, measured tool.

**Build-vs-adopt decision: ADOPT as-is, opt-in, pinned, in shadow mode first. Do not build our own token-economy layer. Keep budget enforcement as our own (deterministic) build.**

| Concern | Call |
| --- | --- |
| Waste reduction for Claude Code agent passes (tool pruning, loop guard) | **Adopt** TokenEconomizer, pinned to a commit SHA and installed from a clone on the runner. Enabled only by a repo variable (default OFF), the same consent model as the learner / kill switch |
| Micro-skills | **Adopt in `envfacts` mode only** (no extra model calls) until a measurement shows the proposer pays back |
| Budget caps and pacing (per run, per week, per repo) | **Build** (already planned): deterministic gate against the telemetry ledger. TokenEconomizer's `status` cost report is an *input* to that ledger, never the enforcer |
| Cache-aware cost accounting ("count cost as it is billed", including the plugin's own calls) | **Adopt method** in our cost reports. Keep labelling it "API-equivalent (estimate)" |
| Deterministic rungs (compiled erosion rules, SZZ, calibration arithmetic) | **Not applicable**: these already cost $0 in model tokens. No plugin there |

**Guardrails for the integration.**
- **Measurement hygiene.** TokenEconomizer changes agent behaviour: it injects facts, removes tools and adds redirects. Every run record must therefore carry `te: {enabled, sha, mechanisms}` in its input manifest. Learned calibrations, replay scores and A/B comparisons must never mix runs with TE on and TE off unless that field is a recorded covariate.
- **Reproducibility.** Learned state (`~/.tokeneconomizer`) is per machine. On ephemeral CI runners it either starts cold every run, which loses most of the benefit, or is restored from an Actions cache keyed by repo + agent + TE SHA. A cached state is an input: hash it into the manifest, and never commit it.
- **No new write path.** Tool pruning writes only `.claude/settings.local.json`, which TE excludes from git. A run's diff guard must still fail if any `.claude/`, `.codex/` or `.github/copilot/` settings file shows up in a pushed diff.
- **Human stays in charge.** The loop guard only redirects and reports. It is not a substitute for our kill switch, repair budgets or `--max-budget-usd`, which remain the hard stops.
- **Version drift.** The narrow supported-version window means a Claude Code bump on the runner can silently put TE outside support. Run `te doctor` as a pre-step and treat "unsupported" as "TE disabled for this run" (fail open, as TE itself does), and log it.
- **Secrets.** TE needs no token. It must not be given one, and it adds no secret to any workflow.

**License notes.** Apache-2.0, which is compatible with both repos. We **do not vendor** it. It is installed at run time from a pinned SHA, so no NOTICE obligation arises in our tree. If code is ever copied, for example the cache-pricing logic, keep its license header and add a NOTICE entry. The arXiv numbers are the authors' own claims, so cite them as such until we reproduce them.

**Integration points in AI seed.**
- **germinate / grow / steward / tend workflows** run Claude Code on the same planted repo every tick. That is TE's best case. Add an optional `policy.cost.token_economizer: {enabled: false, sha: <pinned>, mechanisms: [toolprune, loopguard], microskills: envfacts}` block to the manifest. The planter copies the *setting*, never TE itself. It lands together with the open **Cost governor** item (`CONCEPT.md §2`): the governor enforces the caps, and TE lowers the spend under them.
- **Recipes vs micro-skills.** Micro-skills are a narrow, automatic form of a recipe's `prerequisites` / `pitfalls`, learned per machine. Treat TE facts confirmed in 3 or more sessions as **candidate pitfalls** that the recipe miner may cite, with provenance `te-microskill` and evidence count. They go through the same ≥ 2-independent-occurrences promotion rule (§2). Recipes stay the auditable, versioned source of truth.
- **Replay validation (§4): TE OFF by default.** A replay compares an agent rebuild against real history. Injected facts and pruned tools change the agent, so replay scores must hold TE constant, either off or a pinned state hashed into the run manifest. Only then is a recipe-vs-history score comparable across runs and with GWTP's drift scores (counterbalance contract).
- **Loop-guard events** in a grow/tend pass count toward the per-PR repair budget (`policy.board.max_repair_attempts`) as telemetry only. They never auto-escalate on their own.
- **Phase R-TE (before any scheduled recipe-driven run):** shadow A/B over at least 20 grow passes on one garden repo. Keep TE on only if mean cost drops by 10% or more with no loss in merged-PR rate or verify pass rate.


## Counterbalance contract (shared section — identical in both proposals)

> This section appears verbatim in `bamr87/gitorio` → `packages/git-with-the-program/docs/proposals/rl-drift-learning.md` and in `bamr87/githubai` → `ai-seed/docs/proposals/seed-recipes.md`. Edit both together, or better, move it to the hub (below) and link it from both.

### Roles

| | GWTP (gitorio `packages/git-with-the-program/`) | AI seed (githubai `ai-seed/`) |
| --- | --- | --- |
| Question it answers | "Did this change deviate from declared intent, and how surprising was it?" | "What path should this feature have taken to reach its intent?" |
| Artifact | Drift verdicts on the ledger, calibrated scores (`drift-calibration/v1`) | Seed recipes (`seed-recipe/v1`) |
| Direction | Backward-looking: observation vs. the program (`.program/`) | Forward-looking: expected path from mined progressions |
| Failure mode it checks in the other | Recipes that encode a path the program already forbids, or that "expect" drift | Drift scores that flag the expected, well-trodden path (false positives) or miss steps a recipe says are load-bearing (false negatives) |

GWTP flags drift from intent. AI seed's recipe is the expected path. Neither is ground truth; each is the other's accuracy check, and a human settles disagreements.

### The comparison

For one scope (a FEAT id, a phase, and a commit range), a deterministic comparator joins:

- GWTP's per-change calibrated drift probability `p_drift` and its cited verdicts (assertion id, `file:line-span`, anchored severity);
- the recipe's expected step for that change (step id, expected files, expected tests) or `unmatched` when the change maps to no step.

It emits exactly one of four outcomes per change:

| GWTP says | Recipe says | Outcome | Who acts |
| --- | --- | --- | --- |
| low drift | on-path (matches a step) | `agree-aligned` | nobody; counted only |
| high drift | off-path (unmatched or matches a known pitfall) | `agree-drift` | GWTP's normal ladder (no new finding) |
| high drift | on-path | `disagree-flagged-expected` | **finding → human**: either the program is stale (reprogramming candidate) or the recipe learned a bad habit |
| low drift | off-path | `disagree-missed` | **finding → human**: either GWTP has a blind spot (missing assertion / miscalibrated knob) or the recipe is over-specified |

Thresholds for "high/low" are the calibrated operating point from GWTP's held-out evaluation (not a raw score), and "on/off-path" is the recipe's step-match rule; both are pinned in the contract file so a disagreement is reproducible.

### Findings

A finding is a record, never an action. It is filed as one GitHub issue per scope per cycle (labels `counterbalance` + `human-review`, so ai-seed's board lane parks it and GWTP never auto-files a proposal from it). A human resolves it with one of: `program-stale`, `recipe-wrong`, `gwtp-miscalibrated`, `both-wrong`, `inconclusive`. Resolutions are the highest-value labels either side gets: GWTP consumes them as reward labels (they enter the calibration set), and AI seed consumes them as recipe corrections (a `recipe-wrong` resolution bumps the recipe version and adds a `pitfall`).

Neither side may consume its own disagreement output without a human resolution. That is what stops the two systems from co-adapting into agreement (each "learning" to say what the other says).

### Shared data formats

All formats are JSON (YAML accepted on input), versioned with a `schema:` key, content-addressed (`sha256` of canonical JSON, same canonicalization as GWTP's `src/core/canonical.ts`), and identity-free (no author names or logins; GWTP INV-003 extends to anything a judge could see).

- `phase-map/v1` — the segmentation of a repo's history: `{repo, phases: [{id, kind: release|tag|epic|window|epoch, from_sha, to_sha, from_time, to_time, label}]}`. Produced by GWTP (it already has epochs, spec 04 §1); consumed by AI seed so both sides cut history the same way.
- `change-ref/v1` — a stable handle for one unit of change: `{repo, sha | pr, phase_id, hunk_hash?}`.
- `outcome-label/v1` — an observed outcome attached to a change: `{change, kind: revert|bug-fix-of|review-verdict|ci|counterbalance-resolution|human-label, value, source_url, observed_at}`. Both sides read it; neither side writes the other's.
- `drift-calibration/v1` — GWTP's per-change calibrated probability with its verdict citations and calibrator hash.
- `seed-recipe/v1` — AI seed's recipe (schema in the seed-recipes proposal).
- `counterbalance-finding/v1` — `{scope, change, gwtp: {p_drift, verdict_ids}, recipe: {id, version, step_id|null}, outcome, contract_hash, resolution?}`.

### Where the contract lives

Following the hub rule that a standard evolves in the monorepo first, the schemas and the comparator spec live in **`bamr87/bamr87`** as a design-only proposal first (proposed path: `docs/COUNTERBALANCE.md` plus `templates/counterbalance/*.schema.json`, with a `features/features.d/` fragment `HUB-NEW` and a `changelog.d/` fragment, numbered at merge by `tools.jev number`). Gitorio and githubai vendor a pinned copy (the way gitorio pins `vendor/archify/`) and CI fails on drift from the pin. Until the hub PR exists, this section is the contract of record and both copies must match byte for byte.

### Guardrails common to both sides

- Read-only against history and the forge; the only writes are (a) GWTP's own ledger ref, (b) AI seed draft PRs on `seed/*` branches, and (c) finding issues. Neither side edits the other's repo.
- Deterministic and reproducible: every run records input SHAs, schema versions, model id + prompt sha256 for any model step, and random seeds; a rerun with the same inputs produces byte-identical outputs or the run fails loud.
- Human-gated: no merge, no `.program/` write (GWTP INV-001), no kill-switch or guardrail edit (ai-seed constitution rule 4).
- Cost is reported per cycle as **"API-equivalent (estimate)"**: token counts × list price, even when the run used a Claude Code OAuth subscription, so the number is comparable across auth modes and is never mistaken for an invoice.

## 9. Proposed governance edits (not applied — human-owned files)

**`ai-seed/CONCEPT.md` §2** (user-owned; the planter never rewrites it) — add one unchecked capability:

```diff
+- [ ] Seed recipes: mined, replay-validated build instructions for a feature (intent, prerequisites, ordered steps, files, tests, pitfalls, acceptance, provenance) that feed germinate/grow and counterbalance GWTP drift scores (docs/proposals/seed-recipes.md).
```

**`ai-seed/CONCEPT.md` §2, Cost governor item** (already open). Extend its text with: "…; optional TokenEconomizer (pinned, default off) reduces per-pass spend under the cap (docs/proposals/seed-recipes.md §8.1)."

**`ai-seed/CONCEPT.md` §3** — append: "Recipes are data, not kernel: the kernel reads them when a repo opts in, and the planter never copies them."

**githubai `docs/PRD.md` §5 M4** — add `FR-NEW: feature progressions are mined into replay-validated seed recipes, and disagreements with drift scoring are filed for a human` (placeholder; numbered at merge). Add a second placeholder: `FR-NEW: agent passes may opt into a pinned token-economy plugin (TokenEconomizer) under the cost governor; replay and calibration runs record it in their manifest`.

**githubai `features/features.yml`** — the catalog is still the `TODO-001` stub, so a planned entry `AISEED-NEW` "Seed recipes" (`implemented: false`, `docs: ai-seed/docs/proposals/seed-recipes.md`, `prd: [FR-NEW]`) should land together with the first real catalog entries rather than alone.

**Constitution.** No guardrail is weakened and no new write path is added to the kernel, so no amendment to the seed constitution (CLAUDE.md guardrails 1–7) is required. If R3 ever lets recipes influence what a pass may write, that change needs one.

## 10. Open questions

- Should fleet-wide recipes live in ai-seed (`seed/recipes/`) or in the hub next to the contract schema?
- Similarity threshold 0.6 is a guess; R2 should calibrate it against GWTP's held-out phases.
- Recipes for features that were *removed* (tombstones): keep as negative recipes ("do not rebuild")?
