# ADR 0006 — The agent identity App: one GitHub identity the maintainer owns, for everything the agents write

> An optional, private GitHub App with no webhook, registered by the maintainer from `app/identity/manifest.json`, whose installation token every lane and session writes with, so the agent's work is authored by its own bot and approved by a person.

- **Status**: proposed
- **Date**: 2026-11-22
- **Deciders**: proposed by an agent at the maintainer's request (2026-11-22: "build the GitHub App, incorporate this into the githubai repo", after asking how to tie all of Claude's activity to its own identity so it can be reviewed and approved)
- **Related**: constitution § 1 (missions 2 and 3), § 2 (invariants), § 4 (roles); [app/identity/README.md](../../app/identity/README.md); [docs/security.md](../security.md#authentication); bamr87/bamr87#565 (the fleet's open bot-identity decision) and bamr87/bamr87 ADR 0015 (its default-branch ruleset)

## Context

A lane writes to GitHub with one of three credentials today: the job's `GITHUB_TOKEN`, the shared Claude GitHub App's token that `claude-code-action` obtains through its OIDC exchange, or, in the fleet's hub, the maintainer's own personal token. Each fails the person who must review the agent's work:

- **A personal token makes the maintainer the author.** GitHub never asks an author to review their own pull request and never lets them approve it, so a required approval can never be given, and a merge "by the maintainer" may have been the agent. In the hub's audit, 77 of 173 automated PR comments carried the maintainer's login (bamr87/bamr87#565).
- **The shared Claude App works only inside Actions.** Its token comes from an exchange only `claude-code-action` can make, so a person's interactive session (on the web, in a terminal, in an IDE) cannot act as it. Its pull requests open as the person driving the session.
- **`GITHUB_TOKEN` starts no workflows.** A pull request it opens gets no CI until someone pushes again.

Missions 2 and 3 promise that humans keep the authorization points that matter, with scoped permissions and no hidden runtime. Whether a person can approve the agent's work is such a point.

## Decision

1. **The App.** GitHubAI ships an optional second GitHub App, the agent identity App (`app/identity/`). Each maintainer registers and owns their own: it is private, has no webhook and subscribes to no events. Its permissions are contents, pull requests and issues write, workflows write, actions and checks read, and metadata. `app/identity/register.py` registers it in one step through GitHub's manifest flow on `127.0.0.1`. It keeps the private key at mode 0600 and discards the client and webhook secrets.
2. **The lanes.** Every `claude*.yml` lane declares two optional secrets, `AGENT_APP_CLIENT_ID` and `AGENT_APP_PRIVATE_KEY`. When both exist:
   - the lane mints a one-hour installation token with `actions/create-github-app-token`, scoped to its repository;
   - it resolves the bot's login and user id with `actions/agent-identity`;
   - it passes `github_token`, `bot_id` and `bot_name` to `claude-code-action`, and the token to its own `gh` steps.

   When either secret is missing, the token is empty and `claude-code-action` keeps its own defaults, so the lane is unchanged. Adding optional secrets is additive to the public API.
3. **Sessions hand the PR to the agent.** An interactive session only pushes a `claude/` branch. `agent-handoff.yml`, installed as a stub, opens the draft pull request as the App's bot when a person pushed, and requests that person's review.
4. **Locally.** `app/identity/agent_token.py` mints a token for one repository and runs a command with it, setting `GH_TOKEN` and the bot's git author and committer, without printing it.
5. **Claude's own authentication is untouched.** The model is still reached only with `CLAUDE_CODE_OAUTH_TOKEN` (constitution § 2's first invariant).

## Consequences

**Positive**

- **The person can review and approve.** The agent's pull requests are authored by a bot, so `CODEOWNERS` requests the maintainer's review, their approval is real, and a ruleset can require it. GitHub never lets an App approve a pull request it authored.
- **Attribution is exact.** Commits carry the bot's noreply address, and `is:pr author:app/<slug>` lists everything the agent opened.
- **CI runs** on pull requests the agent opens, unlike with `GITHUB_TOKEN`.
- **One identity on every surface:** Actions, the relay's dispatched runs, web and terminal sessions.
- **No long-lived credential, no runtime.** Tokens are minted inside the maintainer's own runs and expire in an hour.

**Negative**

- **A private key to look after.** The maintainer keeps it in Actions secrets and rotates it in the App's settings.
- **Broader write scope than `GITHUB_TOKEN`.** An installation token is not bounded by a job's `permissions` block. Its bound is the App's permissions and the repositories it is installed on, so the manifest stays least-privilege and `tests/test_identity.py` caps it.
- **The auto-merge lane's approval comes from the App's bot when configured.** It still satisfies a one-approval rule for the pull requests that lane exists for (dependency updates, labelled changes), but never for the agent's own work.
- **The handoff needs the App.** Without it, a session's pull request is still opened by the session's own credentials.

## Alternatives considered

- **Extend the relay App.** It is public and multi-tenant, and its trust promise is that its token only fires `repository_dispatch` (app/README.md). An identity's private key belongs to one maintainer, not to a shared service.
- **Keep the shared Claude App.** It is unreachable from sessions, identical in every repository on GitHub, and not the maintainer's to scope or revoke.
- **A machine user with a personal token.** It works everywhere with one secret, but brings back a long-lived credential, a password and 2FA to keep, and a seat in organizations.
- **`GITHUB_TOKEN` only.** Its pull requests start no CI, and it cannot act outside a workflow run.

## Supersedes / Superseded by

- Supersedes: none
- Superseded by: none
