# Sphinx Documentation Quick Start

This guide shows you how to build and view the auto-generated API documentation.

## Quick Commands

### Build Documentation Once

```bash
# From project root
docker-compose -f infra/docker/docker-compose.yml exec web bash -c "cd docs/api-reference && make html"

# View locally
open docs/api-reference/_build/html/index.html
```

### Live Documentation Server (Auto-rebuild on changes)

```bash
# Start the docs service (runs on port 8001)
docker-compose -f infra/docker/docker-compose.yml up docs

# Open in browser
open http://localhost:8001
```

The live server automatically rebuilds documentation when you edit:

- Source code docstrings
- RST files in `docs/api-reference/`

## What You'll See

The generated documentation includes:

- **Models** - All 12 database models with fields and relationships
- **Services** - Business logic layer (AIService, GitHubService, etc.)
- **Views** - REST API endpoints and ViewSets
- **Serializers** - DRF serializers for API data
- **Management Commands** - CLI tools (auto_issue, generate_docs, etc.)

## Improving Documentation

To improve the auto-generated docs, enhance docstrings in source code:

### Example: Good Docstring

```python
def create_issue(self, repo: str, title: str, body: str) -> Issue:
    """Create a new GitHub issue.

    This method creates an issue in the specified repository using the
    GitHub API and saves a reference in the database.

    Args:
        repo (str): Repository in format 'owner/repo'
        title (str): Issue title
        body (str): Issue body content in Markdown

    Returns:
        Issue: Created Issue model instance

    Raises:
        ValueError: If repo format is invalid
        GitHubAPIError: If GitHub API call fails

    Example:
        >>> service = IssueService()
        >>> issue = service.create_issue(
        ...     repo="owner/repo",
        ...     title="Bug: Login fails",
        ...     body="Steps to reproduce..."
        ... )
        >>> print(issue.github_number)
        42
    """
    # Implementation...
```

### Docstring Guidelines

1. **First line**: Brief one-line summary (< 80 chars)
2. **Blank line** after summary
3. **Args section**: Document all parameters with types
4. **Returns section**: Describe return value and type
5. **Raises section**: List all exceptions that can be raised
6. **Example section**: Show usage example (optional but helpful)

### Type Hints

Always add type hints - Sphinx uses them for better documentation:

```python
# Good
def process_data(input: dict, count: int = 5) -> list[str]:
    ...

# Not as good
def process_data(input, count=5):
    ...
```

## Configuration

All Sphinx settings are in `docs/api-reference/conf.py`:

- **Django integration**: Loads Django settings automatically
- **Extensions**: autodoc, napoleon, viewcode, etc.
- **Theme**: Read the Docs theme
- **Intersphinx**: Links to Python/Django docs

## Troubleshooting

### Documentation not updating?

```bash
# Clean build and rebuild
docker-compose -f infra/docker/docker-compose.yml exec web bash -c "cd docs/api-reference && make clean && make html"
```

### Import errors in build?

Check that:

1. Django settings load correctly
2. PYTHONPATH includes `apps/` directory
3. All dependencies are installed

### Class/method not appearing?

Ensure:

1. Class/method has a docstring
2. Class/method is not private (doesn't start with `_`)
3. Module is imported in RST file with `.. automodule::`

## Next Steps

- Review [API Reference README](README.md) for complete documentation
- Check [Contributing Guidelines](../development/contributing.md)
- See [Django Implementation Guide](../development/django-implementation.md)
