# Chat API Endpoint

## Endpoint: `/api/chat/`

### Method: POST

## Description

The Chat API endpoint provides conversational AI capabilities through GitHubAI's multi-provider AIService infrastructure. It accepts user messages and returns AI-generated responses along with metadata about the provider, model, caching status, and timestamp.

This endpoint integrates seamlessly with the existing AIService, supporting multiple AI providers (OpenAI, XAI/Grok) with automatic response caching for cost efficiency and comprehensive API logging for monitoring and debugging.

**Use Cases**:

- Interactive chat applications
- AI-powered support interfaces
- Conversational tools for developers
- Integration with custom frontends

## Authentication

**Current Status**: No authentication required
**Permissions**: Open access (all requests accepted)
**Recommended for Production**: Add authentication (`IsAuthenticated` permission class)

**Future Implementation**:

```python
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

class ChatView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
```

## Request

### Endpoint URL

```
POST http://localhost:8000/api/chat/
```

### Headers

```http
Content-Type: application/json
Accept: application/json
```

**Optional Headers** (when authentication is enabled):

```http
Authorization: Bearer <token>
```

### Path Parameters

None

### Query Parameters

None

### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `message` | string | Yes | User's message or question to send to the AI assistant. Cannot be blank. |

**Example**:

```json
{
  "message": "What is GitHubAI and what can it do?"
}
```

**Validation Rules**:

- `message` field is required
- `message` cannot be blank or whitespace-only
- No maximum length enforced (provider limits apply)

## Response

### Success Response (200 OK)

Returns AI-generated response with metadata.

**Response Body**:

```json
{
  "response": "GitHubAI is an automation platform...",
  "provider": "xai",
  "model": "grok-3",
  "cached": false,
  "timestamp": "2025-11-22T06:30:57.352960Z"
}
```

**Response Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `response` | string | AI-generated response text |
| `provider` | string | AI provider used (e.g., "xai", "openai") |
| `model` | string | Specific model used (e.g., "grok-3", "gpt-4o-mini") |
| `cached` | boolean | Whether response was served from cache (currently always `false` in response, but caching happens internally) |
| `timestamp` | string (ISO 8601) | When the response was generated |

### Error Responses

#### 400 Bad Request

Returned when request validation fails.

**Example - Missing message field**:

```json
{
  "message": ["This field is required."]
}
```

**Example - Blank message**:

```json
{
  "message": ["This field may not be blank."]
}
```

#### 401 Unauthorized

Returned when authentication is enabled but no valid credentials provided.

```json
{
  "detail": "Authentication credentials were not provided."
}
```

#### 500 Internal Server Error

Returned when AI service fails or unexpected error occurs.

```json
{
  "error": "Failed to generate response. Please try again."
}
```

**Common Causes**:

- AI provider API is down
- Invalid API key configuration
- AI provider rate limit exceeded
- Network connectivity issues

## Examples

### cURL

**Basic Request**:

```bash
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "How do I create a GitHub issue?"}'
```

**Pretty-printed Response**:

```bash
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Explain GitHub Actions"}' \
  | python -m json.tool
```

**With Authentication** (when enabled):

```bash
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token-here" \
  -d '{"message": "What features does GitHubAI have?"}'
```

### Python

**Using `requests` library**:

```python
import requests

# Send chat message
response = requests.post(
    'http://localhost:8000/api/chat/',
    json={'message': 'What is semantic versioning?'}
)

# Check for success
if response.status_code == 200:
    data = response.json()
    print(f"AI: {data['response']}")
    print(f"Provider: {data['provider']}")
    print(f"Model: {data['model']}")
else:
    print(f"Error: {response.status_code}")
    print(response.json())
```

**With error handling**:

```python
import requests
from requests.exceptions import RequestException

def chat_with_ai(message):
    """Send message to GitHubAI chat API."""
    try:
        response = requests.post(
            'http://localhost:8000/api/chat/',
            json={'message': message},
            timeout=30  # 30 second timeout
        )
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        print(f"API request failed: {e}")
        return None

# Usage
result = chat_with_ai("How do I use Docker with Django?")
if result:
    print(result['response'])
```

**With authentication** (when enabled):

```python
import requests

headers = {
    'Authorization': 'Bearer your-token-here',
    'Content-Type': 'application/json'
}

response = requests.post(
    'http://localhost:8000/api/chat/',
    json={'message': 'Hello'},
    headers=headers
)
```

### JavaScript (fetch)

**Basic Request**:

```javascript
async function chatWithAI(message) {
  try {
    const response = await fetch('http://localhost:8000/api/chat/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log('AI Response:', data.response);
    console.log('Provider:', data.provider);
    console.log('Model:', data.model);

    return data;
  } catch (error) {
    console.error('Chat API error:', error);
    return null;
  }
}

// Usage
chatWithAI('What is GitHubAI?');
```

**With axios**:

```javascript
import axios from 'axios';

const chatAPI = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json'
  }
});

async function sendMessage(message) {
  try {
    const response = await chatAPI.post('/api/chat/', { message });
    return response.data;
  } catch (error) {
    if (error.response) {
      // Server responded with error status
      console.error('API Error:', error.response.data);
    } else if (error.request) {
      // No response received
      console.error('No response from server');
    } else {
      // Request setup error
      console.error('Error:', error.message);
    }
    throw error;
  }
}

// Usage
sendMessage('Explain Docker')
  .then(data => console.log(data.response))
  .catch(error => console.error('Failed:', error));
```

### TypeScript

**With type definitions**:

```typescript
interface ChatRequest {
  message: string;
}

interface ChatResponse {
  response: string;
  provider: string;
  model: string;
  cached: boolean;
  timestamp: string;
}

interface ErrorResponse {
  error?: string;
  message?: string[];
}

async function chatWithAI(message: string): Promise<ChatResponse | null> {
  try {
    const response = await fetch('http://localhost:8000/api/chat/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message } as ChatRequest)
    });

    if (!response.ok) {
      const error: ErrorResponse = await response.json();
      console.error('API Error:', error);
      return null;
    }

    const data: ChatResponse = await response.json();
    return data;
  } catch (error) {
    console.error('Network error:', error);
    return null;
  }
}

// Usage with type safety
chatWithAI('What is semantic versioning?').then(data => {
  if (data) {
    console.log(`${data.provider} (${data.model}): ${data.response}`);
  }
});
```

## Rate Limiting

**Current Status**: No rate limiting implemented
**Recommendation**: Implement rate limiting before production deployment

**Suggested Implementation**:

- Per-user limit: 100 requests per hour
- Per-IP limit: 50 requests per hour (unauthenticated)
- Burst allowance: 10 requests per minute

**Example with Django Rate Limit**:

```python
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

class ChatView(APIView):
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
```

## Caching Behavior

The Chat API leverages GitHubAI's `AIResponse` caching system:

1. **Cache Key Generation**: Based on provider, model, temperature, system prompt, and user message
2. **Cache Lookup**: Checked before calling AI provider
3. **Cache Hit**: Returns cached response, increments hit counter
4. **Cache Miss**: Calls AI provider, stores response in cache
5. **Cache Storage**: `AIResponse` model in PostgreSQL database

**Benefits**:

- Reduces AI provider API costs
- Improves response times for repeated queries
- Transparent to API consumers

**Cache Invalidation**:

- No automatic expiration (manual deletion required)
- Cache can be cleared via Django admin or management command

## Logging

All API requests are logged to the `APILog` model:

**Logged Information**:

- Request timestamp
- Endpoint and HTTP method
- Request data (user message)
- Response data (truncated AI response)
- Status code
- Duration in milliseconds
- Provider and model used
- Token usage (when available)
- User ID (if authenticated)
- Error messages (if any)

**Access Logs**:

```python
from core.models import APILog

# View recent chat API calls
recent_logs = APILog.objects.filter(
    api_type='ai',
    endpoint__contains='chat'
).order_by('-created_at')[:10]

for log in recent_logs:
    print(f"{log.created_at}: {log.status_code} - {log.duration_ms}ms")
```

## Performance

**Expected Response Times**:

- Cached responses: 50-100ms
- OpenAI API: 1-3 seconds
- XAI (Grok) API: 1-5 seconds
- Network latency: +50-200ms

**Optimization Tips**:

1. Keep messages concise for faster responses
2. Repeated queries benefit from caching
3. Consider streaming for large responses (future feature)

## Error Handling

**Client-Side Best Practices**:

```javascript
async function robustChatRequest(message, retries = 3) {
  for (let i = 0; i < retries; i++) {
    try {
      const response = await fetch('http://localhost:8000/api/chat/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message }),
        timeout: 30000  // 30 second timeout
      });

      if (response.status === 500 && i < retries - 1) {
        // Retry on server error
        await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
        continue;
      }

      return await response.json();
    } catch (error) {
      if (i === retries - 1) throw error;
    }
  }
}
```

## Testing

**Manual Testing**:

```bash
# Test successful request
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}' \
  -w "\nStatus: %{http_code}\n"

# Test validation error (missing message)
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{}' \
  -w "\nStatus: %{http_code}\n"

# Test validation error (blank message)
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": ""}' \
  -w "\nStatus: %{http_code}\n"
```

**Automated Testing** (example):

```python
import pytest
from django.test import Client
from django.urls import reverse

@pytest.mark.django_db
def test_chat_endpoint_success():
    client = Client()
    response = client.post(
        reverse('chat'),
        data={'message': 'test message'},
        content_type='application/json'
    )

    assert response.status_code == 200
    data = response.json()
    assert 'response' in data
    assert 'provider' in data
    assert 'model' in data

@pytest.mark.django_db
def test_chat_endpoint_validation():
    client = Client()
    response = client.post(
        reverse('chat'),
        data={},
        content_type='application/json'
    )

    assert response.status_code == 400
    assert 'message' in response.json()
```

## Security Considerations

**Current Vulnerabilities**:

1. ❌ No authentication - anyone can use the API
2. ❌ No rate limiting - potential for abuse
3. ❌ No input length limits - potential for large requests

**Recommendations for Production**:

1. ✅ Implement authentication (JWT, session, or API key)
2. ✅ Add rate limiting per user/IP
3. ✅ Set maximum message length (e.g., 10,000 characters)
4. ✅ Enable HTTPS only
5. ✅ Implement CSRF protection for web clients
6. ✅ Add request logging and monitoring
7. ✅ Implement input sanitization
8. ✅ Add WAF (Web Application Firewall) rules

## Related Documentation

- [AI Chat Frontend Feature Documentation](../features/AI_CHAT_FRONTEND.md)
- [Frontend Quick Start Guide](../FRONTEND_QUICKSTART.md)
- [AIService Documentation](../../apps/core/services/README.md)
- [API Overview](./README.md)

## Changelog

- **v0.3.0** (2025-11-22): Initial release of Chat API endpoint

## Support

For issues or questions:

- Check backend logs: `docker-compose logs web`
- Verify AI provider configuration in `.env`
- Review [troubleshooting guide](../features/AI_CHAT_FRONTEND.md#troubleshooting)
- Open GitHub issue: <https://github.com/bamr87/githubai/issues>
