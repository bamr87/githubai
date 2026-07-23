---
description: Analyze a repo and propose its GitHubAI adoption (profile, config, gaps)
---

Analyze the current repository and prepare its GitHubAI adoption. Target repo path (optional): "$ARGUMENTS" (default: cwd).

1. Detect the repo type using the same signals as `setup/install.sh` (action.yml → github-action; mkdocs/docusaurus → docs; notebooks/dvc → data; package.json bin → cli, UI frameworks → webapp, server frameworks → service; pyproject/go.mod/Cargo.toml similarly; else library) and say why.
2. Draft `.github/githubai.yml`: type, a sharp one-sentence `purpose`, `primary_language`, `standards.test_command`/`lint_command` from the repo's actual tooling.
3. Gap report against the chosen profile's standards: missing required files, docs expectations unmet, absent CI, unprotected default branch.
4. Print the exact install command (`setup/install.sh` flags included) and the secret setup steps. Make no changes unless asked.
