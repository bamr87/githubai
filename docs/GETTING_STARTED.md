# Getting Started with GitHubAI

This guide will help you set up and start using GitHubAI quickly.

## Prerequisites

- Docker and Docker Compose installed
- GitHub account and personal access token
- AI provider API key (OpenAI, XAI/Grok, etc.)

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/bamr87/githubai.git
cd githubai
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit with your API keys
nano .env
```

**Required environment variables:**

```bash
# GitHub API
GITHUB_TOKEN=ghp_your_github_token_here

# AI Provider (choose one)
AI_PROVIDER=xai  # or 'openai', 'anthropic', etc.

# XAI Configuration (if using XAI)
XAI_API_KEY=your_xai_api_key
XAI_MODEL=grok-3

# OpenAI Configuration (if using OpenAI)
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4o-mini
```

### 3. Start Services

```bash
# Start all Docker services
docker-compose -f infra/docker/docker-compose.yml up -d

# Initialize database
docker-compose -f infra/docker/docker-compose.yml exec web python manage.py migrate

# Create admin user (optional)
docker-compose -f infra/docker/docker-compose.yml exec web python manage.py createsuperuser
```

### 4. Access the Application

- **Chat Interface**: <http://localhost:5173>
- **Django Admin**: <http://localhost:8000/admin/>
- **API Root**: <http://localhost:8000/api/>

## Key Features

### AI Chat Interface

Open <http://localhost:5173> and start chatting with AI assistants.

### Auto Issue Generation

```bash
# List available analysis types
docker-compose exec web python manage.py auto_issue --list-chores

# Run code quality analysis
docker-compose exec web python manage.py auto_issue \
    --repo bamr87/githubai \
    --chore-type code_quality
```

### API Usage

```bash
# Create auto-issue via API
curl -X POST http://localhost:8000/api/issues/issues/create-auto-issue/ \
    -H "Content-Type: application/json" \
    -d '{"chore_type": "code_quality", "auto_submit": true}'
```

## Next Steps

- **Explore Features**: See [Auto Issue Feature Guide](guides/auto-issue-feature.md)
- **Configure AI Providers**: Read [AI Provider Configuration](guides/ai-provider-configuration.md)
- **Use the Chat Interface**: Check [Chat Interface Guide](guides/chat-interface.md)
- **Setup Test Environment**: Learn about [Test Environment](guides/test-environment.md) for isolated testing
- **View API Documentation**: Browse [API Reference](api/)

## Common Commands

```bash
# View logs
docker-compose logs -f web

# Stop services
docker-compose down

# Restart services
docker-compose restart

# Run tests
docker-compose exec web pytest
```

## Troubleshooting

See the [Troubleshooting Guide](guides/troubleshooting.md) for common issues and solutions.

## Getting Help

- **Documentation**: Browse the [docs/](.) directory
- **Issues**: Report bugs at [GitHub Issues](https://github.com/bamr87/githubai/issues)
- **Contributing**: See [Contributing Guide](development/contributing.md)
