---
file: javascript.instructions.md
description: JavaScript/Node.js specific AI instructions for path-based development and container-first architecture
author: AI-Seed Team <team@ai-seed.org>
created: 2025-07-19
lastModified: 2025-07-19
version: 1.0.0
relatedIssues: []
relatedEvolutions: []
dependencies:
  - space.instructions.md: Foundation principles and path-based development
  - project.instructions.md: Project-specific context and requirements
containerRequirements:
  baseImage: 
    - node:18-alpine
    - node:20-slim
  exposedPorts:
    - 3000/tcp
    - 8080/tcp
  volumes:
    - /app/src:rw
    - /app/node_modules
    - /app/logs:rw
  environment:
    NODE_ENV: development
    PATH: /app/node_modules/.bin:$PATH
  resources:
    cpu: 0.5-2.0
    memory: 512MiB-2GiB
  healthCheck: curl -f http://localhost:3000/health || exit 1
paths:
  nodejs-development-path: Package setup → coding → testing → containerization
  api-service-path: Request routing → middleware → business logic → response
  build-optimization-path: Source → bundling → minification → distribution
changelog:
  - date: 2025-07-19
    change: Initial creation
    author: AI-Seed Team
usage: Reference for all JavaScript/Node.js development within container environments
notes: Emphasizes modern ES modules, async/await patterns, and container-first deployment
---

# JavaScript/Node.js Instructions

Apply the [general coding guidelines](../copilot-instructions.md) to all code.

These instructions provide comprehensive guidance for JavaScript and Node.js development within the AI-seed ecosystem, emphasizing path-based architecture, container-first development, and modern JavaScript patterns.

## Node.js Environment Setup

### Container-First Node.js Development

#### Base Container Configuration
```dockerfile
# Multi-stage Node.js build
FROM node:20-alpine AS base
WORKDIR /app

# Install system dependencies
RUN apk add --no-cache \
    curl \
    git \
    && rm -rf /var/cache/apk/*

# Development stage
FROM base AS development
ENV NODE_ENV=development
ENV PATH=/app/node_modules/.bin:$PATH

# Copy package files first for better caching
COPY package*.json ./
RUN npm ci --include=dev

# Install development tools
RUN npm install -g nodemon eslint prettier

# Production stage
FROM base AS production
ENV NODE_ENV=production
ENV PATH=/app/node_modules/.bin:$PATH

COPY package*.json ./
RUN npm ci --only=production && npm cache clean --force

COPY src/ ./src/
USER 1000:1000
EXPOSE 3000
CMD ["node", "src/index.js"]

# Build stage for frontend applications
FROM base AS build
ENV NODE_ENV=production
COPY package*.json ./
RUN npm ci --include=dev

COPY . .
RUN npm run build

# Static serve stage
FROM nginx:alpine AS static
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Package Management and Dependencies

#### Path-Based Package Structure
```json
{
  "name": "ai-seed-app",
  "version": "1.0.0",
  "description": "AI-powered development seed application",
  "type": "module",
  "main": "src/index.js",
  "scripts": {
    "dev": "nodemon src/index.js",
    "start": "node src/index.js",
    "test": "jest --coverage",
    "test:watch": "jest --watch",
    "test:integration": "jest --config jest.integration.config.js",
    "lint": "eslint src/ --ext .js,.mjs",
    "lint:fix": "eslint src/ --ext .js,.mjs --fix",
    "format": "prettier --write src/",
    "build": "webpack --mode production",
    "build:dev": "webpack --mode development",
    "docker:build": "docker build --target production -t ai-seed-app .",
    "docker:run": "docker run -p 3000:3000 ai-seed-app",
    "path:analyze": "node scripts/analyze-paths.js"
  },
  "dependencies": {
    "express": "^4.18.2",
    "cors": "^2.8.5",
    "helmet": "^7.1.0",
    "morgan": "^1.10.0",
    "pino": "^8.16.1",
    "pino-pretty": "^10.2.3",
    "joi": "^17.11.0",
    "bcryptjs": "^2.4.3",
    "jsonwebtoken": "^9.0.2",
    "redis": "^4.6.10",
    "pg": "^8.11.3"
  },
  "devDependencies": {
    "jest": "^29.7.0",
    "supertest": "^6.3.3",
    "eslint": "^8.54.0",
    "prettier": "^3.1.0",
    "nodemon": "^3.0.1",
    "webpack": "^5.89.0",
    "webpack-cli": "^5.1.4"
  },
  "engines": {
    "node": ">=18.0.0",
    "npm": ">=8.0.0"
  }
}
```

## Path-Based Code Organization

### Project Structure
```
src/
├── index.js                   # Application entry point
├── app.js                     # Express app configuration
├── config/                    # Configuration management path
│   ├── index.js              # Configuration aggregator
│   ├── database.js           # Database configuration
│   ├── redis.js              # Redis configuration
│   └── logger.js             # Logging configuration
├── routes/                    # API routing path
│   ├── index.js              # Route aggregator
│   ├── auth.js               # Authentication routes
│   ├── users.js              # User management routes
│   └── health.js             # Health check routes
├── middleware/                # Request processing path
│   ├── auth.js               # Authentication middleware
│   ├── validation.js         # Request validation
│   ├── error-handler.js      # Error handling middleware
│   ├── rate-limiter.js       # Rate limiting
│   └── path-tracker.js       # Path execution tracking
├── services/                  # Business logic path
│   ├── auth-service.js       # Authentication logic
│   ├── user-service.js       # User management logic
│   └── path-optimizer.js     # Path optimization service
├── models/                    # Data model path
│   ├── user.js               # User data model
│   └── session.js            # Session data model
├── utils/                     # Utility path
│   ├── logger.js             # Centralized logging
│   ├── validation.js         # Input validation helpers
│   ├── crypto.js             # Cryptographic utilities
│   └── path-tracker.js       # Path execution tracking
└── workers/                   # Background processing path
    ├── queue-worker.js       # Queue processing
    └── scheduler.js          # Scheduled tasks
```

### ES Module Path-Based Architecture

#### Path Execution Tracking
```javascript
// Path: execution-tracking-system
// File: src/utils/path-tracker.js

/**
 * @file src/utils/path-tracker.js
 * @description Path execution tracking and optimization utilities
 */

class PathTracker {
    constructor() {
        this.currentPath = null;
        this.pathStack = [];
        this.pathMetrics = new Map();
        this.pathHistory = [];
    }

    /**
     * Enter a new execution path
     * @param {string} pathName - Name of the path being entered
     * @param {Object} context - Additional context for the path
     */
    enterPath(pathName, context = {}) {
        const pathEntry = {
            name: pathName,
            startTime: process.hrtime.bigint(),
            context,
            parent: this.currentPath
        };

        this.pathStack.push(pathEntry);
        this.currentPath = pathName;
        this.pathHistory.push({ action: 'enter', path: pathName, timestamp: Date.now() });

        this.logger?.debug(`Entering path: ${pathName}`, { context, stack: this.getPathStack() });
    }

    /**
     * Exit the current execution path
     * @param {string} pathName - Name of the path being exited
     * @param {Object} result - Result of path execution
     */
    exitPath(pathName, result = {}) {
        if (this.pathStack.length === 0) {
            this.logger?.warn(`Attempting to exit path '${pathName}' but stack is empty`);
            return;
        }

        const currentEntry = this.pathStack[this.pathStack.length - 1];
        if (currentEntry.name !== pathName) {
            this.logger?.warn(`Path mismatch: expected '${currentEntry.name}', got '${pathName}'`);
        }

        // Calculate execution time
        const endTime = process.hrtime.bigint();
        const executionTime = Number(endTime - currentEntry.startTime) / 1e6; // Convert to milliseconds

        // Update metrics
        this.updatePathMetrics(pathName, executionTime, result);

        // Remove from stack
        this.pathStack.pop();
        this.currentPath = this.pathStack.length > 0 ? this.pathStack[this.pathStack.length - 1].name : null;
        this.pathHistory.push({ action: 'exit', path: pathName, timestamp: Date.now(), duration: executionTime });

        this.logger?.debug(`Exiting path: ${pathName} (${executionTime.toFixed(2)}ms)`, { result });
    }

    /**
     * Execute a function within a path context
     * @param {string} pathName - Name of the execution path
     * @param {Function} fn - Function to execute
     * @param {Object} context - Additional context
     */
    async executeInPath(pathName, fn, context = {}) {
        this.enterPath(pathName, context);
        
        try {
            const result = await fn();
            this.exitPath(pathName, { success: true });
            return result;
        } catch (error) {
            this.exitPath(pathName, { success: false, error: error.message });
            throw error;
        }
    }

    /**
     * Update path performance metrics
     * @param {string} pathName - Name of the path
     * @param {number} executionTime - Execution time in milliseconds
     * @param {Object} result - Path execution result
     */
    updatePathMetrics(pathName, executionTime, result) {
        if (!this.pathMetrics.has(pathName)) {
            this.pathMetrics.set(pathName, {
                executions: 0,
                totalTime: 0,
                averageTime: 0,
                minTime: Infinity,
                maxTime: 0,
                errors: 0,
                successes: 0
            });
        }

        const metrics = this.pathMetrics.get(pathName);
        metrics.executions++;
        metrics.totalTime += executionTime;
        metrics.averageTime = metrics.totalTime / metrics.executions;
        metrics.minTime = Math.min(metrics.minTime, executionTime);
        metrics.maxTime = Math.max(metrics.maxTime, executionTime);

        if (result.success === false) {
            metrics.errors++;
        } else {
            metrics.successes++;
        }
    }

    /**
     * Get current path stack as array of path names
     * @returns {string[]} Array of path names in execution order
     */
    getPathStack() {
        return this.pathStack.map(entry => entry.name);
    }

    /**
     * Get comprehensive path metrics
     * @returns {Object} Path execution metrics
     */
    getMetrics() {
        const metrics = {};
        for (const [pathName, pathMetrics] of this.pathMetrics) {
            metrics[pathName] = { ...pathMetrics };
        }
        return metrics;
    }

    /**
     * Generate path performance report
     * @returns {Object} Formatted performance report
     */
    generatePerformanceReport() {
        const report = {
            summary: {
                totalPaths: this.pathMetrics.size,
                totalExecutions: 0,
                totalTime: 0,
                averageTime: 0
            },
            paths: {}
        };

        for (const [pathName, metrics] of this.pathMetrics) {
            report.summary.totalExecutions += metrics.executions;
            report.summary.totalTime += metrics.totalTime;

            report.paths[pathName] = {
                ...metrics,
                successRate: metrics.executions > 0 ? (metrics.successes / metrics.executions * 100).toFixed(2) : 0,
                errorRate: metrics.executions > 0 ? (metrics.errors / metrics.executions * 100).toFixed(2) : 0
            };
        }

        report.summary.averageTime = report.summary.totalExecutions > 0 
            ? report.summary.totalTime / report.summary.totalExecutions 
            : 0;

        return report;
    }
}

// Global path tracker instance
export const pathTracker = new PathTracker();

// Middleware factory for Express.js
export const createPathTrackerMiddleware = (pathName) => {
    return (req, res, next) => {
        const context = {
            method: req.method,
            url: req.url,
            userAgent: req.get('User-Agent'),
            ip: req.ip
        };

        pathTracker.enterPath(pathName, context);

        // Track response
        const originalEnd = res.end;
        res.end = function(...args) {
            pathTracker.exitPath(pathName, {
                statusCode: res.statusCode,
                success: res.statusCode < 400
            });
            originalEnd.apply(this, args);
        };

        next();
    };
};

// Decorator for class methods
export const pathTracked = (pathName) => {
    return (target, propertyKey, descriptor) => {
        const originalMethod = descriptor.value;
        
        descriptor.value = async function(...args) {
            return await pathTracker.executeInPath(
                pathName || `${target.constructor.name}.${propertyKey}`,
                () => originalMethod.apply(this, args),
                { className: target.constructor.name, methodName: propertyKey }
            );
        };
        
        return descriptor;
    };
};
```

### Express.js Application Structure

#### Main Application Setup
```javascript
// Path: express-application-initialization
// File: src/app.js

import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import morgan from 'morgan';
import { pathTracker, createPathTrackerMiddleware } from './utils/path-tracker.js';
import { logger } from './config/logger.js';
import { errorHandler } from './middleware/error-handler.js';
import { authMiddleware } from './middleware/auth.js';
import { validationMiddleware } from './middleware/validation.js';
import { rateLimiterMiddleware } from './middleware/rate-limiter.js';

// Import routes
import authRoutes from './routes/auth.js';
import userRoutes from './routes/users.js';
import healthRoutes from './routes/health.js';

/**
 * Create and configure Express application
 * @returns {express.Application} Configured Express app
 */
export const createApp = () => {
    const app = express();

    // Path: security-middleware-setup
    app.use(helmet({
        contentSecurityPolicy: {
            directives: {
                defaultSrc: ["'self'"],
                styleSrc: ["'self'", "'unsafe-inline'"],
                scriptSrc: ["'self'"],
                imgSrc: ["'self'", "data:", "https:"]
            }
        }
    }));

    // Path: cors-configuration
    app.use(cors({
        origin: process.env.ALLOWED_ORIGINS?.split(',') || ['http://localhost:3000'],
        credentials: true,
        methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
        allowedHeaders: ['Content-Type', 'Authorization']
    }));

    // Path: request-parsing
    app.use(express.json({ limit: '10mb' }));
    app.use(express.urlencoded({ extended: true, limit: '10mb' }));

    // Path: logging-middleware
    app.use(morgan('combined', {
        stream: {
            write: (message) => logger.info(message.trim(), { component: 'http' })
        }
    }));

    // Path: request-tracking
    app.use(createPathTrackerMiddleware('http_request'));

    // Path: rate-limiting
    app.use(rateLimiterMiddleware);

    // Path: health-check-route
    app.use('/health', healthRoutes);

    // Path: authentication-routes
    app.use('/api/auth', authRoutes);

    // Path: protected-routes
    app.use('/api/users', authMiddleware, userRoutes);

    // Path: api-documentation
    app.get('/api', (req, res) => {
        res.json({
            name: 'AI-Seed API',
            version: process.env.npm_package_version || '1.0.0',
            paths: pathTracker.getPathStack(),
            metrics: pathTracker.getMetrics()
        });
    });

    // Path: error-handling
    app.use(errorHandler);

    // Path: 404-handler
    app.use('*', (req, res) => {
        res.status(404).json({
            error: 'Route not found',
            path: req.originalUrl,
            method: req.method,
            timestamp: new Date().toISOString()
        });
    });

    return app;
};

/**
 * Application lifecycle management
 */
export class AppLifecycle {
    constructor(app) {
        this.app = app;
        this.server = null;
        this.isShuttingDown = false;
    }

    /**
     * Start the application server
     * @param {number} port - Port to listen on
     */
    async start(port = 3000) {
        return pathTracker.executeInPath('app_startup', async () => {
            this.server = this.app.listen(port, '0.0.0.0', () => {
                logger.info(`Server started on port ${port}`, { 
                    component: 'app',
                    port,
                    environment: process.env.NODE_ENV
                });
            });

            // Setup graceful shutdown
            this.setupGracefulShutdown();
            
            return this.server;
        });
    }

    /**
     * Setup graceful shutdown handling
     */
    setupGracefulShutdown() {
        const shutdown = async (signal) => {
            if (this.isShuttingDown) return;
            this.isShuttingDown = true;

            logger.info(`Received ${signal}, starting graceful shutdown`, { component: 'app' });

            await pathTracker.executeInPath('app_shutdown', async () => {
                // Stop accepting new connections
                this.server.close(() => {
                    logger.info('HTTP server closed', { component: 'app' });
                });

                // Close database connections, Redis, etc.
                await this.closeResources();

                // Generate final performance report
                const report = pathTracker.generatePerformanceReport();
                logger.info('Path execution report', { component: 'app', report });

                process.exit(0);
            });
        };

        process.on('SIGTERM', () => shutdown('SIGTERM'));
        process.on('SIGINT', () => shutdown('SIGINT'));
    }

    /**
     * Close external resources
     */
    async closeResources() {
        // Implement resource cleanup (database, Redis, etc.)
        logger.info('Resources closed successfully', { component: 'app' });
    }
}
```

#### API Route Implementation
```javascript
// Path: user-management-routes
// File: src/routes/users.js

import { Router } from 'express';
import { pathTracked } from '../utils/path-tracker.js';
import { UserService } from '../services/user-service.js';
import { validationMiddleware } from '../middleware/validation.js';
import { userValidationSchemas } from '../utils/validation.js';
import { logger } from '../config/logger.js';

const router = Router();
const userService = new UserService();

/**
 * User management service with path tracking
 */
class UserController {
    @pathTracked('user_list')
    async getUsers(req, res, next) {
        try {
            const { page = 1, limit = 10, search } = req.query;
            
            const options = {
                page: parseInt(page),
                limit: Math.min(parseInt(limit), 100), // Max 100 items per page
                search
            };

            const users = await userService.getUsers(options);
            
            res.json({
                success: true,
                data: users,
                pagination: {
                    page: options.page,
                    limit: options.limit,
                    total: users.total
                }
            });
        } catch (error) {
            next(error);
        }
    }

    @pathTracked('user_get_by_id')
    async getUserById(req, res, next) {
        try {
            const { id } = req.params;
            const user = await userService.getUserById(id);
            
            if (!user) {
                return res.status(404).json({
                    success: false,
                    error: 'User not found'
                });
            }

            res.json({
                success: true,
                data: user
            });
        } catch (error) {
            next(error);
        }
    }

    @pathTracked('user_create')
    async createUser(req, res, next) {
        try {
            const userData = req.body;
            const newUser = await userService.createUser(userData);
            
            res.status(201).json({
                success: true,
                data: newUser,
                message: 'User created successfully'
            });
        } catch (error) {
            next(error);
        }
    }

    @pathTracked('user_update')
    async updateUser(req, res, next) {
        try {
            const { id } = req.params;
            const updateData = req.body;
            
            const updatedUser = await userService.updateUser(id, updateData);
            
            if (!updatedUser) {
                return res.status(404).json({
                    success: false,
                    error: 'User not found'
                });
            }

            res.json({
                success: true,
                data: updatedUser,
                message: 'User updated successfully'
            });
        } catch (error) {
            next(error);
        }
    }

    @pathTracked('user_delete')
    async deleteUser(req, res, next) {
        try {
            const { id } = req.params;
            const deleted = await userService.deleteUser(id);
            
            if (!deleted) {
                return res.status(404).json({
                    success: false,
                    error: 'User not found'
                });
            }

            res.status(204).send();
        } catch (error) {
            next(error);
        }
    }
}

const userController = new UserController();

// Route definitions with validation
router.get('/', userController.getUsers.bind(userController));

router.get('/:id', 
    validationMiddleware(userValidationSchemas.getUserById),
    userController.getUserById.bind(userController)
);

router.post('/',
    validationMiddleware(userValidationSchemas.createUser),
    userController.createUser.bind(userController)
);

router.put('/:id',
    validationMiddleware(userValidationSchemas.updateUser),
    userController.updateUser.bind(userController)
);

router.delete('/:id',
    validationMiddleware(userValidationSchemas.getUserById),
    userController.deleteUser.bind(userController)
);

export default router;
```

### Async/Await Path Management

#### Service Layer with Path Optimization
```javascript
// Path: business-logic-service-layer
// File: src/services/user-service.js

import { pathTracker } from '../utils/path-tracker.js';
import { logger } from '../config/logger.js';
import { UserModel } from '../models/user.js';
import { CacheService } from './cache-service.js';
import { ValidationError, NotFoundError } from '../utils/errors.js';

/**
 * User service with path-aware operations
 */
export class UserService {
    constructor() {
        this.userModel = new UserModel();
        this.cacheService = new CacheService();
        this.cacheTTL = 300; // 5 minutes
    }

    /**
     * Get users with caching and pagination
     * @param {Object} options - Query options
     * @returns {Promise<Object>} Users with pagination info
     */
    async getUsers(options = {}) {
        return pathTracker.executeInPath('user_service_get_users', async () => {
            const { page = 1, limit = 10, search } = options;
            const cacheKey = `users:${page}:${limit}:${search || 'all'}`;

            // Path: cache-lookup
            const cachedUsers = await pathTracker.executeInPath('cache_lookup', 
                () => this.cacheService.get(cacheKey)
            );

            if (cachedUsers) {
                logger.debug('Users retrieved from cache', { cacheKey });
                return cachedUsers;
            }

            // Path: database-query
            const users = await pathTracker.executeInPath('database_query', async () => {
                const offset = (page - 1) * limit;
                
                let query = this.userModel.query();
                
                if (search) {
                    query = query.where(builder => {
                        builder.where('name', 'ilike', `%${search}%`)
                               .orWhere('email', 'ilike', `%${search}%`);
                    });
                }

                const [users, total] = await Promise.all([
                    query.offset(offset).limit(limit).select('id', 'name', 'email', 'created_at'),
                    query.clone().count('* as count').first()
                ]);

                return {
                    users,
                    total: parseInt(total.count)
                };
            });

            // Path: cache-store
            await pathTracker.executeInPath('cache_store', 
                () => this.cacheService.set(cacheKey, users, this.cacheTTL)
            );

            return users;
        });
    }

    /**
     * Get user by ID with caching
     * @param {string} id - User ID
     * @returns {Promise<Object|null>} User object or null
     */
    async getUserById(id) {
        return pathTracker.executeInPath('user_service_get_by_id', async () => {
            if (!id) {
                throw new ValidationError('User ID is required');
            }

            const cacheKey = `user:${id}`;

            // Path: cache-lookup
            const cachedUser = await pathTracker.executeInPath('cache_lookup',
                () => this.cacheService.get(cacheKey)
            );

            if (cachedUser) {
                logger.debug('User retrieved from cache', { userId: id });
                return cachedUser;
            }

            // Path: database-query
            const user = await pathTracker.executeInPath('database_query',
                () => this.userModel.query().findById(id)
            );

            if (user) {
                // Path: cache-store
                await pathTracker.executeInPath('cache_store',
                    () => this.cacheService.set(cacheKey, user, this.cacheTTL)
                );
            }

            return user;
        });
    }

    /**
     * Create new user with validation
     * @param {Object} userData - User data
     * @returns {Promise<Object>} Created user
     */
    async createUser(userData) {
        return pathTracker.executeInPath('user_service_create', async () => {
            // Path: input-validation
            await pathTracker.executeInPath('input_validation', async () => {
                if (!userData.email || !userData.name) {
                    throw new ValidationError('Email and name are required');
                }

                // Check if email already exists
                const existingUser = await this.userModel.query()
                    .where('email', userData.email)
                    .first();

                if (existingUser) {
                    throw new ValidationError('Email already exists');
                }
            });

            // Path: password-hashing (if password provided)
            if (userData.password) {
                await pathTracker.executeInPath('password_hashing', async () => {
                    const bcrypt = await import('bcryptjs');
                    userData.password = await bcrypt.hash(userData.password, 12);
                });
            }

            // Path: database-insert
            const newUser = await pathTracker.executeInPath('database_insert',
                () => this.userModel.query().insert(userData).returning('*')
            );

            // Path: cache-invalidation
            await pathTracker.executeInPath('cache_invalidation', async () => {
                await this.cacheService.invalidatePattern('users:*');
            });

            logger.info('User created successfully', { userId: newUser.id });
            return newUser;
        });
    }

    /**
     * Update user with optimistic concurrency
     * @param {string} id - User ID
     * @param {Object} updateData - Data to update
     * @returns {Promise<Object|null>} Updated user or null
     */
    async updateUser(id, updateData) {
        return pathTracker.executeInPath('user_service_update', async () => {
            // Path: user-existence-check
            const existingUser = await pathTracker.executeInPath('user_existence_check',
                () => this.getUserById(id)
            );

            if (!existingUser) {
                throw new NotFoundError('User not found');
            }

            // Path: input-validation
            await pathTracker.executeInPath('input_validation', async () => {
                // Remove sensitive fields that shouldn't be updated directly
                delete updateData.id;
                delete updateData.created_at;
                delete updateData.password; // Use separate method for password updates

                if (updateData.email && updateData.email !== existingUser.email) {
                    const emailExists = await this.userModel.query()
                        .where('email', updateData.email)
                        .where('id', '!=', id)
                        .first();

                    if (emailExists) {
                        throw new ValidationError('Email already exists');
                    }
                }
            });

            // Path: database-update
            const updatedUser = await pathTracker.executeInPath('database_update', async () => {
                return this.userModel.query()
                    .patchAndFetchById(id, {
                        ...updateData,
                        updated_at: new Date()
                    });
            });

            // Path: cache-invalidation
            await pathTracker.executeInPath('cache_invalidation', async () => {
                await Promise.all([
                    this.cacheService.delete(`user:${id}`),
                    this.cacheService.invalidatePattern('users:*')
                ]);
            });

            logger.info('User updated successfully', { userId: id });
            return updatedUser;
        });
    }

    /**
     * Delete user with cascade handling
     * @param {string} id - User ID
     * @returns {Promise<boolean>} True if deleted, false if not found
     */
    async deleteUser(id) {
        return pathTracker.executeInPath('user_service_delete', async () => {
            // Path: user-existence-check
            const existingUser = await pathTracker.executeInPath('user_existence_check',
                () => this.getUserById(id)
            );

            if (!existingUser) {
                return false;
            }

            // Path: cascade-deletion (if needed)
            await pathTracker.executeInPath('cascade_deletion', async () => {
                // Delete related data (sessions, tokens, etc.)
                // This would typically involve other services
            });

            // Path: database-delete
            const deletedCount = await pathTracker.executeInPath('database_delete',
                () => this.userModel.query().deleteById(id)
            );

            // Path: cache-invalidation
            await pathTracker.executeInPath('cache_invalidation', async () => {
                await Promise.all([
                    this.cacheService.delete(`user:${id}`),
                    this.cacheService.invalidatePattern('users:*')
                ]);
            });

            logger.info('User deleted successfully', { userId: id });
            return deletedCount > 0;
        });
    }
}
```

### Testing Patterns

#### Path-Based Testing Strategy
```javascript
// Path: comprehensive-testing-suite
// File: src/__tests__/services/user-service.test.js

import { jest } from '@jest/globals';
import { UserService } from '../../services/user-service.js';
import { pathTracker } from '../../utils/path-tracker.js';
import { ValidationError, NotFoundError } from '../../utils/errors.js';

// Mock dependencies
jest.mock('../../models/user.js');
jest.mock('../../services/cache-service.js');
jest.mock('../../config/logger.js');

describe('UserService Path Testing', () => {
    let userService;
    let mockUserModel;
    let mockCacheService;

    beforeEach(() => {
        // Reset path tracker for each test
        pathTracker.currentPath = null;
        pathTracker.pathStack = [];
        pathTracker.pathHistory = [];

        userService = new UserService();
        mockUserModel = userService.userModel;
        mockCacheService = userService.cacheService;
    });

    describe('Path: user_service_get_users', () => {
        test('should follow cache-hit path successfully', async () => {
            // Arrange
            const mockUsers = { users: [{ id: 1, name: 'Test User' }], total: 1 };
            mockCacheService.get.mockResolvedValue(mockUsers);

            // Act
            const result = await userService.getUsers({ page: 1, limit: 10 });

            // Assert
            expect(result).toEqual(mockUsers);
            expect(mockCacheService.get).toHaveBeenCalledWith('users:1:10:all');
            expect(mockUserModel.query).not.toHaveBeenCalled();

            // Verify path execution
            const pathHistory = pathTracker.pathHistory;
            expect(pathHistory).toContainEqual(
                expect.objectContaining({ action: 'enter', path: 'user_service_get_users' })
            );
            expect(pathHistory).toContainEqual(
                expect.objectContaining({ action: 'enter', path: 'cache_lookup' })
            );
        });

        test('should follow cache-miss → database-query → cache-store path', async () => {
            // Arrange
            const mockUsers = [{ id: 1, name: 'Test User' }];
            const mockTotal = { count: '1' };
            
            mockCacheService.get.mockResolvedValue(null);
            mockUserModel.query.mockReturnValue({
                where: jest.fn().mockReturnThis(),
                offset: jest.fn().mockReturnThis(),
                limit: jest.fn().mockReturnThis(),
                select: jest.fn().mockResolvedValue(mockUsers),
                clone: jest.fn().mockReturnValue({
                    count: jest.fn().mockReturnThis(),
                    first: jest.fn().mockResolvedValue(mockTotal)
                })
            });

            // Act
            const result = await userService.getUsers({ page: 1, limit: 10 });

            // Assert
            expect(result).toEqual({ users: mockUsers, total: 1 });
            expect(mockCacheService.set).toHaveBeenCalledWith(
                'users:1:10:all',
                { users: mockUsers, total: 1 },
                300
            );

            // Verify complete path execution
            const pathHistory = pathTracker.pathHistory;
            const pathNames = pathHistory.map(h => h.path);
            
            expect(pathNames).toContain('user_service_get_users');
            expect(pathNames).toContain('cache_lookup');
            expect(pathNames).toContain('database_query');
            expect(pathNames).toContain('cache_store');
        });

        test('should handle search parameter in path execution', async () => {
            // Arrange
            const searchTerm = 'john';
            mockCacheService.get.mockResolvedValue(null);
            
            const mockQuery = {
                where: jest.fn().mockReturnThis(),
                orWhere: jest.fn().mockReturnThis(),
                offset: jest.fn().mockReturnThis(),
                limit: jest.fn().mockReturnThis(),
                select: jest.fn().mockResolvedValue([]),
                clone: jest.fn().mockReturnValue({
                    count: jest.fn().mockReturnThis(),
                    first: jest.fn().mockResolvedValue({ count: '0' })
                })
            };

            mockUserModel.query.mockReturnValue(mockQuery);

            // Act
            await userService.getUsers({ page: 1, limit: 10, search: searchTerm });

            // Assert
            expect(mockCacheService.get).toHaveBeenCalledWith(`users:1:10:${searchTerm}`);
            expect(mockQuery.where).toHaveBeenCalledWith(expect.any(Function));
        });
    });

    describe('Path: user_service_create', () => {
        test('should follow complete creation path successfully', async () => {
            // Arrange
            const userData = {
                name: 'John Doe',
                email: 'john@example.com',
                password: 'password123'
            };

            const mockCreatedUser = { id: 1, ...userData };

            // Mock existing user check (should return null)
            mockUserModel.query.mockReturnValueOnce({
                where: jest.fn().mockReturnThis(),
                first: jest.fn().mockResolvedValue(null)
            });

            // Mock user creation
            mockUserModel.query.mockReturnValueOnce({
                insert: jest.fn().mockReturnThis(),
                returning: jest.fn().mockResolvedValue(mockCreatedUser)
            });

            // Act
            const result = await userService.createUser(userData);

            // Assert
            expect(result).toEqual(mockCreatedUser);
            expect(mockCacheService.invalidatePattern).toHaveBeenCalledWith('users:*');

            // Verify path execution includes password hashing
            const pathHistory = pathTracker.pathHistory;
            const pathNames = pathHistory.map(h => h.path);

            expect(pathNames).toContain('user_service_create');
            expect(pathNames).toContain('input_validation');
            expect(pathNames).toContain('password_hashing');
            expect(pathNames).toContain('database_insert');
            expect(pathNames).toContain('cache_invalidation');
        });

        test('should follow validation-error path for duplicate email', async () => {
            // Arrange
            const userData = {
                name: 'John Doe',
                email: 'existing@example.com'
            };

            // Mock existing user found
            mockUserModel.query.mockReturnValue({
                where: jest.fn().mockReturnThis(),
                first: jest.fn().mockResolvedValue({ id: 1, email: 'existing@example.com' })
            });

            // Act & Assert
            await expect(userService.createUser(userData))
                .rejects
                .toThrow(ValidationError);

            // Verify path stopped at validation
            const pathHistory = pathTracker.pathHistory;
            const pathNames = pathHistory.map(h => h.path);

            expect(pathNames).toContain('user_service_create');
            expect(pathNames).toContain('input_validation');
            expect(pathNames).not.toContain('database_insert');
        });
    });

    describe('Path Performance Metrics', () => {
        test('should track path execution metrics correctly', async () => {
            // Arrange
            mockCacheService.get.mockResolvedValue({ users: [], total: 0 });

            // Act - Execute multiple operations
            await userService.getUsers({ page: 1, limit: 10 });
            await userService.getUsers({ page: 2, limit: 10 });

            // Assert
            const metrics = pathTracker.getMetrics();
            
            expect(metrics['user_service_get_users']).toBeDefined();
            expect(metrics['user_service_get_users'].executions).toBe(2);
            expect(metrics['user_service_get_users'].averageTime).toBeGreaterThan(0);
            expect(metrics['user_service_get_users'].successes).toBe(2);
            expect(metrics['user_service_get_users'].errors).toBe(0);
        });

        test('should generate comprehensive performance report', async () => {
            // Arrange
            mockCacheService.get.mockResolvedValue(null);
            mockUserModel.query.mockReturnValue({
                where: jest.fn().mockReturnThis(),
                offset: jest.fn().mockReturnThis(),
                limit: jest.fn().mockReturnThis(),
                select: jest.fn().mockResolvedValue([]),
                clone: jest.fn().mockReturnValue({
                    count: jest.fn().mockReturnThis(),
                    first: jest.fn().mockResolvedValue({ count: '0' })
                })
            });

            // Act
            await userService.getUsers({ page: 1, limit: 5 });
            const report = pathTracker.generatePerformanceReport();

            // Assert
            expect(report.summary).toBeDefined();
            expect(report.summary.totalPaths).toBeGreaterThan(0);
            expect(report.summary.totalExecutions).toBeGreaterThan(0);
            expect(report.paths['user_service_get_users']).toBeDefined();
            expect(report.paths['user_service_get_users'].successRate).toBe('100.00');
        });
    });

    describe('Path Error Handling', () => {
        test('should handle database errors gracefully', async () => {
            // Arrange
            const dbError = new Error('Database connection failed');
            mockCacheService.get.mockResolvedValue(null);
            mockUserModel.query.mockImplementation(() => {
                throw dbError;
            });

            // Act & Assert
            await expect(userService.getUsers()).rejects.toThrow(dbError);

            // Verify path error tracking
            const metrics = pathTracker.getMetrics();
            expect(metrics['user_service_get_users'].errors).toBe(1);
        });
    });
});
```

### Container Integration

#### Docker Compose for Development
```yaml
# Path: multi-service-development-environment
# File: docker-compose.yml

version: '3.8'

services:
  # Main Node.js application
  app:
    build:
      context: .
      dockerfile: Dockerfile
      target: development
    environment:
      - NODE_ENV=development
      - DATABASE_URL=postgresql://postgres:password@db:5432/ai_seed_dev
      - REDIS_URL=redis://redis:6379/0
      - LOG_LEVEL=debug
      - PATH_MONITORING=true
    volumes:
      - ./src:/app/src:rw
      - ./package*.json:/app/
      - node_modules:/app/node_modules
      - ./logs:/app/logs:rw
    ports:
      - "3000:3000"
      - "9229:9229"  # Node.js debug port
    depends_on:
      - db
      - redis
    networks:
      - ai-seed-network
    command: ["npm", "run", "dev"]
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # PostgreSQL database
  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=ai_seed_dev
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/db/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    networks:
      - ai-seed-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis for caching and sessions
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - ai-seed-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 3

  # Testing service
  test:
    build:
      context: .
      dockerfile: Dockerfile
      target: development
    environment:
      - NODE_ENV=test
      - DATABASE_URL=postgresql://postgres:password@test_db:5432/ai_seed_test
      - REDIS_URL=redis://test_redis:6379/0
    volumes:
      - ./src:/app/src:ro
      - ./tests:/app/tests:ro
      - ./coverage:/app/coverage:rw
    depends_on:
      - test_db
      - test_redis
    networks:
      - ai-seed-network
    command: ["npm", "test"]
    profiles:
      - testing

  test_db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=ai_seed_test
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    networks:
      - ai-seed-network
    profiles:
      - testing

  test_redis:
    image: redis:7-alpine
    networks:
      - ai-seed-network
    profiles:
      - testing

  # Development tools
  adminer:
    image: adminer:4.8.1
    ports:
      - "8080:8080"
    networks:
      - ai-seed-network
    profiles:
      - tools

volumes:
  postgres_data:
  redis_data:
  node_modules:

networks:
  ai-seed-network:
    driver: bridge
```

## Integration with Other Instructions

This JavaScript instruction file works in conjunction with:
- **space.instructions.md**: Foundational path-based principles and container-first development
- **project.instructions.md**: AI-seed specific requirements and patterns
- **python.instructions.md**: Cross-language integration patterns
- **test.instructions.md**: Comprehensive testing strategies for JavaScript
- **ci-cd.instructions.md**: Automated build and deployment pipelines

## Future Evolution

### Advanced JavaScript Patterns
- **WebAssembly Integration**: High-performance computing paths with WASM modules
- **Micro-Frontend Architecture**: Distributed frontend development with path coordination
- **GraphQL Path Optimization**: Query path analysis and optimization
- **Event-Driven Architecture**: Message-driven path execution and coordination

### Performance and Monitoring
- **Real-Time Path Analytics**: Live path performance monitoring and optimization
- **Predictive Path Planning**: AI-driven path selection based on historical data
- **Auto-Scaling Path Management**: Dynamic resource allocation based on path usage
- **Advanced Caching Strategies**: Multi-level caching with path-aware invalidation
