#!/bin/bash
# GitHubAI Django - Complete Startup Guide

echo "🚀 GitHubAI Django Startup Guide"
echo "=================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Check for .env file
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  IMPORTANT: Edit .env and add your API keys!"
    echo ""
    echo "Required variables:"
    echo "  - OPENAI_API_KEY: Get from https://platform.openai.com/api-keys"
    echo "  - GITHUB_TOKEN: Get from https://github.com/settings/tokens"
    echo "  - DJANGO_SECRET_KEY: Generate a secure random key"
    echo ""
    read -p "Press ENTER after you've updated .env, or Ctrl+C to exit..."
fi

echo "✅ Environment file exists"
echo ""

# Build containers
echo "🔨 Building Docker containers (this may take a few minutes)..."
docker-compose -f infra/docker/docker-compose.yml build

if [ $? -ne 0 ]; then
    echo "❌ Build failed. Check the error messages above."
    exit 1
fi

echo "✅ Build complete"
echo ""

# Start services
echo "🚀 Starting services..."
docker-compose -f infra/docker/docker-compose.yml up -d

if [ $? -ne 0 ]; then
    echo "❌ Failed to start services. Check the error messages above."
    exit 1
fi

echo "✅ Services started"
echo ""

# Wait for database
echo "⏳ Waiting for database to be ready..."
sleep 5

# Run migrations
echo "📦 Running database migrations..."
docker-compose -f infra/docker/docker-compose.yml exec -T web python manage.py migrate

if [ $? -ne 0 ]; then
    echo "❌ Migrations failed. Check the error messages above."
    exit 1
fi

echo "✅ Migrations complete"
echo ""

# Create superuser
echo "👤 Creating Django superuser..."
echo "   (You'll be prompted for username, email, and password)"
docker-compose -f infra/docker/docker-compose.yml exec web python manage.py createsuperuser

# Collect static files
echo "📁 Collecting static files..."
docker-compose -f infra/docker/docker-compose.yml exec -T web python manage.py collectstatic --noinput

echo ""
echo "=========================================="
echo "✅ GitHubAI Django is ready!"
echo "=========================================="
echo ""
echo "Access your application:"
echo "  🌐 Django Admin: http://localhost:8000/admin/"
echo "  🔌 REST API:     http://localhost:8000/api/"
echo "  💚 Health Check: http://localhost:8000/health/"
echo ""
echo "View logs:"
echo "  docker-compose -f infra/docker/docker-compose.yml logs -f"
echo ""
echo "Stop services:"
echo "  docker-compose -f infra/docker/docker-compose.yml down"
echo ""
echo "Management commands:"
echo "  docker-compose -f infra/docker/docker-compose.yml exec web python manage.py --help"
echo ""
echo "Next steps:"
echo "  1. Login to admin with your superuser credentials"
echo "  2. Create issue templates"
echo "  3. Test the REST API"
echo "  4. Review DJANGO_IMPLEMENTATION.md for full documentation"
echo ""
echo "🎉 Happy coding!"
