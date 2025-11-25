# API Reference Documentation

This directory contains **auto-generated API documentation** for GitHubAI using Sphinx.

## Overview

The API reference is automatically generated from Python docstrings in the source code using Sphinx with the following extensions:

- **sphinx.ext.autodoc**: Auto-generates documentation from docstrings
- **sphinx.ext.napoleon**: Supports Google-style and NumPy-style docstrings
- **sphinx.ext.viewcode**: Adds links to highlighted source code
- **sphinxcontrib-django**: Django-specific documentation support
- **sphinx-autodoc-typehints**: Type hint documentation
- **myst-parser**: Markdown support in documentation

## Building Documentation

### Local Build (Docker)

```bash
# Install dependencies (already in requirements-dev.txt)
docker-compose -f infra/docker/docker-compose.yml exec web pip install -r requirements-dev.txt

# Build HTML documentation
docker-compose -f infra/docker/docker-compose.yml exec web bash -c "cd docs/api-reference && make html"

# View generated docs (open in browser)
open docs/api-reference/_build/html/index.html
```

### Live Reload (Development)

```bash
# Start sphinx-autobuild for live preview
docker-compose -f infra/docker/docker-compose.yml exec web bash -c "cd docs/api-reference && make livehtml"
# Then open http://localhost:8000 in your browser
```

### Using Makefile

```bash
cd docs/api-reference

# Build HTML
make html

# Build and watch for changes
make livehtml

# Clean build artifacts
make clean

# Install dependencies
make install
```

## Documentation Structure

```
docs/api-reference/
├── conf.py              # Sphinx configuration
├── index.rst            # Main documentation index
├── models.rst           # Auto-generated model docs (12 models)
├── services.rst         # Auto-generated service docs (8 services)
├── views.rst            # Auto-generated view/API docs
├── serializers.rst      # Auto-generated serializer docs
├── management.rst       # Management command docs
├── Makefile             # Build automation
├── _build/              # Generated HTML (gitignored)
├── _static/             # Custom CSS/JS
└── _templates/          # Custom Jinja2 templates
```

## What's Documented

### Auto-Generated from Code

✅ **Models** (`core.models`): 12 database models including:

- AI Provider models (AIProvider, AIModel, APILog, AIResponse)
- Prompt management (PromptTemplate, PromptSchema, etc.)
- Issue models (Issue, IssueTemplate, IssueFileReference)
- Documentation & versioning models

✅ **Services** (`core.services`): Business logic layer including:

- AIService (AI provider abstraction)
- GitHubService (GitHub API integration)
- IssueService, AutoIssueService
- DocGenerationService, VersioningService

✅ **Views** (`core.views`): REST API endpoints

- IssueViewSet (CRUD operations)
- ChatView (AI chat interface)
- HealthCheckView

✅ **Serializers** (`core.serializers`): DRF serializers for API data

✅ **Management Commands**: CLI tools (auto_issue, generate_docs, bump_version, etc.)

### Manual Documentation

The following remain as **manually curated Markdown files** in `docs/`:

- User guides (`docs/guides/`)
- Getting started (`docs/GETTING_STARTED.md`)
- Feature documentation (`docs/features/`)
- API usage examples (`docs/api/`)
- Release notes (`docs/releases/`)

## Contributing

### Improving Documentation

To improve auto-generated documentation, enhance the **docstrings in source code**:

1. **Use Google-style docstrings**:

   ```python
   def my_function(param1, param2):
       """Brief description.

       Longer description with more details about what the function does.

       Args:
           param1 (str): Description of param1
           param2 (int): Description of param2

       Returns:
           dict: Description of return value with structure

       Raises:
           ValueError: When param1 is invalid

       Example:
           >>> result = my_function("test", 42)
           >>> print(result)
           {'status': 'success'}
       """
   ```

2. **Add type hints** (required for quality autodoc):

   ```python
   def my_function(param1: str, param2: int) -> dict:
       ...
   ```

3. **Document all public methods and classes**

4. **Rebuild docs** to see changes:

   ```bash
   make html
   ```

### Documentation Quality Standards

- **Class docstrings**: Required for all models, services, views, serializers
- **Method docstrings**: Required for all public methods
- **Args/Returns/Raises**: Document all parameters and return values
- **Type hints**: Use type annotations for all function signatures
- **Examples**: Include usage examples where helpful

## Configuration

### Sphinx Settings (`conf.py`)

Key configurations:

- **Django integration**: `os.environ['DJANGO_SETTINGS_MODULE'] = 'githubai.settings'`
- **PYTHONPATH**: Adds `apps/` directory to path
- **Theme**: Read the Docs theme (`sphinx_rtd_theme`)
- **Extensions**: autodoc, napoleon, viewcode, intersphinx, autosummary
- **Napoleon**: Google-style docstrings enabled
- **Intersphinx**: Links to Python, Django, Celery docs

### Customization

- **Theme**: Edit `html_theme` in `conf.py`
- **CSS**: Add custom styles to `_static/custom.css`
- **Templates**: Override templates in `_templates/`
- **Extensions**: Add more Sphinx extensions to `extensions` list

## Deployment

### GitHub Pages

Add to `.github/workflows/docs.yml`:

```yaml
name: Build Documentation

on:
  push:
    branches: [main]

jobs:
  build-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: pip install -r requirements-dev.txt
      - name: Build docs
        run: |
          cd docs/api-reference
          make html
      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: docs/api-reference/_build/html
```

### Read the Docs

1. Sign up at <https://readthedocs.org/>
2. Import GitHubAI repository
3. Configure build:
   - Python version: 3.12
   - Requirements file: `requirements-dev.txt`
   - Configuration file: `docs/api-reference/conf.py`

## Troubleshooting

### Import Errors

If you see `failed to import class/module` warnings:

1. Check `PYTHONPATH` in `conf.py`
2. Verify Django settings are loaded: `django.setup()`
3. Ensure class names in `.rst` files match actual code

### Missing Docstrings

If classes/methods don't appear in docs:

1. Add docstrings to source code
2. Use `:undoc-members:` directive to show undocumented items
3. Check autodoc settings in `conf.py`

### Build Errors

```bash
# Clean and rebuild
make clean
make html

# Check for Python syntax errors
python -m py_compile apps/core/models.py

# Verify Django can import modules
python manage.py shell -c "from core.models import *"
```

## Resources

- [Sphinx Documentation](https://www.sphinx-doc.org/)
- [sphinxcontrib-django](https://github.com/sphinxcontrib/sphinxcontrib-django)
- [Google Style Docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- [Read the Docs Theme](https://sphinx-rtd-theme.readthedocs.io/)
