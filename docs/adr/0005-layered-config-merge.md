# ADR 0005 — Layered config: base, then profile, then repository

> A repository's effective configuration is `profiles/_base.yml`, then `profiles/<repo.type>.yml`, then its own `.github/githubai.yml`, deep-merged at runtime by `actions/load-config` with maps recursing and lists and scalars replacing.

- **Status**: accepted
- **Date**: 2026-07-22
- **Deciders**: the maintainer (bamr87); recorded after the fact on 2026-11-15 from the shipped code and docs (#137)
- **Related**: #101 (the rebuild as the Claude Code SDLC framework); PRD § 3 (the `.github/githubai.yml` row) and § 4 "Config over code"; [docs/configuration.md](../configuration.md); [profiles/README.md](../../profiles/README.md); [`actions/load-config/load_config.py`](../../actions/load-config/load_config.py); tests `tests/test_load_config.py`

## Context

GitHubAI serves different kinds of repository from one set of reusable workflows. Behaviour has to differ per repository without forking workflows ("config over code"), prompts have to stay generic while the standards they apply are repository-specific, and someone has to be able to answer "why did Claude do that".

## Decision

`actions/load-config/load_config.py` resolves the effective configuration from three layers, later layers winning:

1. `profiles/_base.yml`: the framework defaults and the label taxonomy.
2. `profiles/<repo.type>.yml`: the standards for that kind of repository.
3. The repository's own `.github/githubai.yml`: optional per-repository overrides.

Maps merge recursively; lists and scalars replace the inherited value. The repository config is read first only to learn `repo.type`, then re-applied on top of the profile so its own overrides always win, and an unknown type fails with the list of available profiles. The merged result reaches Claude as a rendered `prompt_context` block, and the same result is reproducible locally with `--print`. App mode's org policy is not a layer in this chain ([ADR 0003](0003-subtractive-org-policy.md)). `tests/test_load_config.py` holds the merge semantics (`test_profile_layer_applies`, `test_repo_config_wins_over_profile`, `test_lists_replace_not_concatenate`, `test_unknown_type_fails_listing_profiles`).

## Consequences

**Positive**

- Per-repository behaviour lives in profiles and `githubai.yml`, not in forked workflows, and upgrades by a ref bump.
- "Why did Claude do that" is debuggable: `load_config.py --print` shows the exact block Claude received.

**Negative**

- Lists replace rather than concatenate, so a repository that overrides `auto_merge.allowed_paths` must restate the whole list.
- The config schema keys are public API: renaming one is a breaking change.

## Alternatives considered

- **Per-repository differences in copied or forked workflows** — rejected by "config over code": logic lives in this repository and consumers upgrade by ref bump. No other alternative was recorded when the merge shipped.

## Supersedes / Superseded by

- Supersedes: none
- Superseded by: none
