# GitHubAI Documentation

Welcome to the GitHubAI documentation! This guide will help you find the information you need.

## Quick Links

- **New Users**: Start with [Getting Started Guide](GETTING_STARTED.md)
- **API Reference**: See [api/](api/) directory
- **Release Notes**: Check [releases/](releases/) directory

## Documentation Structure

### 📚 User Guides

Essential guides for using GitHubAI features:

- **[Auto Issue Feature](guides/auto-issue-feature.md)** - Automated repository analysis and issue generation
- **[AI Provider Configuration](guides/ai-provider-configuration.md)** - Configure OpenAI, XAI/Grok, and other providers
- **[Chat Interface](guides/chat-interface.md)** - Use the AI chat web interface
- **[Troubleshooting](guides/troubleshooting.md)** - Common issues and solutions

### 🔌 API Reference

Complete API documentation:

- **[Auto-Generated API Reference](api-reference/README.md)** - Complete code reference (Sphinx)
  - Models, Services, Views, Serializers
  - Automatically generated from docstrings
- **[Auto Issue Endpoints](api/AUTO_ISSUE_ENDPOINTS.md)** - REST API for automated issue creation
- **[Chat Endpoint](api/CHAT_ENDPOINT.md)** - Conversational AI API

### 🛠️ Development

For contributors and developers:

- **[Django Implementation](development/django-implementation.md)** - Architecture and implementation details
- **[Testing Guide](development/testing-guide.md)** - How to test features
- **[Contributing](development/contributing.md)** - How to contribute to GitHubAI

### 📋 Release History

- **[Changelog](releases/CHANGELOG.md)** - All version changes
- **[v0.3.0 Release Notes](releases/v0.3.0.md)** - AI Chat Frontend
- **[v0.2.0 Release Notes](releases/v0.2.0.md)** - Auto Issue Generation

## Features Overview

### Auto Issue Generation

Automatically analyze your repository and create GitHub issues for:

- Code quality issues
- TODO/FIXME comments
- Documentation gaps
- Outdated dependencies
- Test coverage
- General repository health

### AI Chat Interface

Interactive web-based chat with AI assistants:

- Multi-provider support (OpenAI, XAI/Grok)
- Response caching for cost efficiency
- Modern React UI with Ant Design

### User Feedback Processing

Convert raw user feedback into structured GitHub issues:

- Bug reports
- Feature requests
- AI-refined content

## Getting Help

- **Documentation**: Browse this docs folder
- **Issues**: [GitHub Issues](https://github.com/bamr87/githubai/issues)
- **Source Code**: [GitHub Repository](https://github.com/bamr87/githubai)

## Quick Start

```bash
# Clone repository
git clone https://github.com/bamr87/githubai.git
cd githubai

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Start services
docker-compose -f infra/docker/docker-compose.yml up -d

# Access chat interface
open http://localhost:5173
```

See [Getting Started Guide](GETTING_STARTED.md) for detailed instructions.
