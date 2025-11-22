# AI Provider Configuration Guide

This document explains how to configure and use different AI providers with GitHubAI.

## Supported Providers

Currently supported AI providers:

1. **OpenAI** - GPT models (gpt-4o-mini, gpt-4, etc.)
2. **XAI** - Grok models (grok-beta, etc.)

## Configuration

### Environment Variables

Update your `.env` file with the following variables:

```bash
# AI Provider Selection
AI_PROVIDER=openai  # Options: openai, xai

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.2
OPENAI_MAX_TOKENS=2500
OPENAI_BASE_URL=https://api.openai.com/v1

# XAI Configuration
XAI_API_KEY=your-xai-api-key-here
XAI_MODEL=grok-beta
XAI_TEMPERATURE=0.2
XAI_MAX_TOKENS=2500
XAI_BASE_URL=https://api.x.ai/v1
```

### Legacy Configuration

The following legacy settings are maintained for backward compatibility:

```bash
AI_API_KEY=your-api-key  # Falls back to OPENAI_API_KEY
AI_MODEL=gpt-4o-mini     # Falls back to OPENAI_MODEL
AI_TEMPERATURE=0.2       # Falls back to OPENAI_TEMPERATURE
AI_MAX_TOKENS=2500       # Falls back to OPENAI_MAX_TOKENS
```

## Usage

### Basic Usage

```python
from core.services.ai_service import AIService

# Use default provider (configured in settings)
ai_service = AIService()
response = ai_service.call_ai_chat(
    system_prompt="You are a helpful assistant.",
    user_prompt="Hello, how are you?"
)
```

### Provider-Specific Usage

```python
# Use a specific provider for this request
response = ai_service.call_ai_chat(
    system_prompt="You are a helpful assistant.",
    user_prompt="Hello, how are you?",
    provider_name="xai"  # Force use of XAI
)
```

### Switching Providers

```python
# Switch the service instance to use a different provider
ai_service.switch_provider("xai")
response = ai_service.call_ai_chat(
    system_prompt="You are a helpful assistant.",
    user_prompt="Hello, how are you?"
)
```

### Provider Information

```python
# Get available providers
providers = AIService.get_available_providers()
print(providers)  # ['openai', 'xai']

# Get current default provider
current = AIService.get_current_provider()
print(current)  # 'openai'
```

## Management Commands

### Test Providers

Test all configured providers:

```bash
python manage.py test_ai_providers --test-all
```

Test a specific provider:

```bash
python manage.py test_ai_providers --test-provider openai --prompt "Hello, world!"
```

List available providers:

```bash
python manage.py test_ai_providers --list-providers
```

### Configuration Management

Show current configuration:

```bash
python manage.py configure_ai --show-config
```

Check API key status:

```bash
python manage.py configure_ai --check-keys
```

Set default provider:

```bash
python manage.py configure_ai --set-provider xai
```

## API Features

### Caching

Responses are automatically cached based on:

- Provider name
- Model
- Temperature
- System prompt
- User prompt

This means switching providers will create separate cache entries, preventing cross-contamination.

### Logging

All API calls are logged with provider information in the `APILog` model:

```python
# API logs include provider information
{
    'provider': 'openai',
    'model': 'gpt-4o-mini',
    'endpoint': '/openai/chat/completions',
    'tokens_used': 150
}
```

### Error Handling

Provider-specific errors are wrapped in `AIProviderError`:

```python
from core.services.ai_providers import AIProviderError

try:
    response = ai_service.call_ai_chat(...)
except AIProviderError as e:
    print(f"AI Provider error: {e}")
```

## Adding New Providers

To add a new AI provider:

1. Create a new provider class in `core/services/ai_providers.py`:

```python
class NewProviderProvider(AIProvider):
    @property
    def provider_name(self) -> str:
        return "newprovider"

    def get_client(self):
        # Initialize your provider's client
        pass

    def call_chat_completion(self, messages, model=None, temperature=None, max_tokens=None):
        # Implement the API call
        pass
```

2. Register it in the factory:

```python
class AIProviderFactory:
    PROVIDERS = {
        "openai": OpenAIProvider,
        "xai": XAIProvider,
        "newprovider": NewProviderProvider,  # Add here
    }
```

3. Add configuration to `settings.py`:

```python
# New Provider Configuration
NEWPROVIDER_API_KEY = env("NEWPROVIDER_API_KEY", default="")
NEWPROVIDER_MODEL = env("NEWPROVIDER_MODEL", default="default-model")
# ... etc
```

4. Update the factory's `create_provider` method to handle the new provider.

## Migration Notes

### Database Changes

The `AIResponse` model now includes a `provider` field. Run migrations:

```bash
python manage.py migrate
```

### Backward Compatibility

All existing code will continue to work. The system maintains backward compatibility with:

- Legacy environment variable names
- Existing API signatures
- Current cache entries (though they won't match new provider-aware hashes)

### GitHub Actions

Update your GitHub Actions secrets to include the new provider API keys:

- `OPENAI_API_KEY`
- `XAI_API_KEY`

The workflow will use the `AI_PROVIDER` environment variable to determine which provider to use.
