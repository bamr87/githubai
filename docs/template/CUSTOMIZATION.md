# Customization & Placeholder Map

The template uses a small set of placeholders so you can adapt it to your
project quickly.

## Placeholders

| Placeholder | Meaning | Example |
| --- | --- | --- |
| `{{PROJECT_NAME}}` | Human-readable project name | `Acme Widgets` |
| `{{PRIMARY_LANGUAGE}}` | Main implementation language | `Python` / `TypeScript` / `Go` |
| `{{AI_PROVIDER}}` | Default model provider | `openai` / `anthropic` / `github` |
| `{{DEFAULT_MODEL}}` | Default model id passed to `actions/ai-inference` | `openai/gpt-4o-mini` |
| `{{REPO_OWNER}}` | GitHub org / user that owns the repo | `acme` |
| `{{REPO_NAME}}` | Repository name | `widgets` |
| `{{DEFAULT_BRANCH}}` | Default branch | `main` |

## Files that contain placeholders

- `.github/copilot-instructions.md`
- `.github/instructions/*.instructions.md`
- `.github/prompts/*.prompt.md`
- `AGENTS.md`
- `examples/workflows/*.yml` (only `bamr87/githubai` references — replace with your fork's path if you fork)

## Quick replace (Bash)

```bash
PROJECT_NAME="Acme Widgets"
PRIMARY_LANGUAGE="Python"

# macOS users: replace `sed -i` with `sed -i ''`
grep -rl '{{PROJECT_NAME}}'    .github AGENTS.md docs | xargs sed -i "s|{{PROJECT_NAME}}|$PROJECT_NAME|g"
grep -rl '{{PRIMARY_LANGUAGE}}' .github AGENTS.md docs | xargs sed -i "s|{{PRIMARY_LANGUAGE}}|$PRIMARY_LANGUAGE|g"
```

## Choosing a model

The default in every reusable workflow is `openai/gpt-4o-mini` (cheap,
fast, GitHub-hosted, works with `GITHUB_TOKEN`). Override per workflow:

```yaml
jobs:
  review:
    uses: bamr87/githubai/.github/workflows/agentic-review.yml@main
    with:
      model: anthropic/claude-3-5-sonnet
```

If you use a model **outside** the GitHub-hosted catalog you'll need to
either:
1. Run a different action (e.g. `anthropics/claude-code-action`) and pass the
   prompt file as the system prompt, or
2. Add a small wrapper workflow that supplies your own `OPENAI_API_KEY` /
   `ANTHROPIC_API_KEY` secret.

## Choosing labels

The triage and scan agents only apply labels that already exist in your
repo. Create the labels you want them to use:

```bash
gh label create chore       --color cccccc --description "Maintenance task"
gh label create code-quality --color fbca04 --description "Code health"
gh label create needs-triage --color d93f0b --description "Awaiting triage"
gh label create needs-clarification --color d4c5f9 --description "More info needed"
gh label create agentic     --color 0e8a16 --description "Created by an AI agent"
gh label create feedback    --color 1d76db --description "Routed via feedback form"
```

## Disabling a persona

Either delete its caller workflow in your `.github/workflows/`, or comment
out the `uses:` line. The reusable workflows in this repo do nothing on
their own — they only run when invoked.
