# GitHubAI Django - Complete Implementation Guide

## Overview

This is the complete technical documentation for the GitHubAI Django application. A production-ready Django web application with Docker containerization that provides AI-powered GitHub automation through REST APIs, admin interfaces, and CLI tools.

**Architecture**: Django 4.2+ | PostgreSQL | Redis | Celery | Nginx | Docker

## Key Features

- **Django 4.2+ web framework** with PostgreSQL database
- **Docker multi-container setup** (web, database, Redis, Celery, nginx)
- **6 Django apps** with full MVC/MTV architecture
- **REST API** with Django REST Framework
- **Async processing** with Celery and Redis
- **Comprehensive admin interface** for all operations
- **Management commands** replacing original CLI scripts
- **Database persistence** for all operations
- **API logging and intelligent caching**

## 📁 Project Structure

```
githubai/
├── docker-compose.yml           # Docker orchestration
├── Dockerfile                   # Multi-stage build
├── manage.py                    # Django entry point
├── .env.example                 # Environment template
├── DOCKER_README.md            # Docker guide
│
├── project/           # Django project
│   ├── settings.py             # Configuration
│   ├── urls.py                 # URL routing
│   ├── wsgi.py / asgi.py      # WSGI/ASGI
│   └── celery.py              # Celery config
│
├── core/                       # Shared functionality
│   ├── models.py              # APILog, TimeStampedModel
│   ├── views.py               # Health check
│   └── admin.py               # API log admin
│
├── issues/                     # Issue management
│   ├── models.py              # Issue, IssueTemplate, IssueFileReference
│   ├── services.py            # Migrated from create_issue.py
│   ├── views.py               # REST API viewsets
│   ├── serializers.py         # DRF serializers
│   ├── tasks.py               # Celery tasks
│   ├── admin.py               # Django admin
│   └── management/commands/
│       └── create_issue.py    # CLI command
│
├── docs/                       # Documentation generation
│   ├── models.py              # ChangelogEntry, DocumentationFile
│   ├── services.py            # Migrated from auto_doc_generator.py, docgen.py
│   ├── tasks.py               # Celery tasks
│   ├── admin.py               # Django admin
│   └── management/commands/
│       └── generate_docs.py   # CLI command
│
├── versioning/                 # Semantic versioning
│   ├── models.py              # Version
│   ├── services.py            # Migrated from scripts/versioning.py
│   ├── tasks.py               # Celery tasks
│   ├── admin.py               # Django admin
│   └── management/commands/
│       └── bump_version.py    # CLI command
│
├── ai_services/                # AI integration
│   ├── models.py              # AIResponse (caching)
│   ├── services.py            # Migrated from openai_utils.py
│   └── admin.py               # AI response admin
│
├── github_integration/         # GitHub API
│   ├── services.py            # Migrated from github_api_utils.py
│   └── [no models]            # Uses core.APILog
│
└── nginx/                      # Reverse proxy config
    ├── nginx.conf
    └── conf.d/githubai.conf
```

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Copy environment file
cp .env.example .env

# Edit .env and add your keys
nano .env  # Add AI_API_KEY and GITHUB_TOKEN
```

### 2. Build and Run

```bash
# Make scripts executable
chmod +x build.sh init.sh

# Build containers
./build.sh

# Start all services
docker-compose up -d

# Initialize database
./init.sh
```

### 3. Access Application

- **Django Admin**: <http://localhost:8000/admin/>
- **API Root**: <http://localhost:8000/api/>
- **Issues API**: <http://localhost:8000/api/issues/>
- **Health Check**: <http://localhost:8000/health/>

## 💻 Management Commands

All original CLI functionality preserved as Django commands:

```bash
# Create sub-issue
docker-compose exec web python manage.py create_issue \
    --repo bamr87/githubai \
    --parent 123

# Create README update
docker-compose exec web python manage.py create_issue \
    --repo bamr87/githubai \
    --issue-number 456 \
    --readme-update

# Generate documentation
docker-compose exec web python manage.py generate_docs --file src/module.py
docker-compose exec web python manage.py generate_docs --commit
docker-compose exec web python manage.py generate_docs --pr 789

# Bump version
docker-compose exec web python manage.py bump_version
docker-compose exec web python manage.py bump_version --type minor
```

## 🔌 REST API Endpoints

### Issues

- `GET /api/issues/issues/` - List all issues
- `POST /api/issues/issues/` - Create new issue
- `GET /api/issues/issues/{id}/` - Get issue details
- `POST /api/issues/issues/create-sub-issue/` - Create sub-issue
- `POST /api/issues/issues/create-readme-update/` - Create README update
- `GET /api/issues/templates/` - List issue templates

### Example API Usage

```bash
# Create sub-issue via API
curl -X POST http://localhost:8000/api/issues/issues/create-sub-issue/ \
    -H "Content-Type: application/json" \
    -d '{
        "repo": "bamr87/githubai",
        "parent_issue_number": 123,
        "file_refs": ["README.md"]
    }'

# List all issues
curl http://localhost:8000/api/issues/issues/
```

## 🔄 Async Tasks with Celery

All long-running operations run asynchronously:

```python
# In your code
from issues.tasks import create_sub_issue_task

# Queue the task
task = create_sub_issue_task.delay(
    repo='bamr87/githubai',
    parent_issue_number=123
)

# Check status
task.status  # 'PENDING', 'SUCCESS', 'FAILURE'
task.result  # Task result when complete
```

## 🗃️ Database Models

### Core Models

- **APILog**: Logs all AI and GitHub API calls
- **TimeStampedModel**: Base model with timestamps

### Issues Models

- **Issue**: GitHub issues with relationships
- **IssueTemplate**: YAML-driven templates
- **IssueFileReference**: Files referenced in issues

### Docs Models

- **ChangelogEntry**: Generated changelog entries
- **DocumentationFile**: Parsed code documentation

### Versioning Models

- **Version**: Semantic version history

### AI Services Models

- **AIResponse**: Cached AI responses (reduces API costs)

## 📊 Django Admin Features

Access at <http://localhost:8000/admin/> with superuser account:

- **View/manage all issues** with filtering and search
- **Edit issue templates** for customization
- **Review API logs** for debugging
- **Check AI response cache** and hit rates
- **Track version history** with git tags
- **View changelog entries** with generated content
- **Monitor documentation generation**

## 🐳 Docker Services & Configuration

The application includes 6 containerized services:

1. **web** (Django): Main application server (port 8000)
2. **db** (PostgreSQL): Persistent database (port 5432)
3. **redis**: Cache and message broker (port 6379)
4. **celery_worker**: Background task processor
5. **celery_beat**: Scheduled task scheduler
6. **nginx**: Reverse proxy and static file server (port 80)

### Docker Commands

```bash
# Start all services
docker-compose up -d

# Stop containers
docker-compose down

# Stop and remove volumes
docker-compose down -v

# View logs
docker-compose logs -f
docker-compose logs -f web
docker-compose logs -f celery_worker

# Rebuild from scratch
docker-compose down -v
docker-compose build --no-cache
docker-compose up

# Check service status
docker-compose ps
```

### Troubleshooting Docker

**Database connection errors:**

```bash
docker-compose down
docker-compose up -d db
# Wait 10 seconds
docker-compose up
```

**Reset database:**

```bash
docker-compose down -v
docker-compose up -d db
docker-compose exec web python manage.py migrate
```

**Check service health:**

```bash
docker-compose ps
curl http://localhost:8000/health/
```

## 🔧 Development vs Production

### Development Mode

```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

Features:

- Hot reload on code changes
- Debug mode enabled
- Verbose logging
- Development dependencies

### Production Mode

Update `.env`:

```env
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=<strong-random-key>
```

Run with production settings:

```bash
docker-compose up -d
```

## 🧪 Testing

Tests migrated to pytest-django:

```bash
# Run all tests
docker-compose exec web pytest

# Run specific app tests
docker-compose exec web pytest issues/
docker-compose exec web pytest docs/

# With coverage
docker-compose exec web pytest --cov
```

## 📝 Migration Notes

### What Changed

1. **Architecture**: Script-based → Django MVC/MTV
2. **Storage**: File-based → PostgreSQL database
3. **API**: Direct calls → Service layer with logging
4. **Async**: Synchronous → Celery tasks
5. **CLI**: Python scripts → Django management commands
6. **Deployment**: Manual → Docker containers

### What's Preserved

✅ All original functionality ✅ CLI command compatibility ✅ GitHub Actions integration (via management commands) ✅ AI and GitHub API interactions ✅ Template system ✅ Versioning logic

### New Capabilities

- 🎯 **REST API** for programmatic access
- 💾 **Database persistence** for all operations
- 📊 **Admin interface** for management
- ⚡ **Async processing** for long operations
- 📈 **API caching** to reduce costs
- 📝 **Comprehensive logging** for auditing
- 🔄 **Retry logic** for failed operations
- 🐳 **Containerization** for easy deployment

## 🚨 Important Notes

1. **Environment Variables**: Required in `.env`:
   - `AI_API_KEY`
   - `GITHUB_TOKEN`
   - `DJANGO_SECRET_KEY`

2. **Database Migrations**: Run on first setup:

   ```bash
   docker-compose exec web python manage.py migrate
   ```

3. **Static Files**: Collected automatically in Docker:

   ```bash
   docker-compose exec web python manage.py collectstatic
   ```

4. **Superuser**: Create for admin access:

   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

## 📚 Additional Documentation

- `DOCKER_README.md` - Detailed Docker setup guide
- `project/settings.py` - All configuration options
- Django apps' `services.py` - Migrated business logic
- Models' docstrings - Database schema documentation

## 🎯 Next Steps

1. ✅ Deploy to production environment
2. ✅ Setup CI/CD pipeline for Docker
3. ✅ Add webhook endpoints for GitHub events
4. ✅ Implement comprehensive test suite
5. ✅ Add API authentication tokens
6. ✅ Setup monitoring and alerting
7. ✅ Add frontend UI (optional)

## 🤝 Contributing

The Django refactoring maintains full backward compatibility while adding new capabilities. Contribute by:

- Adding new management commands
- Creating API endpoints
- Extending models
- Writing tests
- Improving documentation

---

**Status**: ✅ Complete Django refactoring with Docker containerization

**Migration Path**: Old scripts → Django management commands → REST API
