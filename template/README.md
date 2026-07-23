# Template files installed into consumer repos

Everything in this directory is what `setup/install.sh` copies into a repository adopting GitHubAI. The workflow files are thin callers: all logic lives in this repo's reusable workflows (`.github/workflows/claude-*.yml`), so consumers update by ref, not by re-copying files.

| File | Installed to | Purpose |
|------|--------------|---------|
| `workflows/*.yml` | `.github/workflows/` | Thin callers binding repo events to the reusable workflows |
| `githubai.yml` | `.github/githubai.yml` | Repo config: type, purpose, automation posture overrides |
| `CLAUDE.md` | `CLAUDE.md` | Agent context for interactive `@claude` sessions |

Consumer-facing compatibility rule: file names here, the inputs the stubs pass, and the reusable workflow paths they reference are public API. Renaming any of them is a breaking change.

The stubs reference `@main` by default; the installer's `--ref` flag pins them to a tag or SHA at install time, and `docs/security.md` covers why you may want that.
