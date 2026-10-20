#!/bin/bash
# AI-Seed Simple End-to-End Testing Suite
# Path: System Testing → Quick Validation → Basic Checks

set -uo pipefail

echo "🌱 AI-Seed Simple End-to-End Testing"
echo "===================================="

# Test results tracking
PASS_COUNT=0
FAIL_COUNT=0

# Test helper functions
test_check() {
    local test_name="$1"
    local test_command="$2"
    
    echo -n "🧪 $test_name: "
    if eval "$test_command" > /dev/null 2>&1; then
        echo "✅ PASS"
        ((PASS_COUNT++))
    else
        echo "❌ FAIL"
        ((FAIL_COUNT++))
    fi
}

echo "📦 Container Health:"
test_check "All containers up" "docker-compose ps | grep -c 'Up' | grep -q '4'"
test_check "Frontend accessible" "curl -f -s http://localhost:3000"
test_check "API health check" "curl -f -s http://localhost:3001/health"
test_check "Database ready" "docker-compose exec -T database pg_isready -U seed_user -d ai_seed_dev"

echo ""
echo "🔗 API Endpoints:"
test_check "Evolution API" "curl -f -s http://localhost:3001/api/evolution"
test_check "Metrics API" "curl -f -s http://localhost:3001/api/metrics"
test_check "Paths API" "curl -f -s http://localhost:3001/api/paths"

echo ""
echo "🧠 Evolution Engine:"
test_check "Engine health" "docker-compose exec -T api node -e \"const http = require('http'); http.get('http://evolution:5000/health', (res) => { process.exit(res.statusCode === 200 ? 0 : 1); }).on('error', () => process.exit(1));\""

echo ""
echo "🌐 Frontend Features:"
test_check "HTML content" "curl -s http://localhost:3000 | grep -q 'AI-Seed'"
test_check "Vite dev server" "curl -s http://localhost:3000 | grep -q 'vite'"

echo ""
echo "💾 Database:"
test_check "DB connection" "docker-compose exec -T database psql -U seed_user -d ai_seed_dev -c 'SELECT 1;'"

echo ""
echo "📊 FINAL RESULTS"
echo "================"
echo "✅ Passed: $PASS_COUNT"
echo "❌ Failed: $FAIL_COUNT"
echo "📊 Total: $((PASS_COUNT + FAIL_COUNT))"

if [ $FAIL_COUNT -eq 0 ]; then
    echo ""
    echo "🎉 ALL TESTS PASSED!"
    echo "✨ AI-Seed is fully functional and ready!"
    echo ""
    echo "🌱 System Status: HEALTHY"
    echo "🚀 Ready for development and production use"
    echo ""
    echo "Quick access URLs:"
    echo "  Frontend: http://localhost:3000"
    echo "  API Health: http://localhost:3001/health"
    echo "  Evolution Data: http://localhost:3001/api/evolution"
    echo "  Metrics: http://localhost:3001/api/metrics"
    echo ""
    exit 0
else
    echo ""
    echo "⚠️  $FAIL_COUNT test(s) failed"
    echo "🔧 Please review and fix issues"
    exit 1
fi
