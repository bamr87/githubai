---
name: README Update Request
about: Request an update to README (generic)
title: "[README Update]: "
labels: README-update
prompt: |
  Generate a structured README file based on the original README file provided and any additional information provided.
template: README_update_template.md
include_files:
  - README.md
  - src/README.md
  - src/githubai/README.md
  - src/readmeai/README.md
---

## What specific information or section do you want to add or modify in the README?

*(Clearly describe what you want added or modified.)*

## Why is this update necessary?

*(Explain clearly why this is needed.)*

## What impact will this update have?

*(Describe the expected impact.)*

## Additional context

*(Any extra context or details.)*


## Include additional files to consider in the update:

include_files_additional:
    - src/readmeai/create_readme_update.py
    - src/githubai/create_sub_issue.py