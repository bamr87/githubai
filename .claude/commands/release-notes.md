---
description: Draft release notes the way claude-release.yml does in CI
---

Draft release notes for this repository, mirroring `.github/workflows/claude-release.yml` publish mode. Argument (optional): the tag to draft for — "$ARGUMENTS"; default is the latest tag.

1. Determine the tag range (`git tag --sort=-v:refname`, `git describe`).
2. Read `git log <prev>..<tag>` and merged PRs in range.
3. Produce categorized notes — Breaking (top, loud) / Features / Fixes / Docs / Chores — omitting empty sections and crediting external contributors. Output the markdown only; do not create the release unless explicitly asked.
