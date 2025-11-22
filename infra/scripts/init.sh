#!/bin/bash
# Script to initialize Django database and create superuser

set -e

echo "🔧 Initializing GitHubAI Django application..."

# Run migrations
echo "📦 Running database migrations..."
docker-compose -f infra/docker/docker-compose.yml exec web python manage.py makemigrations
docker-compose -f infra/docker/docker-compose.yml exec web python manage.py migrate

# Create superuser
echo "👤 Creating Django superuser..."
echo "Please enter superuser credentials:"
docker-compose -f infra/docker/docker-compose.yml exec web python manage.py createsuperuser

# Collect static files
echo "📁 Collecting static files..."
docker-compose -f infra/docker/docker-compose.yml exec web python manage.py collectstatic --noinput

echo "✅ Initialization complete!"
echo ""
echo "You can now access:"
echo "  - Django Admin: http://localhost:8000/admin/"
echo "  - API: http://localhost:8000/api/"
echo "  - Health Check: http://localhost:8000/health/"
