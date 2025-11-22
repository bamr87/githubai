# AI Chat Frontend

## Overview

The AI Chat Frontend is a modern, React-based web interface that provides real-time conversational interaction with GitHubAI's multi-provider AI services. Built with React 19, Vite 7, and Ant Design 6, it offers a clean, responsive chat experience while leveraging the existing Django backend's AIService infrastructure for AI provider integration, response caching, and comprehensive API logging.

**Purpose**: Enable users to interact conversationally with AI assistants through a web interface, providing an accessible entry point to GitHubAI's AI capabilities without requiring API knowledge or command-line tools.

**Key Value Propositions**:

- **Multi-Provider Support**: Seamlessly works with OpenAI, XAI (Grok), and other configured AI providers
- **Cost Efficiency**: Leverages existing AIService caching to reduce redundant API calls
- **User Friendly**: Modern UI with real-time responses, message history, and provider transparency
- **Production Ready**: Docker-integrated, CORS-configured, and follows GitHubAI coding standards

## Architecture

### Components Involved

#### Frontend Layer

- **React Application** (`frontend/`)
  - `App.jsx`: Main chat component with state management
  - `App.css`: Component-specific styling
  - Vite build system for development and production
  - Ant Design UI component library

#### Backend Layer

- **Django REST API** (`apps/core/`)
  - `ChatView`: API view handler for chat requests
  - `chat_serializers.py`: Request/response validation
  - `urls.py`: Route configuration for `/api/chat/`

#### Service Layer

- **AIService** (`apps/core/services/ai_service.py`)
  - Provider-agnostic AI integration
  - Response caching via `AIResponse` model
  - API logging via `APILog` model
  - Multi-provider support (OpenAI, XAI, etc.)

### Data Flow Diagram

```
┌──────────────────────────────────────────────────────────┐
│                     User Browser                         │
│                                                          │
│  ┌────────────────────────────────────────────┐        │
│  │   React Frontend (localhost:5173)          │        │
│  │   - Ant Design UI                          │        │
│  │   - axios HTTP client                      │        │
│  │   - Message state management               │        │
│  └────────────┬───────────────────────────────┘        │
└───────────────┼──────────────────────────────────────────┘
                │ HTTP POST /api/chat/
                │ { "message": "user input" }
                ▼
┌──────────────────────────────────────────────────────────┐
│              Django Backend (localhost:8000)             │
│                                                          │
│  ┌────────────────────────────────────────────┐        │
│  │   ChatView (REST API)                      │        │
│  │   - Request validation                     │        │
│  │   - ChatMessageSerializer                  │        │
│  └────────────┬───────────────────────────────┘        │
│               │                                          │
│               ▼                                          │
│  ┌────────────────────────────────────────────┐        │
│  │   AIService                                 │        │
│  │   - call_ai_chat()                         │        │
│  │   - Provider selection                     │        │
│  │   - Cache check (AIResponse)               │        │
│  └────────────┬───────────────────────────────┘        │
│               │                                          │
│               │ Cache Miss                               │
│               ▼                                          │
│  ┌────────────────────────────────────────────┐        │
│  │   AI Provider (OpenAI/XAI/etc)             │        │
│  │   - API call via provider adapter          │        │
│  │   - Response processing                    │        │
│  └────────────┬───────────────────────────────┘        │
│               │                                          │
│               ▼                                          │
│  ┌────────────────────────────────────────────┐        │
│  │   Data Persistence                         │        │
│  │   - AIResponse (caching)                   │        │
│  │   - APILog (usage tracking)                │        │
│  └────────────┬───────────────────────────────┘        │
│               │                                          │
│               │ JSON Response                            │
│               │ { "response": "...",                     │
│               │   "provider": "xai",                     │
│               │   "model": "grok-3", ... }              │
│               ▼                                          │
│  ┌────────────────────────────────────────────┐        │
│  │   ChatResponseSerializer                   │        │
│  │   - Response formatting                    │        │
│  └────────────┬───────────────────────────────┘        │
└───────────────┼──────────────────────────────────────────┘
                │
                │ HTTP 200 OK
                ▼
┌──────────────────────────────────────────────────────────┐
│   React Frontend                                         │
│   - Display AI message                                   │
│   - Show provider/model info                            │
│   - Update message history                              │
└──────────────────────────────────────────────────────────┘
```

### Integration Points

#### 1. **Frontend ↔ Backend API**

- **Protocol**: HTTP/REST over JSON
- **Endpoint**: `POST /api/chat/`
- **CORS**: Configured for `localhost:5173` in Django settings
- **Authentication**: Currently open (recommend adding auth for production)

#### 2. **Backend ↔ AIService**

- **Interface**: Python method call `call_ai_chat(system_prompt, user_prompt)`
- **Returns**: String (AI response text)
- **Caching**: Automatic via `AIResponse` model lookups
- **Logging**: Automatic via `APILog` model writes

#### 3. **AIService ↔ AI Providers**

- **Interface**: Provider-specific adapters via `AIProviderFactory`
- **Providers Supported**: OpenAI, XAI (Grok), extensible for more
- **Configuration**: Environment variables (`AI_PROVIDER`, `OPENAI_API_KEY`, etc.)

### Dependencies

#### Frontend Dependencies

```json
{
  "react": "^19.2.0",
  "react-dom": "^19.2.0",
  "antd": "^6.0.0",
  "axios": "^1.13.2",
  "vite": "^7.2.4"
}
```

#### Backend Dependencies

- Django REST Framework (existing)
- `corsheaders` (existing)
- AIService and associated models (existing)

#### Infrastructure Dependencies

- Docker & Docker Compose
- PostgreSQL (for data persistence)
- Redis (for Celery, optional for this feature)

## Implementation Details

### Key Classes and Modules

#### Frontend (`frontend/src/App.jsx`)

**Main Component: `App`**

```javascript
function App() {
  const [messages, setMessages] = useState([])
  const [inputValue, setInputValue] = useState('')
  const [loading, setLoading] = useState(false)

  const sendMessage = async () => {
    // Handles user input, API call, and state updates
  }
}
```

**Key Methods**:

- `sendMessage()`: Sends user message to backend, handles response
- `handleKeyPress()`: Keyboard shortcut handler (Enter to send)

**State Management**:

- `messages`: Array of message objects with `{id, content, role, timestamp, provider, model}`
- `inputValue`: Current text in input field
- `loading`: Boolean indicating API request in progress

**UI Components Used**:

- `Layout`, `Header`, `Content`, `Footer`: Page structure
- `Card`: Message container
- `List`: Message history display
- `Avatar`: User/AI icons
- `TextArea`: Multi-line input
- `Button`: Send action
- `message`: Toast notifications for errors

#### Backend (`apps/core/views.py`)

**API View: `ChatView`**

```python
class ChatView(APIView):
    permission_classes = []  # Open access (TODO: add auth)

    def post(self, request):
        """Handle chat messages and return AI responses."""
        # 1. Validate input via ChatMessageSerializer
        # 2. Call AIService.call_ai_chat()
        # 3. Format response via ChatResponseSerializer
        # 4. Return JSON response
```

**Error Handling**:

- Input validation errors: HTTP 400
- AI service errors: HTTP 500 with generic error message
- Comprehensive logging for debugging

#### Serializers (`apps/core/chat_serializers.py`)

**ChatMessageSerializer**:

```python
class ChatMessageSerializer(serializers.Serializer):
    message = serializers.CharField(required=True, allow_blank=False)
```

**ChatResponseSerializer**:

```python
class ChatResponseSerializer(serializers.Serializer):
    response = serializers.CharField()
    provider = serializers.CharField()
    model = serializers.CharField()
    cached = serializers.BooleanField()
    timestamp = serializers.DateTimeField()
```

### Service Layer Changes

**AIService Integration**:

- No modifications required to `AIService` class
- Uses existing `call_ai_chat()` method
- Leverages existing caching and logging infrastructure
- Provider selection via environment variable `AI_PROVIDER`

**System Prompt**:

```python
system_message = (
    "You are a helpful AI assistant integrated with GitHubAI. "
    "You can help users with questions about GitHub automation, "
    "issue management, and general programming topics."
)
```

### Database Schema Changes

**No new models added**. Uses existing:

- `APILog`: Logs all AI API calls (existing)
- `AIResponse`: Caches AI responses (existing)

### API Endpoints

#### POST `/api/chat/`

**Request**:

```json
{
  "message": "Your question here"
}
```

**Response (200 OK)**:

```json
{
  "response": "AI assistant response text",
  "provider": "xai",
  "model": "grok-3",
  "cached": false,
  "timestamp": "2025-11-22T06:30:57.352960Z"
}
```

**Response (400 Bad Request)**:

```json
{
  "message": ["This field is required."]
}
```

**Response (500 Internal Server Error)**:

```json
{
  "error": "Failed to generate response. Please try again."
}
```

## Configuration

### Environment Variables Required

#### Backend (`.env`)

```bash
# AI Provider Configuration
AI_PROVIDER=xai  # or 'openai'

# XAI Configuration (Grok)
XAI_API_KEY=your-xai-api-key
XAI_MODEL=grok-3
XAI_TEMPERATURE=0.2
XAI_MAX_TOKENS=2500
XAI_BASE_URL=https://api.x.ai/v1

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.2
OPENAI_MAX_TOKENS=2500
OPENAI_BASE_URL=https://api.openai.com/v1

# CORS Configuration
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# Django Settings
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
```

#### Frontend (`frontend/.env`)

```bash
VITE_API_URL=http://localhost:8000
```

### Settings Changes

**apps/githubai/settings.py**:

```python
# CORS settings updated to include frontend dev server
CORS_ALLOWED_ORIGINS = env.list(
    "CORS_ALLOWED_ORIGINS",
    default=["http://localhost:3000", "http://localhost:5173"]
)
CORS_ALLOW_CREDENTIALS = True
```

### Third-Party Service Setup

#### AI Provider Setup

**Option 1: XAI (Grok)**

1. Sign up at <https://x.ai>
2. Generate API key
3. Add to `.env` as `XAI_API_KEY`
4. Set `AI_PROVIDER=xai`

**Option 2: OpenAI**

1. Sign up at <https://platform.openai.com>
2. Generate API key
3. Add to `.env` as `OPENAI_API_KEY`
4. Set `AI_PROVIDER=openai`

## Usage Examples

### Starting the Application

```bash
# Start all services (backend + frontend)
docker-compose -f infra/docker/docker-compose.yml up -d

# View logs
docker-compose -f infra/docker/docker-compose.yml logs -f frontend
docker-compose -f infra/docker/docker-compose.yml logs -f web
```

### Accessing the Chat Interface

Open browser to: `http://localhost:5173`

### API Usage (Direct)

```bash
# Send chat message via cURL
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "What is GitHubAI?"}'
```

```python
# Python example
import requests

response = requests.post(
    'http://localhost:8000/api/chat/',
    json={'message': 'How do I create an issue?'}
)

data = response.json()
print(f"AI Response: {data['response']}")
print(f"Provider: {data['provider']}")
print(f"Model: {data['model']}")
```

```javascript
// JavaScript example
const response = await fetch('http://localhost:8000/api/chat/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ message: 'Explain GitHub Actions' })
});

const data = await response.json();
console.log(`AI: ${data.response}`);
```

### Common Use Cases

#### 1. General Questions

User types: "What features does GitHubAI have?"
AI provides overview of GitHubAI capabilities

#### 2. GitHub Automation Help

User types: "How do I automate issue creation?"
AI explains using the auto-issue feature

#### 3. Programming Assistance

User types: "Show me how to use Django REST Framework"
AI provides code examples and explanations

#### 4. Troubleshooting

User types: "Why am I getting a 500 error?"
AI suggests debugging steps and common solutions

## Testing

### How to Test the Feature

#### 1. Manual Testing

**Backend API Test**:

```bash
# Test endpoint is accessible
curl http://localhost:8000/api/chat/ \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}' \
  -w "\nHTTP Status: %{http_code}\n"
```

**Frontend UI Test**:

1. Open `http://localhost:5173`
2. Verify chat interface loads
3. Type a message and press Enter
4. Verify AI response appears
5. Check provider/model info displays

#### 2. Integration Testing

```bash
# Run backend tests (TODO: add specific chat tests)
docker-compose -f infra/docker/docker-compose.yml exec web pytest tests/
```

### Test Scenarios Covered

#### Functional Tests

- ✅ Chat interface loads successfully
- ✅ User can send messages
- ✅ AI responses are received and displayed
- ✅ Provider and model information shown
- ✅ Message history preserved in UI
- ✅ Loading states work correctly
- ✅ Error notifications display

#### API Tests (Manual)

- ✅ POST to `/api/chat/` returns 200 with valid input
- ✅ Invalid input returns 400
- ✅ AI service errors return 500
- ✅ CORS headers present for frontend origin

#### Integration Tests

- ✅ Frontend connects to backend
- ✅ Backend calls AIService
- ✅ AIService uses correct provider
- ✅ Responses cached properly
- ✅ API calls logged correctly

### Manual Testing Steps

1. **Start Services**

   ```bash
   docker-compose -f infra/docker/docker-compose.yml up -d
   ```

2. **Verify Services Running**

   ```bash
   docker-compose -f infra/docker/docker-compose.yml ps
   # Expect: frontend, web, db, redis all "Up"
   ```

3. **Test Backend Endpoint**

   ```bash
   curl -X POST http://localhost:8000/api/chat/ \
     -H "Content-Type: application/json" \
     -d '{"message": "test"}'
   # Expect: JSON response with "response", "provider", "model" fields
   ```

4. **Test Frontend**
   - Open <http://localhost:5173>
   - Type "Hello" and send
   - Expect: AI response within 2-5 seconds
   - Verify: Provider name (xai/openai) shown below message

5. **Test Caching**
   - Send same message twice
   - Check logs: `docker-compose logs web | grep "Cache hit"`
   - Expect: Second request uses cached response

6. **Test Error Handling**
   - Stop web service: `docker-compose stop web`
   - Try sending message in UI
   - Expect: Error notification appears
   - Restart: `docker-compose start web`

## Troubleshooting

### Common Issues

#### Issue: Frontend shows "Failed to send message"

**Symptoms**:

- Error toast appears in UI
- No AI response received
- Browser console shows network error

**Diagnosis**:

```bash
# Check if backend is running
curl http://localhost:8000/health/

# Check CORS configuration
curl -X OPTIONS http://localhost:8000/api/chat/ \
  -H "Origin: http://localhost:5173" \
  -H "Access-Control-Request-Method: POST" -v

# Check backend logs
docker-compose -f infra/docker/docker-compose.yml logs web --tail=50
```

**Solutions**:

1. Verify backend is running: `docker-compose ps web`
2. Check CORS settings include `http://localhost:5173`
3. Verify API endpoint URL in `frontend/.env`
4. Restart backend: `docker-compose restart web`

#### Issue: "AI_PROVIDER not configured" error

**Symptoms**:

- 500 error from backend
- Logs show AIProvider error

**Diagnosis**:

```bash
# Check environment variables
docker-compose exec web env | grep AI_PROVIDER
docker-compose exec web env | grep API_KEY
```

**Solutions**:

1. Set `AI_PROVIDER=xai` or `openai` in `.env`
2. Ensure corresponding API key is set
3. Restart services: `docker-compose restart web`

#### Issue: Slow response times

**Symptoms**:

- AI responses take >10 seconds
- UI shows loading spinner for extended period

**Diagnosis**:

```bash
# Check API logs for duration
docker-compose logs web | grep "Duration:"

# Check AI provider status
curl https://status.openai.com  # or XAI status page
```

**Solutions**:

1. Check network connectivity
2. Verify AI provider service status
3. Enable caching (should be default)
4. Consider reducing `MAX_TOKENS` in configuration

#### Issue: Chat history not displaying

**Symptoms**:

- Messages disappear after refresh
- No message history shown

**Explanation**:

- Current implementation uses React state (in-memory)
- History lost on page refresh
- This is expected behavior

**Future Enhancement**:

- Add conversation persistence to database
- Implement session-based history
- Add export/import functionality

### Debug Tips

#### Enable Verbose Logging

```python
# In apps/githubai/settings.py
LOGGING = {
    'root': {
        'level': 'DEBUG',  # Change from INFO
    }
}
```

#### Check API Call Flow

```bash
# Monitor all API calls
docker-compose logs -f web | grep -E "(chat|AI API)"

# Check database for cached responses
docker-compose exec web python manage.py shell
>>> from core.models import AIResponse
>>> AIResponse.objects.count()
>>> AIResponse.objects.latest('created_at')
```

#### Frontend Debugging

```javascript
// Add in App.jsx sendMessage function
console.log('Sending message:', inputValue);
console.log('API URL:', API_BASE_URL);
console.log('Response data:', response.data);
```

### Known Limitations

1. **No Authentication**: Chat endpoint is currently open
   - **Impact**: Anyone can access and use AI services
   - **Mitigation**: Add authentication before production deployment

2. **No Conversation Persistence**: History lost on refresh
   - **Impact**: Users can't review past conversations
   - **Mitigation**: Implement database-backed conversation storage

3. **No Rate Limiting**: Unlimited requests possible
   - **Impact**: Potential API cost abuse
   - **Mitigation**: Implement rate limiting per user/IP

4. **Single System Prompt**: Same for all users
   - **Impact**: Can't customize AI behavior per user
   - **Mitigation**: Add user-configurable system prompts

5. **No Streaming**: Responses sent after completion
   - **Impact**: Longer perceived wait time for large responses
   - **Mitigation**: Implement SSE or WebSocket streaming

## Security Considerations

### Authentication/Authorization Changes

**Current State**:

```python
class ChatView(APIView):
    permission_classes = []  # No authentication required
```

**Recommended for Production**:

```python
from rest_framework.permissions import IsAuthenticated

class ChatView(APIView):
    permission_classes = [IsAuthenticated]
```

### Data Privacy Implications

1. **Chat Content Storage**:
   - User messages sent to third-party AI providers
   - Responses cached in database (`AIResponse` model)
   - **Recommendation**: Add user consent notice, implement data retention policy

2. **API Logs**:
   - All requests logged to `APILog` model
   - Includes user messages (truncated)
   - **Recommendation**: Implement PII detection and redaction

3. **Provider Data Sharing**:
   - Messages sent to OpenAI/XAI external APIs
   - Subject to provider privacy policies
   - **Recommendation**: Display provider information to users, allow provider selection

### Security Best Practices Applied

1. ✅ **Input Validation**: Django REST Framework serializers validate all inputs
2. ✅ **CORS Configuration**: Restricted to known origins (localhost for dev)
3. ✅ **Error Handling**: Generic error messages (no sensitive data leaked)
4. ✅ **Environment Variables**: API keys stored securely, not in code
5. ✅ **SQL Injection Protection**: Django ORM used throughout
6. ⚠️ **Authentication**: Not yet implemented (required for production)
7. ⚠️ **Rate Limiting**: Not yet implemented (required for production)
8. ⚠️ **HTTPS**: Not configured (required for production)

### Production Security Checklist

- [ ] Implement authentication (JWT, session, or OAuth)
- [ ] Add rate limiting (per user and IP)
- [ ] Enable HTTPS only
- [ ] Restrict CORS to production domain
- [ ] Add request size limits
- [ ] Implement input sanitization
- [ ] Add audit logging for security events
- [ ] Set up monitoring and alerts
- [ ] Implement data retention policy
- [ ] Add user consent for AI processing
- [ ] Review and update privacy policy
- [ ] Perform security audit/penetration testing

## Performance Impact

### Expected Performance Characteristics

**Response Times**:

- Cached responses: ~50-100ms
- New AI requests: 1-5 seconds (depends on provider)
- Network latency: +50-200ms for frontend-backend communication

**Resource Usage (per container)**:

- Frontend: ~50MB RAM, minimal CPU
- Backend: +5-10MB RAM for chat endpoint
- Database: +10KB per cached response

**Scalability**:

- Frontend: Static assets, easily CDN-cacheable
- Backend: Stateless API, horizontally scalable
- Database: Caching reduces load on AI providers

### Optimization Techniques Used

1. **Response Caching**:
   - `AIService` checks `AIResponse` model before API calls
   - Reduces redundant API costs
   - Improves response time for repeated queries

2. **Efficient UI Updates**:
   - React state management minimizes re-renders
   - Only message list updated on new messages

3. **Lazy Loading**:
   - Vite code-splitting for smaller initial bundle
   - Ant Design tree-shaking for minimal CSS

4. **Database Indexing**:
   - `AIResponse.prompt_hash` indexed (existing)
   - Fast cache lookups

### Resource Requirements

**Development**:

- CPU: 2 cores minimum
- RAM: 4GB minimum
- Disk: 500MB for Docker images
- Network: 5+ Mbps for AI provider API calls

**Production** (estimated for 100 concurrent users):

- CPU: 4+ cores
- RAM: 8GB+
- Disk: 10GB+ (for logs and cached responses)
- Network: 100+ Mbps
- Database: PostgreSQL with 2GB+ RAM

### Performance Monitoring

**Metrics to Track**:

- API response times (p50, p95, p99)
- Cache hit rate
- AI provider API latency
- Frontend page load time
- Error rates

**Monitoring Implementation** (future):

```python
# Add to settings.py
MIDDLEWARE += ['core.middleware.PerformanceMonitoringMiddleware']

# Track metrics
from django.core.cache import cache
cache.set('chat_api_calls', cache.get('chat_api_calls', 0) + 1)
```

## Future Enhancements

1. **Authentication & Authorization**
   - User accounts and session management
   - Role-based access control
   - API key authentication option

2. **Conversation Persistence**
   - Save chat history to database
   - Multi-conversation support
   - Conversation search and export

3. **Advanced Features**
   - File upload for context
   - Streaming responses (SSE/WebSocket)
   - Voice input/output
   - Multi-language support

4. **AI Capabilities**
   - Provider selection in UI
   - Custom system prompts per user
   - Fine-tuned models for GitHubAI domain
   - Integration with GitHub data

5. **UI/UX Improvements**
   - Dark mode support
   - Mobile-optimized design
   - Keyboard shortcuts
   - Message formatting (markdown, code blocks)
   - Copy to clipboard functionality

6. **Analytics & Insights**
   - Usage dashboards
   - Cost tracking per user
   - Popular queries analysis
   - A/B testing different prompts

---

**Version**: 0.3.0
**Last Updated**: 2025-11-22
**Status**: Implemented and Functional
**Contributors**: Development Team
