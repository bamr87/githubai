#!/bin/bash
# Script to build and run GitHubAI in Docker

set -e

echo "🐳 Building GitHubAI Docker containers..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your API keys before running!"
    exit 1
fi

# Build containers
docker-compose -f infra/docker/docker-compose.yml build

echo "✅ Build complete!"
echo ""
echo "To start the application, run:"
echo "  docker-compose -f infra/docker/docker-compose.yml up"
echo ""
echo "Or in development mode:"
echo "  docker-compose -f infra/docker/docker-compose.yml -f infra/docker/docker-compose.dev.yml up"
