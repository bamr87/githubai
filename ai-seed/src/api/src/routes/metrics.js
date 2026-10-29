import express from 'express'

const router = express.Router()

// Mock metrics data
const getMetrics = () => ({
  timestamp: new Date().toISOString(),
  paths: {
    total: 12,
    active: 8,
    optimized: 5,
    healthy: 10,
    warning: 2,
    error: 0
  },
  evolution: {
    cycles: 23,
    improvements: 47,
    efficiency: 94.2,
    lastCycle: new Date(Date.now() - 30 * 60 * 1000).toISOString()
  },
  system: {
    uptime: formatUptime(process.uptime()),
    cpu: Math.random() * 30 + 10, // Mock CPU usage 10-40%
    memory: Math.random() * 20 + 60, // Mock memory usage 60-80%
    containers: 6,
    nodeVersion: process.version,
    platform: process.platform
  },
  performance: {
    pathEfficiency: [
      { name: 'Build', efficiency: 98, executions: 145 },
      { name: 'Test', efficiency: 95, executions: 89 },
      { name: 'Deploy', efficiency: 92, executions: 67 },
      { name: 'Monitor', efficiency: 97, executions: 234 },
      { name: 'Evolution', efficiency: 89, executions: 23 }
    ]
  }
})

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

// GET /api/metrics - Get system metrics
router.get('/', (req, res) => {
  try {
    const metrics = getMetrics()
    res.json(metrics)
  } catch (error) {
    res.status(500).json({
      error: 'Failed to retrieve metrics',
      message: error.message
    })
  }
})

// GET /api/metrics/paths - Get path-specific metrics
router.get('/paths', (req, res) => {
  try {
    const metrics = getMetrics()
    res.json({
      timestamp: metrics.timestamp,
      paths: metrics.paths,
      performance: metrics.performance
    })
  } catch (error) {
    res.status(500).json({
      error: 'Failed to retrieve path metrics',
      message: error.message
    })
  }
})

// GET /api/metrics/system - Get system metrics
router.get('/system', (req, res) => {
  try {
    const metrics = getMetrics()
    res.json({
      timestamp: metrics.timestamp,
      system: metrics.system,
      memory: process.memoryUsage(),
      cpu: process.cpuUsage()
    })
  } catch (error) {
    res.status(500).json({
      error: 'Failed to retrieve system metrics',
      message: error.message
    })
  }
})

export default router