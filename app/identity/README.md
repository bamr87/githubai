# The agent identity App

> A GitHub App you register once and own, so every commit, pull request, comment and label your Claude Code agents make is authored by a bot you can review and approve, from Actions and from interactive sessions alike.

## Why it exists

Without it, an agent writes to GitHub as whoever's credentials it was handed:

- **Your personal access token.** The work is authored by you, so GitHub never asks you to review it and never lets you approve it, and a merge "by you" may have been the agent.
- **The shared Claude GitHub App** (`claude[bot]`, through `claude-code-action`'s own token exchange). It works only inside Actions, it is the same bot in every repository on GitHub, and nothing in a local or cloud session can act as it.
- **The workflow's `GITHUB_TOKEN`.** Pull requests it opens start no CI.

The agent identity App replaces all three with one identity you own, `<name>[bot]`:

- **You can review and approve.** The agent is the author, so `CODEOWNERS` requests your review, your approval is a real one, and a ruleset can require it. GitHub never lets an App approve its own pull request.
- **Attribution is exact.** Commits carry the bot's noreply address, so GitHub shows the bot as their author, and one search lists everything the agent did: `is:pr author:app/<name>`.
- **CI runs.** Installation tokens start workflows, unlike `GITHUB_TOKEN`.
- **Nothing long-lived.** Tokens last one hour, are scoped to one repository where the tools can, and are minted inside your own runs. There is no webhook and no server, so nothing runs outside your Actions and your terminal (constitution § 1, mission 3).

Claude's own authentication does not change: the model is still reached with your `CLAUDE_CODE_OAUTH_TOKEN`. The App only decides who the agent is on GitHub.

## Register it

From a clone of this repository, on a machine with a browser:

```bash
python3 app/identity/register.py
```

```bash
python3 app/identity/register.py --org my-org --name my-org-claude
```

The script serves one page on `127.0.0.1:8719`. You submit it, confirm the name on GitHub, and GitHub sends a one-time code back to the script, which exchanges it for the App's credentials. It keeps the private key at `~/.config/githubai/<slug>.pem` (mode 0600) and the non-secret details beside it in `<slug>.json`, discards the client and webhook secrets (the App needs neither), and prints the next three steps. `--dry-run` prints the manifest without starting anything. The permissions are in [`manifest.json`](manifest.json):

| Permission | Access | Why |
| --- | --- | --- |
| Contents | write | push branches |
| Pull requests | write | open, update and comment on pull requests, and approve in the auto-merge lane (never its own) |
| Issues | write | triage labels and comments |
| Workflows | write | push a branch that changes `.github/workflows/` (the implement and maintenance lanes may) |
| Actions, Checks | read | read CI results |
| Metadata | read | required by GitHub |

It has no administration, secrets, members or environments access, and subscribes to no events.

## Install it and store two secrets

1. Install it on the repositories its agents may write to (the link the script printed, or `https://github.com/apps/<slug>/installations/new`).
2. Store the client id and the key as Actions secrets, per repository or once per organization:

   ```bash
   gh secret set AGENT_APP_CLIENT_ID --body '<client id>' --repo owner/repo
   ```

   ```bash
   gh secret set AGENT_APP_PRIVATE_KEY --repo owner/repo < ~/.config/githubai/<slug>.pem
   ```

That is all the lanes need. Every reusable workflow declares both secrets as optional, and the installed stubs pass `secrets: inherit`.

## What changes in the lanes

Each `claude*.yml` workflow mints a token with `actions/create-github-app-token` when both secrets exist, resolves the bot's login and user id with [`actions/agent-identity`](../../actions/agent-identity/action.yml), and hands both to `claude-code-action` (`github_token`, `bot_id`, `bot_name`) and to its own `gh` steps. When either secret is missing, the token is empty and the action falls back to `claude-code-action`'s own defaults, so a lane without the App behaves exactly as before. `tests/test_identity.py` holds every lane to this.

| Lane | Without the App | With the App |
| --- | --- | --- |
| implement | the PR is opened by the Claude GitHub App | the PR is opened by `<name>[bot]`, CI runs on it, and your review is requested through `CODEOWNERS` |
| review, triage, `@claude` | comments from `claude[bot]` | comments from `<name>[bot]` |
| auto-merge | approved by `github-actions[bot]` | approved by `<name>[bot]`; it can never approve a PR it authored |
| maintenance, release | as `claude[bot]` | as `<name>[bot]` |

## Sessions: hand the pull request to the agent

An interactive session pushes with the credentials of the person driving it. For the pull request to be authored by the agent, the session only pushes a `claude/` branch, and [`agent-handoff.yml`](../../.github/workflows/agent-handoff.yml) (installed as a stub) does the rest:

1. It runs on a push to `claude/**` by a person, not a bot.
2. It mints the App's token and opens a draft pull request from the branch as `<name>[bot]`. The title is the first commit's subject, and the body lists the commits and any `Claude-Session:` or `Claude-Run:` links in them.
3. It asks the person who pushed to review it.

A later push updates the same pull request. Without the App's secrets it leaves a notice and opens nothing. `vars.AGENT_HANDOFF_ENABLED=false` turns it off.

## Act as it from a terminal

[`agent_token.py`](agent_token.py) mints a one-hour token for one repository and runs a command with it, without printing it:

```bash
python3 app/identity/agent_token.py --app <slug> --repo owner/repo whoami
```

```bash
python3 app/identity/agent_token.py --app <slug> --repo owner/repo -- gh pr create --draft --fill
```

```bash
python3 app/identity/agent_token.py --app <slug> --repo owner/repo -- claude
```

The command gets `GH_TOKEN` and the bot's `GIT_AUTHOR_*` and `GIT_COMMITTER_*` variables, so `gh` acts as the bot, and so does `git push` once `gh auth setup-git` has made `gh` git's credential helper. The last example starts a Claude Code session that writes as the bot for that hour. The script signs the App's JWT with `openssl` and needs no Python packages. `env` mode prints `export` lines for your own shell and is the one mode that shows the token.

## Rotate, revoke, remove

- **Rotate the key:** in the App's settings, generate a new private key, update `AGENT_APP_PRIVATE_KEY`, then delete the old key there.
- **Revoke at once:** suspend the installation, or uninstall the App. Every token it minted stops working within the hour, and the lanes fall back to their defaults.
- **Remove:** delete the two secrets. The lanes and the handoff go back to exactly what they did before.

## What it is not

- **Not the relay App.** [`../README.md`](../README.md) describes app mode: a public, multi-tenant router whose token only fires `repository_dispatch`. This App is private to you and never receives an event.
- **Not a reviewer.** The App approves only in the auto-merge lane you opted into, and never a pull request it authored. Requiring your approval on the agent's work is a branch rule only you set: a ruleset requiring one approval, with your own admin role allowed to bypass in pull-request mode.
