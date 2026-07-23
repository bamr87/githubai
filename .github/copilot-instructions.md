# Copilot instructions

This repo's canonical agent context is [/CLAUDE.md](../CLAUDE.md); follow it. Non-negotiables: keep the OAuth-first auth pattern in every workflow, treat workflow names/inputs/config keys/labels as public API (add, don't rename), never interpolate issue or PR content into `run:` scripts or prompts, one markdown paragraph per line, and run `python3 -m pytest -q` before proposing changes.
