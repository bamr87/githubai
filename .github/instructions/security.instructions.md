---
applyTo: "**"
---

# Security Instructions

Security rules that apply to **all** files in **{{PROJECT_NAME}}**. These override any conflicting guidance.

## Secrets

- Never commit secrets, API keys, tokens, private keys, passwords, or `.env` files.
- Reference secrets via environment variables or the platform's secret store (`${{ secrets.X }}` in workflows).
- If a secret leaks: rotate immediately, then scrub history with `git filter-repo`. Don't just delete the file.

## Input handling

- Treat **all** external input as untrusted: HTTP bodies, query params, headers, webhooks, CLI args, environment variables, file contents.
- Validate type, length, and shape before use.
- For SQL: use parameterized queries / ORM bindings. Never string-concatenate.
- For shell: never `shell=True` with user input. Prefer argument arrays.
- For HTML/Markdown rendering: escape by default; opt in to raw HTML only with explicit allowlist.
- For file paths: resolve and confirm the result is inside the expected base directory (no `..` traversal).

## Dependencies

- Before adding a dependency, check the GitHub Advisory DB.
- Prefer well-maintained packages. Avoid abandoned (>2 years no release) unless there's no alternative.
- Pin versions in lockfiles. Renovate/Dependabot handles updates.

## Auth & sessions

- Authenticate first, authorize second. Never trust a client-supplied user ID.
- Tokens: short-lived, scoped, rotated. Refresh tokens stored httpOnly + secure.
- Rate-limit authentication endpoints.

## Crypto

- Use the platform's standard crypto library. Never roll your own.
- TLS for all network I/O. No plaintext fallbacks.

## Logs

- Never log secrets, full request bodies, full headers, or PII.
- Log auth events (success and failure) for audit.

## CI / Workflows

- Pin GitHub Actions to a commit SHA or a tagged major version (`@v4`), never `@main`.
- Set the minimum `permissions:` block per job.
- Untrusted input from `pull_request_target` events must never reach `run:` script bodies.
