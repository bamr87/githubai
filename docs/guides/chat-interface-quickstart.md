# GitHubAI Frontend - Quick Start Guide

## Overview

The GitHubAI frontend is a React-based chat interface that connects to the Django backend's AI services. It provides a clean, modern UI for interacting with AI assistants powered by OpenAI, XAI (Grok), and other providers.

## Prerequisites

- Docker and Docker Compose installed
- GitHubAI backend services running
- AI provider API keys configured in `.env`

## Getting Started

### 1. Start the Application

```bash
# From the project root
docker-compose -f infra/docker/docker-compose.yml up -d
```

This starts all services:

- **Frontend**: <http://localhost:5173>
- **Backend API**: <http://localhost:8000>
- **Database**: PostgreSQL on port 5432
- **Cache**: Redis on port 6379

### 2. Access the Chat Interface

Open your browser and navigate to:

```
http://localhost:5173
```

You should see the GitHubAI chat interface with:

- A header with the GitHubAI logo
- An empty chat area
- An input box at the bottom to start chatting

### 3. Start Chatting

Type a message in the input box and press Enter or click the Send button. The AI assistant will respond using the configured AI provider (check your `.env` file for `AI_PROVIDER` setting).

## Features

### Chat Interface

- **Real-time responses** from AI assistants
- **Message history** displayed in conversation format
- **Provider information** shown with each AI response
- **Keyboard shortcuts**: Enter to send, Shift+Enter for new line

### AI Integration

- Uses the same `AIService` as the backend
- Supports multiple AI providers (OpenAI, XAI/Grok)
- Response caching for cost efficiency
- Full API logging and monitoring

## Troubleshooting

### Frontend not loading

```bash
# Check frontend logs
docker-compose -f infra/docker/docker-compose.yml logs frontend

# Rebuild frontend container
docker-compose -f infra/docker/docker-compose.yml up -d --build frontend
```

### API connection errors

```bash
# Verify backend is running
docker-compose -f infra/docker/docker-compose.yml ps web

# Check CORS settings in apps/githubai/settings.py
# Should include: http://localhost:5173
```

### Chat not responding

1. Check AI provider API key in `.env`
2. Verify `AI_PROVIDER` is set (e.g., `AI_PROVIDER=xai`)
3. Check backend logs:

```bash
docker-compose -f infra/docker/docker-compose.yml logs web
```

## Development

### Local Development (without Docker)

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev

# The app will be available at http://localhost:5173
```

Make sure the backend API is running and accessible at `http://localhost:8000`.

### Making Changes

The Vite dev server supports hot module replacement (HMR). Any changes you make to files in `frontend/src/` will automatically reload in the browser.

## API Endpoint

The frontend communicates with the backend through:

**POST** `/api/chat/`

Request:

```json
{
  "message": "Your question here"
}
```

Response:

```json
{
  "response": "AI assistant response",
  "provider": "xai",
  "model": "grok-3",
  "cached": false,
  "timestamp": "2025-11-21T12:00:00Z"
}
```

## Next Steps

- Customize the AI system message in `apps/core/views.py` (`ChatView`)
- Add authentication to protect the chat endpoint
- Implement conversation history persistence
- Add file upload capabilities for context
- Create additional pages (issue management, documentation, etc.)

## Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   React     │  HTTP   │    Django    │  Cache  │    Redis    │
│  Frontend   │────────>│   REST API   │<───────>│             │
│  (Vite)     │         │   (DRF)      │         └─────────────┘
└─────────────┘         └──────────────┘
                               │
                               │ Uses
                               ▼
                        ┌──────────────┐
                        │  AIService   │
                        │  (OpenAI,    │
                        │   XAI, etc)  │
                        └──────────────┘
```

## Support

For issues or questions:

1. Check the logs: `docker-compose -f infra/docker/docker-compose.yml logs`
2. Review the Django coding guidelines in `.github/copilot-instructions.md`
3. Ensure all environment variables are properly configured in `.env`
