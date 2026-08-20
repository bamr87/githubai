# GitHubAI documentation

| Page | What it covers |
|------|----------------|
| [Getting started](getting-started.md) | Adopt GitHubAI in any repo: install, secrets, first issue |
| [Configuration](configuration.md) | Full `.github/githubai.yml` schema and profile merge semantics |
| [Workflows](workflows.md) | Contract of every workflow: triggers, inputs, permissions, behavior |
| [Security](security.md) | Auth model, permissions, untrusted input, the auto-merge gate |
| [Architecture](architecture.md) | Design decisions and the invariants behind them |
| [GitHub App mode](../app/README.md) | Org-scale event routing, org policy, and the activity dashboard |
| [Relay operations](../app/OPERATIONS.md) | Deploying, configuring, monitoring and troubleshooting the relay |
| [Relay data handling](../app/DATA-HANDLING.md) | Exactly what the hosted service stores, and for how long |
| [Marketplace](../app/MARKETPLACE.md) | What is built, what a listing still needs, what is undecided |
| [Migration from v0.x](migration-v0.md) | Where every v0 Django-app feature went |

Repo-type standards live in [profiles/](../profiles/), template files in [template/](../template/), and the product requirements in [PRD.md](../PRD.md).
