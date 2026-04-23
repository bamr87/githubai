---
applyTo: "tests/**,**/test_*.py,**/*_test.py,**/*.test.{js,ts,jsx,tsx}"
---

# Test Instructions

Rules for Copilot when writing or editing tests in **{{PROJECT_NAME}}**.

## General

- One behavior per test. Name tests `test_<subject>_<behavior>_<expected>`.
- AAA structure: **Arrange / Act / Assert**, separated by blank lines.
- Prefer pure assertions (`assert x == y`) over framework-specific magic.
- Tests must be deterministic. No real network, no real clock, no random without seed.

## Python (pytest)

- Use **fixtures** for setup. Scope them as narrowly as possible (`function` by default).
- Parametrize with `@pytest.mark.parametrize` instead of loops over assertions.
- Mark slow / external tests with `@pytest.mark.integration` (skipped by default).
- Use `pytest.raises` for expected exceptions; assert on the message when meaningful.

## JavaScript / TypeScript

- Use the test runner already configured in `package.json` (Vitest, Jest, etc.) — do not introduce a new one.
- Mock with the runner's built-in mock API, not ad-hoc globals.
- Component tests use `@testing-library/*` — query by accessible role, not by class.

## Coverage

- New code paths require new tests. Don't lower coverage thresholds to make a PR green.
- Don't test private implementation details — test behavior at the public boundary.

## Anti-patterns to avoid

- Mocking the system under test.
- Sleeping to wait for async work — use the runner's awaiting primitives.
- Sharing mutable state between tests.
