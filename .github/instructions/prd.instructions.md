---
applyTo: "**/PRD.md"
description: "Instructions for GitHub Copilot to build, maintain, and evolve the Product Requirements Document (PRD.md) as a living, single-source blueprint for software products. Ensures KISS (Keep It Simple, Stupid), DRY (Don't Repeat Yourself), and MVP (Minimum Viable Product) principles."
---

# PRD Instructions: Building, Maintaining, and Evolving the Ultimate Blueprint

These instructions guide GitHub Copilot in VS Code to generate, edit, and refine `PRD.md`—the one true, living document distilling product requirements into a coherent, evolving reality.

Apply these globally to `PRD.md` edits or generations. When prompted (e.g., "@workspace /generate PRD section"), output Markdown-only updates that fit the template below. Always enforce:
- **KISS**: ≤800 lines total; short sentences; no fluff.
- **DRY**: No duplicates—link to ADRs, tickets, or code.
- **MVP**: Focus on shippable core; defer nice-to-haves to OOS.

Reference the [Ultimate PRD Template](DONTIGNORETHISPRD.md) for structure. If generating from scratch, start with it.

## Core Principles
- **Living Document**: Every edit is a commit; version via Git. Auto-suggest merges on conflicts.
- **Single Source of Truth (SSOT)**: PRD owns requirements; everything else (code, tests) derives from it.
- **Clear Communication**: Expand acronyms on first use, maintain consistent terminology.
- **CCC Enforcement**: Consistency (uniform tone/acronyms), Cross-referencing (hyperlinks), Collaboration (editable prompts like "Add your take here").
- **GROKME Integration**: If repo has GROKME (Grok Readily Optimized Knowledge Management Engine), invoke it to synthesize sections (e.g., auto-pull metrics).

## Template Structure
When generating or editing, strictly adhere to this 10-section skeleton. Output only the changed sections + diffs if editing. Use Markdown tables/lists for scannability.

### 0. WHY (Why Hell-bent Yield)
- 1-sentence north star (e.g., "Empower users to [core value] via [MVP feature].").
- 1 success metric (KFI: Key Focus Indicator, e.g., ">80% retention").
- Brief justification of the core problem being solved.

### 1. MVP (Minimum Viable Promise)
- 3–7 bullet user stories: "As [user], I [action] so [benefit]" (MoSCoW: Must only).
- Prioritize P0/P1 pains; defer via OOS.
- KISS: One story per bullet; link to prototypes.

### 2. UX (User eXperience Flow)
- 1 linear diagram (Mermaid or ASCII).
- 1 Figma/URL link.
- DRY: No prose—visuals only.

### 3. API (Atomic Programmable Interface)
- Table: | Endpoint | Method | Request | Response | Errors |
- Examples as JSON snippets.
- Note: Test with mock/dry-run modes first.

### 4. NFR (Non-Functional Realities)
- Table (<10 rows): | Category | Requirement | Metric |
  - Latency, Scale, Security, Privacy, Accessibility.
- MVP: Baseline only (e.g., "99% uptime").

### 5. EDGE (Exceptions, Dependencies, Gotchas, Errors)
- Bullets: One per item (e.g., "Dep: External API X; Gotcha: Rate limits").
- TDD (Technical Debt Disclaimer): Flag intentional shortcuts.

### 6. OOS (Out Of Scope)
- Bullets: Explicit kills (e.g., "Won't: Multi-language support—post-MVP").
- Be explicit about what's deferred to maintain focus.

### 7. ROAD (Rolling Objectives And Dates)
- Table: | Milestone | Objective | Date/Quarter |
- Next 3 only; use RICE scoring if justifying.

### 8. RISK (Reality-Induced Setback Kilolist)
- Table: | Risk | Impact (RICE) | Mitigation |
- Top 3; one line each.

### 9. DONE (Definition Of “No-more-Engineering-Needed”)
- Checklist: Machine (e.g., "Tests pass 95%") + Human (e.g., "Stakeholder sign-off").
- MVP: Binary—done or not.

## Generation Workflow
- **New PRD**: Prompt like "Create MVP PRD for [product idea]". Output full template filled minimally.
- **Section Edit**: E.g., "Update UX for mobile." Output diff: ```diff:disable-run
- **Evolution**: On repo changes (e.g., new ticket), suggest: "Evolve ROAD based on [commit]."

## Maintenance Rules
- **Consistency**: Active voice, present tense, second person ("You install via..."). Standard acronyms (expand first).
- **Cross-Referencing**: Every link: `[Section X](#section-x)` or external (e.g., `#123`).
- **Collaboration**: Add prompts: "TODO: [Role] review by [date]."
- **Versioning**: Footer: `Version: [date] | Last Evolved: [reason]`.
- **KISS Prune**: If >800 lines, suggest cuts: "DRY this by linking to [file]."

## Evolution Triggers
- **Auto-Suggest**: On PR merges, chat: "Evolve PRD? [Options: Update ROAD, Add RISK]."
- **Quarterly Review**: Re-evaluate WHY section based on metrics and outcomes.
- **GROKME Tie-In**: If enabled, "Grok this PRD section for CCC compliance."

## Best Practices
- Output readable Markdown: H1 for sections, tables/lists for data.
- No code—PRD is prose blueprint.
- If unclear prompt, ask: "Clarify [ambiguity] to KISS."
- Remember: PRDs are living documents—ship and iterate based on reality.

For more, see [Ultimate Template](DONTIGNORETHISPRD.md).
```