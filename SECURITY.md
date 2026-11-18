<!-- kit: community v0.1.0 · the fleet default SECURITY policy (UPS-REPO-14), extended with GitHubAI's scope. -->

# Security Policy

> Which GitHubAI versions get security fixes, how to report a vulnerability privately, how soon you hear back, and what the policy covers.

## Supported versions

| Version | Supported |
| --- | --- |
| The [latest release](https://github.com/bamr87/githubai/releases/latest), and `main`, which installed workflow stubs reference by default | ✅ |
| Anything older | ❌ |

Security fixes land on `main` first and ship as patch releases through release-please. A repository pinned to an older tag with the installer's `--ref` gets a fix by moving to the latest release.

## Reporting a vulnerability

**Do not open a public issue.** Report privately through GitHub's [private vulnerability reporting](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing-information-about-vulnerabilities/privately-reporting-a-security-vulnerability) on [bamr87/githubai](https://github.com/bamr87/githubai/security) (**Security → Report a vulnerability**), or email **amr.abdel@gmail.com**.

Please include the affected component (see [Scope](#scope)), the version or commit, what an attacker can do, and the steps to reproduce.

## Response window

You will get an acknowledgement **within 7 days**. We then agree a fix timeline with you, and credit you in the advisory unless you ask us not to.

## Scope

This policy covers the code GitHubAI ships to the repositories that adopt it:

- the reusable workflows, `.github/workflows/claude.yml` and `.github/workflows/claude-*.yml`, and the stubs in `template/workflows/` that call them;
- the composite action `actions/load-config/`;
- the installer, `setup/install.sh`;
- the GitHub App relay, `app/relay/`.

[docs/security.md](docs/security.md) describes how these handle credentials, authorization and untrusted issue and PR content, and [app/DATA-HANDLING.md](app/DATA-HANDLING.md) lists what the relay stores and what it never stores. A way around either one is a vulnerability under this policy.

Out of scope: `ai-seed/`, imported reference material that nothing in this repository runs, and flaws in GitHub Actions or `anthropics/claude-code-action` themselves, which belong to those projects.
