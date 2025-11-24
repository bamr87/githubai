# AI Configuration - Quick Start Guide

## Overview

GitHubAI now supports database-driven AI model configuration. Manage providers, models, and API keys through the Django admin interface instead of hardcoded values.

## Admin Access

**URL**: <http://localhost:8000/admin/>

**Pages**:

- **AI Providers** - Manage API keys and provider settings
- **AI Models** - View and configure available models
- **Prompt Templates** - Link templates to specific models

## Adding a Provider

1. Navigate to **Admin > Core > AI Providers > Add AI Provider**

2. Fill in the form:
   - **Name**: Provider identifier (e.g., `openai`, `anthropic`)
   - **Display Name**: Human-readable name (e.g., `OpenAI`, `Anthropic`)
   - **API Key**: Your API key (secured, password field)
   - **Base URL**: API endpoint (e.g., `https://api.openai.com/v1`)
   - **Is Active**: Check to enable this provider

3. Click **Save**

## Adding a Model

1. Navigate to **Admin > Core > AI Models > Add AI Model**

2. Fill in required fields:
   - **Provider**: Select from dropdown
   - **Name**: Model identifier (e.g., `gpt-4o-mini`)
   - **Display Name**: Human-readable name
   - **Max Tokens**: Maximum output tokens
   - **Context Window**: Total context size
   - **Capabilities**: Select applicable (chat, vision, code, etc.)

3. Optional fields:
   - **Pricing**: Input/output price per 1M tokens
   - **Is Default**: Set as default for this provider
   - **Release/Deprecation Dates**: Lifecycle tracking

4. Click **Save**

## Using in Code

### Default Behavior

```python
from core.services.ai_service import AIService

# Uses default provider from database
ai_service = AIService()
response = ai_service.call_ai_chat(
    system_prompt="You are helpful",
    user_prompt="Hello!"
)
```

### Specific Provider

```python
# Use specific provider
ai_service = AIService(provider_name='openai')
```

### Specific Model

```python
from core.models import AIModel

# Get model by ID
model = AIModel.objects.get(name='gpt-4o')
ai_service = AIService(ai_model_id=model.id)
```

### With Templates

```python
# Template uses its configured ai_model
ai_service = AIService()
response = ai_service.call_ai_chat(
    prompt_template_id=1,
    context={'message': 'Hello'}
)
```

## Seeding Initial Data

```bash
# Populate providers and models
docker-compose exec web python manage.py seed_ai_providers

# Update API keys from environment
docker-compose exec web python manage.py seed_ai_providers --update-keys
```

This creates:

- **OpenAI**: 4 models (GPT-4o, GPT-4o Mini, GPT-4 Turbo, GPT-3.5 Turbo)
- **XAI**: 2 models (Grok Beta, Grok Vision Beta)
- **Anthropic**: 3 models (Claude 3.5 Sonnet, Opus, Haiku)

## Updating API Keys

### Via Admin (Recommended)

1. Go to **Admin > Core > AI Providers**
2. Click on provider name
3. Enter new API key in password field
4. Click **Save**

### Via Command

```bash
# Re-run seed command with --update-keys flag
docker-compose exec web python manage.py seed_ai_providers --update-keys
```

## Common Tasks

### Set Default Model for Provider

1. **Admin > Core > AI Models**
2. Select model(s)
3. Choose **Actions > Set as default for provider**
4. Click **Go**

### Disable a Model

1. **Admin > Core > AI Models**
2. Select model(s)
3. Choose **Actions > Deactivate selected models**
4. Click **Go**

### Link Template to Model

1. **Admin > Core > Prompt Templates**
2. Click template name
3. In **Model Configuration** section, select **AI Model** from dropdown
4. Click **Save**

## Checking Configuration

```bash
# List providers and models
docker-compose exec web python -c "
import django; django.setup()
from core.models import AIProvider, AIModel

for p in AIProvider.objects.filter(is_active=True):
    print(f'{p.display_name}:')
    for m in p.models.filter(is_active=True):
        print(f'  - {m.display_name}')
"
```

## Troubleshooting

### "No active models found for provider"

- Ensure at least one model is active for that provider
- Check provider's `is_active` status
- Run seed command: `python manage.py seed_ai_providers`

### "Provider configuration validation failed"

- API key not set or invalid
- Add API key through admin interface
- Verify API key has correct format

### Legacy Settings Still Used

- Database providers take precedence
- Check if provider exists in database
- Fallback to settings.py only if not in DB

## Security

### API Keys

- Stored in database (can be encrypted in production)
- Password field in admin (not visible after save)
- Not exposed in API responses

### Best Practices

1. Use different API keys for dev/staging/prod
2. Rotate keys regularly
3. Restrict admin access
4. Consider encryption for production

## Cost Tracking

Pricing information stored per model enables:

- Calculate costs from token usage
- Compare model costs
- Budget planning

Example:

```python
from core.models import AIModel, PromptExecution

# Get model pricing
model = AIModel.objects.get(name='gpt-4o-mini')
print(f"Input: ${model.input_price_per_million}/1M tokens")
print(f"Output: ${model.output_price_per_million}/1M tokens")

# Calculate costs from executions
executions = PromptExecution.objects.filter(ai_model=model)
total_tokens = sum(e.tokens_used or 0 for e in executions)
cost = (total_tokens / 1_000_000) * float(model.output_price_per_million)
print(f"Total cost: ${cost:.2f}")
```

## FAQ

**Q: Can I still use settings.py for configuration?**
A: Yes, the system falls back to settings.py if provider not in database.

**Q: Do I need to update existing code?**
A: No, all existing code is backward compatible.

**Q: How do I add a new provider like Anthropic?**
A: Use the admin interface or run `seed_ai_providers` (includes Anthropic).

**Q: What happens if I delete a provider?**
A: Models under that provider become inactive. Existing references preserved.

**Q: Can I have multiple API keys for the same provider?**
A: Not currently. Use multiple provider entries with different names if needed.

## Next Steps

1. ✅ Access admin interface
2. ✅ Run `seed_ai_providers` to populate data
3. ✅ Add/update API keys through admin
4. ⏩ Link prompt templates to preferred models
5. ⏩ Set up cost tracking (future enhancement)
6. ⏩ Configure API key encryption for production

---

**For detailed documentation**: See `docs/features/AI_MODEL_ABSTRACTION.md`
