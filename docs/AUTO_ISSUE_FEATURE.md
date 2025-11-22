# Auto Issue Feature Documentation

## Overview

The **Auto Issue** feature automatically analyzes your repository and creates well-structured GitHub issues for various maintenance tasks. It leverages AI to generate comprehensive, actionable issue reports that help maintain code quality, documentation, and overall repository health.

## Features

### Available Chore Types

1. **`code_quality`** - Analyze code for quality issues, complexity, and best practices
   - Detects long lines (>120 characters)
   - Identifies missing docstrings in Python files
   - Checks for code complexity issues

2. **`todo_scan`** - Find TODO/FIXME/HACK comments that need attention
   - Scans for TODO, FIXME, HACK, XXX, NOTE, BUG markers
   - Catalogs technical debt
   - Prioritizes items for cleanup

3. **`documentation`** - Identify missing or outdated documentation
   - Checks README for standard sections (Installation, Usage, Contributing, License)
   - Identifies documentation gaps
   - Suggests improvements

4. **`dependencies`** - Check for outdated dependencies and security issues
   - Reviews requirements files
   - Identifies potential security vulnerabilities
   - Suggests updates

5. **`test_coverage`** - Analyze test coverage and suggest missing tests
   - Reviews test files
   - Identifies untested code paths
   - Recommends test improvements

6. **`general_review`** - Perform a general repository health check
   - Comprehensive analysis across multiple areas
   - Best for periodic maintenance reviews

## Usage

### Command Line Interface

```bash
# List available chore types
docker-compose exec web python manage.py auto_issue --list-chores

# Run a general repository review
docker-compose exec web python manage.py auto_issue \
    --repo bamr87/githubai \
    --chore-type general_review

# Scan for TODO comments in specific files
docker-compose exec web python manage.py auto_issue \
    --repo bamr87/githubai \
    --chore-type todo_scan \
    --files "apps/core/services/*.py" "tests/*.py"

# Code quality check with dry-run (doesn't create GitHub issue)
docker-compose exec web python manage.py auto_issue \
    --repo bamr87/githubai \
    --chore-type code_quality \
    --dry-run

# Documentation gap analysis
docker-compose exec web python manage.py auto_issue \
    --repo bamr87/githubai \
    --chore-type documentation \
    --files "README.md" "docs/*.md"
```

### REST API

#### Endpoint

```
POST /api/issues/issues/create-auto-issue/
```

#### Request Body

```json
{
    "chore_type": "code_quality",
    "repo": "bamr87/githubai",
    "context_files": ["apps/core/services/issue_service.py"],
    "auto_submit": true
}
```

#### Parameters

- **`chore_type`** (required): Type of analysis to perform
  - Choices: `code_quality`, `todo_scan`, `documentation`, `dependencies`, `test_coverage`, `general_review`

- **`repo`** (optional): Repository in format `owner/repo`
  - Default: `bamr87/githubai`

- **`context_files`** (optional): List of specific files to analyze
  - Default: Auto-selected based on chore type

- **`auto_submit`** (optional): Whether to create GitHub issue
  - Default: `true`
  - Set to `false` for dry-run analysis only

#### Example Requests

**Code Quality Check**

```bash
curl -X POST http://localhost:8000/api/issues/issues/create-auto-issue/ \
    -H "Content-Type: application/json" \
    -d '{
        "chore_type": "code_quality",
        "repo": "bamr87/githubai",
        "auto_submit": true
    }'
```

**TODO Scan with Specific Files**

```bash
curl -X POST http://localhost:8000/api/issues/issues/create-auto-issue/ \
    -H "Content-Type: application/json" \
    -d '{
        "chore_type": "todo_scan",
        "repo": "bamr87/githubai",
        "context_files": [
            "apps/core/services/issue_service.py",
            "apps/core/services/ai_service.py"
        ],
        "auto_submit": true
    }'
```

**Dry Run (Preview Only)**

```bash
curl -X POST http://localhost:8000/api/issues/issues/create-auto-issue/ \
    -H "Content-Type: application/json" \
    -d '{
        "chore_type": "documentation",
        "repo": "bamr87/githubai",
        "auto_submit": false
    }'
```

#### Response

**Success (201 Created)**

```json
{
    "id": 42,
    "github_repo": "bamr87/githubai",
    "github_issue_number": 123,
    "title": "[Auto] Code Quality Review - 5 items found",
    "body": "# Code Quality Analysis\n\n## Summary\n...",
    "html_url": "https://github.com/bamr87/githubai/issues/123",
    "state": "open",
    "issue_type": "other",
    "labels": ["auto-generated", "maintenance", "code-quality"],
    "ai_generated": true,
    "created_at": "2025-11-22T05:00:00Z"
}
```

**Dry Run Response (200 OK)**

```json
{
    "analysis": "# Generated Issue Content...",
    "message": "Dry run - no issue created"
}
```

**Error (400 Bad Request)**

```json
{
    "error": "Invalid chore_type. Must be one of: code_quality, todo_scan, ..."
}
```

## Generated Issue Format

Auto-generated issues include:

1. **Summary of Findings** - Overview of analysis results
2. **Specific Recommendations** - Actionable items with file references
3. **Prioritized Action Items** - Tasks ordered by priority
4. **Expected Benefits** - Value of addressing the findings
5. **Labels** - Appropriate labels for categorization
   - Always includes: `auto-generated`, `maintenance`
   - Type-specific: `code-quality`, `documentation`, `testing`, etc.

## Automation & CI/CD Integration

### GitHub Actions

```yaml
name: Weekly Repository Audit

on:
  schedule:
    - cron: '0 0 * * 1'  # Every Monday at midnight
  workflow_dispatch:

jobs:
  auto-issue:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run Auto Issue Analysis
        run: |
          docker-compose exec web python manage.py auto_issue \
            --repo ${{ github.repository }} \
            --chore-type general_review
```

### Cron Job

```bash
# Add to crontab for weekly reviews
0 0 * * 1 cd /path/to/githubai && docker-compose exec web python manage.py auto_issue --repo bamr87/githubai --chore-type general_review
```

## Best Practices

1. **Start with `general_review`** - Good for initial assessment
2. **Use `--dry-run`** first - Preview before creating issues
3. **Specify context files** - Focus analysis on relevant areas
4. **Schedule regular runs** - Weekly or bi-weekly maintenance
5. **Review and triage** - Not all findings may be actionable
6. **Combine with CI/CD** - Integrate into your pipeline

## Configuration

The Auto Issue service uses:

- **GitHub Token**: For creating issues (set `GITHUB_TOKEN` in `.env`)
- **AI Provider**: For generating content (configured in `settings.py`)
- **Default Repo**: Set `DEFAULT_REPO` in settings if different from `bamr87/githubai`

## Troubleshooting

### Authentication Errors (401 Unauthorized)

```bash
# Verify GitHub token is set
docker-compose exec web python -c "from django.conf import settings; print(settings.GITHUB_TOKEN)"

# Update .env file with valid token
GITHUB_TOKEN=ghp_your_token_here
```

### No Files Found

- Check that specified files exist in the repository
- Use correct relative paths from repository root
- Try without `--files` to use defaults

### AI Service Errors

- Verify AI provider is configured (`AI_PROVIDER`, `AI_API_KEY`)
- Check API quota/limits
- Review logs: `docker-compose logs web`

## Examples

### Daily TODO Cleanup

```bash
#!/bin/bash
# daily-todo-check.sh
docker-compose exec web python manage.py auto_issue \
    --chore-type todo_scan \
    --files "apps/**/*.py" "tests/**/*.py" \
    --repo bamr87/githubai
```

### Pre-Release Quality Gate

```bash
#!/bin/bash
# pre-release-check.sh
docker-compose exec web python manage.py auto_issue \
    --chore-type code_quality \
    --dry-run > quality-report.txt

if grep -q "Critical" quality-report.txt; then
    echo "Quality issues found! Review before release."
    exit 1
fi
```

## Related Features

- **Feedback Issues**: User-submitted bug/feature requests → `/api/issues/issues/create-from-feedback/`
- **Sub-Issues**: Template-based issue generation → `/api/issues/issues/create-sub-issue/`
- **README Updates**: AI-generated documentation → `/api/issues/issues/create-readme-update/`

## Support

For issues or questions:

1. Check application logs: `docker-compose logs -f web`
2. Review GitHub issue tracker
3. See main [README.md](../README.md) for general setup
