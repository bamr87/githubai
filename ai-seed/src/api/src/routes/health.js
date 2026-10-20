import express from 'express'

const router = express.Router()

// Mock health data
const getHealthStatus = () => {
  const services = [
    { 
      name: 'Frontend', 
      status: 'healthy', 
      uptime: '2d 14h', 
      responseTime: '45ms',
      url: 'http://frontend:3000'
    },
    { 
      name: 'API', 
      status: 'healthy', 
      uptime: formatUptime(process.uptime()), 
      responseTime: '120ms',
      url: 'http://api:8000'
    },
    { 
      name: 'AI Engine', 
      status: Math.random() > 0.8 ? 'warning' : 'healthy', 
      uptime: '1d 8h', 
      responseTime: `${Math.floor(Math.random() * 200 + 200)}ms`,
      url: 'http://ai-engine:5000'
    },
    { 
      name: 'Database', 
      status: 'healthy', 
      uptime: '7d 3h', 
      responseTime: '25ms',
      url: 'postgresql://database:5432'
    },
    { 
      name: 'Cache', 
      status: 'healthy', 
      uptime: '7d 3h', 
      responseTime: '8ms',
      url: 'redis://cache:6379'
    },
    { 
      name: 'Monitor', 
      status: 'healthy', 
      uptime: '2d 14h', 
      responseTime: '15ms',
      url: 'http://monitor:80'
    }
  ]

  const overall = services.some(s => s.status === 'error') ? 'error' :
                  services.some(s => s.status === 'warning') ? 'warning' : 'healthy'

  return {
    overall,
    timestamp: new Date().toISOString(),
    services,
    resources: {
      cpu: { 
        usage: Math.random() * 30 + 10, 
        cores: 4 
      },
      memory: { 
        usage: Math.random() * 20 + 60, 
        total: '8GB',
        used: `${Math.floor((Math.random() * 20 + 60) * 8 / 100 * 10) / 10}GB`
      },
      disk: { 
        usage: Math.random() * 20 + 40, 
        total: '100GB',
        used: `${Math.floor((Math.random() * 20 + 40))}GB`
      },
      network: { 
        in: `${(Math.random() * 2 + 0.5).toFixed(1)}MB/s`, 
        out: `${(Math.random() * 1 + 0.3).toFixed(1)}MB/s` 
      }
    },
    paths: {
      healthy: 8,
      warning: 2,
      error: 0,
      total: 10
    }
  }
}

// Format uptime in a human-readable format
function formatUptime(seconds) {
  const days = Math.floor(seconds / 86400)
  const hours = Math.floor((seconds % 86400) / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  
  if (days > 0) {
    return `${days}d ${hours}h ${minutes}m`
  } else if (hours > 0) {
    return `${hours}h ${minutes}m`
  } else {
    return `${minutes}m`
  }
}

// GET /api/health - Get overall health status
router.get('/', (req, res) => {
  try {
    const health = getHealthStatus()
    res.json(health)
  } catch (error) {
    res.status(500).json({
      error: 'Failed to retrieve health status',
      message: error.message
    })
  }
})

// GET /api/health/services - Get service health
router.get('/services', (req, res) => {
  try {
    const health = getHealthStatus()
    res.json({
      timestamp: health.timestamp,
      services: health.services,
      overall: health.overall
    })
  } catch (error) {
    res.status(500).json({
      error: 'Failed to retrieve service health',
      message: error.message
    })
  }
})

// GET /api/health/resources - Get resource usage
router.get('/resources', (req, res) => {
  try {
    const health = getHealthStatus()
    res.json({
      timestamp: health.timestamp,
      resources: health.resources,
      process: {
        uptime: process.uptime(),
        memory: process.memoryUsage(),
        cpu: process.cpuUsage(),
        version: process.version,
        platform: process.platform
      }
    })
  } catch (error) {
    res.status(500).json({
      error: 'Failed to retrieve resource status',
      message: error.message
    })
  }
})

export default router