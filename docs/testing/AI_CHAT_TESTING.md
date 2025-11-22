# Testing: AI Chat Frontend

## Test Coverage

### Current Status

**Unit Tests**: 0% (not yet implemented)
**Integration Tests**: 0% (not yet implemented)
**E2E Tests**: 0% (manual testing only)
**Manual Testing**: ✅ Verified working

**Priority for Next Sprint**:

1. Backend API unit tests
2. Frontend component tests
3. Integration tests
4. E2E automated tests

## Running Tests

### Backend API Tests (To Be Implemented)

**All Tests**:

```bash
docker-compose -f infra/docker/docker-compose.yml exec web pytest tests/test_chat_api.py
```

**Specific Test**:

```bash
docker-compose -f infra/docker/docker-compose.yml exec web pytest tests/test_chat_api.py::test_chat_endpoint_success
```

**With Coverage**:

```bash
docker-compose -f infra/docker/docker-compose.yml exec web pytest --cov=apps.core.views --cov-report=html tests/test_chat_api.py
```

### Frontend Tests (To Be Implemented)

**All Tests**:

```bash
cd frontend && npm test
```

**Watch Mode**:

```bash
cd frontend && npm test -- --watch
```

**Coverage**:

```bash
cd frontend && npm test -- --coverage
```

## Test Scenarios

### 1. **Chat API - Successful Message**

**Purpose**: Verify basic chat functionality works end-to-end
**Test Type**: Integration

**Steps**:

1. Start backend services
2. Send POST request to `/api/chat/` with valid message
3. Verify 200 response received
4. Verify response contains required fields

**Expected**:

- HTTP 200 OK
- Response body contains: `response`, `provider`, `model`, `cached`, `timestamp`
- Response time < 10 seconds
- AI response is relevant to input

**Test Code (pytest)**:

```python
@pytest.mark.django_db
def test_chat_endpoint_success(client, mocker):
    # Mock AIService
    mock_ai_service = mocker.patch('core.views.AIService')
    mock_instance = mock_ai_service.return_value
    mock_instance.call_ai_chat.return_value = "Test AI response"
    mock_instance.provider_name = "xai"
    mock_instance.model = "grok-3"

    # Make request
    response = client.post(
        '/api/chat/',
        data={'message': 'test question'},
        content_type='application/json'
    )

    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert data['response'] == "Test AI response"
    assert data['provider'] == "xai"
    assert data['model'] == "grok-3"
    assert 'timestamp' in data
```

### 2. **Chat API - Input Validation**

**Purpose**: Verify API rejects invalid inputs
**Test Type**: Unit

**Steps**:

1. Send requests with missing/invalid message field
2. Verify appropriate error responses

**Expected**:

- Missing `message`: HTTP 400, error message
- Blank `message`: HTTP 400, error message
- Empty JSON body: HTTP 400, error message

**Test Code**:

```python
@pytest.mark.django_db
class TestChatValidation:
    def test_missing_message_field(self, client):
        response = client.post(
            '/api/chat/',
            data={},
            content_type='application/json'
        )
        assert response.status_code == 400
        assert 'message' in response.json()

    def test_blank_message(self, client):
        response = client.post(
            '/api/chat/',
            data={'message': ''},
            content_type='application/json'
        )
        assert response.status_code == 400

    def test_whitespace_only_message(self, client):
        response = client.post(
            '/api/chat/',
            data={'message': '   '},
            content_type='application/json'
        )
        assert response.status_code == 400
```

### 3. **Chat API - AIService Integration**

**Purpose**: Verify proper integration with AIService
**Test Type**: Integration

**Steps**:

1. Mock AIService methods
2. Send chat request
3. Verify AIService called with correct parameters
4. Verify response formatted correctly

**Expected**:

- `call_ai_chat()` called with system and user prompts
- System prompt contains GitHubAI context
- Response includes provider metadata

**Test Code**:

```python
@pytest.mark.django_db
def test_aiservice_integration(client, mocker):
    # Mock AIService
    mock_call = mocker.patch('core.services.ai_service.AIService.call_ai_chat')
    mock_call.return_value = "Mocked AI response"

    # Make request
    response = client.post(
        '/api/chat/',
        data={'message': 'test'},
        content_type='application/json'
    )

    # Verify AIService was called correctly
    assert mock_call.called
    call_args = mock_call.call_args
    assert 'GitHubAI' in call_args.kwargs['system_prompt']
    assert call_args.kwargs['user_prompt'] == 'test'
```

### 4. **Chat API - Error Handling**

**Purpose**: Verify graceful handling of AI service failures
**Test Type**: Unit

**Steps**:

1. Mock AIService to raise exception
2. Send chat request
3. Verify 500 error returned with generic message

**Expected**:

- HTTP 500 Internal Server Error
- Generic error message (no sensitive details leaked)
- Error logged for debugging

**Test Code**:

```python
@pytest.mark.django_db
def test_aiservice_error_handling(client, mocker):
    # Mock AIService to raise exception
    mock_ai_service = mocker.patch('core.views.AIService')
    mock_instance = mock_ai_service.return_value
    mock_instance.call_ai_chat.side_effect = Exception("AI provider error")

    # Make request
    response = client.post(
        '/api/chat/',
        data={'message': 'test'},
        content_type='application/json'
    )

    # Assertions
    assert response.status_code == 500
    data = response.json()
    assert 'error' in data
    assert 'Failed to generate response' in data['error']
    # Ensure no internal error details leaked
    assert 'AI provider error' not in data['error']
```

### 5. **Frontend - Message Sending**

**Purpose**: Verify user can send messages through UI
**Test Type**: Component (React Testing Library)

**Steps**:

1. Render App component
2. Type message in input field
3. Click send button
4. Verify message appears in chat

**Expected**:

- Input cleared after sending
- User message displayed with correct styling
- Loading indicator shown during request
- AI response displayed when received

**Test Code (Jest + React Testing Library)**:

```javascript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import axios from 'axios';
import App from './App';

jest.mock('axios');

test('user can send message and receive response', async () => {
  // Mock API response
  axios.post.mockResolvedValue({
    data: {
      response: 'AI test response',
      provider: 'xai',
      model: 'grok-3',
      cached: false,
      timestamp: new Date().toISOString()
    }
  });

  // Render component
  render(<App />);

  // Type message
  const input = screen.getByPlaceholderText(/Type your message/i);
  fireEvent.change(input, { target: { value: 'test message' } });

  // Send message
  const sendButton = screen.getByText(/Send/i);
  fireEvent.click(sendButton);

  // Verify user message displayed
  expect(screen.getByText('test message')).toBeInTheDocument();

  // Wait for AI response
  await waitFor(() => {
    expect(screen.getByText('AI test response')).toBeInTheDocument();
  });

  // Verify provider info displayed
  expect(screen.getByText(/xai/i)).toBeInTheDocument();
});
```

### 6. **Frontend - Error Handling**

**Purpose**: Verify UI handles API errors gracefully
**Test Type**: Component

**Steps**:

1. Mock API to return error
2. Send message
3. Verify error notification shown
4. Verify message not added to chat

**Expected**:

- Error toast notification appears
- User message shown but no AI response
- Input remains functional after error

**Test Code**:

```javascript
test('displays error notification on API failure', async () => {
  // Mock API error
  axios.post.mockRejectedValue(new Error('Network error'));

  render(<App />);

  const input = screen.getByPlaceholderText(/Type your message/i);
  fireEvent.change(input, { target: { value: 'test' } });

  const sendButton = screen.getByText(/Send/i);
  fireEvent.click(sendButton);

  // Wait for error notification
  await waitFor(() => {
    expect(screen.getByText(/Failed to send message/i)).toBeInTheDocument();
  });
});
```

### 7. **Integration - Full User Flow**

**Purpose**: Verify complete user journey from UI to AI and back
**Test Type**: End-to-End

**Steps**:

1. Open frontend in browser
2. Type question in chat
3. Press Enter to send
4. Verify AI response appears
5. Send follow-up question
6. Verify both messages retained in history

**Expected**:

- Both messages and responses visible
- Provider/model info shown
- No console errors
- Reasonable response time (<10s)

**Manual Test**:

```
1. Navigate to http://localhost:5173
2. Type: "What is GitHubAI?"
3. Press Enter
4. ✓ User message appears immediately
5. ✓ Loading indicator shows
6. ✓ AI response appears within 5 seconds
7. ✓ Provider "xai" and model "grok-3" shown
8. Type: "Tell me more about the auto-issue feature"
9. Press Enter
10. ✓ Previous messages still visible
11. ✓ New AI response appears
12. ✓ Conversation history maintained
```

### 8. **Performance - Response Caching**

**Purpose**: Verify AI response caching reduces API calls
**Test Type**: Integration

**Steps**:

1. Send identical message twice
2. Verify first call hits AI provider
3. Verify second call uses cache
4. Check APILog for cache hit

**Expected**:

- First request: ~2-5s, creates APILog entry
- Second request: ~100ms, uses cached response
- `AIResponse` model contains cached entry

**Test Code**:

```python
@pytest.mark.django_db
def test_response_caching(client):
    message = "What is semantic versioning?"

    # First request
    start1 = time.time()
    response1 = client.post(
        '/api/chat/',
        data={'message': message},
        content_type='application/json'
    )
    duration1 = time.time() - start1

    # Second request (should be cached)
    start2 = time.time()
    response2 = client.post(
        '/api/chat/',
        data={'message': message},
        content_type='application/json'
    )
    duration2 = time.time() - start2

    # Assertions
    assert response1.status_code == 200
    assert response2.status_code == 200
    assert response1.json()['response'] == response2.json()['response']
    assert duration2 < duration1  # Second should be faster
```

### 9. **Security - CORS Headers**

**Purpose**: Verify CORS properly configured
**Test Type**: Integration

**Steps**:

1. Send OPTIONS preflight request
2. Verify CORS headers present
3. Verify allowed origin includes frontend

**Expected**:

- `Access-Control-Allow-Origin` header present
- Frontend origin (localhost:5173) allowed
- Credentials allowed

**Test Code**:

```bash
# Manual test
curl -X OPTIONS http://localhost:8000/api/chat/ \
  -H "Origin: http://localhost:5173" \
  -H "Access-Control-Request-Method: POST" \
  -v | grep "Access-Control"
```

### 10. **Load Testing - Multiple Concurrent Requests**

**Purpose**: Verify system handles concurrent users
**Test Type**: Performance

**Steps**:

1. Send 10 simultaneous requests
2. Verify all succeed
3. Measure average response time
4. Check for any timeout errors

**Expected**:

- All requests return 200 OK
- Average response time < 10s
- No timeouts or connection errors
- Database handles concurrent writes

**Test Code** (using locust):

```python
from locust import HttpUser, task, between

class ChatUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def send_chat_message(self):
        self.client.post(
            "/api/chat/",
            json={"message": "Test message"},
            headers={"Content-Type": "application/json"}
        )
```

## Manual Testing Checklist

### Pre-Testing Setup

- [ ] All Docker services running (`docker-compose ps`)
- [ ] Backend accessible (`curl http://localhost:8000/health/`)
- [ ] Frontend accessible (<http://localhost:5173> loads)
- [ ] AI provider API key configured in `.env`
- [ ] `AI_PROVIDER` set in `.env`

### Backend API Tests

- [ ] POST to `/api/chat/` with valid message returns 200
- [ ] Response includes all required fields (response, provider, model, cached, timestamp)
- [ ] Missing `message` field returns 400 error
- [ ] Blank `message` returns 400 error
- [ ] CORS headers present for frontend origin
- [ ] API call logged to `APILog` table
- [ ] Response cached in `AIResponse` table
- [ ] Second identical request uses cache

### Frontend UI Tests

- [ ] Chat interface loads without errors
- [ ] Can type in input field
- [ ] Send button enabled when text present
- [ ] Send button disabled when text empty
- [ ] Pressing Enter sends message
- [ ] Shift+Enter creates new line in input
- [ ] User message appears immediately after sending
- [ ] Loading indicator shows during API call
- [ ] AI response appears after API call completes
- [ ] Provider and model info displayed below AI message
- [ ] Message history preserved (multiple messages visible)
- [ ] Error notification appears if API fails
- [ ] Can send multiple messages in sequence
- [ ] Timestamps are reasonable

### Integration Tests

- [ ] Frontend successfully calls backend API
- [ ] Backend successfully calls AIService
- [ ] AIService successfully calls AI provider
- [ ] Response flows back through all layers
- [ ] Caching works across frontend requests
- [ ] Multiple browser tabs work independently

### Error Handling Tests

- [ ] Stop backend → frontend shows error notification
- [ ] Invalid API key → 500 error with generic message
- [ ] AI provider timeout → handled gracefully
- [ ] Network interruption → error displayed to user
- [ ] Invalid JSON → 400 error
- [ ] Large message (>10000 chars) → handled or rejected

### Performance Tests

- [ ] Initial page load < 2 seconds
- [ ] First AI response < 10 seconds
- [ ] Cached response < 1 second
- [ ] UI remains responsive during API call
- [ ] No memory leaks after 10+ messages
- [ ] Browser console shows no errors

### Security Tests

- [ ] No API keys exposed in frontend code
- [ ] Error messages don't leak sensitive information
- [ ] CORS restricted to known origins
- [ ] No SQL injection possible through message input
- [ ] No XSS possible through chat display

## Test Data Requirements

### Required Fixtures

**AI Provider Configuration**:

```bash
# In .env
AI_PROVIDER=xai
XAI_API_KEY=test-key-here
XAI_MODEL=grok-3
```

**Test Messages**:

```python
TEST_MESSAGES = [
    "What is GitHubAI?",
    "How do I create an issue?",
    "Explain GitHub Actions",
    "What features does GitHubAI have?",
    "Help me with Django",
]
```

### Environment Setup

**Development**:

```bash
# Start all services
docker-compose -f infra/docker/docker-compose.yml up -d

# Run migrations
docker-compose exec web python manage.py migrate

# Create test data
docker-compose exec web python manage.py shell
>>> from core.models import AIResponse
>>> # Add test cached responses
```

### Mock Data

**Mocked AI Response**:

```json
{
  "response": "This is a test AI response for automated testing purposes.",
  "provider": "xai",
  "model": "grok-3",
  "cached": false,
  "timestamp": "2025-11-22T10:00:00Z"
}
```

## Test Automation

### Continuous Integration

**GitHub Actions Workflow** (`.github/workflows/test-chat-feature.yml`):

```yaml
name: Chat Feature Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_DB: test_db
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: test_pass
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-django pytest-cov

      - name: Run backend tests
        env:
          DATABASE_URL: postgresql://test_user:test_pass@localhost:5432/test_db
          REDIS_URL: redis://localhost:6379/0
          AI_PROVIDER: mock
        run: pytest tests/test_chat_api.py --cov

      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'

      - name: Install frontend dependencies
        run: |
          cd frontend
          npm install

      - name: Run frontend tests
        run: |
          cd frontend
          npm test -- --coverage
```

## Known Test Gaps

1. **Backend Unit Tests**: Not yet implemented
   - Need tests for `ChatView`
   - Need tests for serializers
   - Need AIService integration tests

2. **Frontend Tests**: Not yet implemented
   - Need component tests
   - Need integration tests
   - Need E2E tests with Cypress or Playwright

3. **Performance Tests**: Manual only
   - Need automated load testing
   - Need response time benchmarks
   - Need concurrent user testing

4. **Security Tests**: Basic manual only
   - Need automated security scanning
   - Need penetration testing
   - Need authentication testing (when implemented)

## Next Steps

1. **Priority 1**: Implement backend API unit tests
2. **Priority 2**: Add frontend component tests
3. **Priority 3**: Set up CI/CD test automation
4. **Priority 4**: Create E2E test suite
5. **Priority 5**: Implement performance benchmarks

---

**Last Updated**: 2025-11-22
**Test Coverage Goal**: 80% by v0.4.0
**Status**: Manual testing complete, automated tests pending
