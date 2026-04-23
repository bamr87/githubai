# Using GitHubAI as a Template

GitHubAI ships a **drop-in `.github/` agentic toolkit** you can adopt in any repo
to add AI-assisted code review, issue triage, scheduled repo analysis, doc
generation, version bumping, and PRD upkeep — without running a server.

There are three ways to consume it. Pick the one that fits your team.

---

## Option A — Use as a GitHub Template (recommended for new repos)

1. On GitHub, click **Use this template → Create a new repository**.
2. Clone your new repo locally.
3. Run the bootstrap script (renames placeholders, removes irrelevant files):

   ```bash
   ./scripts/init-template.sh
   ```

   *(Coming in Phase 3 — until then, do step 4 manually.)*
4. Search-and-replace the placeholders listed in
   [CUSTOMIZATION.md](CUSTOMIZATION.md).
5. Commit and push.

---

## Option B — Reusable workflows from a remote ref

You don't need to copy the workflows; you can call them from your repo.

1. In your consumer repo, create `.github/workflows/pr-review.yml`:

   ```yaml
   name: PR Review (agentic)
   on:
     pull_request:
       types: [opened, synchronize, reopened, ready_for_review]
   permissions:
     contents: read
     pull-requests: write
     models: read
   jobs:
     review:
       uses: bamr87/githubai/.github/workflows/agentic-review.yml@main
   ```

2. Browse [`examples/workflows/`](../../examples/workflows/) for the rest
   (triage, scan, improve, prd-sync, feedback-to-issue).
3. Pin `@main` to a released tag (e.g. `@v1`) once you trust it.

You'll still want to copy `.github/prompts/` and `.github/instructions/`
into your repo so the workflows can find their prompt files (they
reference paths inside the *caller* repo by default — pass
`prompt-file:` to override).

---

## Option C — Copy `.github/` directly (for existing repos)

```bash
# from your repo root
git clone --depth=1 https://github.com/bamr87/githubai /tmp/githubai-template
cp -r /tmp/githubai-template/.github/prompts        .github/
cp -r /tmp/githubai-template/.github/instructions   .github/
cp    /tmp/githubai-template/.github/workflows/agentic-*.yml      .github/workflows/
cp    /tmp/githubai-template/.github/workflows/copilot-setup-steps.yml .github/workflows/
cp    /tmp/githubai-template/AGENTS.md              .
cp -r /tmp/githubai-template/.vscode/mcp.json       .vscode/
cp -r /tmp/githubai-template/examples/workflows     examples/
```

Then follow [CUSTOMIZATION.md](CUSTOMIZATION.md) to replace placeholders.

---

## Required repository settings

For the workflows to function, enable in **Settings → …**:

- **Actions → General → Workflow permissions:** *Read and write permissions*
  (or grant per-job — the workflows do declare scoped `permissions:` blocks).
- **Actions → General → Allow GitHub Actions to create and approve pull
  requests.**
- **Models → Enabled** (for `actions/ai-inference` against GitHub-hosted
  models).
- **Copilot → Coding agent → Enabled** (optional — only if you want
  `@copilot` task delegation).

No external API keys are needed by default — `actions/ai-inference` uses
the GitHub-hosted model catalog with `GITHUB_TOKEN`.

---

## What each workflow does

| Workflow | Trigger | Purpose |
| --- | --- | --- |
| `agentic-review.yml` | PR | Posts a structured AI code review comment |
| `agentic-track.yml` | Issue | Triages, labels, optionally decomposes |
| `agentic-analyze.yml` | Schedule / manual | Opens issues for code/doc/dep gaps |
| `agentic-improve.yml` | Push to main | PR with doc updates + semver bump |
| `agentic-prd-sync.yml` | Schedule | PR aligning `PRD.md` / `README.md` / `IP.md` |
| `agentic-feedback-to-issue.yml` | Issue with `feedback` label | Refines into structured issue |
| `copilot-setup-steps.yml` | Coding agent boot | Installs language toolchains |
| `agentic-lint.yml` | PR / push (in this repo) | Validates prompt + workflow files |

---

## Customizing behavior

- **Tweak agent behavior** → edit `.github/prompts/*.prompt.md` (no YAML changes needed).
- **Add path-specific guidance** → add `.github/instructions/<name>.instructions.md` with an `applyTo:` glob.
- **Switch models** → pass `with: { model: anthropic/claude-3-5-sonnet }` to the reusable workflow.
- **Add MCP tools for chat** → edit `.vscode/mcp.json`.

---

## Migrating from the legacy Django stack

If you're an existing GitHubAI user running the Django app, see
[MIGRATION.md](MIGRATION.md) for a service-by-service mapping from the old
REST API and management commands to the new workflows.
