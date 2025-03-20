# 🚀 AI-Driven GitHub Issue Automation

This repository implements an advanced, AI-powered automation feature for structuring and managing GitHub Issues. It leverages **OpenAI's GPT-4** and **GitHub Actions** to automatically create detailed and structured sub-issues (like functional requirements or test plans) based on generic issues (feature requests or bug reports).

---

## ✨ Features

- **Fully Automated Workflow**: Issues created by users automatically trigger structured sub-issue generation.
- **Template-Driven**: Flexible templates define how OpenAI structures issue content.
- **Unified Approach**: Single workflow handles multiple issue types without additional setup.
- **Scalable and Maintainable**: Easily add new issue types or templates with minimal changes.

---

## 📂 Repository Structure

```
my-repo/
├── .github/
│   ├── workflows/
│   │   └── openai-issue-processing.yml
│   └── ISSUE_TEMPLATE/
│       ├── feature_request_generic.md
│       ├── feature_functional_requirements.md
│       ├── bug_report_generic.md
│       └── bug_test_plan.md
└── openai/
    ├── create_sub_issue.py
    ├── requirements.txt
    └── README.md
```

---

## 🔧 Getting Started

### Prerequisites
- A GitHub repository.
- OpenAI API access ([Get your API key here](https://platform.openai.com/api-keys)).

### Step-by-Step Installation

#### 1. Set Up GitHub Secrets
- Navigate to your repository settings:
  ```
  Settings → Secrets and variables → Actions
  ```
- Add the following secrets:
  - `OPENAI_API_KEY`: Your OpenAI API Key.
  - Optional: `OPENAI_ORG_ID`: Your OpenAI Organization ID (if applicable).

#### 2. Define Issue Templates

Place your issue templates under `.github/ISSUE_TEMPLATE/`. Each template must include YAML front matter and a hidden comment indicating its filename:

Example (`feature_functional_requirements.md`):

```md
---
name: Feature Functional Requirements
about: AI-generated functional requirements based on feature request
title: "[Functional Requirements]: "
labels: functional-requirements
prompt: |
  Generate structured functional requirements based on the original feature request provided.
---

<!-- template: feature_functional_requirements.md -->

## Overview of the Feature

## Functional Specifications

## Acceptance Criteria

## Dependencies

## Risks & Mitigations
```

#### 3. Set Up GitHub Actions Workflow

Create `.github/workflows/openai-issue-processing.yml`:

```yaml
name: OpenAI Unified Issue Processing

on:
  issues:
    types: [opened]

permissions:
  issues: write

jobs:
  process-issue:
    runs-on: ubuntu-latest
    env:
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
      OPENAI_ORG_ID: ${{ secrets.OPENAI_ORG_ID }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r githubai/requirements.txt
      - run: |
          python githubai/create_sub_issue.py \
            --repo "${{ github.repository }}" \
            --parent-issue-number "${{ github.event.issue.number }}"
```

#### 4. Install Python Dependencies

From your project's root directory, install the dependencies:

```bash
pip install -r openai/requirements.txt
```

---

## ⚙️ Usage

- Create a new GitHub Issue using your defined templates.
- The automation automatically creates a structured sub-issue linked to the original issue.

---

## 🧹 Troubleshooting

**403 Forbidden Error:**
- Ensure the workflow YAML includes:
  ```yaml
  permissions:
    issues: write
  ```

**OpenAI API Errors:**
- Check API key and permissions at [platform.openai.com](https://platform.openai.com).

---

## 🔒 Security Best Practices

- Never commit API keys directly to your repository.
- Regularly rotate your OpenAI API keys.
- Limit permissions to exactly what your workflow requires.

---

## 🤝 Contributing

Contributions, suggestions, and issues are welcome! Please create a GitHub Issue or Pull Request.

---

## 📄 License

MIT © Barody Broject

