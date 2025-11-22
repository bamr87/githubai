# GitHubAI Coding Guidelines

## Project Overview
GitHubAI is a production-ready Django application for automating GitHub workflows using AI. It uses Django REST Framework, Celery, Redis, and PostgreSQL, all containerized with Docker.

## Architecture & Structure
- **Apps (`apps/`)**:
  - `core`: Shared utilities, base models (`APILog`), and exceptions.
  - `ai_services`: AI integration with caching (`AIResponse`) and logging.
  - `github_integration`: Wrappers for GitHub API interactions.
  - `issues`: Issue management logic, templates, and API views.
  - `docs`: Automated documentation generation.
  - `versioning`: Semantic versioning logic.
- **Infrastructure (`infra/`)**: Docker configurations and utility scripts.
- **Settings**: Located in `githubai/settings.py`.

## Development Workflow

### Docker
Always run commands within the Docker container to ensure correct environment and dependencies.
- **Start Dev Server**: `docker-compose -f infra/docker/docker-compose.yml -f infra/docker/docker-compose.dev.yml up`
- **Run Commands**: `docker-compose -f infra/docker/docker-compose.yml exec web <command>`

### Testing
- **Run Tests**: `docker-compose -f infra/docker/docker-compose.yml exec web pytest`
- **Configuration**: See `pyproject.toml` and `pytest.ini`.

### Linting & Formatting
- **Tools**: `black` (120 line length), `flake8`, `pylint`.
- **Configuration**: Defined in `pyproject.toml`.

## Coding Conventions

### Python Style
- Follow PEP 8.
- Use `black` for formatting.
- Use `snake_case` for functions/variables, `PascalCase` for classes.
- **Docstrings**: Required for all public modules, classes, and functions.

### Service Layer Pattern
- Business logic should reside in `services.py` within each app, not in views or models.
- Example: `AIService` in `apps/ai_services/services.py`.

### Logging
- Use the project logger: `logger = logging.getLogger('githubai')`.
- Log significant events, especially external API calls.

### AI Integration
- **Do not call AI APIs directly.** Use `apps.ai_services.services.AIService`.
- This service handles:
  - **Caching**: Checks `AIResponse` to save costs.
  - **Logging**: Records usage in `APILog`.
  - **Error Handling**: Standardized exception handling.

### Management Commands
- Custom commands are in `apps/<app>/management/commands/`.
- Run via Docker: `docker-compose exec web python manage.py <command_name>`.

## Key Files
- `apps/ai_services/services.py`: Core AI interaction logic.
- `apps/core/models.py`: `APILog` model.
- `infra/docker/docker-compose.yml`: Main service definition.