<!-- Claude reviews every non-draft PR against the repo standards; a filled-in template speeds that up. -->

## What & why

<!-- One paragraph. Link the issue: Closes #NNN -->

## How verified

<!-- Commands run and their results; "not verified" is an acceptable, honest answer. -->

## Risk & compatibility

<!-- Anything a consumer of this framework could break on: renamed workflows/inputs/config keys, permission changes, prompt behavior changes. "None" if truly none. -->

## Definition of Done

<!-- fleet-dod:start v1 -->
- [ ] **Title** is a Conventional Commit (`feat:`, `fix:`, `docs:`, `chore:` …). It becomes the squash subject and drives the next version and the release-please CHANGELOG entry. Never edit `CHANGELOG.md` or version numbers by hand.
- [ ] **CI is green**: tests, lint, build and the conformance check.
- [ ] **Tests** were added or updated for the change, or this box says why none apply.
- [ ] **Docs** are current (README-First, README-Last): the nearest `README.md`, `docs/`, `SCHEMA.md` if files were added, moved or removed, and `features/features.yml` if a user-facing capability changed.
- [ ] **Agent instructions**: `AGENTS.md` is updated if commands, layout or conventions changed. `CLAUDE.md` stays a pointer to it.
- [ ] **Decision recorded** in `docs/adr/NNNN-slug.md` if this is hard to reverse.
- [ ] **Backlog of record** is updated: the issue is linked above, or the backlog item is moved to Done in this PR.
- [ ] **Clean diff**: no secrets, lockfiles, generated artefacts or unrelated changes.
<!-- fleet-dod:end -->

<!-- Repo-specific gates go BELOW this line. A repo may add boxes; it never removes or rewords the ones above. -->

- [ ] **Sync duties** from `AGENTS.md` are done in this PR (installer labels, `template/workflows/` stubs, `docs/workflows.md`, regenerated `docs/reference/` and docs index), or none apply.
