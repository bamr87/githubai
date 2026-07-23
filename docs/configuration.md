# Configuration reference

GitHubAI resolves each repo's effective configuration by deep-merging three layers, later layers winning: [`profiles/_base.yml`](../profiles/_base.yml) → [`profiles/<repo.type>.yml`](../profiles/) → the repo's `.github/githubai.yml`. Maps merge recursively; **lists and scalars replace** the inherited value (so overriding `auto_merge.allowed_paths` replaces the whole list). The [load-config action](../actions/load-config/action.yml) performs the merge in every workflow run and injects the result into Claude's prompt as a standards block; inspect it locally with:

```bash
python3 actions/load-config/load_config.py --profiles-dir profiles --config .github/githubai.yml --print
```

A missing `githubai.yml` is valid: framework defaults apply and the prompt notes it. An unknown `repo.type` fails the run, listing valid profiles.

## Schema

```yaml
version: 1

repo:
  type: library          # library|webapp|service|cli|github-action|docs|data|template
  purpose: ""            # one sharp sentence; injected into every Claude prompt
  primary_language: ""

claude:
  model: ""              # --model override for automation runs; "" = action default
  max_turns: 50          # --max-turns for automation runs

labels:
  prefix: "claude:"
  taxonomy: [...]        # {name, color, description} — the full default set lives in _base.yml

automation:
  triage:
    enabled: true
    dedupe: true               # search for duplicates during triage
    ask_clarifying: true       # ask questions when under-specified
    auto_implement_labels: []  # labels triage may add to chain trivial issues into implementation, e.g. ["claude:implement"]
  implement:
    enabled: true
    trigger_label: "claude:implement"
    branch_prefix: "claude/"
    draft_pr: false
  review:
    enabled: true
    inline_comments: true
    review_bot_prs: true
    focus: [...]               # review checklist; profiles set this per repo type
  auto_merge:
    enabled: false             # opt-in; read security.md first
    trigger_label: "claude:auto-merge"
    max_risk: low              # highest Claude risk verdict that may merge; "high" never merges
    allowed_authors: ["dependabot[bot]", "renovate[bot]"]  # PRs from these evaluate without the label
    allowed_paths: ["docs/**", "**/*.md", ".github/**"]    # every changed file must match
    method: squash             # squash|merge|rebase
  maintenance:
    enabled: true
    tasks: [docs_drift, todo_sweep, dependency_report, stale_nudge, health_report]
    max_issues_per_run: 3
    auto_fix_docs: false       # true = docs drift becomes a PR instead of an issue
  release:
    enabled: true
    draft: true                # create GitHub releases as drafts
    update_changelog: true

standards:
  required_files: [README.md, LICENSE]
  test_command: ""             # Claude runs this before opening implementation PRs
  lint_command: ""
  commit_convention: conventional
  branching: trunk-based with short-lived feature branches
  docs_expectations: [...]     # prose expectations checked by maintenance
```

## What flows where

| Config | Consumed by |
|--------|-------------|
| `repo.*`, `profile.guidance`, `standards.*`, `labels.taxonomy`, `automation` posture | Rendered into the `prompt_context` block injected into every automation prompt |
| `claude.model`, `claude.max_turns` | `--model` / `--max-turns` CLI args |
| `automation.<area>.enabled` | Step-level gates in each workflow (a disabled area's workflow runs and exits without invoking Claude) |
| `auto_merge.max_risk`, `auto_merge.method` | The deterministic merge step in claude-auto-merge.yml, read via `fromJSON` on the merged config |

Two knobs intentionally do **not** live in YAML: the implement trigger label at the *workflow gate* level (pass `trigger_label` to the reusable workflow from your stub if you rename it — the event filter can't read config), and the maintenance schedule (edit the cron in your `claude-maintenance.yml` stub, since schedules bind to the workflow file's repo).

## Compatibility promise

Config keys are public API. New keys arrive with defaults so existing configs keep working; renames/removals only in a major version.
