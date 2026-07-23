---
description: Run repo maintenance tasks the way claude-maintenance.yml does in CI
---

Run maintenance for this repository, mirroring `.github/workflows/claude-maintenance.yml`. Optional task subset: "$ARGUMENTS" (empty = all enabled in config).

Follow the playbook — docs_drift (compare docs claims vs reality), todo_sweep (one grouped issue), dependency_report (read manifests only, never install), stale_nudge (max 5 polite nudges), health_report (single updatable "Repo health report" issue) — with the hard rules: dedupe against the `<!-- githubai:maintenance -->` marker before filing, respect max_issues_per_run, label creations `type:chore` + `claude:triaged`, and never commit to the default branch.
