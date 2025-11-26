# Initial Data Loading Guide

GitHubAI uses a **two-tier data loading strategy** to separate critical technical configuration from content data.

## Overview

### Category 1: Critical Technical Configuration

- **What**: API keys, provider settings, model configurations
- **Source**: Environment variables, secrets files, interactive prompts
- **Command**: `load_config_data`
- **When**: First deployment, key rotation, provider changes

### Category 2: Content Data

- **What**: Prompt templates, issue templates, sample issues
- **Source**: AI-generated from prompts, JSON fixtures, or interactive input
- **Command**: `generate_content_data`
- **When**: Customizing installation, demo setup, testing

---

## Quick Start

### Production Deployment

Use the interactive setup wizard:

```bash
# Run the complete setup wizard
docker-compose exec web python manage.py setup_wizard
```

This will guide you through:

1. Configuring AI providers and API keys
2. Seeding AI models
3. Generating initial content (optional)
4. Validating configuration

### Test Environment

Load test fixtures automatically:

```bash
# Load both config and content fixtures
docker-compose exec web python manage.py loaddata \
    apps/core/fixtures/test_config.json \
    apps/core/fixtures/test_content.json
```

Or use pytest fixtures (automatic):

```python
@pytest.mark.django_db
def test_my_feature(load_test_config, sample_content_data):
    # Config and content are automatically loaded
    from core.models import AIProvider
    provider = AIProvider.objects.get(name='openai')
    assert provider.has_api_key
```

### Demo Environment

Generate rich demo content with AI:

```bash
# Interactive generation
docker-compose exec web python manage.py generate_content_data --interactive

# Or use the demo prompt file
docker-compose exec web python manage.py generate_content_data \
    --prompt-file apps/core/fixtures/demo_prompts.yaml
```

---

## Detailed Usage

## Category 1: Loading Configuration Data

### From Environment Variables

Configuration is loaded from `.env` file or environment:

```bash
# Required variables
OPENAI_API_KEY=sk-...
XAI_API_KEY=xai-...

# Optional variables
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_TEMPERATURE=0.2
OPENAI_MAX_TOKENS=2500
```

Load configuration:

```bash
docker-compose exec web python manage.py load_config_data
```

### From Secrets Files

Store API keys in separate files:

```bash
# Create secrets directory
mkdir -p infra/secrets

# Store keys in individual files
echo "sk-your-api-key" > infra/secrets/openai_api_key.txt
echo "xai-your-key" > infra/secrets/xai_api_key.txt

# Load from secrets directory
docker-compose exec web python manage.py load_config_data \
    --secrets-dir infra/secrets
```

### Interactive Mode

Prompt for all configuration values:

```bash
docker-compose exec web python manage.py load_config_data --interactive
```

You'll be prompted for:

- OpenAI API key
- OpenAI base URL (default: <https://api.openai.com/v1>)
- Default temperature (default: 0.2)
- Default max tokens (default: 2500)
- Same for XAI and other providers

### From Configuration File

Create a JSON configuration file:

```json
{
  "providers": [
    {
      "name": "openai",
      "display_name": "OpenAI",
      "api_key": "sk-...",
      "base_url": "https://api.openai.com/v1",
      "default_temperature": 0.2,
      "default_max_tokens": 2500,
      "is_active": true,
      "models": [
        {
          "name": "gpt-4o-mini",
          "display_name": "GPT-4o Mini",
          "capabilities": ["chat", "code"],
          "max_tokens": 16384,
          "context_window": 128000,
          "is_default": true
        }
      ]
    }
  ]
}
```

Load from file:

```bash
docker-compose exec web python manage.py load_config_data \
    --config-file path/to/config.json
```

### Test Mode

Load minimal test configuration without real API keys:

```bash
docker-compose exec web python manage.py load_config_data --test
```

This creates test providers with placeholder API keys for unit testing.

### Update Keys Only

Rotate API keys without changing other configuration:

```bash
# Update .env with new keys, then:
docker-compose exec web python manage.py load_config_data --update-keys-only
```

### With Validation

Automatically validate after loading:

```bash
docker-compose exec web python manage.py load_config_data --validate
```

---

## Category 2: Generating Content Data

### Interactive Mode

```bash
docker-compose exec web python manage.py generate_content_data --interactive
```

You'll be prompted for:

- Whether to generate prompt templates (and how many)
- Template categories (chat, auto_issue, documentation, etc.)
- Whether to generate issue templates
- Whether to generate sample issues
- Repository for sample issues

### From Prompt File

Create a YAML file with generation instructions:

```yaml
# demo_prompts.yaml
generate_prompt_templates: true
prompt_templates:
  count: 5
  categories:
    - chat
    - auto_issue
    - documentation

generate_issue_templates: true
issue_templates:
  count: 3

generate_sample_issues: true
sample_issues:
  count: 10
  repo: "owner/repo"
```

Generate content:

```bash
docker-compose exec web python manage.py generate_content_data \
    --prompt-file apps/core/fixtures/demo_prompts.yaml
```

### Specify AI Provider

Use a specific provider for generation:

```bash
docker-compose exec web python manage.py generate_content_data \
    --interactive \
    --provider xai
```

### Custom Output Path

Save to custom fixture location:

```bash
docker-compose exec web python manage.py generate_content_data \
    --interactive \
    --output apps/core/fixtures/my_custom_data.json
```

### Dry Run

Preview what would be generated without creating database records:

```bash
docker-compose exec web python manage.py generate_content_data \
    --interactive \
    --dry-run
```

### Load Generated Fixture

After generation, load the fixture:

```bash
docker-compose exec web python manage.py loaddata \
    apps/core/fixtures/generated_content_data.json
```

---

## Validating Configuration

### Basic Validation

```bash
docker-compose exec web python manage.py validate_config
```

Checks:

- Database connectivity
- AIProvider API keys exist
- AIProvider base URLs configured
- AIModel configurations valid
- Default models set

### Validate Specific Provider

```bash
docker-compose exec web python manage.py validate_config --provider openai
```

### Skip Connectivity Tests

```bash
docker-compose exec web python manage.py validate_config --skip-connectivity
```

### Auto-Fix Issues

Attempt to fix common issues automatically:

```bash
docker-compose exec web python manage.py validate_config --fix
```

Currently auto-fixes:

- Setting default model when none exists (picks first model)

---

## Testing with Fixtures

### Pytest Integration

The `conftest.py` provides several fixtures:

#### `load_test_config` (session-scoped)

Loads test configuration once per test session:

```python
@pytest.mark.django_db
def test_provider_config(load_test_config):
    from core.models import AIProvider
    provider = AIProvider.objects.get(name='openai')
    assert provider.has_api_key
```

#### `sample_content_data`

Loads sample content data:

```python
@pytest.mark.django_db
def test_prompt_templates(sample_content_data):
    from core.models import PromptTemplate
    templates = PromptTemplate.objects.all()
    assert templates.count() >= 2
```

#### `ai_provider_config`

Provides structured access to providers:

```python
def test_default_provider(ai_provider_config):
    assert ai_provider_config['default_provider'] is not None
    assert ai_provider_config['default_model'] is not None
```

#### `test_prompt_templates`

Dictionary of templates by category:

```python
def test_chat_template(test_prompt_templates):
    chat = test_prompt_templates['chat']
    assert chat.name == 'Test Chat Assistant'
```

#### `test_issues`

List of sample issues:

```python
def test_sample_issues(test_issues):
    assert len(test_issues) >= 2
    assert all(issue.github_repo == 'test/repo' for issue in test_issues)
```

### Manual Fixture Loading

Load fixtures in tests:

```python
from django.core.management import call_command

@pytest.fixture
def custom_data(db):
    call_command('loaddata', 'apps/core/fixtures/test_config.json')
    call_command('loaddata', 'apps/core/fixtures/test_content.json')
```

---

## Creating Custom Fixtures

### Export Existing Data

Use Django's `dumpdata` command:

```bash
# Export all AIProvider and AIModel records
docker-compose exec web python manage.py dumpdata \
    core.AIProvider core.AIModel \
    --indent 2 \
    --output apps/core/fixtures/my_providers.json

# Export specific records
docker-compose exec web python manage.py dumpdata \
    core.PromptTemplate \
    --pks 1,2,3 \
    --indent 2 \
    --output apps/core/fixtures/my_templates.json
```

### Sanitize Fixtures

Remove sensitive data from exported fixtures:

```bash
# Use jq to remove API keys
cat apps/core/fixtures/providers.json | \
    jq '.[].fields.api_key = "test-key"' > \
    apps/core/fixtures/providers_clean.json
```

Or create a sanitization script:

```python
import json

with open('providers.json', 'r') as f:
    data = json.load(f)

for record in data:
    if record['model'] == 'core.aiprovider':
        record['fields']['api_key'] = 'test-key-placeholder'

with open('providers_clean.json', 'w') as f:
    json.dump(data, f, indent=2)
```

---

## Environment-Specific Workflows

### Development

```bash
# 1. Load test configuration
docker-compose exec web python manage.py load_config_data --test

# 2. Seed standard models
docker-compose exec web python manage.py seed_ai_providers

# 3. Seed prompt templates
docker-compose exec web python manage.py seed_prompt_templates
```

### Staging

```bash
# 1. Load configuration from environment
docker-compose exec web python manage.py load_config_data

# 2. Seed models with real API keys
docker-compose exec web python manage.py seed_ai_providers --update-keys

# 3. Generate demo content
docker-compose exec web python manage.py generate_content_data \
    --prompt-file apps/core/fixtures/demo_prompts.yaml

# 4. Validate
docker-compose exec web python manage.py validate_config
```

### Production

```bash
# Use the interactive wizard
docker-compose exec web python manage.py setup_wizard

# Or manual steps:
# 1. Load from secrets
docker-compose exec web python manage.py load_config_data \
    --secrets-dir /run/secrets

# 2. Seed models
docker-compose exec web python manage.py seed_ai_providers --update-keys

# 3. Generate custom content interactively
docker-compose exec web python manage.py generate_content_data --interactive

# 4. Validate
docker-compose exec web python manage.py validate_config
```

---

## Migrations vs Fixtures vs Commands

### When to Use Each

| Approach | Use Case | Pros | Cons |
|----------|----------|------|------|
| **Data Migrations** | Core schema-dependent data that must exist | Runs automatically with `migrate`, version controlled | Hard to update, tied to migration history |
| **Management Commands** | Configuration that changes between environments | Flexible, can read from multiple sources, interactive | Must be run manually |
| **Fixtures** | Test data, demo data, repeatable snapshots | Easy to create/load, JSON format | Static, can become outdated |

### GitHubAI Strategy

- **Data Migrations**: Not used for initial data (to avoid environment-specific issues)
- **Management Commands**: Primary method for configuration and content generation
- **Fixtures**: Used for test data and optional demo data

### Creating a Data Migration (Optional)

If you want automatic seeding on first deployment:

```python
# apps/core/migrations/0007_load_initial_config.py
from django.db import migrations
from django.core.management import call_command

def load_config(apps, schema_editor):
    """Load initial configuration on first deployment."""
    call_command('load_config_data', '--test', '--non-interactive')

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0006_previous_migration'),
    ]

    operations = [
        migrations.RunPython(load_config, migrations.RunPython.noop),
    ]
```

**Warning**: Only use data migrations for truly universal data. Environment-specific configuration should use management commands.

---

## Troubleshooting

### "No active AI providers configured"

**Solution**: Load configuration first:

```bash
docker-compose exec web python manage.py load_config_data --interactive
```

### "Provider missing API key"

**Solution**: Update API keys:

```bash
# Set environment variable
export OPENAI_API_KEY=sk-your-key

# Reload configuration
docker-compose exec web python manage.py load_config_data --update-keys-only
```

### "Validation failed"

**Solution**: Run validation with fix flag:

```bash
docker-compose exec web python manage.py validate_config --fix
```

### Fixtures won't load

**Problem**: Foreign key violations or duplicate keys

**Solution**:

```bash
# Clear database first
docker-compose exec web python manage.py flush --no-input

# Then load fixtures in order
docker-compose exec web python manage.py loaddata test_config.json
docker-compose exec web python manage.py loaddata test_content.json
```

### AI generation fails

**Problem**: API key invalid or rate limited

**Solution**:

1. Validate configuration:

   ```bash
   docker-compose exec web python manage.py validate_config
   ```

2. Check API key in admin: `/admin/core/aiprovider/`

3. Use dry-run mode first:

   ```bash
   docker-compose exec web python manage.py generate_content_data \
       --interactive --dry-run
   ```

---

## Best Practices

### Security

1. **Never commit real API keys**: Use `.env` files and add to `.gitignore`
2. **Use secrets management**: Store keys in `infra/secrets/` or use Docker secrets
3. **Sanitize fixtures**: Remove API keys before committing test fixtures
4. **Rotate keys regularly**: Use `--update-keys-only` flag

### Testing

1. **Use session-scoped fixtures**: Load config once per test session
2. **Isolate test data**: Use unique identifiers for test records
3. **Mock external APIs**: Don't make real API calls in unit tests
4. **Use markers**: Mark integration tests that require real API keys

```python
@pytest.mark.integration
@pytest.mark.django_db
def test_real_ai_call():
    # Only runs with --run-integration flag
    pass
```

### Production

1. **Run setup wizard first**: Use interactive wizard for initial setup
2. **Validate after changes**: Always run validation after updating config
3. **Version your fixtures**: Tag generated fixtures with dates/versions
4. **Document customizations**: Keep notes on custom templates and configurations

---

## Example Workflows

### New Production Deployment

```bash
# 1. Clone repository
git clone https://github.com/bamr87/githubai.git
cd githubai

# 2. Set environment variables
cp .env.example .env
# Edit .env with your API keys

# 3. Start services
docker-compose up -d

# 4. Run migrations
docker-compose exec web python manage.py migrate

# 5. Run setup wizard
docker-compose exec web python manage.py setup_wizard

# 6. Create superuser
docker-compose exec web python manage.py createsuperuser

# 7. Access admin
# Visit http://localhost:8000/admin/
```

### Refreshing Demo Environment

```bash
# 1. Clear existing data
docker-compose exec web python manage.py flush --no-input

# 2. Run migrations
docker-compose exec web python manage.py migrate

# 3. Load configuration
docker-compose exec web python manage.py load_config_data

# 4. Generate new demo content
docker-compose exec web python manage.py generate_content_data \
    --prompt-file apps/core/fixtures/demo_prompts.yaml

# 5. Validate
docker-compose exec web python manage.py validate_config
```

### Running Tests with Fresh Data

```bash
# 1. Fixtures load automatically via conftest.py
pytest tests/test_ai_services.py

# 2. Or manually load fixtures
docker-compose exec web python manage.py loaddata \
    test_config.json test_content.json

# 3. Run specific tests
pytest tests/test_ai_services.py -v

# 4. Include integration tests
pytest --run-integration
```

---

## Reference

### Available Commands

| Command | Purpose | Example |
|---------|---------|---------|
| `load_config_data` | Load critical technical configuration | `load_config_data --interactive` |
| `generate_content_data` | Generate content using AI | `generate_content_data --prompt-file demo.yaml` |
| `validate_config` | Validate configuration | `validate_config --fix` |
| `setup_wizard` | Interactive production setup | `setup_wizard` |
| `seed_ai_providers` | Seed standard AI models | `seed_ai_providers --update-keys` |
| `seed_prompt_templates` | Seed default prompt templates | `seed_prompt_templates` |
| `loaddata` | Load Django fixtures | `loaddata test_config.json` |
| `dumpdata` | Export data to fixtures | `dumpdata core.AIProvider --indent 2` |

### Available Fixtures

| Fixture File | Contains | Use Case |
|--------------|----------|----------|
| `test_config.json` | Test AIProvider + AIModel | Unit testing |
| `test_content.json` | Test PromptTemplate + Issue | Unit testing |
| `demo_prompts.yaml` | Generation instructions | Demo setup |
| `generated_content_data.json` | AI-generated content | Custom content |

### Pytest Fixtures

| Fixture Name | Scope | Returns | Dependencies |
|--------------|-------|---------|--------------|
| `load_test_config` | session | None | `django_db_setup` |
| `sample_content_data` | function | None | `load_test_config` |
| `ai_provider_config` | function | dict | `load_test_config` |
| `test_prompt_templates` | function | dict | `sample_content_data` |
| `test_issues` | function | list | `sample_content_data` |

---

## Next Steps

- Review [AI Configuration Guide](ai-configuration.md)
- Learn about [Testing Guide](../development/testing-guide.md)
- Explore [Prompt Management](../features/PROMPT_MANAGEMENT.md)
- See [API Documentation](../api-reference/README.md)
