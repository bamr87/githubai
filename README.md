# Automated Versioning with GitHub Actions

This repository includes workflows and tools to automate versioning, documentation, and issue management for Python projects. It leverages GitHub Actions and OpenAI to streamline development processes.

## Key Features

### 1. AI-Powered Documentation Generation
- Automatically generates changelogs and documentation summaries using OpenAI.
- Includes a workflow (`auto-doc-generator.yml`) that triggers on pushes to the `main` branch.
- Supports pull request-specific documentation updates via `auto-doc-generator-pr.yml`.

### 2. Enhanced Issue Management
- AI-driven issue templates for feature requests, bug reports, and README updates.
- Automatically generates structured sub-issues and README updates based on user input.
- Templates are YAML-driven for consistency and customization.

### 3. Automated Versioning
- Semantic versioning based on commit message tags (`[major]`, `[minor]`, `[patch]`).
- Workflow (`versioning.yml`) updates the version, creates Git tags, and optionally publishes to PyPI.

## Setup Instructions

### Prerequisites
- A GitHub repository with a Python project.
- GitHub Actions enabled for the repository.
- OpenAI API access ([Get your API key here](https://platform.openai.com/api-keys)).

### Installation & Setup

#### Step 1: Clone Repository
```bash
git clone https://github.com/yourusername/yourproject.git
cd yourproject
```

#### Step 2: Set Up Python Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
```

#### Step 3: Configure GitHub Actions
Copy the provided workflows (`versioning.yml`, `auto-doc-generator.yml`, `openai-issue-processing.yml`) into `.github/workflows/`.

#### Step 4: Define Issue Templates
Add the provided templates into `.github/ISSUE_TEMPLATE/`, customizing prompts as needed.

#### Step 5: Set Up GitHub Secrets
Navigate to `Settings → Secrets and variables → Actions`, then add:
- `OPENAI_API_KEY`: Your OpenAI API Key.
- `GITHUB_TOKEN`: Your GitHub token.

## Usage

### Automated Documentation
- Push changes to the `main` branch to trigger documentation updates.
- For pull requests, use the `feature-documentation` branch to generate PR-specific documentation.

### Issue Management
- Create issues using the provided templates to trigger AI-driven content generation.

### Versioning
- Use commit messages with `[major]`, `[minor]`, or `[patch]` tags to control version increments.

## Example Commit Messages

- To increment the major version:
  ```
  feat: Add new feature [major]
  ```

- To increment the minor version:
  ```
  feat: Add new feature [minor]
  ```

- To increment the patch version (default):
  ```
  fix: Fix a bug [patch]
  ```

## Conclusion

This repository provides a comprehensive solution for automating versioning, documentation, and issue management, enhancing productivity and consistency in Python projects.
