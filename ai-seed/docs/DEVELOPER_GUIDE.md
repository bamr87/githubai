# AI-Seed: Complete Developer Guide

## Table of Contents
- [Architecture Overview](#architecture-overview)
- [Development Setup](#development-setup)
- [API Documentation](#api-documentation)
- [Frontend Development](#frontend-development)
- [Testing Strategy](#testing-strategy)
- [Deployment Guide](#deployment-guide)
- [Evolution System](#evolution-system)
- [Contributing](#contributing)

## Architecture Overview

AI-Seed is built on a **path-based architecture** that emphasizes natural workflow optimization and AI-driven evolution. The system consists of:

### Core Components
- **Frontend**: React-based dashboard with real-time evolution monitoring
- **API**: Node.js/Express backend with comprehensive evolution tracking
- **Evolution Engine**: AI-powered system for continuous improvement
- **Database**: PostgreSQL for persistent data storage
- **Container Infrastructure**: Docker-based development and deployment

### Path-Based Design Principles
1. **Least Resistance**: All workflows follow the most efficient routes
2. **Organic Growth**: System evolves naturally through AI-guided improvements
3. **Context Awareness**: Every operation includes path tracking and metrics
4. **Self-Optimization**: Continuous monitoring and enhancement

## Development Setup

### Prerequisites
- Node.js 18+ 
- Docker & Docker Compose
- Git

### Quick Start
```bash
# Clone the repository
git clone https://github.com/bamr87/ai-seed.git
cd ai-seed

# Start the complete development environment
docker-compose up -d

# Access the application
open http://localhost:3000
```

### Manual Setup
```bash
# Frontend setup
cd src/frontend
npm install
npm run dev

# API setup (in another terminal)
cd src/api
npm install
npm run dev

# Database setup
docker run -d --name ai-seed-db \
  -e POSTGRES_DB=ai_seed_dev \
  -e POSTGRES_USER=seed_user \
  -e POSTGRES_PASSWORD=seed_password \
  -p 5432:5432 postgres:15-alpine
```

## API Documentation

### Base URL
- Development: `http://localhost:3001/api`
- Production: `https://api.ai-seed.com/api`

### Evolution Endpoints

#### GET /evolution
Get comprehensive evolution engine status
```json
{
  "timestamp": "2025-01-23T05:27:14.000Z",
  "engine": {
    "status": "running",
    "currentCycle": 24,
    "totalCycles": 23,
    "efficiency": 94.2
  },
  "metrics": {
    "improvementsMade": 47,
    "pathsOptimized": 12,
    "efficiencyGain": 15.8
  },
  "healthIndicators": {
    "buildSystem": 85,
    "codeQuality": 78,
    "testCoverage": 72
  }
}
```

#### POST /evolution/cycle/start
Start a new evolution cycle
```bash
curl -X POST http://localhost:3001/api/evolution/cycle/start
```

#### GET /evolution/health
Get detailed health metrics
```json
{
  "success": true,
  "data": {
    "overall": 85,
    "components": {...},
    "trends": {
      "improving": ["buildSystem", "security"],
      "stable": ["performance"],
      "declining": ["testCoverage"]
    }
  }
}
```

## Frontend Development

### Project Structure
```
src/frontend/
├── src/
│   ├── components/        # Reusable UI components
│   │   ├── EvolutionEngine.jsx
│   │   ├── Dashboard.jsx
│   │   └── Navigation.jsx
│   ├── pages/            # Route components
│   ├── hooks/            # Custom React hooks
│   ├── utils/            # Helper functions
│   └── test/             # Test utilities
├── public/               # Static assets
└── package.json
```

### Key Components

#### EvolutionEngine Component
Displays real-time evolution metrics and controls:
- Engine status monitoring
- Cycle management
- Suggestion implementation
- Performance tracking

#### Dashboard Component
Main application interface featuring:
- Evolution overview cards
- Real-time activity feed
- Health indicators
- Growth visualizations

### Development Commands
```bash
# Start development server
npm run dev

# Run tests
npm run test

# Run tests with coverage
npm run test:coverage

# Lint code
npm run lint

# Build for production
npm run build
```

## Testing Strategy

### Frontend Testing
- **Unit Tests**: Component behavior and logic
- **Integration Tests**: Component interactions
- **E2E Tests**: Complete user workflows

Example test:
```javascript
import { render, screen } from '@testing-library/react'
import EvolutionEngine from '../EvolutionEngine'

test('renders evolution status', () => {
  render(<EvolutionEngine />)
  expect(screen.getByText('AI Evolution Engine')).toBeInTheDocument()
})
```

### Backend Testing
- **Unit Tests**: Individual function testing
- **Integration Tests**: API endpoint testing
- **Performance Tests**: Load and stress testing

Example API test:
```javascript
import request from 'supertest'
import app from '../app'

test('GET /api/evolution returns data', async () => {
  const res = await request(app)
    .get('/api/evolution')
    .expect(200)
  
  expect(res.body).toHaveProperty('engine')
})
```

### Test Coverage Goals
- Frontend: >90% component coverage
- Backend: >85% line coverage
- Integration: All critical paths

## Deployment Guide

### Docker Deployment
```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy to production
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose ps
```

### Environment Variables
```bash
# Frontend
VITE_API_URL=http://localhost:3001

# Backend
NODE_ENV=production
DATABASE_URL=postgresql://user:pass@localhost:5432/ai_seed
PORT=3001
```

### Health Checks
- Frontend: `http://localhost:3000/health`
- API: `http://localhost:3001/api/health`
- Database: Connection testing via API

## Evolution System

### How It Works
1. **Continuous Monitoring**: System tracks all operations and performance
2. **Pattern Recognition**: AI identifies optimization opportunities
3. **Automated Improvements**: Safe changes are applied automatically
4. **Human Oversight**: Critical changes require approval

### Evolution Cycles
- **Duration**: 15-30 minutes per cycle
- **Frequency**: Every 4-6 hours
- **Types**: Performance, Security, Quality, Features

### Metrics Tracked
- Build times and efficiency
- Test coverage and success rates
- Code quality scores
- User experience metrics
- System reliability indicators

### Path Optimization
The system identifies and optimizes common execution paths:
- Build pipelines
- Test suites  
- Deployment processes
- User workflows

## Contributing

### Development Workflow
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes following the coding standards
4. Add tests for new functionality
5. Run the test suite: `npm test`
6. Run the linting: `npm run lint`
7. Commit changes: `git commit -m 'Add amazing feature'`
8. Push to branch: `git push origin feature/amazing-feature`
9. Open a Pull Request

### Coding Standards
- **JavaScript**: ESLint with Airbnb config
- **React**: Functional components with hooks
- **Testing**: Jest/Vitest with high coverage
- **Documentation**: JSDoc for complex functions

### Pull Request Guidelines
- Include tests for new features
- Update documentation as needed
- Follow conventional commit messages
- Ensure CI passes before requesting review

### Evolution-Friendly Development
- Consider path impact of changes
- Include performance metrics
- Test for evolution compatibility
- Document optimization opportunities

---

*This documentation is part of the AI-Seed evolution system and is continuously updated based on system growth and community feedback.*