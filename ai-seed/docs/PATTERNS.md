# Pattern provenance — where every mechanism was proven

AI-Seed invents as little as possible. Each mechanism in the kernel was extracted from a sibling repo in the bamr87 fleet where it already runs in production, usually after an incident taught the lesson. This registry maps every framework element to its source — read the source repo when you need the deep version, and keep this table honest when the kernel evolves.

The point of this file is bidirectional: the fleet repos are the framework's **design considerations and implementation examples**, and the kernel is the fleet's patterns made portable.

## The registry

| AI-Seed mechanism | Proven in | What the source demonstrates |
|---|---|---|
| Centralized concept seed with an Evolution Log tick clock (`CONCEPT.md` §8) | [year-of-ai/year-of-ai.github.io](https://github.com/year-of-ai/year-of-ai.github.io) `lineage/seeds/<year>.md` | Concept-as-data grows 11+ member repos; §8 entries (`G<gen>-T<seq>`) make growth auditable and resumable |
| Policy over workflow (model tiers, cadence, auth declared as data) | year-of-ai `lineage/policy.yml` | Changing models/cadence/art-direction is a data edit, never a workflow edit |
| 3-tier model escalation (plan → build → verify) with per-pass `is_error` detection and API-key fallback | year-of-ai + [ai-world-view](https://github.com/ai-world-view/ai-world-view.github.io) `grow-lineage.yml` | `claude-code-action` exits 0 on agent errors; snapshot the execution JSON per pass, fire the fallback on evidence |
| Gate job as a separate job (kill switch + input validation before any model pass) | year-of-ai `grow-lineage.yml` `gate:` | A paused fleet or malformed input can never reach `if: always()` publish steps |
| In-tree model-free kill switch (`.seed/pause.yml`) | year-of-ai `_data/fleet_pause.yml` (ADR-0003) | One human edit halts every mutating loop org-wide, without touching workflows |
| Per-repo write serializer (`concurrency.group: seed-write-<name>`, no cancel-in-progress) | year-of-ai ADR-0003 repo-write-serializer | Two writers never race one branch; superseded runs queue rather than die mid-push |
| Fail-loud empty tick with auth-vs-stalled diagnosis | year-of-ai / ai-world-view grow workflows | A tick where every model pass died at startup must never report green; the error message names the failure class |
| Stalest-first rotation with a per-run cap (garden orchestration) | year-of-ai `orchestrate.yml` + `cadence.repos_per_run` | Bounded daily spend while every member still grows perpetually |
| Rebase-retry pushes for shared-branch writers | year-of-ai (a tick clock was lost to a non-fast-forward push) | Any push to a branch that advances often must retry with rebase |
| Planter that resumes an interrupted plant and refuses repos with real content | year-of-ai / ai-world-view `plant-lineage.rb` | Idempotent planting: refill only when every file belongs to the plant surface |
| Default-OFF `*_ENABLED` repo variables ("the variable is the consent") | [bamr87/lifehacker.dev](https://github.com/bamr87/lifehacker.dev) (`docs/CICD.md`; e.g. `THEME_SCOUT_ENABLED`) | Every AI loop ships idle; a human turning the variable on is the recorded opt-in |
| Dry-run default on manual runs; scheduled runs apply | lifehacker.dev `theme-scout.yml` | Enabling the schedule is the checked box; a hand-run stays safe by default |
| Repo-as-CMS / all state in-tree (backlog, ledgers, health as committed files) | lifehacker.dev | The repo is the database; every state change is a reviewable diff |
| Frozen data contracts for machine hand-offs (`findings.jsonl` / `queue.json`) | lifehacker.dev `docs/ARCHITECTURE.md` | Loops compose only through versioned, append-only file contracts — mirrored by `seed-telemetry/v1` |
| Same harness for humans and CI (one script set, two callers) | lifehacker.dev `scripts/ci/run-all.sh` | `seed.py check` is the one structural gate for the CLI, the tests, and `seed-verify.yml` |
| Untrusted-input quarantine with a bounded action allowlist | lifehacker.dev `.claude/skills/_shared/quarantine.md`; hub `templates/agent-context/quarantine.template.md` | Issue/PR/web text is data to classify, never instructions; at worst an injection gets something labeled |
| OAuth-first, API-key-fallback at every Claude call site | [bamr87/bamr87](https://github.com/bamr87/bamr87) `docs/AI-INTEGRATION.md` (all `claude-code-action` call sites) | One auth doctrine across ~40 repos; subscription primary, metered key as fallback |
| `@claude` mention steward workflow | bamr87 hub `templates/agent-context/claude.yml` (kit v0.4.0) | Serialized per-thread concurrency; mention-gated consent; already installed here as `claude.yml` |
| PRs that need CI must not be opened with `github.token` | bamr87 hub (fleet-pulse post-mortem, standing rule 3) | GitHub fires no workflow events for refs the installation token pushes — hence `SEED_PAT` |
| Never end a workflow in a bare push to a protected branch | bamr87 hub (four loops silently dead for three weeks) | Publish via PR (or a publish helper that falls back to one); AI-Seed is PR-only everywhere |
| Prefer `needs:` over `workflow_run` for sequencing | bamr87 hub (`actions-review` skipped as collateral) | `workflow_run` survives here only as pure observation (failure triage) |
| Labels as the pipeline state machine, with human brake labels | bamr87 hub `docs/ISSUE-PIPELINE.md` (`agent:ready`, `agent:hold`, `human-review`) | A missed run costs latency, not a stuck issue; a human stops anything by editing one label |
| Central token contract declared in version control and audited by tooling | bamr87 hub `_data/fleet.yml` | The manifest's `auth:` block names which secret does what; secret values never live in files |
| Vendored single-file tools with a parity/drift check | bamr87 hub drift gate check (i); [bamr87/SCHEMA](https://github.com/bamr87/SCHEMA) (stdlib-only, adopters vendor single files) | Three divergent lint forks appeared unnoticed once; `.seed/tools/seed.py` parity is checked in CI |
| Structure as a lintable contract (optional SCHEMA.md seeding, `plant --schema`) | bamr87/SCHEMA | One `SCHEMA.md` per directory; the pyramid describes the pyramid; implemented in kernel v0.2.1 |
| Dry-run as the default posture; a single explicit apply gate for writes | [bamr87/wtd](https://github.com/bamr87/wtd) (`--apply` / `WTD_FLEET_APPLY`) | Autonomy ships observable-first; writes require the explicit gate |
| Agents never hold credentials; the platform performs validated writes | wtd `dispatcher.py` / `outcome.py` | Model output is a proposal validated against grants; mutations run in workflow-owned steps |
| `.github/workflows/` unwritable by agents — no exceptions | wtd (`outcome.py::_safe_rel_path`) | Workflows execute with the fleet's secrets; letting agents edit them is privilege escalation |
| Stable dedup keys and self-markers on everything a loop writes | wtd (`<!-- wtd-fleet:<key> -->`) | Rescans converge instead of duplicating; the loop never feeds itself |
| Headless `claude -p --output-format json` as the CLI-side OAuth lane | wtd `providers/claude_code.py` | The subscription lane outside Actions: same OAuth token, JSON result contract |
| Loop guards on comment/issue-writing automations | [bamr87/gitorio](https://github.com/bamr87/gitorio) (compiler-enforced: agents that write comments must never retrigger themselves) | Event-emitting sinks are mapped to the events they emit; unguarded feedback loops are refused |
| Least-privilege computed `permissions:` and narrow `--allowedTools` grants | gitorio golden rule 5 | `Bash(gh pr create:*)`-style scoping, never blanket grants |
| Prompts live in-repo, reviewable and hot-editable | gitorio (`.factory/prompts/*.md`) | Prompt text is versioned content; here prompts live in the workflow env blocks and `CONCEPT.md` |
| Constitution files with human-ratification-only politics | [bamr87/git-with-the-program](https://github.com/bamr87/git-with-the-program) `.program/` (INV-001) | The manifest's `guardrails:` block is agent-read-only; changes arrive as human-reviewed PRs |
| Self-hosting obligation | git-with-the-program TRJ-003; SCHEMA's self-describing root | ai-seed is planted with its own kernel; the framework's first enforcement target is itself |
| Judgment ladder for escalating verification (roadmap) | git-with-the-program `docs/spec/03-judge.md` | deterministic check → single judge → panel → human, each rung superseding the last |

## How to use this registry

- **Extending the kernel?** Find the fleet repo that already solved the problem and extract, don't invent. If nothing in the fleet solved it, prototype it in one repo first — the kernel takes only proven patterns.
- **Debugging a loop?** The source repo usually documents the incident that motivated the mechanism (workflow header comments and ADRs). The failure you are seeing has likely been seen before.
- **Changing a mechanism here?** Update this table in the same PR, and consider whether the source repos should adopt the improvement back — pollination runs both ways.
