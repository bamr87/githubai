import express from 'express'
import cors from 'cors'
import helmet from 'helmet'
import morgan from 'morgan'
import dotenv from 'dotenv'
import metricsRoutes from './routes/metrics.js'
import healthRoutes from './routes/health.js'
import pathRoutes from './routes/paths.js'
import evolutionRoutes from './routes/evolution.js'

// Load environment variables
dotenv.config()

const app = express()
const PORT = process.env.API_PORT || 8000

// Middleware
app.use(helmet())
app.use(cors({
  origin: process.env.FRONTEND_URL || 'http://localhost:3000',
  credentials: true
}))
app.use(morgan('combined'))
app.use(express.json())
app.use(express.urlencoded({ extended: true }))

// Routes
app.use('/api/metrics', metricsRoutes)
app.use('/api/health', healthRoutes)
app.use('/api/paths', pathRoutes)
app.use('/api/evolution', evolutionRoutes)

// Root endpoint
app.get('/', (req, res) => {
  res.json({
    name: 'AI-Seed API',
    version: '1.0.0',
    status: 'running',
    description: 'Backend service for AI-Seed evolution engine',
    endpoints: {
      metrics: '/api/metrics',
      health: '/api/health',
      paths: '/api/paths',
      evolution: '/api/evolution'
    }
  })
})

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    memory: process.memoryUsage()
  })
})

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack)
  res.status(500).json({
    error: 'Something went wrong!',
    message: process.env.NODE_ENV === 'development' ? err.message : 'Internal server error'
  })
})

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({
    error: 'Route not found',
    path: req.originalUrl,
    method: req.method
  })
})

// Start server
app.listen(PORT, '0.0.0.0', () => {
  console.log(`🚀 AI-Seed API server running on port ${PORT}`)
  console.log(`📊 Metrics: http://localhost:${PORT}/api/metrics`)
  console.log(`❤️ Health: http://localhost:${PORT}/health`)
  console.log(`🌱 Environment: ${process.env.NODE_ENV || 'development'}`)
})

export default app