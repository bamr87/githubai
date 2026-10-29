# API Reference

## Overview
The AI-Seed API provides comprehensive access to the evolution engine and system metrics. All endpoints return JSON responses and follow RESTful conventions.

## Authentication
Currently, the API operates without authentication in development mode. Production deployments should implement appropriate security measures.

## Base URL
- Development: `http://localhost:3001/api`
- Production: `https://api.ai-seed.com/api`

## Response Format
All API responses follow this structure:
```json
{
  "success": true,
  "data": { ... },
  "timestamp": "2025-01-23T05:27:14.000Z",
  "message": "Optional message"
}
```

Error responses:
```json
{
  "success": false,
  "error": "Error description",
  "message": "Detailed error message",
  "timestamp": "2025-01-23T05:27:14.000Z"
}
```

## Endpoints

### Evolution Engine

#### GET /evolution
Get complete evolution engine status and metrics.

**Response:**
```json
{
  "timestamp": "2025-01-23T05:27:14.000Z",
  "engine": {
    "status": "running",
    "currentCycle": 24,
    "totalCycles": 23,
    "efficiency": 94.2,
    "lastActivity": "2025-01-23T05:25:14.000Z"
  },
  "metrics": {
    "totalCycles": 23,
    "improvementsMade": 47,
    "efficiencyGain": 15.8,
    "pathsOptimized": 12,
    "timesSaved": "2.3 hours",
    "bugsFixed": 8,
    "performanceGains": "15.8%",
    "reliabilityIncrease": "12.4%",
    "healthScore": 85
  },
  "recentActivity": [
    {
      "id": 1,
      "type": "optimization",
      "description": "Improved Docker build cache",
      "impact": "+15% efficiency",
      "timestamp": "2025-01-23T05:25:14.000Z",
      "pathsAffected": ["build-path"]
    }
  ],
  "healthIndicators": {
    "buildSystem": 85,
    "codeQuality": 78,
    "testCoverage": 72,
    "documentation": 85,
    "security": 91,
    "performance": 89
  },
  "suggestions": [
    {
      "id": "suggestion-1",
      "priority": "high",
      "type": "performance",
      "title": "Optimize container image layers",
      "description": "Reduce Docker image size by 30%",
      "estimatedImpact": "Build time -45s, Storage -150MB",
      "complexity": "medium",
      "pathsAffected": ["build-path", "deploy-path"]
    }
  ]
}
```

#### GET /evolution/metrics
Get evolution metrics only.

**Response:**
```json
{
  "timestamp": "2025-01-23T05:27:14.000Z",
  "metrics": {
    "totalCycles": 23,
    "improvementsMade": 47,
    "efficiencyGain": 15.8,
    "healthScore": 85
  },
  "engine": {
    "status": "running",
    "efficiency": 94.2,
    "currentCycle": 24
  }
}
```

#### GET /evolution/activity
Get recent evolution activity.

**Response:**
```json
{
  "timestamp": "2025-01-23T05:27:14.000Z",
  "activity": [
    {
      "id": 1,
      "type": "optimization",
      "description": "Improved Docker build cache",
      "impact": "+15% efficiency",
      "timestamp": "2025-01-23T05:25:14.000Z",
      "pathsAffected": ["build-path"]
    }
  ]
}
```

#### GET /evolution/suggestions
Get AI-generated improvement suggestions.

**Response:**
```json
{
  "timestamp": "2025-01-23T05:27:14.000Z",
  "suggestions": [
    {
      "id": "suggestion-1",
      "priority": "high",
      "type": "performance",
      "title": "Optimize container image layers",
      "description": "Reduce Docker image size by 30%",
      "estimatedImpact": "Build time -45s, Storage -150MB",
      "complexity": "medium",
      "pathsAffected": ["build-path", "deploy-path"]
    }
  ]
}
```

#### GET /evolution/health
Get detailed system health metrics.

**Response:**
```json
{
  "success": true,
  "data": {
    "overall": 85,
    "components": {
      "buildSystem": 85,
      "codeQuality": 78,
      "testCoverage": 72,
      "documentation": 85,
      "security": 91,
      "performance": 89
    },
    "trends": {
      "improving": ["buildSystem", "security"],
      "stable": ["performance"],
      "declining": ["testCoverage", "documentation"]
    },
    "lastUpdated": "2025-01-23T05:27:14.000Z"
  }
}
```

### Evolution Control

#### POST /evolution/start
Start the evolution engine.

**Request Body:**
```json
{
  "mode": "automatic",
  "cycles": 1
}
```

**Response:**
```json
{
  "message": "Evolution engine started",
  "mode": "automatic", 
  "cycles": 1,
  "estimatedDuration": "15 minutes",
  "startTime": "2025-01-23T05:27:14.000Z"
}
```

#### POST /evolution/stop
Stop the evolution engine.

**Response:**
```json
{
  "message": "Evolution engine stopped",
  "stopTime": "2025-01-23T05:27:14.000Z",
  "cyclesCompleted": 23,
  "lastActivity": "Path optimization completed"
}
```

### Evolution Cycles

#### POST /evolution/cycle/start
Start a new evolution cycle.

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 25,
    "status": "in_progress",
    "startTime": "2025-01-23T05:27:14.000Z",
    "improvements": []
  },
  "message": "Evolution cycle started"
}
```

#### POST /evolution/cycle/complete
Complete the current evolution cycle.

**Request Body:**
```json
{
  "improvements": [
    {
      "type": "performance",
      "description": "Optimized database queries",
      "impact": "high"
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 24,
    "status": "completed",
    "startTime": "2025-01-23T05:00:14.000Z",
    "endTime": "2025-01-23T05:27:14.000Z",
    "improvements": [...]
  },
  "message": "Evolution cycle completed"
}
```

### Suggestions

#### POST /evolution/suggestions/:id/apply
Apply a specific improvement suggestion.

**Parameters:**
- `id` (string): The suggestion ID

**Response:**
```json
{
  "message": "Applying suggestion: Optimize container image layers",
  "suggestion": {
    "id": "suggestion-1",
    "title": "Optimize container image layers",
    "type": "performance",
    "priority": "high"
  },
  "applicationId": "app-1706857634000",
  "estimatedTime": "5-10 minutes", 
  "startTime": "2025-01-23T05:27:14.000Z"
}
```

**Error Response (404):**
```json
{
  "error": "Suggestion not found",
  "id": "invalid-id"
}
```

## Error Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request - Invalid parameters |
| 404 | Not Found - Resource doesn't exist |
| 500 | Internal Server Error |

## Rate Limiting
Currently no rate limiting is enforced in development. Production deployments should implement appropriate rate limiting.

## Examples

### Using curl

```bash
# Get evolution status
curl http://localhost:3001/api/evolution

# Start evolution engine
curl -X POST http://localhost:3001/api/evolution/start \
  -H "Content-Type: application/json" \
  -d '{"mode": "automatic", "cycles": 1}'

# Apply a suggestion
curl -X POST http://localhost:3001/api/evolution/suggestions/suggestion-1/apply
```

### Using JavaScript/Fetch

```javascript
// Get evolution data
const response = await fetch('http://localhost:3001/api/evolution');
const data = await response.json();

// Start new cycle
const cycleResponse = await fetch('http://localhost:3001/api/evolution/cycle/start', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Apply suggestion
const applyResponse = await fetch('http://localhost:3001/api/evolution/suggestions/suggestion-1/apply', {
  method: 'POST'
});
```

### Using Python/Requests

```python
import requests

# Get evolution status
response = requests.get('http://localhost:3001/api/evolution')
data = response.json()

# Start evolution engine
start_response = requests.post('http://localhost:3001/api/evolution/start', 
                              json={'mode': 'automatic', 'cycles': 1})

# Apply suggestion
apply_response = requests.post('http://localhost:3001/api/evolution/suggestions/suggestion-1/apply')
```