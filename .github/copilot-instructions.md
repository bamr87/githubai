# GitHubAI Coding Guidelines

## Project Overview
GitHubAI is a production-ready Django application for AI-powered GitHub automation. Single-app Django architecture with service layer pattern, PostgreSQL, Redis, Celery workers, and Docker containerization.

## Architecture

### Consolidated App Structure
**All functionality is in `apps/core/`** - previously separate apps (ai_services, github_integration, issues, docs, versioning) were merged:
- `models.py`: All domain models (AIProvider, AIModel, PromptTemplate, Issue, etc.)
- `services/`: Business logic services (`AIService`, `GitHubService`, `IssueService`, `AutoIssueService`, `DocGenerationService`, `VersioningService`)
- `views.py`: REST API endpoints (ViewSets and APIViews)
- `admin.py`: Django admin with custom actions for prompt refinement
- `tasks.py`: Celery async tasks
- `management/commands/`: CLI commands

### Service Layer Pattern (Critical)
**Never put business logic in views or models** - always use service classes:
```python
# ✅ Correct: Import and use service
from core.services import AIService
ai_service = AIService()
response = ai_service.call_ai_chat(system_prompt="...", user_prompt="...")

# ❌ Wrong: Don't call AI APIs directly
import openai  # DON'T DO THIS
```

### AI Integration Architecture
- **AIService** (`apps/core/services/ai_service.py`): Central AI interface with:
  - Database-driven provider configuration (`AIProvider`, `AIModel` models)
  - Response caching via `AIResponse` model (saves costs)
  - Usage logging via `APILog` model
  - Provider abstraction via `AIProviderFactory` pattern
- **Prompt Management**: `PromptTemplate` model with versioning, Jinja2 rendering, admin-based refinement
- **Multi-provider support**: OpenAI, XAI (Grok), extensible via provider factory

### Data Models Key Patterns
- **TimeStampedModel**: Base class for all models - auto `created_at`/`updated_at` with indexes
- **Unique constraints**: Names have `unique=True` (e.g., `PromptTemplate.name`, `AIProvider.name`)
- **Versioning pattern**: `parent_version` ForeignKey + `version_number` field (see `PromptTemplate`)
- **Indexes**: Use `db_index=True` on frequently queried fields (status, timestamps, identifiers)

## Development Workflow

### Docker Commands (Always Use Full Paths)
```bash
# Start development (hot-reload enabled)
docker-compose -f infra/docker/docker-compose.yml -f infra/docker/docker-compose.dev.yml up

# Run any command in container
docker-compose -f infra/docker/docker-compose.yml exec web <command>

# Examples:
docker-compose -f infra/docker/docker-compose.yml exec web python manage.py migrate
docker-compose -f infra/docker/docker-compose.yml exec web pytest
docker-compose -f infra/docker/docker-compose.yml exec web python manage.py shell
```

### Testing
```bash
# Run all tests
docker-compose -f infra/docker/docker-compose.yml exec web pytest

# Run specific test file
docker-compose -f infra/docker/docker-compose.yml exec web pytest tests/test_prompt_refinement.py

# Run with coverage
docker-compose -f infra/docker/docker-compose.yml exec web pytest --cov

# Skip integration tests (marked with @pytest.mark.integration)
pytest -m "not integration"
```

**Test Configuration**:
- `pytest.ini`: Django settings, test paths
- `pyproject.toml`: Coverage, markers, addopts
- Integration tests require `--run-integration` flag

### Python Environment
- **PYTHONPATH**: `apps/` added to path in settings.py and docker-compose
- **Import style**: `from core.models import ...` (not `from apps.core.models`)
- **Black**: 120 character line length
- **Logger**: Always use `logger = logging.getLogger('githubai')`

## Critical Patterns

### Service Usage in Views
```python
# Pattern: Import service, instantiate, use methods
from core.services import IssueService, AIService

def my_view(request):
    service = IssueService()
    issue = service.create_sub_issue_from_template(
        repo="owner/repo",
        parent_issue_number=123,
        file_refs=["README.md"]
    )
```

### AI Service Caching Pattern
AIService automatically checks `AIResponse` cache before API calls:
```python
ai_service = AIService()
# This checks cache first, only calls API if cache miss
response = ai_service.call_ai_chat(
    system_prompt="You are a helpful assistant",
    user_prompt="Generate a summary",
    use_cache=True  # default is True
)
```

### Prompt Template Rendering
```python
from core.models import PromptTemplate
from jinja2 import Template

# Prompts use Jinja2 syntax: {{ variable_name }}
prompt = PromptTemplate.objects.get(name="My Prompt")
template = Template(prompt.user_prompt_template)
rendered = template.render(repo="owner/repo", issue_number=123)
```

### Admin Custom Actions Pattern
See `apps/core/admin.py` for examples:
- Define form class inside action method
- Use `request.POST` for submissions
- Render with custom template in `apps/core/templates/admin/`
- Redirect after successful operation

### Version Management
When creating new versions of prompts/models:
```python
# Names must be unique - append version suffix
new_name = f"{base_name} v{new_version_number}"
while PromptTemplate.objects.filter(name=new_name).exists():
    new_name = f"{base_name} v{new_version_number}.{counter}"
    counter += 1
```

## Management Commands
Located in `apps/core/management/commands/`:
```bash
# Create issues
python manage.py create_issue --repo owner/repo --parent 123
python manage.py auto_issue --chore-type code_quality

# Documentation
python manage.py generate_docs --file path/to/file.py

# Versioning
python manage.py bump_version --type minor
```

## Key Files Reference
- **AI Service**: `apps/core/services/ai_service.py` - All AI interactions
- **Models**: `apps/core/models.py` - 12 models, 612 lines
- **Admin**: `apps/core/admin.py` - Custom actions, inline forms
- **Settings**: `apps/githubai/settings.py` - PYTHONPATH modification at line 21-22
- **Docker Compose**: `infra/docker/docker-compose.yml` - 6 services (web, db, redis, celery_worker, celery_beat, nginx)

## Common Pitfalls
1. **Don't import with `apps.` prefix** - PYTHONPATH handles this
2. **Always use Docker commands** - Don't run `python manage.py` locally
3. **Never call AI APIs directly** - Always through AIService
4. **Check unique constraints** - Names must be unique, append versions
5. **Use service layer** - Keep views thin, logic in services
6. **Integration tests** - Mark with `@pytest.mark.integration`, skip by default