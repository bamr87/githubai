# GitHubAI: AI-Powered GitHub Automation

A production-ready Django web application that leverages AI models to automate GitHub workflows including AI-driven issue management, automated documentation generation, semantic versioning, and code documentation extraction.

## Features

### 🤖 AI-Driven Issue Management

- Automatically generates structured sub-issues (functional requirements, test plans, etc.) from parent issues
- Creates AI-powered README updates by analyzing repository files
- **Auto-Issue Generation**: Automatically analyzes repository for maintenance tasks and creates GitHub issues
  - Code quality analysis
  - TODO/FIXME scanning
  - Documentation gap detection
  - Dependency checks
  - Test coverage analysis
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

# Auto-generate repository maintenance issues
docker-compose exec web python manage.py auto_issue --list-chores
docker-compose exec web python manage.py auto_issue --chore-type code_quality
docker-compose exec web python manage.py auto_issue --chore-type todo_scan --files "apps/core/services/*.py"
docker-compose exec web python manage.py auto_issue --chore-type general_review --dry-run
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

# Create GitHub issue from user feedback
curl -X POST http://localhost:8000/api/issues/issues/create-from-feedback/ \
    -H "Content-Type: application/json" \
    -d '{
        "feedback_type": "bug",
        "summary": "Login button not working",
        "description": "When I click the login button on the homepage, nothing happens.",
        "repo": "owner/repo",
        "context_files": ["README.md"]
    }'

# Auto-generate repository maintenance issue
curl -X POST http://localhost:8000/api/issues/issues/create-auto-issue/ \
    -H "Content-Type: application/json" \
    -d '{
        "chore_type": "code_quality",
        "repo": "bamr87/githubai",
        "context_files": ["apps/core/services/issue_service.py"],
        "auto_submit": true
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
- `POST /api/issues/issues/create-from-feedback/` - Create issue from user feedback
- `POST /api/issues/issues/create-auto-issue/` - Auto-generate maintenance issue
- `GET /api/issues/templates/` - List issue templates

### System

- `GET /health/` - Health check endpoint
- `GET /admin/` - Django admin interface

## GitHub Actions Integration

The Django management commands can be used in GitHub Actions workflows. See [Development Documentation](docs/development/) for examples.

## Documentation

### 📚 Comprehensive Documentation

- **[Getting Started](docs/GETTING_STARTED.md)** - Quick setup guide for new users
- **[Documentation Index](docs/README.md)** - Complete documentation navigation

### 📖 User Guides

- **[Auto Issue Feature](docs/guides/auto-issue-feature.md)** - Automated repository analysis
- **[AI Chat Interface](docs/guides/chat-interface.md)** - Using the web chat interface
- **[AI Provider Configuration](docs/guides/ai-provider-configuration.md)** - Configure OpenAI, XAI, etc.
- **[Troubleshooting](docs/guides/troubleshooting.md)** - Common issues and solutions

### 🔌 API Reference

- **[Auto Issue Endpoints](docs/api/AUTO_ISSUE_ENDPOINTS.md)** - REST API for auto-issue generation
- **[Chat Endpoint](docs/api/CHAT_ENDPOINT.md)** - Conversational AI API
- **[Interactive API](http://localhost:8000/api/)** - Browse API when server is running

### 🛠️ Development

- **[Django Implementation](docs/development/django-implementation.md)** - Architecture and design
- **[Testing Guide](docs/development/testing-guide.md)** - How to test features
- **[Contributing](docs/development/contributing.md)** - How to contribute

### 📋 Release Notes

- **[Changelog](docs/releases/CHANGELOG.md)** - All version changes
- **[v0.3.0 Release](docs/releases/v0.3.0.md)** - AI Chat Frontend
- **[v0.2.0 Release](docs/releases/v0.2.0.md)** - Auto Issue Generation

## Contributing

Contributions are welcome! Please see our [Contributing Guide](docs/development/contributing.md) for details on:

- Development setup
- Coding standards
- Testing guidelines
- Pull request process

Quick start:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

See [docs/development/contributing.md](docs/development/contributing.md) for complete guidelines.

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

## License

MIT License
