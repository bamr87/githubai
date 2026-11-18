<!-- kit: governance v0.1.0 -->
# 0002 — Missions

- **Status:** proposed
- **Date:** 2026-11-16
- **Proposed by:** Grok Bot (agent), at the maintainer's request
- **Ratified by:**
- **Affects:** constitution §1; PRD §1.1; feature GHAI-007
- **Supersedes:** none
- **Related:** [docs/PRD.md](../../docs/PRD.md) §1.1; feature GHAI-007

## Context

Constitution §1 Mission was a product description (or, for a new constitution, had not been written yet), not a three-mission direction statement. The fleet now requires every repo's constitution §1 to be one direction statement followed by exactly three numbered missions, adopted through a numbered amendment the maintainer ratifies by merging. The maintainer asked for those missions to be comprehensive and epic: GitHubAI as the ultimate open home for all things AI-assisted software delivery. Mission 1 follows the maintainer's wording, adapted to this domain: provide data, tools, resources and transparency for all stakeholders, domain practitioners and the general public. The ambition is the direction, not a claim that the work is already finished. The missions are aligned with this repo's existing constitution and PRD.

## Amendment

Replace constitution §1 with the following, retitled **Missions**:

GitHubAI's direction is to become the ultimate open home for all things AI-assisted software delivery — data, tools, resources and transparency, gathered in one place that anyone can inspect and reuse.

1. **Provide data, tools, resources and transparency for all stakeholders, maintainers and software practitioners, and the general public.** Repository owners, contributors and anyone adopting an AI staff engineer are first-class audiences. The aim is a shared, inspectable commons: the same workflows, the same authentication model, and the same authorization points for everyone.
2. **Give every repository an installable Claude Code loop across the whole software-delivery life cycle — issue triage, label-gated implementation, PR review, a guarded auto-merge lane, weekly maintenance and release drafting.** One install command is the path in; the north star is that every repository can ship with an AI staff engineer, while humans retain the authorization points that matter.
3. **Keep those lanes reusable, reviewable and policy-safe: open workflow source, scoped permissions, and authentication by the maintainer's own Claude Code OAuth token, with no hidden runtime.** The framework should be something a maintainer can read, fork and trust, not a black box running on someone else's servers.

These missions set the course; they do not claim the work is finished. They serve the PRD's north star: Claude Code as a first-class participant in the whole SDLC, installable in any repo in one command.

_Source: [PRD.md](PRD.md) §1.1._


Existing §1 normative content is preserved under the missions, not dropped:

### Current product promise

The following user-story, previously the whole of §1, remains the near-term promise these missions aim at:

1. As a maintainer, I run one install command and my repo gains issue triage, label-gated implementation, PR review, an auto-merge lane, weekly maintenance, and release drafting — all authenticated by my `CLAUDE_CODE_OAUTH_TOKEN`.

## Consequences

Agents and reviewers judge fit against these three missions before inventing scope, treating them as the direction of the repo rather than a description of what already ships. The same text is added as PRD §1.1 so the constitution's `_Source:` line stays accurate. The original PRD purpose / overview paragraph is left in place. This PR also aligns the README and AGENTS.md taglines with the missions and links them to constitution §1, and adds feature GHAI-007 to the feature catalog, traced to requirement MR1. Merging this PR ratifies amendment 0002. Until then the record stays `Status: proposed`.
