# Test Environment Guide

Complete guide for instantiating and using the GitHubAI TEST environment - an isolated Docker-based setup for analyzing AI-generated initial data without affecting development or production.

## Overview

The TEST environment provides:

- **Isolated infrastructure**: Separate containers, database, Redis, ports
- **Mock AI provider**: Deterministic canned responses without API costs
- **Fresh data generation**: Reproducible test data from fixtures or AI
- **Easy teardown/rebuild**: Start fresh anytime for testing

## Quick Start

### One-Command Launch

```bash
# From project root
./infra/scripts/launch_test_env.sh
```

This will:

1. Start test containers (separate from dev)
2. Wait for services to be healthy
3. Initialize database and load test data
4. Display access URLs and credentials

### Access the Test Environment

| Service | URL | Credentials |
|---------|-----|-------------|
| Django Admin | <http://localhost:8001/admin/> | admin / admin123 |
| API Root | <http://localhost:8001/api/> | (same) |
| Chat Interface | <http://localhost:5174/> | - |
| Documentation | <http://localhost:8002/> | - |

## Architecture

### Isolated Components

The test environment uses **separate instances** of everything:

| Component | Dev/Prod | Test | Purpose |
|-----------|----------|------|----------|
| Database | `githubai` | `test` | Data isolation |
| Web Port | 8000 | 8001 | No conflicts |
| Frontend Port | 5173 | 5174 | No conflicts |
| Redis DB | 0 | 1 | Cache isolation |
| Docker Volumes | `postgres_data` | `postgres_test_data` | Storage isolation |
| Environment | `.env` | `.env.test` | Config isolation |

### Docker Compose Setup

Test environment uses **override pattern**:

```bash
# Base services
docker-compose -f infra/docker/docker-compose.yml

# + Test overrides
docker-compose -f infra/docker/docker-compose.test.yml
```

Override file changes:

- Container names (suffix: `_test`)
- Database name (`test`)
- Ports (8001, 5174, etc.)
- Environment (`settings_test.py`)
- Volumes (`postgres_test_data`, etc.)

### MockAIProvider

**Purpose**: Deterministic AI responses without API costs

**How it works**:

1. Load canned responses from `test_ai_responses_2025-11-25.json`
2. Match prompts by exact text or category
3. Return pre-defined responses
4. Track usage stats (no real API calls)

**Response Strategy**:

```
User Prompt → MockAIProvider
    ↓
1. Try exact match (full prompt text)
2. Try category match (code_quality, chat, etc.)
3. Use default fallback
    ↓
Return canned response
```

**Benefits**:

- ✅ No API costs
- ✅ Deterministic (same input = same output)
- ✅ Fast (no network calls)
- ✅ Reproducible tests

## Usage Scenarios

### Scenario 1: Quick Test (Existing Data)

Start test environment with existing data:

```bash
./infra/scripts/launch_test_env.sh
```

Use case: Resume previous test session, check UI changes

### Scenario 2: Fresh Start

Complete fresh setup, wipe everything:

```bash
./infra/scripts/launch_test_env.sh --full
```

Use case: Test initial data loading from scratch

### Scenario 3: Persistent Test Data

Fresh start but keep data for next time:

```bash
./infra/scripts/launch_test_env.sh --full --persist
```

Use case: Build test dataset once, reuse multiple times

### Scenario 4: Manual Setup

Step-by-step manual control:

```bash
# Start containers
docker-compose -f infra/docker/docker-compose.yml \
               -f infra/docker/docker-compose.test.yml up -d

# Wait for health checks
sleep 5

# Initialize environment
docker-compose exec web python manage.py setup_test_env --full

# Analyze what was loaded
docker-compose exec web python manage.py setup_test_env --analyze
```

Use case: Debug setup issues, customize initialization

### Scenario 5: Teardown

Stop and remove test environment:

```bash
./infra/scripts/launch_test_env.sh --teardown
```

Or manually:

```bash
docker-compose -f infra/docker/docker-compose.yml \
               -f infra/docker/docker-compose.test.yml down -v
```

## Configuration

### Environment Variables (.env.test)

Copy template and customize:

```bash
cp .env.test.example .env.test
nano .env.test
```

**Key settings**:

```bash
# Database (isolated)
DATABASE_URL=postgresql://test:test123@db:5432/test

# Use MockAIProvider
AI_PROVIDER=mock
MOCK_API_KEY=mock-test-key-2025-11-25
MOCK_MODEL=mock-gpt-4

# Or use real provider for integration testing
# AI_PROVIDER=openai
# OPENAI_API_KEY=sk-real-key-here

# Test data volumes
TEST_DATA_PROVIDERS=2
TEST_DATA_MODELS=4
TEST_DATA_TEMPLATES=10
TEST_DATA_ISSUES=20
```

### Django Settings (settings_test.py)

Test-specific settings automatically loaded:

- **Database**: Uses `DATABASE_URL` from `.env.test`
- **MockAIProvider**: Auto-registered if `TEST_ENV=true`
- **Celery**: Runs synchronously (`CELERY_TASK_ALWAYS_EAGER=True`)
- **Query Logging**: Enabled for debugging
- **Security**: Relaxed (all hosts allowed, simple secret key)

## Management Commands

### setup_test_env

Main orchestration command for test environment.

**Usage**:

```bash
docker-compose exec web python manage.py setup_test_env [OPTIONS]
```

**Options**:

- `--full`: Full fresh setup (flush DB, reload everything)
- `--persist`: Mark DB as persistent (for future use)
- `--analyze`: Show current test data without changes
- `--skip-content`: Only load config, skip content generation
- `--verbose`: Detailed output for debugging

**Examples**:

```bash
# Quick setup
python manage.py setup_test_env

# Full fresh
python manage.py setup_test_env --full

# Analyze current data
python manage.py setup_test_env --analyze

# Config only, no content
python manage.py setup_test_env --full --skip-content
```

**What it does**:

1. Database setup (flush if `--full`)
2. Load `test_config.json` (2 providers, 4 models)
3. Load `test_content.json` (2 templates, 2 issues)
4. Create test superuser (admin/admin123)
5. Validate configuration
6. Display summary with URLs

### Other Useful Commands

```bash
# Validate config
docker-compose exec web python manage.py validate_config

# Load specific fixture
docker-compose exec web python manage.py loaddata test_config.json

# Django shell
docker-compose exec web python manage.py shell

# Run tests
docker-compose exec web pytest

# View logs
docker-compose logs -f web
```

## Test Fixtures

### Dated Fixture Format

All test fixtures use **dated naming** for versioning:

```
test_ai_responses_2025-11-25.json
test_config_2025-11-25.json
test_content_2025-11-25.json
```

**Why dated?**

- Clear versioning (know when created)
- Easy to compare changes over time
- Can keep multiple versions
- No v1/v2 confusion

### test_config.json

**Purpose**: Critical technical configuration

**Contains**:

- 2 AIProviders (OpenAI, XAI) with test keys
- 4 AIModels (gpt-4o-mini, grok-beta, etc.)

**When to use**: Every test needs providers/models

### test_content.json

**Purpose**: Sample content data

**Contains**:

- 2 PromptTemplates (chat, auto_issue)
- 1 IssueTemplate (bug report)
- 2 sample Issues

**When to use**: Testing content-related features

### test_ai_responses_2025-11-25.json

**Purpose**: Canned responses for MockAIProvider

**Contains**:

- 5 exact prompt/response pairs
- 5 category fallbacks (code_quality, chat, etc.)
- 1 default fallback

**When to use**: MockAIProvider auto-loads this

**Structure**:

```json
{
  "fixture_version": "2025-11-25",
  "responses": [
    {
      "prompt": "exact prompt text here",
      "response": "exact response to return",
      "tokens_used": 100,
      "category": "code_quality"
    }
  ],
  "fallbacks": {
    "code_quality": "generic code quality response",
    "chat": "generic chat response",
    "default": "catch-all response"
  }
}
```

## Analyzing AI-Generated Data

### Purpose of Test Environment

The test environment is specifically designed to:

1. **Generate initial data** using AI (MockAIProvider or real)
2. **Review outputs** in isolated environment
3. **Validate quality** of AI-generated content
4. **Iterate** on prompts and templates
5. **Export** validated data for production

### Workflow: Analyze AI Output

**Step 1: Generate with Mock**

```bash
# Start test env with MockAIProvider
./infra/scripts/launch_test_env.sh --full

# MockAIProvider returns canned responses
# Good for: structure testing, UI validation
```

**Step 2: Generate with Real AI** (optional)

```bash
# Edit .env.test
AI_PROVIDER=openai
OPENAI_API_KEY=sk-your-real-key

# Restart with real AI
./infra/scripts/launch_test_env.sh --full

# Real AI generates novel content
# Good for: content quality testing
```

**Step 3: Review in Admin**

```bash
# Open http://localhost:8001/admin/
# Login: admin / admin123

# Review generated:
# - Prompt templates (core > Prompt templates)
# - Issue templates (core > Issue templates)
# - Sample issues (core > Issues)
```

**Step 4: Test in UI**

```bash
# Open http://localhost:5174/
# Try chat interface with generated templates
# Create test issues
# Verify workflows
```

**Step 5: Analyze Data**

```bash
# Get statistics
docker-compose exec web python manage.py setup_test_env --analyze

# Export for review
docker-compose exec web python manage.py dumpdata core.PromptTemplate \
    --indent 2 > generated_templates_review.json

# Django shell analysis
docker-compose exec web python manage.py shell
>>> from core.models import PromptTemplate
>>> templates = PromptTemplate.objects.all()
>>> for t in templates:
...     print(f"{t.name}: {len(t.user_prompt_template)} chars")
```

**Step 6: Export Validated Data**

```bash
# Export validated templates
docker-compose exec web python manage.py dumpdata \
    core.PromptTemplate \
    --indent 2 \
    > apps/core/fixtures/validated_templates_2025-11-25.json

# Use in production
python manage.py loaddata validated_templates_2025-11-25.json
```

## Troubleshooting

### Port Conflicts

**Problem**: `port is already allocated`

**Solution**:

```bash
# Check what's using ports
lsof -ti:8001,5174,8002,5433,6380

# Stop conflicting services or change ports in docker-compose.test.yml
```

### Database Connection Failed

**Problem**: Can't connect to `test` database

**Solution**:

```bash
# Check DB is running
docker-compose ps db

# Check logs
docker-compose logs db

# Restart DB
docker-compose restart db
```

### MockAIProvider Not Found

**Problem**: `ModuleNotFoundError: No module named 'core.services.mock_provider'`

**Solution**:

```bash
# Verify file exists
ls -la apps/core/services/mock_provider.py

# Check settings_test.py loads correctly
docker-compose exec web python -c "
from django.conf import settings
print(settings.AI_PROVIDER)
"
```

### .env.test Not Loaded

**Problem**: Settings use `.env` instead of `.env.test`

**Solution**:

```bash
# Verify DJANGO_SETTINGS_MODULE
docker-compose exec web env | grep DJANGO_SETTINGS_MODULE
# Should show: githubai.settings_test

# Check settings_test.py
docker-compose exec web python -c "
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'githubai.settings_test'
from django.conf import settings
print(settings.TEST_ENV)
"
```

### Services Won't Start

**Problem**: `docker-compose up` fails

**Solution**:

```bash
# Clean up old containers
docker-compose down -v

# Rebuild images
docker-compose build --no-cache

# Check disk space
df -h

# Check Docker status
docker info
```

## Best Practices

### 1. Always Use Isolated Environment

✅ **Do**: Use test environment for testing

```bash
./infra/scripts/launch_test_env.sh
```

❌ **Don't**: Test in dev environment

```bash
# Don't do this for testing initial data
docker-compose up  # Uses dev database
```

### 2. Use --full for Clean Analysis

✅ **Do**: Fresh start for validating AI generation

```bash
./infra/scripts/launch_test_env.sh --full
```

❌ **Don't**: Test with stale data

```bash
# Old data mixed with new = confusing results
```

### 3. Date Your Fixtures

✅ **Do**: Use dated naming

```
test_ai_responses_2025-11-25.json
validated_templates_2025-12-01.json
```

❌ **Don't**: Use version numbers

```
test_ai_responses_v1.json  # Unclear when created
```

### 4. Teardown Between Major Tests

✅ **Do**: Clean slate for major changes

```bash
./infra/scripts/launch_test_env.sh --teardown
./infra/scripts/launch_test_env.sh --full
```

❌ **Don't**: Let test data accumulate

```bash
# Running tests for weeks without cleanup = data drift
```

### 5. Document Your Canned Responses

✅ **Do**: Add context to mock responses

```json
{
  "prompt": "Analyze code quality...",
  "response": "...",
  "category": "code_quality",
  "_note": "Added 2025-11-25 for testing code review feature"
}
```

❌ **Don't**: Leave mysterious responses

```json
{
  "response": "some random text"
}
```

## Advanced Usage

### Custom Fixture Development

Create dated fixtures for specific scenarios:

```bash
# 1. Generate data in test env
./infra/scripts/launch_test_env.sh --full

# 2. Manually create/edit via admin (http://localhost:8001/admin/)

# 3. Export custom fixture
docker-compose exec web python manage.py dumpdata \
    core.PromptTemplate \
    core.IssueTemplate \
    --indent 2 \
    > apps/core/fixtures/custom_scenario_2025-11-25.json

# 4. Use in future tests
docker-compose exec web python manage.py loaddata \
    custom_scenario_2025-11-25.json
```

### Integration Testing with Real AI

Switch to real AI for integration tests:

```bash
# 1. Edit .env.test
AI_PROVIDER=openai
OPENAI_API_KEY=sk-real-key-here

# 2. Launch with real AI
./infra/scripts/launch_test_env.sh --full

# 3. Generate real AI content
docker-compose exec web python manage.py generate_content_data \
    --interactive

# 4. Review quality
# Open http://localhost:8001/admin/

# 5. Export validated
docker-compose exec web python manage.py dumpdata \
    core.PromptTemplate \
    --indent 2 \
    > validated_real_ai_2025-11-25.json
```

### Pytest with Test Environment

Run automated tests in test environment:

```bash
# Start test environment
./infra/scripts/launch_test_env.sh

# Run pytest
docker-compose exec web pytest tests/ -v

# With coverage
docker-compose exec web pytest --cov=core tests/

# Specific test file
docker-compose exec web pytest tests/test_data_loading.py
```

## Related Documentation

- [Initial Data Loading](initial-data-loading.md) - Two-tier data loading system
- [Getting Started](../GETTING_STARTED.md) - General setup guide
- [AI Configuration](ai-configuration.md) - AI provider setup
- [Testing Guide](../development/testing-guide.md) - Automated testing

## Summary

The TEST environment provides:

- ✅ **Isolation**: Separate from dev/prod
- ✅ **Reproducibility**: Dated fixtures + MockAIProvider
- ✅ **Cost-Free**: No API charges with mock
- ✅ **Fresh Start**: Easy teardown/rebuild
- ✅ **Analysis**: Review AI-generated data safely
- ✅ **Export**: Validate and promote to production

**Quick Commands**:

```bash
# Start test environment
./infra/scripts/launch_test_env.sh

# Fresh start
./infra/scripts/launch_test_env.sh --full

# Teardown
./infra/scripts/launch_test_env.sh --teardown
```

**Access**:

- Admin: <http://localhost:8001/admin/> (admin/admin123)
- API: <http://localhost:8001/api/>
- Chat: <http://localhost:5174/>

---

**Last Updated**: November 25, 2025
**Fixture Version**: 2025-11-25
**Test Environment Status**: ✅ Production Ready
