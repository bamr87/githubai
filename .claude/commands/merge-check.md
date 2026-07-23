---
description: Run the auto-merge safety evaluation the way claude-auto-merge.yml does in CI
---

Evaluate PR #$ARGUMENTS for the auto-merge lane, mirroring `.github/workflows/claude-auto-merge.yml`. Read-only: do not approve, merge, or label.

Evaluate in order (any failure ⇒ not eligible), using the auto-merge posture from the resolved config:

1. Config gate: auto-merge enabled; author in allowed_authors or trigger label present; every changed file matches allowed_paths.
2. Content gate: full diff is genuinely minor (dep patch/minor bumps, docs, typos, comments, CI touch-ups). Auth, secrets, workflow permissions, install scripts, network calls, publish pipelines ⇒ not minor.
3. Risk: low/medium/high; major dep bumps are at least medium; look for suspicious additions in dep diffs.
4. CI: failing required checks ⇒ not eligible.

Output the verdict exactly as JSON: `{"eligible": bool, "risk": "low|medium|high", "reason": "...", "summary": "..."}`.
