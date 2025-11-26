# GitHubAI Fixtures

This directory contains JSON fixtures and generation templates for GitHubAI's two-tier data loading strategy.

## Overview

GitHubAI separates data into two categories:

1. **Critical Technical Configuration** (Category 1): API keys, providers, models
2. **Content Data** (Category 2): Prompt templates, issue templates, sample data

## Available Fixtures

### test_config.json

**Purpose**: Test configuration for automated testing
**Contains**:

- 2 AIProviders (OpenAI, XAI) with test API keys
- 2 AIModels (gpt-4o-mini, grok-beta)

**Usage**:

```bash
# Load in tests (automatic via conftest.py)
pytest tests/

# Or manually
python manage.py loaddata apps/core/fixtures/test_config.json
```

### test_content.json

**Purpose**: Sample content data for testing
**Contains**:

- 2 PromptTemplates (chat, auto_issue)
- 1 IssueTemplate
- 2 sample Issues

**Usage**:

```bash
# Automatic via pytest fixture
@pytest.mark.django_db
def test_my_feature(sample_content_data):
    pass

# Or manually
python manage.py loaddata apps/core/fixtures/test_content.json
```

### demo_prompts.yaml

**Purpose**: Instructions for generating rich demo content
**Contains**: Configuration for AI-powered content generation

**Usage**:

```bash
python manage.py generate_content_data \
    --prompt-file apps/core/fixtures/demo_prompts.yaml
```

### generated_content_data.json (created on demand)

**Purpose**: AI-generated content from `generate_content_data` command
**Contains**: Custom-generated templates and sample data

**Usage**:

```bash
# Generate content first
python manage.py generate_content_data --interactive

# Then load
python manage.py loaddata apps/core/fixtures/generated_content_data.json
```

## Creating Custom Fixtures

### Method 1: Export Existing Data

```bash
# Export specific models
python manage.py dumpdata core.AIProvider core.AIModel \
    --indent 2 \
    --output apps/core/fixtures/my_providers.json

# Export specific records by primary key
python manage.py dumpdata core.PromptTemplate \
    --pks 1,2,3 \
    --indent 2 \
    --output apps/core/fixtures/my_templates.json
```

### Method 2: Generate with AI

```bash
# Interactive generation
python manage.py generate_content_data --interactive

# From YAML instructions
python manage.py generate_content_data \
    --prompt-file path/to/instructions.yaml \
    --output apps/core/fixtures/my_custom_data.json
```

### Method 3: Manual Creation

Create JSON file following Django fixture format:

```json
[
  {
    "model": "core.prompttemplate",
    "pk": 1,
    "fields": {
      "name": "My Template",
      "category": "chat",
      "system_prompt": "You are helpful",
      "user_prompt_template": "{{ message }}",
      "is_active": true
    }
  }
]
```

## Sanitizing Fixtures

Remove sensitive data before committing:

```bash
# Remove API keys using jq
cat providers.json | \
    jq '.[].fields.api_key = "test-key"' > \
    providers_clean.json

# Or use Python
python -c "
import json
with open('providers.json') as f:
    data = json.load(f)
for record in data:
    if 'api_key' in record['fields']:
        record['fields']['api_key'] = 'test-key'
with open('providers_clean.json', 'w') as f:
    json.dump(data, f, indent=2)
"
```

## Best Practices

1. **Never commit real API keys**: Sanitize fixtures before committing
2. **Use descriptive names**: Include purpose in filename (e.g., `test_`, `demo_`, `prod_`)
3. **Version fixtures**: Tag with dates or versions if schema changes
4. **Keep fixtures small**: Separate large datasets into multiple files
5. **Document dependencies**: Note if fixtures require specific order

## Loading Order

When loading multiple fixtures, load in this order:

1. Configuration fixtures (providers, models)
2. Template fixtures (prompt templates, issue templates)
3. Content fixtures (issues, executions)

Example:

```bash
python manage.py loaddata \
    test_config.json \
    test_content.json
```

## Troubleshooting

### "IntegrityError: duplicate key"

**Problem**: Fixture contains records that already exist

**Solution**: Clear database first or use different primary keys

```bash
python manage.py flush --no-input
python manage.py loaddata test_config.json
```

### "DoesNotExist: Foreign key not found"

**Problem**: Fixture references records that don't exist yet

**Solution**: Load dependency fixtures first

```bash
# Load config first (contains AIProvider)
python manage.py loaddata test_config.json
# Then load content (references AIProvider)
python manage.py loaddata test_content.json
```

### "Invalid JSON"

**Problem**: Malformed JSON in fixture file

**Solution**: Validate JSON syntax

```bash
# Validate with Python
python -m json.tool apps/core/fixtures/test_config.json

# Or use jq
jq . apps/core/fixtures/test_config.json
```

## Related Documentation

- [Initial Data Loading Guide](../../docs/guides/initial-data-loading.md) - Complete guide
- [Testing Guide](../../docs/development/testing-guide.md) - Using fixtures in tests
- [AI Configuration](../../docs/guides/ai-configuration.md) - Provider setup

## Commands Reference

| Command | Purpose |
|---------|---------|
| `loaddata <fixture>` | Load fixture into database |
| `dumpdata <app.Model>` | Export data to fixture |
| `load_config_data` | Load critical configuration |
| `generate_content_data` | Generate content with AI |
| `validate_config` | Validate configuration |
