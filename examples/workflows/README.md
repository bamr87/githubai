# Examples — caller workflows

These are minimal, copy-pasteable workflows you can drop into **any** repo's
`.github/workflows/` directory to consume the agentic reusable workflows
defined in `.github/workflows/agentic-*.yml` of this template.

| File | What it does |
| --- | --- |
| [`pr-review.yml`](pr-review.yml) | AI review on every PR |
| [`issue-triage.yml`](issue-triage.yml) | Triage / label new issues |
| [`weekly-scan.yml`](weekly-scan.yml) | Scheduled repo health scan that opens issues |
| [`improve-on-push.yml`](improve-on-push.yml) | Auto-doc + version-bump PR on push to main |
| [`prd-sync.yml`](prd-sync.yml) | Weekly PRD/README distill |
| [`feedback-to-issue.yml`](feedback-to-issue.yml) | Refines feedback-form issues into structured ones |

## Pinning

Examples reference `@main` for readability. **In production, pin to a
released tag** (e.g. `@v1`) so a template change can't break your repo
without you opting in:

```yaml
uses: bamr87/githubai/.github/workflows/agentic-review.yml@v1
```

## Required permissions

Each example sets the minimum permissions the reusable workflow needs.
Don't loosen them.

## See also

- [Usage guide](../../docs/template/USAGE.md)
- [Customization & placeholders](../../docs/template/CUSTOMIZATION.md)
- [Migration from the legacy Django stack](../../docs/template/MIGRATION.md)
