#!/bin/bash
# Launch GitHubAI Test Environment
# Creates isolated test environment with mock AI data for review/testing
#
# Usage:
#   ./infra/scripts/launch_test_env.sh [--full] [--persist] [--teardown]
#
# Options:
#   --full      Full fresh setup (flush DB, regenerate all data)
#   --persist   Keep test DB between runs
#   --teardown  Stop and remove test environment
#   --help      Show this help message

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Docker Compose command
DOCKER_COMPOSE="docker-compose -f infra/docker/docker-compose.yml -f infra/docker/docker-compose.test.yml"

# Help message
show_help() {
    echo "GitHubAI Test Environment Launcher"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --full      Full fresh setup (flush DB, regenerate all data)"
    echo "  --persist   Keep test DB between runs"
    echo "  --teardown  Stop and remove test environment"
    echo "  --help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                    # Quick start with existing data"
    echo "  $0 --full             # Fresh start, clean slate"
    echo "  $0 --full --persist   # Fresh start, keep for next time"
    echo "  $0 --teardown         # Stop and cleanup"
}

# Teardown function
teardown() {
    echo -e "${YELLOW}Stopping test environment...${NC}"
    cd "$PROJECT_ROOT"
    $DOCKER_COMPOSE down -v
    echo -e "${GREEN}✓ Test environment stopped and cleaned up${NC}"
    exit 0
}

# Parse arguments
FULL_FLAG=""
PERSIST_FLAG=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --full)
            FULL_FLAG="--full"
            shift
            ;;
        --persist)
            PERSIST_FLAG="--persist"
            shift
            ;;
        --teardown)
            teardown
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

echo "================================================================================"
echo "GitHubAI Test Environment Launcher"
echo "================================================================================"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}✗ Docker is not running${NC}"
    echo "Please start Docker and try again"
    exit 1
fi

# Check if .env.test exists
cd "$PROJECT_ROOT"
if [ ! -f ".env.test" ]; then
    echo -e "${YELLOW}⚠ .env.test not found${NC}"
    echo "Creating .env.test from template..."
    cp .env.test.example .env.test
    echo -e "${GREEN}✓ Created .env.test${NC}"
    echo ""
    echo -e "${YELLOW}Note: Review .env.test and customize if needed${NC}"
    echo ""
fi

# Step 1: Start Docker services
echo "--------------------------------------------------------------------------------"
echo "▶ Step 1: Starting Docker Services"
echo "--------------------------------------------------------------------------------"
echo ""

echo "Starting test containers..."
$DOCKER_COMPOSE up -d

echo ""
echo "Waiting for services to be healthy..."
sleep 5

# Check if services are running
if ! $DOCKER_COMPOSE ps | grep -q "Up"; then
    echo -e "${RED}✗ Failed to start services${NC}"
    echo "Check logs: docker-compose logs"
    exit 1
fi

echo -e "${GREEN}✓ Services started${NC}"
echo ""

# Step 2: Wait for database
echo "--------------------------------------------------------------------------------"
echo "▶ Step 2: Waiting for Database"
echo "--------------------------------------------------------------------------------"
echo ""

MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if $DOCKER_COMPOSE exec -T web python -c "
import sys
import psycopg2
try:
    psycopg2.connect('postgresql://githubai_test:test123@db:5432/githubai_test')
    sys.exit(0)
except Exception:
    sys.exit(1)
" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Database ready${NC}"
        break
    fi

    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo -n "."
    sleep 1
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo -e "\n${RED}✗ Database failed to become ready${NC}"
    exit 1
fi

echo ""

# Step 3: Run setup_test_env
echo "--------------------------------------------------------------------------------"
echo "▶ Step 3: Initialize Test Environment"
echo "--------------------------------------------------------------------------------"
echo ""

SETUP_CMD="python manage.py setup_test_env $FULL_FLAG $PERSIST_FLAG --verbose"

echo "Running: $SETUP_CMD"
echo ""

if $DOCKER_COMPOSE exec web $SETUP_CMD; then
    echo ""
    echo -e "${GREEN}✓ Test environment initialized${NC}"
else
    echo ""
    echo -e "${RED}✗ Setup failed${NC}"
    echo "Check logs above for errors"
    exit 1
fi

# Step 4: Display access information
echo ""
echo "================================================================================"
echo "✅ Test Environment Ready!"
echo "================================================================================"
echo ""
echo "🌐 Access URLs:"
echo "   • Django Admin:    http://localhost:8001/admin/"
echo "   • API Root:        http://localhost:8001/api/"
echo "   • Chat Interface:  http://localhost:5174/"
echo "   • Documentation:   http://localhost:8002/"
echo ""
echo "🔑 Test Credentials:"
echo "   • Username: admin"
echo "   • Password: admin123"
echo ""
echo "🤖 AI Provider:"
echo "   • Using MockAIProvider (deterministic canned responses)"
echo "   • No real API costs incurred"
echo ""
echo "📊 Useful Commands:"
echo "   • View logs:     docker-compose logs -f web"
echo "   • Shell access:  docker-compose exec web bash"
echo "   • Django shell:  docker-compose exec web python manage.py shell"
echo "   • Run tests:     docker-compose exec web pytest"
echo "   • Teardown:      $0 --teardown"
echo ""
echo "📚 Documentation:"
echo "   • See docs/guides/test-environment.md for full guide"
echo ""
echo "================================================================================"
