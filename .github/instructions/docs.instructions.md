---
applyTo: "**/*.md,docs/**"
---

# Documentation Instructions

Conventions for Markdown and documentation in **{{PROJECT_NAME}}**.

## Voice & style

- Active voice, present tense, second person ("You install via…").
- Short sentences. Prefer bullet lists over long paragraphs for procedures.
- Expand acronyms on first use: `Pull Request (PR)`.

## Structure

- One `H1` per file, matching the file's purpose.
- Sentence case for headings.
- Code fences always specify a language: ` ```bash `, ` ```python `, ` ```json `.
- Relative links between docs (`[Usage](./USAGE.md)`), absolute for external.

## Changelog

- Follow [Keep a Changelog](https://keepachangelog.com/) format.
- Group entries under: `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`.
- One bullet per change, present tense, ending without a period.

## README

- The first screenful must answer: *what is this, who is it for, how do I try it in 60 seconds*.
- Keep installation steps copy-pasteable.
- Pin example versions to actual current versions; don't invent.

## What to avoid

- Marketing language ("blazing fast", "best-in-class", "revolutionary").
- Screenshots without alt text.
- Step lists that mix prose and commands without code fences.
- Stale TODOs in published docs — convert them to issues.
