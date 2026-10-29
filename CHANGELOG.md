# Changelog

All notable changes to this project are documented in this file. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `CHANGELOG.md`, in Keep a Changelog format.
- `ai-seed/`: [bamr87/ai-seed](https://github.com/bamr87/ai-seed) imported with its full history, as reference material; its thin `ci.yml` and `markdown-oneline.yml` callers were dropped because the root runs both.

### Changed

Merged to `main` since v0.5.3:

- 2026-10-17: docs(readme): align README with the portfolio standard ([#120](https://github.com/bamr87/githubai/pull/120))
- 2026-10-14: ci: stagger AI cron schedule (bamr87/bamr87#348) ([#118](https://github.com/bamr87/githubai/pull/118))
- 2026-10-06: fix(workflows): allow dependabot/renovate actors in review and auto-merge ([#117](https://github.com/bamr87/githubai/pull/117))
- 2026-10-03: fix: concurrency guard on claude.yml and docs drift from #114 ([#116](https://github.com/bamr87/githubai/pull/116))
- 2026-09-12: style(markdown): one paragraph per line + CI enforcement ([#112](https://github.com/bamr87/githubai/pull/112))
- 2026-09-12: fix(ci): raise max_turns to 100 so weekly maintenance can finish ([#115](https://github.com/bamr87/githubai/pull/115))
- 2026-08-19: feat(app): hosted multi-tenant GitHub App relay (PRD M3) ([#110](https://github.com/bamr87/githubai/pull/110))
- 2026-08-06: chore: bump GitHub Actions to latest stable versions ([#107](https://github.com/bamr87/githubai/pull/107))
- 2026-07-22: feat!: rebuild GitHubAI as the Claude Code SDLC framework (OAuth-first) ([#101](https://github.com/bamr87/githubai/pull/101))

## [0.5.3] - 2026-07-17

- 2026-07-17: style(markdown): one paragraph per line + CI enforcement ([#99](https://github.com/bamr87/githubai/pull/99))

## [0.5.2] - 2026-07-17

- 2026-07-16: ci: reduce Actions waste — follow-up: fix bare-runner env in versioning, git root in doc_service ([#98](https://github.com/bamr87/githubai/pull/98))
- 2026-07-16: ci: reduce Actions waste — fix chronic failures, delete dead/twin workflows, slim versioning ([#92](https://github.com/bamr87/githubai/pull/92))
- 2026-07-16: chore: adopt standardization baseline (editorconfig,ci,agent-context,claude) ([#91](https://github.com/bamr87/githubai/pull/91))
- 2026-07-12: chore: adopt standardization baseline (.editorconfig) ([#90](https://github.com/bamr87/githubai/pull/90))

## [0.5.1] - 2025-11-29

- 2025-11-29: feat(prd-machine): add multi-document sync for PRD, README, and IP alignment
- 2025-11-29: docs: address PRD MACHINE conflict recommendations

## [0.5.0] - 2025-11-29

- 2025-11-29: feat(core): add PRD MACHINE for AI-powered PRD automation

## [0.4.1] - 2025-11-26

- 2025-11-26: feat(docker): add VS Code remote debugging support
- 2025-11-26: chore: clean up whitespace in commit and publish workflow documentation
- 2025-11-26: chore: add commit and publish workflow documentation
- 2025-11-26: feat(frontend): Complete frontend rebuild with routing, pages, and API integration v0.4.0
- 2025-11-26: Simplify test environment naming and add data loading commands
- 2025-11-26: feat: Add TEST environment harness for isolated AI data testing
- 2025-11-24: Implement Sphinx-based automatic documentation generation for GitHubAI
- 2025-11-24: fix: update copyright notice in LICENSE file to reflect GitHubAI Contributors
- 2025-11-24: Upgrade Django to 5.1, Python to 3.12, and update dependencies; remove old migrations and generate fresh schema; implement new STORAGES setting; enable…
- 2025-11-24: Implement comprehensive prompt management system with versioning, execution tracking, and AI integration
- …and 7 earlier changes.

## [0.1.14] - 2025-11-15

- 2025-11-15: Refactor test files for improved readability and consistency; update .gitignore to include .pypirc

## [0.1.13] - 2025-04-15

- 2025-04-14: Add AI-generated changelog and documentation summary ([#79](https://github.com/bamr87/githubai/pull/79))

## [0.1.12] - 2025-04-14

- 2025-04-13: Add .DS_Store to .gitignore to prevent macOS system files from being tracked

## [0.1.11] - 2025-04-14

- 2025-04-13: Add verbose flag to twine upload command for better logging

## [0.1.10] - 2025-04-14

- 2025-04-13: Update versioning workflow to publish to test PyPI and ensure proper formatting in requirements

## [0.1.9] - 2025-04-13

- 2025-04-13: Refactor pyproject.toml for consistency and formatting improvements

## [0.1.8] - 2025-04-13

- 2025-04-13: Update versioning.yml

## [0.1.7] - 2025-04-13

- 2025-04-13: Enhance versioning workflow to include automatic publishing to PyPI and update README with publishing instructions

## [0.1.6] - 2025-04-12

- 2025-04-12: Fix diff handling in auto_doc_generator to support both bytes and string formats

## [0.1.5] - 2025-04-12

- 2025-04-12: Add AI-generated changelog and documentation summary ([#76](https://github.com/bamr87/githubai/pull/76))

## [0.1.4] - 2025-04-12

- 2025-04-12: Ensure documentation branch is up-to-date before pushing changes

## [0.1.3] - 2025-04-12

- 2025-04-12: Refactor versioning workflow: consolidate version bump logic into a dedicated script and update VSCode settings for Python formatting
- 2025-04-12: Enhance versioning workflow with commit message validation and conflict handling; add local version bump simulation script
- 2025-04-12: Refactor README to enhance clarity on automated versioning, documentation, and issue management features
- 2025-04-10: Update workflow to trigger on 'main' branch and fix GITHUB_TOKEN reference
- 2025-04-10: Merge pull request #72 from bamr87/main ([#73](https://github.com/bamr87/githubai/pull/73))
- 2025-04-10: Add automated versioning based on commit message tags ([#71](https://github.com/bamr87/githubai/pull/71))
- 2025-04-07: Update trigger branch for AI documentation generation workflow to 'doc-feature'
- 2025-04-07: Add AI-generated changelog and documentation summary ([#66](https://github.com/bamr87/githubai/pull/66))
- 2025-04-07: Add GitHub Actions workflow for AI-powered documentation generation on PRs
- 2025-04-07: Update GitHub token reference in AI Doc Generator workflow
- …and 47 earlier changes.

[Unreleased]: https://github.com/bamr87/githubai/compare/v0.5.3...HEAD
[0.5.3]: https://github.com/bamr87/githubai/compare/v0.5.2...v0.5.3
[0.5.2]: https://github.com/bamr87/githubai/compare/v0.5.1...v0.5.2
[0.5.1]: https://github.com/bamr87/githubai/compare/v0.5.0...v0.5.1
[0.5.0]: https://github.com/bamr87/githubai/compare/v0.4.1...v0.5.0
[0.4.1]: https://github.com/bamr87/githubai/compare/v0.1.14...v0.4.1
[0.1.14]: https://github.com/bamr87/githubai/compare/v0.1.13...v0.1.14
[0.1.13]: https://github.com/bamr87/githubai/compare/v0.1.12...v0.1.13
[0.1.12]: https://github.com/bamr87/githubai/compare/v0.1.11...v0.1.12
[0.1.11]: https://github.com/bamr87/githubai/compare/v0.1.10...v0.1.11
[0.1.10]: https://github.com/bamr87/githubai/compare/v0.1.9...v0.1.10
[0.1.9]: https://github.com/bamr87/githubai/compare/v0.1.8...v0.1.9
[0.1.8]: https://github.com/bamr87/githubai/compare/v0.1.7...v0.1.8
[0.1.7]: https://github.com/bamr87/githubai/compare/v0.1.6...v0.1.7
[0.1.6]: https://github.com/bamr87/githubai/compare/v0.1.5...v0.1.6
[0.1.5]: https://github.com/bamr87/githubai/compare/v0.1.4...v0.1.5
[0.1.4]: https://github.com/bamr87/githubai/compare/v0.1.3...v0.1.4
[0.1.3]: https://github.com/bamr87/githubai/tree/v0.1.3
