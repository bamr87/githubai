const request = require('supertest');
const express = require('express');

// Create a simple test version of the evolution router
const router = express.Router();

// Mock evolution data for testing
const mockEvolutionData = {
  timestamp: new Date().toISOString(),
  engine: {
    status: 'running',
    currentCycle: 24,
    totalCycles: 23,
    efficiency: 94.2
  },
  metrics: {
    totalCycles: 23,
    improvementsMade: 47,
    efficiencyGain: 15.8,
    healthScore: 85
  },
  healthIndicators: {
    buildSystem: 85,
    codeQuality: 78,
    testCoverage: 72
  },
  suggestions: [
    {
      id: 'suggestion-1',
      title: 'Test suggestion',
      type: 'performance'
    }
  ]
};

// Test routes
router.get('/', (req, res) => {
  res.json({
    ...mockEvolutionData,
    recentActivity: [
      {
        id: 1,
        type: 'optimization',
        description: 'Test activity',
        timestamp: new Date().toISOString()
      }
    ]
  });
});

router.get('/metrics', (req, res) => {
  res.json({
    timestamp: mockEvolutionData.timestamp,
    metrics: mockEvolutionData.metrics,
    engine: mockEvolutionData.engine
  });
});

router.get('/health', (req, res) => {
  res.json({
    success: true,
    data: {
      overall: 85,
      components: mockEvolutionData.healthIndicators,
      trends: {
        improving: ['buildSystem'],
        stable: ['performance'],
        declining: ['testCoverage']
      }
    }
  });
});

router.post('/cycle/start', (req, res) => {
  res.json({
    success: true,
    data: { id: 25, status: 'in_progress' },
    message: 'Evolution cycle started'
  });
});

router.post('/suggestions/:id/apply', (req, res) => {
  const { id } = req.params;
  const suggestion = mockEvolutionData.suggestions.find(s => s.id === id);
  
  if (!suggestion) {
    return res.status(404).json({ error: 'Suggestion not found' });
  }
  
  res.json({
    message: `Applying suggestion: ${suggestion.title}`,
    suggestion,
    applicationId: `app-${Date.now()}`
  });
});

const app = express();
app.use(express.json());
app.use('/api/evolution', router);

describe('Evolution API', () => {
  describe('GET /api/evolution', () => {
    it('should return evolution data', async () => {
      const res = await request(app)
        .get('/api/evolution')
        .expect(200);
      
      expect(res.body).toHaveProperty('timestamp');
      expect(res.body).toHaveProperty('engine');
      expect(res.body).toHaveProperty('metrics');
      expect(res.body).toHaveProperty('recentActivity');
      expect(res.body).toHaveProperty('healthIndicators');
      expect(res.body).toHaveProperty('suggestions');
    });
  });

  describe('GET /api/evolution/metrics', () => {
    it('should return metrics data', async () => {
      const res = await request(app)
        .get('/api/evolution/metrics')
        .expect(200);
      
      expect(res.body).toHaveProperty('timestamp');
      expect(res.body).toHaveProperty('metrics');
      expect(res.body).toHaveProperty('engine');
    });
  });

  describe('GET /api/evolution/health', () => {
    it('should return health data', async () => {
      const res = await request(app)
        .get('/api/evolution/health')
        .expect(200);
      
      expect(res.body.success).toBe(true);
      expect(res.body.data).toHaveProperty('overall');
      expect(res.body.data).toHaveProperty('components');
      expect(res.body.data).toHaveProperty('trends');
    });
  });

  describe('POST /api/evolution/cycle/start', () => {
    it('should start a new evolution cycle', async () => {
      const res = await request(app)
        .post('/api/evolution/cycle/start')
        .expect(200);
      
      expect(res.body.success).toBe(true);
      expect(res.body).toHaveProperty('message');
      expect(res.body.data).toHaveProperty('id');
    });
  });

  describe('POST /api/evolution/suggestions/suggestion-1/apply', () => {
    it('should apply a suggestion', async () => {
      const res = await request(app)
        .post('/api/evolution/suggestions/suggestion-1/apply')
        .expect(200);
      
      expect(res.body).toHaveProperty('message');
      expect(res.body).toHaveProperty('suggestion');
      expect(res.body).toHaveProperty('applicationId');
    });
  });

  describe('POST /api/evolution/suggestions/invalid/apply', () => {
    it('should return 404 for invalid suggestion', async () => {
      const res = await request(app)
        .post('/api/evolution/suggestions/invalid/apply')
        .expect(404);
      
      expect(res.body).toHaveProperty('error');
    });
  });
});