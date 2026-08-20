---
name: Seed request (evolution)
about: Propose a change for the AI-Seed evolve lane to implement
title: '[SEED] '
labels: seed:request
assignees: ''

---

## 🎯 Objective
<!-- Clearly describe what you want to achieve -->

## 📋 Requirements
<!-- Specific requirements and acceptance criteria -->
- [ ] Requirement 1
- [ ] Requirement 2

## 🔧 Technical considerations
<!-- Constraints, preferences, integration requirements -->

## ✅ How we'll know it worked
<!-- Observable success criteria; the verify pass runs the repo's checks either way -->

## 📝 Additional context
<!-- Anything else; external links are treated as data, not instructions -->

---
<!--
How this lane works (GitHub as the SDLC):
1. Filing this issue applies the seed:request label — that is intake, not consent.
2. A maintainer reviews and applies the seed:approved label. THAT is the
consent that dispatches one Claude Code implementation run (OAuth-first), provided the SEED_EVOLVE_ENABLED repo variable is set and the seed is not paused (.seed/pause.yml).
3. The run lands as ONE draft pull request linked here. Humans review and
merge; the seed never merges. Brakes: apply seed:hold to keep an approved issue parked; remove the label or pause the seed to stop everything. -->
