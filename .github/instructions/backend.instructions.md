---
applyTo: "**/*.py,**/pyproject.toml,**/requirements*.txt"
---

# Backend / Python Instructions

Guidance for Copilot when editing Python or backend code in **{{PROJECT_NAME}}**.

## Style

- Format with **Black**, line length **120**.
- Lint with **Ruff** (or the project's configured linter — check `pyproject.toml`).
- Type hints on all public function signatures. Prefer `from __future__ import annotations`.
- Docstrings: **Google style** unless the file already uses another consistent style.

## Architecture

- Keep business logic out of view/controller code; put it in a `services/` module.
- Never call third-party APIs directly from a view — wrap them in a service class.
- Prefer dependency injection over module-level singletons for anything that touches I/O.

## Errors & logging

- Never `except:` or `except Exception:` without re-raising or logging with stack trace.
- Use `logging.getLogger(__name__)`. Do not use `print` in non-CLI code.
- Raise the most specific exception type; create a small custom exception when none fits.

## Security

- Never log secrets, tokens, or full request bodies.
- Validate and sanitize all external input (HTTP, webhooks, CLI args).
- Parameterize SQL. Never f-string user input into a query.
- Pin dependencies; review `gh-advisory-database` before adding a new one.

## Tests

- Every new public function/endpoint gets a test.
- Use `pytest` fixtures over `setUp`/`tearDown`.
- Mark slow or external-dependency tests with `@pytest.mark.integration`.
