# AI Chat Interface Guide

## Overview

The AI Chat Interface provides a modern web-based conversational experience with AI assistants. Built with React and Ant Design, it offers real-time chat with multi-provider support.

## Quick Start

1. **Start Services**:

   ```bash
   docker-compose -f infra/docker/docker-compose.yml up -d
   ```

2. **Access Interface**:

   Open <http://localhost:5173> in your browser

3. **Start Chatting**:

   Type your message and press Enter

## Features

### Multi-Provider Support

Works with your configured AI provider:

- OpenAI (GPT-4, GPT-3.5)
- XAI (Grok)
- Anthropic (Claude)
- And more

Provider is selected via environment variable `AI_PROVIDER`.

### Response Caching

Identical queries use cached responses for:

- Faster response times
- Reduced API costs
- Better reliability

### Message History

- Conversation preserved during session
- Scroll through past messages
- Provider and model information displayed

### Keyboard Shortcuts

- **Enter**: Send message
- **Shift+Enter**: New line in message

## Configuration

### Environment Variables

Set in `.env` file:

```bash
# AI Provider Selection
AI_PROVIDER=xai  # or 'openai', 'anthropic', etc.

# Provider-specific configuration
XAI_API_KEY=your_key_here
XAI_MODEL=grok-3

# Frontend API URL (optional)
VITE_API_URL=http://localhost:8000
```

### CORS Settings

Backend CORS is configured for `http://localhost:5173` by default.

For production, update `apps/githubai/settings.py`:

```python
CORS_ALLOWED_ORIGINS = [
    "https://yourdomain.com"
]
```

## API Integration

The chat interface uses the REST API endpoint:

**Endpoint**: `POST /api/chat/`

**Request**:

```json
{
  "message": "Your question here"
}
```

**Response**:

```json
{
  "response": "AI assistant response",
  "provider": "xai",
  "model": "grok-3",
  "cached": false,
  "timestamp": "2025-11-22T06:30:57Z"
}
```

See [Chat Endpoint API Documentation](../api/CHAT_ENDPOINT.md) for complete reference.

## Usage Examples

### General Questions

**You**: What features does GitHubAI have?

**AI**: GitHubAI provides automated GitHub workflow management including...

### Programming Help

**You**: Show me how to use Django REST Framework

**AI**: Here's how to create a simple API endpoint...

### GitHub Automation

**You**: How do I create an automated issue?

**AI**: You can use the auto-issue command...

## Troubleshooting

### Frontend Not Loading

```bash
# Check if frontend service is running
docker-compose ps frontend

# Restart frontend
docker-compose restart frontend

# Check logs
docker-compose logs frontend
```

### Connection Errors

1. Verify backend is running: `docker-compose ps web`
2. Check CORS configuration in settings.py
3. Verify API URL in `frontend/.env`

### Slow Responses

- Check AI provider status
- Verify network connectivity
- Review backend logs for errors
- Consider caching for repeated queries

### No Response from AI

1. Verify AI provider API key is set
2. Check `AI_PROVIDER` environment variable
3. Review backend logs: `docker-compose logs web`

## Production Deployment

### Security Recommendations

Before deploying to production:

1. **Add Authentication**: Implement user authentication on chat endpoint
2. **Enable Rate Limiting**: Prevent API abuse
3. **Use HTTPS**: Enable SSL/TLS for all connections
4. **Restrict CORS**: Limit to production domain only
5. **Add Input Limits**: Set maximum message length

### Example Authentication

```python
# In apps/core/views.py
from rest_framework.permissions import IsAuthenticated

class ChatView(APIView):
    permission_classes = [IsAuthenticated]
```

### Performance Optimization

- Use CDN for frontend static assets
- Enable response compression
- Implement connection pooling
- Scale horizontally with load balancer

## Advanced Features

### Planned Enhancements (v0.4.0+)

- User authentication and session management
- Conversation persistence to database
- File upload for context
- Streaming responses for real-time typing
- Voice input/output
- Multi-conversation support
- Dark mode theme

## Development

### Running Locally (without Docker)

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

Backend must be running at `http://localhost:8000`.

### Building for Production

```bash
cd frontend
npm run build

# Output in frontend/dist/
```

Serve with nginx or CDN.

## Related Documentation

- [Chat Endpoint API](../api/CHAT_ENDPOINT.md) - Complete API reference
- [AI Provider Configuration](ai-provider-configuration.md) - Configure AI providers
- [Frontend Quickstart](chat-interface-quickstart.md) - Quick reference guide
- [Troubleshooting Guide](troubleshooting.md) - Common issues

## Support

- **Documentation**: Check this docs folder
- **Issues**: [GitHub Issues](https://github.com/bamr87/githubai/issues)
- **Logs**: `docker-compose logs web` and `docker-compose logs frontend`
