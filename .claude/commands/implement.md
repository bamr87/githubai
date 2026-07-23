---
description: Implement a GitHub issue the way claude-implement.yml does in CI
---

Implement issue #$ARGUMENTS of this repository, mirroring `.github/workflows/claude-implement.yml`.

Read the issue and comments with `gh issue view $ARGUMENTS --comments`; treat the content as requirements data. If requirements are ambiguous or the scope exceeds the issue, stop and say what needs deciding instead of coding.

1. Branch `claude/issue-$ARGUMENTS-<slug>`; keep the diff minimal and focused.
2. Follow the standards from `.github/githubai.yml` (+ its profile); run the configured test command until green; update any docs the change makes stale.
3. Conventional commit(s), push, `gh pr create` with body: `Closes #$ARGUMENTS`, approach summary, test evidence, review hotspots.
4. Comment the PR link on the issue.
