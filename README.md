# GitHubAI: AI-Powered GitHub Automation

A production-ready Django web application that leverages AI models to automate GitHub workflows including AI-driven issue management, automated documentation generation, semantic versioning, and code documentation extraction.

## Features

### 🤖 AI-Driven Issue Management

- Automatically generates structured sub-issues (functional requirements, test plans, etc.) from parent issues
- Creates AI-powered README updates by analyzing repository files
- YAML-driven templates for customizable and consistent issue generation
- Full REST API and web interface for issue management

### 📚 Automated Documentation Generation

- Generates changelog entries from commit messages and diffs
- Extracts and documents Python code docstrings and comments
- Supports both push and pull request events
- Database-backed documentation tracking

### 🔢 Semantic Versioning

- Intelligent version bumping based on commit message tags (`[major]`, `[minor]`, `[patch]`)
- Syncs with Git tags for consistency
- Version history tracking with database persistence

### ⚡ Modern Architecture

- **Django 4.2+** with PostgreSQL database
- **Docker containerization** for easy deployment
- **REST API** with Django REST Framework
- **Async processing** with Celery and Redis
- **Admin interface** for all operations
- **API caching** to reduce AI API costs
- **Comprehensive logging** for auditing

## Quick Start

### Prerequisites

- Docker and Docker Compose
- AI API key (e.g., [OpenAI](https://platform.openai.com/api-keys), [Anthropic](https://console.anthropic.com/), etc.)
- GitHub personal access token

### Installation

```bash
# Clone repository
git clone https://github.com/bamr87/githubai.git
cd githubai

# Setup environment
cp .env.example .env
# Edit .env and add your AI_API_KEY and GITHUB_TOKEN

# Run automated setup
chmod +x start.sh
./start.sh

# Access application
open http://localhost:8000/admin/
```

### Manual Setup

```bash
# Build containers
./build.sh

# Start services
docker-compose up -d

# Initialize database
./init.sh

# Create superuser
docker-compose exec web python manage.py createsuperuser
```

## Usage

### Management Commands

```bash
# Create AI-generated sub-issue
docker-compose exec web python manage.py create_issue \
    --repo owner/repo \
    --parent 123

# Create README update
docker-compose exec web python manage.py create_issue \
    --repo owner/repo \
    --issue-number 456 \
    --readme-update

# Generate documentation
docker-compose exec web python manage.py generate_docs --file path/to/file.py
docker-compose exec web python manage.py generate_docs --commit HEAD

# Bump version
docker-compose exec web python manage.py bump_version
docker-compose exec web python manage.py bump_version --type minor
```

### REST API

```bash
# Health check
curl http://localhost:8000/health/

# List issues
curl http://localhost:8000/api/issues/issues/

# Create sub-issue via API
curl -X POST http://localhost:8000/api/issues/issues/create-sub-issue/ \
    -H "Content-Type: application/json" \
    -d '{
        "repo": "owner/repo",
        "parent_issue_number": 123,
        "file_refs": ["README.md"]
    }'

# List templates
curl http://localhost:8000/api/issues/templates/
```

### Admin Interface

Access Django admin at `http://localhost:8000/admin/`:

- Manage issues and templates
- View AI response cache and hit rates
- Monitor API logs
- Track version history
- Review changelog entries

## Project Structure

```
githubai/
├── documentation/              # Project documentation
├── infra/                      # Infrastructure configuration
│   ├── docker/                 # Docker files
│   ├── nginx/                  # Nginx configuration
│   └── scripts/                # Utility scripts
├── manage.py                   # Django entry point
├── pyproject.toml              # Project configuration
│
├── project/           # Django project settings
├── core/                       # Shared models (APILog, base classes)
├── issues/                     # Issue management app
├── docs/                       # Documentation generation app
├── versioning/                 # Semantic versioning app
├── ai_services/                # AI integration with caching
├── github_integration/         # GitHub API wrapper
└── tests/                      # Test suite
```

## Docker Services

The application includes 6 containerized services:

- **web**: Django application server
- **db**: PostgreSQL database
- **redis**: Cache and message broker
- **celery_worker**: Background task processor
- **celery_beat**: Scheduled task scheduler
- **nginx**: Reverse proxy and static file server

## Configuration

Key environment variables in `.env`:

```env
# Django
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://user:pass@db:5432/githubai

# APIs
AI_API_KEY=your-ai-key
GITHUB_TOKEN=your-github-token

# OpenAI
AI_MODEL=gpt-4o-mini
AI_TEMPERATURE=0.2
AI_MAX_TOKENS=2500
```

### Security Best Practices

- **Never commit `.env` file** - It contains sensitive credentials
- Use strong, unique `DJANGO_SECRET_KEY` for production
- Set `DJANGO_DEBUG=False` in production environments
- Restrict `DJANGO_ALLOWED_HOSTS` to your actual domain in production
- Use environment-specific `.env` files (`.env.production`, `.env.staging`)
- Rotate API keys and tokens regularly
- Review and limit GitHub token scopes to minimum required permissions

## Development

### Run in Development Mode

```bash
docker-compose -f infra/docker/docker-compose.yml -f infra/docker/docker-compose.dev.yml up
```

Features hot-reload, debug mode, and verbose logging.

### Run Tests

```bash
docker-compose -f infra/docker/docker-compose.yml exec web pytest
docker-compose -f infra/docker/docker-compose.yml exec web pytest --cov
```

### View Logs

```bash
# All services
docker-compose -f infra/docker/docker-compose.yml logs -f

# Specific service
docker-compose -f infra/docker/docker-compose.yml logs -f web
docker-compose -f infra/docker/docker-compose.yml logs -f celery_worker
```

## API Endpoints

### Issues

- `GET /api/issues/issues/` - List all issues
- `POST /api/issues/issues/` - Create new issue
- `GET /api/issues/issues/{id}/` - Get issue details
- `POST /api/issues/issues/create-sub-issue/` - Create sub-issue
- `POST /api/issues/issues/create-readme-update/` - Create README update
- `GET /api/issues/templates/` - List issue templates

### System

- `GET /health/` - Health check endpoint
- `GET /admin/` - Django admin interface

## GitHub Actions Integration

The Django management commands can be used in GitHub Actions workflows. See [documentation/DJANGO_IMPLEMENTATION.md](documentation/DJANGO_IMPLEMENTATION.md) for examples.

## Documentation

- [documentation/DJANGO_IMPLEMENTATION.md](documentation/DJANGO_IMPLEMENTATION.md) - Complete implementation guide
- [documentation/CHANGELOG_AI.md](documentation/CHANGELOG_AI.md) - AI-generated changelog
- Admin interface - Interactive documentation at `/admin/`

## Contributing

Contributions are welcome! Please follow these guidelines:

### Getting Started

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature-name`)
3. Set up your development environment using Docker (see [Development](#development) section)

### Coding Standards

- Follow PEP 8 style guide for Python code
- Use `black` for code formatting (120 character line length)
- Run `flake8` and `pylint` for linting
- Write docstrings for all public modules, classes, and functions
- Use `snake_case` for functions and variables, `PascalCase` for classes
- Place business logic in `services.py` files, not in views or models

### Before Submitting

1. Add tests for new functionality
2. Ensure all tests pass: `docker-compose -f infra/docker/docker-compose.yml exec web pytest`
3. Run linters:
   ```bash
   docker-compose -f infra/docker/docker-compose.yml exec web black .
   docker-compose -f infra/docker/docker-compose.yml exec web flake8
   docker-compose -f infra/docker/docker-compose.yml exec web pylint apps/
   ```
4. Update documentation if needed

### Pull Request Process

1. Update the README.md or relevant documentation with details of changes
2. Ensure your PR description clearly explains the problem and solution
3. Reference any related issues in your PR description (e.g., "Fixes #123")
4. Request review from maintainers
5. Address any feedback from code reviews
6. Once approved, a maintainer will merge your PR

### Code Review Checklist

- [ ] Code follows project coding standards
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] No unnecessary dependencies added
- [ ] Commit messages are clear and descriptive
- [ ] No security vulnerabilities introduced

For more details, see:
- [Issue Tracker](https://github.com/bamr87/githubai/issues)
- [Pull Requests](https://github.com/bamr87/githubai/pulls)

## Troubleshooting

### Database connection errors

```bash
docker-compose -f infra/docker/docker-compose.yml down
docker-compose -f infra/docker/docker-compose.yml up -d db
# Wait 10 seconds
docker-compose -f infra/docker/docker-compose.yml up
```

### Reset database

```bash
docker-compose -f infra/docker/docker-compose.yml down -v
docker-compose -f infra/docker/docker-compose.yml up -d db
docker-compose -f infra/docker/docker-compose.yml exec web python manage.py migrate
```

### View service status

```bash
docker-compose -f infra/docker/docker-compose.yml ps
curl http://localhost:8000/health/
```

### Port already in use

If port 8000 is already in use:
```bash
# Find process using port 8000
lsof -i :8000
# Kill the process
kill -9 <PID>
# Or change port in docker-compose.yml
```

### Container build fails

```bash
# Clean rebuild
docker-compose -f infra/docker/docker-compose.yml down
docker system prune -a
docker-compose -f infra/docker/docker-compose.yml build --no-cache
docker-compose -f infra/docker/docker-compose.yml up
```

### Celery worker not processing tasks

```bash
# Check Celery worker logs
docker-compose -f infra/docker/docker-compose.yml logs celery_worker
# Restart Celery services
docker-compose -f infra/docker/docker-compose.yml restart celery_worker celery_beat
```

### Redis connection errors

```bash
# Check Redis status
docker-compose -f infra/docker/docker-compose.yml exec redis redis-cli ping
# Should return "PONG"
# Restart Redis
docker-compose -f infra/docker/docker-compose.yml restart redis
```

### Static files not loading

```bash
# Collect static files
docker-compose -f infra/docker/docker-compose.yml exec web python manage.py collectstatic --noinput
```

### API authentication issues

Ensure your `.env` file contains valid credentials:
- `AI_API_KEY`: Valid OpenAI or Anthropic API key
- `GITHUB_TOKEN`: Valid GitHub personal access token with appropriate scopes

### Getting help

- Check existing [GitHub Issues](https://github.com/bamr87/githubai/issues)
- Review application logs: `docker-compose -f infra/docker/docker-compose.yml logs -f`
- Join discussions in [GitHub Discussions](https://github.com/bamr87/githubai/discussions)

## License

MIT License
