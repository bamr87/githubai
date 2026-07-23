# Repo-type profiles

A profile is a YAML file that encodes the standards and automation posture for one kind of repository. The consumer repo picks a profile with `repo.type` in `.github/githubai.yml`, and the [load-config action](../actions/load-config/) resolves the effective configuration in three layers: `_base.yml` first, then the selected profile, then the consumer's `githubai.yml`. Maps merge deeply; lists replace the inherited value outright.

| Profile | For |
|---------|-----|
| `library` | Packages other code depends on (npm, PyPI, crates, gems) |
| `webapp` | Deployable web applications serving end users |
| `service` | Backend services, APIs, workers, daemons |
| `cli` | Command-line tools distributed to end users |
| `github-action` | Repos shipping a GitHub Action or reusable workflows |
| `docs` | Documentation sites, handbooks, knowledge bases |
| `data` | Datasets, pipelines, notebooks, analytics/ML code |
| `template` | Template/framework repos other repos adopt (this repo uses it) |

## Anatomy of a profile

Every profile sets three kinds of things:

- `profile.guidance` — prose standards injected verbatim into every Claude prompt (triage, review, implement, maintenance). This is where "what good looks like" for the repo type lives.
- `automation.*` overrides — e.g. `review.focus` areas, or a tighter `auto_merge.allowed_paths` for risk-heavy repo types.
- `standards.*` overrides — required files and documentation expectations checked during maintenance runs.

## Adding a profile

Create `profiles/<name>.yml` with at least `profile.name`, `profile.description`, `profile.guidance`, and `repo.type: <name>`. Keep guidance to the standards that genuinely differ from `_base.yml` — the base already covers universal rules. Then add the name to the table above and to the installer's detection hints in [`setup/install.sh`](../setup/install.sh) if it is auto-detectable. The test suite validates structure automatically.
