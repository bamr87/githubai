# AGENTS.md

> This file describes the AI agents that operate on **{{PROJECT_NAME}}** and how
> they collaborate. It is the human-readable counterpart to
> `.github/copilot-instructions.md` and the prompt files in `.github/prompts/`.

## Where the agents live

| Surface                       | Used for                                              | Configured by                                    |
| ----------------------------- | ----------------------------------------------------- | ------------------------------------------------ |
| GitHub Copilot Chat (IDE)     | Day-to-day Q&A, in-editor edits                       | `.github/copilot-instructions.md`, `instructions/*` |
| Copilot prompt files          | Reusable single-shot tasks (review, triage, docs)     | `.github/prompts/*.prompt.md`                    |
| Copilot coding agent          | Multi-file tasks delegated from issues / `@copilot`   | `.github/workflows/copilot-setup-steps.yml`      |
| Reusable workflows (CI)       | Headless automation (PR review, scheduled scans)      | `.github/workflows/agentic-*.yml`                |
| MCP tools                     | Filesystem + GitHub access from chat / agents         | `.vscode/mcp.json`                               |

## Personas

Each persona is a *role* — the same model can play any of them by being
invoked with the corresponding prompt file.

### 🧑‍⚖️ Reviewer

- **Prompt:** `.github/prompts/review-pr.prompt.md`
- **Workflow:** `agentic-review.yml`
- **Trigger:** `pull_request` (opened, synchronize, ready_for_review)
- **Outputs:** A single PR comment with blocking issues / suggestions / nits.

### 🗂️ Triager

- **Prompt:** `.github/prompts/triage-issue.prompt.md`
- **Workflow:** `agentic-track.yml`
- **Trigger:** `issues` (opened, reopened, edited)
- **Outputs:** Labels applied, optional sub-issues, a triage comment.

### 🔍 Scanner

- **Prompt:** `.github/prompts/auto-issue-scan.prompt.md`
- **Workflow:** `agentic-analyze.yml`
- **Trigger:** `schedule` (weekly) or `workflow_dispatch`
- **Outputs:** New issues for code-quality / TODOs / doc gaps / etc.

### 📝 Scribe

- **Prompts:** `.github/prompts/generate-docs.prompt.md`, `.github/prompts/bump-version.prompt.md`
- **Workflow:** `agentic-improve.yml`
- **Trigger:** `push` to default branch
- **Outputs:** A PR with doc updates and (optionally) a version bump.

### 📐 PRD Architect

- **Prompt:** `.github/prompts/prd-distill.prompt.md`
- **Workflow:** `agentic-prd-sync.yml`
- **Trigger:** `schedule` (weekly) or `workflow_dispatch`
- **Outputs:** A PR updating `PRD.md` / `README.md` / `IP.md` and follow-up issues.

### 📨 Intake

- **Prompt:** `.github/prompts/feedback-to-issue.prompt.md`
- **Workflow:** `agentic-feedback-to-issue.yml`
- **Trigger:** `issues` opened with the `feedback` label
- **Outputs:** The same issue, rewritten into the appropriate template shape and labeled.

## Collaboration rules

1. **Triage first, act second.** New issues always go through the Triager
   before any other agent acts on them.
2. **One PR per agent run.** Agents that write to the repo open exactly one
   PR labeled `agentic` so humans can review.
3. **Humans hold the merge button.** No agent merges PRs automatically. No
   agent closes issues automatically.
4. **Least privilege.** Each workflow declares the minimum `permissions:`
   block required. The Copilot coding agent runs with its own scoped token.
5. **Prompt files are source of truth.** If an agent's behavior needs to
   change, edit the prompt file — not the workflow YAML.

## Invoking from another repo

Pick what you need from `examples/workflows/` and drop it into your repo's
`.github/workflows/` directory. The reusable workflows here are versioned
by Git ref:

```yaml
uses: bamr87/githubai/.github/workflows/agentic-review.yml@main
```

See [docs/template/USAGE.md](docs/template/USAGE.md) for the full guide.
