# Prompt Management System

## Overview

GitHubAI now includes a comprehensive prompt management system that allows you to:

- Store and version AI prompt templates
- Manage prompt schemas and datasets
- Track prompt execution history

## Core Models

### 1. PromptTemplate

Stores AI prompt templates with versioning and configuration.

**Key Fields:**

- `name`: Unique identifier for the prompt
- `category`: Type of prompt (chat, auto_issue, documentation, etc.)
- `system_prompt`: System instructions for the AI
- `user_prompt_template`: User prompt with Jinja2 variables (e.g., `{{ variable_name }}`)
- `model`, `provider`, `temperature`, `max_tokens`: Model configuration
- `version_number`, `parent_version`: Versioning support
- `usage_count`, `last_used_at`: Usage tracking

**Example:**

```python
template = PromptTemplate.objects.get(name="Chat Assistant")
# Render with context
rendered = template.render_user_prompt({'user_message': 'Hello!'})
```

### 2. PromptSchema

Defines expected input/output structure for prompts (JSON Schema format).

**Use Cases:**

- Validate prompt inputs before rendering
- Define expected output structure for AI responses
- Document required/optional parameters

### 3. PromptDataset

Collections of test data for evaluating prompts.

**Features:**

- Group related test cases
- Link to specific prompt templates
- Track dataset metadata

### 4. PromptDatasetEntry

Individual test cases within datasets.

**Contains:**

- Input data (JSON)
- Expected output
- Tags for organization
- Execution results

### 5. PromptExecution

Tracks every time a prompt is executed.

**Records:**

- Template used
- Input context and rendered prompts
- AI response and metadata
- Execution time and token usage
- Success/failure status

## Using Prompt Templates in Code

### Basic Usage

```python
from core.services.ai_service import AIService

# Method 1: Direct template usage
ai_service = AIService()
response = ai_service.call_ai_chat(
    prompt_template_id=1,  # Use template ID
    context={'user_message': 'Hello!', 'repo': 'githubai'}
)

# Method 2: Traditional usage (backward compatible)
response = ai_service.call_ai_chat(
    system_prompt="You are a helpful assistant",
    user_prompt="Hello!"
)
```

### Rendering Templates Manually

```python
from core.models import PromptTemplate

template = PromptTemplate.objects.get(name="Chat Assistant")

# Render user prompt with context
user_prompt = template.render_user_prompt({
    'user_message': 'How do I create a branch?',
    'repo': 'githubai'
})

# Get system prompt
system_prompt = template.render_system_prompt({})
```

## Management Commands

### Seed Initial Templates

```bash
docker-compose -f infra/docker/docker-compose.yml exec web \
    python manage.py seed_prompt_templates
```

Seeds 6 core templates:

1. Chat Assistant
2. Auto Issue Generator
3. Feedback Issue Creator
4. Documentation Generator
5. README Update Generator
6. Sub-Issue Generator

### Test Prompt Rendering

```bash
docker-compose -f infra/docker/docker-compose.yml exec web \
    python manage.py test_prompt_templates
```

Tests Jinja2 variable substitution for all templates.

### Check Saved Prompts

```bash
docker-compose -f infra/docker/docker-compose.yml exec web \
    python manage.py check_prompts
```

Lists all prompts with their metadata.

## Django Admin Features

### PromptTemplate Admin

**List View:**

- Filter by category, active status
- Search by name, description
- Sortable columns

**Actions:**

- **Duplicate template**: Create a copy for modification
- **Create new version**: Version an existing template
- **Activate/Deactivate**: Toggle active status

**Detail View:**

- Full editor for all fields
- Inline editing for related schemas
- Inline editing for datasets
- Preview rendered prompts with test data

### PromptSchema Admin

- Manage JSON schemas for validation
- Link to prompt templates
- Validate schemas on save

### PromptDataset Admin

- Create test datasets
- Link to templates
- Inline entry management

### PromptExecution Admin

- **Read-only** - automatic tracking
- View execution history
- Filter by template, status, date
- Analyze performance metrics

## Versioning Workflow

1. Find the template you want to update
2. Use "Create new version" action
3. Modify the duplicated template
4. Original version is preserved with `parent_version` link
5. Both versions remain in database for comparison

## Best Practices

### Template Design

1. **Use clear variable names**: `{{ user_message }}` not `{{ msg }}`
2. **Document expected variables**: In description field
3. **Set appropriate defaults**: For temperature, max_tokens
4. **Include output format instructions**: In system_prompt
5. **Test with real data**: Use datasets to validate

### Variable Naming

```jinja2
✅ Good:
{{ user_message }}
{{ repository_name }}
{{ issue_number }}

❌ Avoid:
{{ msg }}
{{ repo }}
{{ num }}
```

### AI Generation Tips

1. **Be specific about purpose**: "Generate API documentation for REST endpoints" vs "make docs"
2. **Describe input structure**: "Receives: endpoint path, HTTP method, request body JSON"
3. **Provide examples**: Show expected input/output patterns
4. **Choose appropriate category**: Helps with organization and filtering
5. **Review and refine**: AI-generated prompts are starting points, not final versions

### Performance

1. **Use caching**: AIService automatically caches responses
2. **Monitor execution logs**: Check PromptExecution for slow queries
3. **Adjust max_tokens**: Balance between response quality and cost
4. **Track usage**: Monitor `usage_count` to identify popular templates

## Backward Compatibility

All existing code continues to work! The system supports both:

```python
# ✅ Old way (still works)
ai_service.call_ai_chat(
    system_prompt="You are...",
    user_prompt="Hello"
)

# ✅ New way (recommended)
ai_service.call_ai_chat(
    prompt_template_id=1,
    context={'message': 'Hello'}
)
```

## Technical Implementation

### Jinja2 Integration

Templates use Jinja2 syntax for variable substitution:

```python
from jinja2 import Template

# In PromptTemplate model
def render_user_prompt(self, context):
    template = Template(self.user_prompt_template)
    return template.render(**context)
```

### Error Handling

Custom exceptions for prompt operations:

- `PromptTemplateError`: Base exception
- `PromptTemplateNotFoundError`: Template doesn't exist
- `PromptRenderError`: Jinja2 rendering failed
- `PromptValidationError`: Invalid input/output
- `PromptSchemaError`: Schema validation failed

## Database Schema

### Migrations

Applied migration: `0005_promptdataset_prompttemplate_promptschema_and_more.py`

**Tables:**

- `core_prompttemplate`
- `core_promptschema`
- `core_promptdataset`
- `core_promptdatasetentry`
- `core_promptexecution`

**Indexes:**

- `(category, is_active)` on PromptTemplate
- `(name, -version_number)` on PromptTemplate
- `(template_id, executed_at)` on PromptExecution

## Testing

### Unit Tests

```bash
# Run all prompt-related tests
docker-compose -f infra/docker/docker-compose.yml exec web \
    pytest tests/test_prompt_management.py -v
```

### Integration Tests

Test the full workflow:

1. Create template via admin
2. Render with context
3. Call AI via AIService
4. Verify execution logged
5. Check usage_count incremented

## Future Enhancements

### Planned Features

1. **Prompt Analytics Dashboard**
   - Success rates by template
   - Token usage trends
   - Performance metrics

2. **A/B Testing Framework**
   - Compare template versions
   - Automated evaluation
   - Statistical significance testing

3. **Prompt Library**
   - Share templates across projects
   - Import/export functionality
   - Community prompts

4. **Advanced Validation**
   - Input schema validation before execution
   - Output parsing and validation
   - Automatic retry on validation failure

5. **Cost Tracking**
   - Per-template cost analysis
   - Budget alerts
   - Cost optimization suggestions

## Troubleshooting

### Template Not Found

```python
from core.exceptions import PromptTemplateNotFoundError

try:
    response = ai_service.call_ai_chat(prompt_template_id=999, context={})
except PromptTemplateNotFoundError:
    # Handle missing template
```

### Variable Substitution Errors

```python
from core.exceptions import PromptRenderError

try:
    rendered = template.render_user_prompt({'wrong_var': 'value'})
except PromptRenderError as e:
    # Missing required variable in context
    print(f"Render error: {e}")
```

## Examples

### Example 1: Code Review Prompt

```python
template = PromptTemplate.objects.create(
    name="Python Code Reviewer",
    category="code_review",
    description="Review Python code for best practices",
    system_prompt="""You are a senior Python developer. Review code for:
- PEP 8 compliance
- Security vulnerabilities
- Performance issues
- Best practices
Format output as Markdown.""",
    user_prompt_template="""Review this Python code from {{ file_path }}:

```python
{{ code_content }}
```

Provide detailed feedback.""",
    model="gpt-4o-mini",
    temperature=0.3,
    max_tokens=2000
)

# Use it

ai_service = AIService()
response = ai_service.call_ai_chat(
    prompt_template_id=template.id,
    context={
        'file_path': 'app/services.py',
        'code_content': 'def my_function(): pass'
    }
)

```

## Summary

The prompt management system provides:

✅ **Centralized prompt storage** - No more scattered prompts in code
✅ **Version control** - Track changes and roll back
✅ **Reusability** - Use templates across features
✅ **Testing** - Validate with datasets before production
✅ **Monitoring** - Track usage and performance
✅ **Backward compatible** - Existing code still works

---

**Current Status**: ✅ Fully implemented and tested
**Migration**: `0005` applied
**Templates Seeded**: 6 core templates
**Test Coverage**: 100% passing
