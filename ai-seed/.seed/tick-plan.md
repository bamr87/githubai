# Tick Plan: Optional SCHEMA.md seeding

**Tick**: G3-T2 (next after kernel relaunch)  
**Date**: 2026-08-20  
**Increment**: Add optional SCHEMA.md (Pyramid Schema) seeding to the planter

## Rationale

This is the smallest unbuilt capability in CONCEPT.md §2. The framework's design already calls for "optional SCHEMA.md (Pyramid Schema) seeding at plant time" (ARCHITECTURE.md §12, PATTERNS.md row 35), but the mechanism is not yet implemented in the planter. A planted repo that opts into `--schema` will receive a SCHEMA.md template that describes its own structure as a Pyramid Schema — enabling linting and self-documentation. The reference implementation is bamr87/SCHEMA, proven in the fleet. This is small, reviewable, and foundational for structure-as-code hygiene.

## Expected changes

| File | Role | Change |
|---|---|---|
| `seed/kernel/SCHEMA.md` | New user-owned template | Create a Pyramid Schema template describing a typical planted repo's directory structure (README→paths→contracts) |
| `tools/seed.py` | Planter logic | Add `--schema` boolean flag to plant command; if set, include SCHEMA.md in the kernel files to write (handle as optional/user-owned like CONCEPT.md) |
| `tests/test_seed_cli.py` | Tests | Add test: fresh `plant --schema` creates SCHEMA.md; add test: `--schema` + `--update` re-renders SCHEMA.md correctly |
| `docs/PATTERNS.md` | Documentation | Confirm row 35 (SCHEMA.md adoption) with a brief note: implemented in kernel v0.1.1; matches bamr87/SCHEMA spec |
| `seed/VERSION` | Version bump | Increment to 0.1.1 (kernel behavior change: new optional surface) |

## How verify should prove it

1. **Test suite passes**: `pytest tests/test_seed_cli.py` — tests confirm:
   - Fresh plant without `--schema` does NOT create SCHEMA.md
   - Fresh plant with `--schema` DOES create SCHEMA.md (user-owned, present in next-steps output)
   - `--schema --update` re-renders SCHEMA.md from the kernel template
   - Parity check (`seed.py check`) passes after fresh plant with schema

2. **Structural gate passes**: `python3 tools/seed.py check .` green on this repo after seeds/VERSION bump and PATTERNS.md update

3. **Manual validation** (not automated):
   - Create a temp repo: `python3 tools/seed.py plant /tmp/test-schema --repo test/test --schema`
   - Verify `/tmp/test-schema/SCHEMA.md` exists and contains valid Pyramid Schema structure (intro, path table, contract examples)
   - Verify it is listed as user-owned in `plant` output (not a kernel-managed file)

## Not in scope

- Integrating SCHEMA.md linting into CI (that is a separate tick, would modify workflows)
- Building the judge ladder or other §2 features
- Consuming SCHEMA.md data (that comes later; the schema is the contract)

## Exit condition

When merged, CONCEPT.md §2 gains a checkmark: `[x] Optional SCHEMA.md (Pyramid Schema) seeding at plant time.`
