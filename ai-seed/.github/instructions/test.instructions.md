---
file: test.instructions.md
description: Comprehensive testing standards and AI instructions for test-driven development within path-based architecture
author: AI-Seed Team <team@ai-seed.org>
created: 2025-07-19
lastModified: 2025-07-19
version: 1.0.0
relatedIssues: []
relatedEvolutions: []
dependencies:
  - space.instructions.md: Foundation principles and path-based development
  - project.instructions.md: Project-specific context and requirements
  - python.instructions.md: Python testing patterns and practices
  - javascript.instructions.md: JavaScript/Node.js testing frameworks
containerRequirements:
  baseImage: 
    - node:18-alpine
    - python:3.11-slim
  exposedPorts: 3000-3009
  volumes:
    - /tests:rw
    - /coverage:rw
    - /test-results:rw
  environment:
    NODE_ENV: test
    PYTHON_ENV: test
    CI: true
  resources:
    cpu: 1.0-4.0
    memory: 1GiB-4GiB
  healthCheck: /health endpoint validation
paths:
  test-execution-path: Setup → discovery → execution → reporting → cleanup
  coverage-analysis-path: Code analysis → test mapping → coverage calculation → reporting
  quality-assurance-path: Static analysis → dynamic testing → performance testing → security testing
changelog:
  - date: 2025-07-19
    change: Initial creation
    author: AI-Seed Team
usage: Reference for all testing strategies, frameworks, and quality assurance practices
notes: Emphasizes path-based testing, containerized test environments, and AI-assisted test generation
---

# Testing Instructions

These instructions provide comprehensive guidance for implementing robust, path-aware testing strategies within the AI-seed ecosystem, emphasizing container-first testing, automated quality assurance, and AI-assisted test generation and maintenance.

## Testing Philosophy and Strategy

### Path-Based Testing Approach

Testing should follow the natural execution paths through the application, ensuring comprehensive coverage of all routes from input to output while maintaining clear isolation and reproducibility.

#### Core Testing Paths
- **Unit Testing Path**: Individual function/component validation
- **Integration Testing Path**: Component interaction validation
- **End-to-End Testing Path**: Complete user journey validation
- **Performance Testing Path**: Load, stress, and scalability validation
- **Security Testing Path**: Vulnerability and penetration testing
- **Regression Testing Path**: Change impact and stability validation

### Testing Hierarchy and Organization

```
tests/
├── README.md                    # Testing overview and strategy
├── config/                      # Test configuration files
│   ├── jest.config.js          # JavaScript test configuration
│   ├── pytest.ini             # Python test configuration
│   ├── docker-compose.test.yml # Container test orchestration
│   └── test-env.sh             # Test environment setup
├── unit/                        # Unit tests path
│   ├── README.md               # Unit testing guidelines
│   ├── javascript/             # JavaScript unit tests
│   ├── python/                 # Python unit tests
│   └── shared/                 # Shared test utilities
├── integration/                 # Integration tests path
│   ├── README.md               # Integration testing guidelines
│   ├── api/                    # API integration tests
│   ├── database/               # Database integration tests
│   ├── services/               # Service integration tests
│   └── external/               # External service tests
├── e2e/                         # End-to-end tests path
│   ├── README.md               # E2E testing guidelines
│   ├── user-journeys/          # Complete user workflow tests
│   ├── critical-paths/         # Business-critical path tests
│   └── regression/             # Regression test suites
├── performance/                 # Performance tests path
│   ├── README.md               # Performance testing guidelines
│   ├── load/                   # Load testing scenarios
│   ├── stress/                 # Stress testing scenarios
│   └── benchmarks/             # Performance benchmark tests
├── security/                    # Security tests path
│   ├── README.md               # Security testing guidelines
│   ├── vulnerability/          # Vulnerability scanning tests
│   ├── penetration/            # Penetration testing scenarios
│   └── compliance/             # Security compliance tests
├── fixtures/                    # Test data and fixtures path
│   ├── data/                   # Test data files
│   ├── mocks/                  # Mock objects and services
│   └── stubs/                  # Service stubs and fakes
├── utils/                       # Test utilities path
│   ├── helpers/                # Test helper functions
│   ├── assertions/             # Custom assertion libraries
│   ├── factories/              # Test data factories
│   └── path-tracking/          # Path-aware testing utilities
└── reports/                     # Test reports and coverage path
    ├── coverage/               # Code coverage reports
    ├── performance/            # Performance test results
    ├── security/               # Security test reports
    └── ci/                     # CI/CD test result artifacts
```

## Container-First Testing Environment

### Test Container Configuration

#### Multi-Stage Test Dockerfile
```dockerfile
# Path: test-environment-setup
# File: Dockerfile.test

# Base test environment
FROM node:18-alpine AS test-base
WORKDIR /app

# Install test dependencies
RUN apk add --no-cache \
    python3 \
    py3-pip \
    bash \
    curl \
    git \
    && npm install -g @playwright/test \
    && pip3 install pytest pytest-cov pytest-asyncio

# Copy test configuration
COPY tests/config/ ./tests/config/
COPY package*.json ./
COPY requirements*.txt ./

# Install dependencies
RUN npm ci --include=dev
RUN pip3 install -r requirements-test.txt

# JavaScript test environment
FROM test-base AS javascript-tests
COPY src/ ./src/
COPY tests/unit/javascript/ ./tests/unit/javascript/
COPY tests/integration/ ./tests/integration/
COPY tests/e2e/ ./tests/e2e/

# Set test environment
ENV NODE_ENV=test
ENV CI=true

# Run JavaScript tests
CMD ["npm", "run", "test:ci"]

# Python test environment
FROM test-base AS python-tests
COPY src/ ./src/
COPY tests/unit/python/ ./tests/unit/python/
COPY tests/integration/ ./tests/integration/

# Set test environment
ENV PYTHON_ENV=test
ENV PYTHONPATH=/app/src

# Run Python tests
CMD ["python", "-m", "pytest", "--cov=src", "--cov-report=html", "--cov-report=term"]

# Performance test environment
FROM test-base AS performance-tests
RUN npm install -g artillery k6

COPY tests/performance/ ./tests/performance/
COPY src/ ./src/

# Set performance test environment
ENV NODE_ENV=performance
ENV PERFORMANCE_TEST=true

# Run performance tests
CMD ["npm", "run", "test:performance"]

# Security test environment
FROM test-base AS security-tests
RUN apk add --no-cache nmap \
    && npm install -g retire snyk \
    && pip3 install safety bandit

COPY . .

# Run security tests
CMD ["npm", "run", "test:security"]

# All tests environment
FROM test-base AS all-tests
COPY . .

# Install all test dependencies
RUN npm ci --include=dev \
    && pip3 install -r requirements-test.txt

# Default test command
CMD ["npm", "run", "test:all"]
```

#### Docker Compose Test Orchestration
```yaml
# Path: test-orchestration-setup
# File: docker-compose.test.yml

version: '3.8'

services:
  # Test database
  test-db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: test_db
      POSTGRES_USER: test_user
      POSTGRES_PASSWORD: test_password
    volumes:
      - test-db-data:/var/lib/postgresql/data
      - ./tests/fixtures/sql:/docker-entrypoint-initdb.d
    networks:
      - test-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U test_user -d test_db"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Test Redis
  test-redis:
    image: redis:7-alpine
    networks:
      - test-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3

  # JavaScript unit tests
  js-unit-tests:
    build:
      context: .
      dockerfile: Dockerfile.test
      target: javascript-tests
    environment:
      - DATABASE_URL=postgresql://test_user:test_password@test-db:5432/test_db
      - REDIS_URL=redis://test-redis:6379
      - NODE_ENV=test
    depends_on:
      test-db:
        condition: service_healthy
      test-redis:
        condition: service_healthy
    volumes:
      - ./tests/reports:/app/tests/reports
    networks:
      - test-network
    command: ["npm", "run", "test:unit"]

  # Python unit tests
  py-unit-tests:
    build:
      context: .
      dockerfile: Dockerfile.test
      target: python-tests
    environment:
      - DATABASE_URL=postgresql://test_user:test_password@test-db:5432/test_db
      - REDIS_URL=redis://test-redis:6379
      - PYTHON_ENV=test
    depends_on:
      test-db:
        condition: service_healthy
      test-redis:
        condition: service_healthy
    volumes:
      - ./tests/reports:/app/tests/reports
    networks:
      - test-network
    command: ["python", "-m", "pytest", "tests/unit/python/", "-v"]

  # Integration tests
  integration-tests:
    build:
      context: .
      dockerfile: Dockerfile.test
      target: all-tests
    environment:
      - DATABASE_URL=postgresql://test_user:test_password@test-db:5432/test_db
      - REDIS_URL=redis://test-redis:6379
      - NODE_ENV=test
      - PYTHON_ENV=test
    depends_on:
      test-db:
        condition: service_healthy
      test-redis:
        condition: service_healthy
    volumes:
      - ./tests/reports:/app/tests/reports
    networks:
      - test-network
    command: ["npm", "run", "test:integration"]

  # End-to-end tests
  e2e-tests:
    build:
      context: .
      dockerfile: Dockerfile.test
      target: all-tests
    environment:
      - DATABASE_URL=postgresql://test_user:test_password@test-db:5432/test_db
      - REDIS_URL=redis://test-redis:6379
      - NODE_ENV=test
      - APP_URL=http://app-under-test:3000
    depends_on:
      test-db:
        condition: service_healthy
      test-redis:
        condition: service_healthy
      app-under-test:
        condition: service_healthy
    volumes:
      - ./tests/reports:/app/tests/reports
    networks:
      - test-network
    command: ["npm", "run", "test:e2e"]

  # Application under test
  app-under-test:
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=postgresql://test_user:test_password@test-db:5432/test_db
      - REDIS_URL=redis://test-redis:6379
      - NODE_ENV=test
    depends_on:
      test-db:
        condition: service_healthy
      test-redis:
        condition: service_healthy
    networks:
      - test-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Performance tests
  performance-tests:
    build:
      context: .
      dockerfile: Dockerfile.test
      target: performance-tests
    environment:
      - APP_URL=http://app-under-test:3000
    depends_on:
      app-under-test:
        condition: service_healthy
    volumes:
      - ./tests/reports:/app/tests/reports
    networks:
      - test-network
    command: ["npm", "run", "test:performance"]

  # Security tests
  security-tests:
    build:
      context: .
      dockerfile: Dockerfile.test
      target: security-tests
    environment:
      - APP_URL=http://app-under-test:3000
    depends_on:
      app-under-test:
        condition: service_healthy
    volumes:
      - ./tests/reports:/app/tests/reports
    networks:
      - test-network
    command: ["npm", "run", "test:security"]

volumes:
  test-db-data:

networks:
  test-network:
    driver: bridge
```

## Path-Aware Testing Framework

### JavaScript/Node.js Testing with Path Tracking

```javascript
// Path: javascript-testing-framework
// File: tests/utils/path-aware-testing.js

import { pathTracker } from '../../src/utils/path-tracker.js';
import { logger } from '../../src/config/logger.js';

/**
 * Path-aware testing utilities for comprehensive test execution tracking
 */
export class PathAwareTestSuite {
    constructor(suiteName) {
        this.suiteName = suiteName;
        this.testResults = [];
        this.pathMetrics = {};
        this.setupCallbacks = [];
        this.teardownCallbacks = [];
    }

    /**
     * Execute test suite with path tracking
     */
    async runSuite(tests) {
        return pathTracker.executeInPath(`test_suite_${this.suiteName}`, async () => {
            logger.info(`Starting test suite: ${this.suiteName}`, 'test_execution');

            // Path: test-suite-setup
            await pathTracker.executeInPath('test_suite_setup', async () => {
                await this.executeSetupCallbacks();
            });

            const results = {
                suiteName: this.suiteName,
                startTime: new Date().toISOString(),
                tests: [],
                pathMetrics: {},
                summary: {}
            };

            // Path: test-execution
            for (const test of tests) {
                const testResult = await this.executeTest(test);
                results.tests.push(testResult);
            }

            // Path: test-suite-teardown
            await pathTracker.executeInPath('test_suite_teardown', async () => {
                await this.executeTeardownCallbacks();
            });

            // Path: results-compilation
            results.endTime = new Date().toISOString();
            results.pathMetrics = pathTracker.getMetrics();
            results.summary = this.compileSummary(results.tests);

            logger.info(`Completed test suite: ${this.suiteName}`, 'test_execution', {
                totalTests: results.tests.length,
                passed: results.summary.passed,
                failed: results.summary.failed,
                duration: results.summary.duration
            });

            return results;
        });
    }

    /**
     * Execute individual test with comprehensive path tracking
     */
    async executeTest(testDefinition) {
        const testPath = `test_${testDefinition.name.replace(/\s+/g, '_').toLowerCase()}`;
        
        return pathTracker.executeInPath(testPath, async () => {
            const testResult = {
                name: testDefinition.name,
                description: testDefinition.description,
                startTime: new Date().toISOString(),
                status: 'running',
                pathsExecuted: [],
                assertions: [],
                errors: [],
                duration: 0
            };

            const startTime = Date.now();

            try {
                // Path: test-setup
                if (testDefinition.setup) {
                    await pathTracker.executeInPath(`${testPath}_setup`, async () => {
                        await testDefinition.setup();
                    });
                }

                // Path: test-execution
                const testContext = new TestContext(testResult);
                await pathTracker.executeInPath(`${testPath}_execution`, async () => {
                    await testDefinition.test(testContext);
                });

                // Path: test-validation
                await pathTracker.executeInPath(`${testPath}_validation`, async () => {
                    this.validateTestResults(testContext);
                });

                testResult.status = 'passed';
                
            } catch (error) {
                testResult.status = 'failed';
                testResult.errors.push({
                    message: error.message,
                    stack: error.stack,
                    path: pathTracker.getCurrentPath()
                });
                
                logger.error(`Test failed: ${testDefinition.name}`, 'test_execution', {
                    error: error.message,
                    path: pathTracker.getCurrentPath()
                });
                
            } finally {
                // Path: test-teardown
                if (testDefinition.teardown) {
                    try {
                        await pathTracker.executeInPath(`${testPath}_teardown`, async () => {
                            await testDefinition.teardown();
                        });
                    } catch (teardownError) {
                        testResult.errors.push({
                            message: `Teardown failed: ${teardownError.message}`,
                            stack: teardownError.stack,
                            type: 'teardown'
                        });
                    }
                }

                testResult.endTime = new Date().toISOString();
                testResult.duration = Date.now() - startTime;
                testResult.pathsExecuted = pathTracker.getExecutedPaths();
            }

            return testResult;
        });
    }

    /**
     * Test context with assertion utilities
     */
}

export class TestContext {
    constructor(testResult) {
        this.testResult = testResult;
        this.assertions = [];
    }

    /**
     * Path-aware assertion that equals
     */
    assertEquals(actual, expected, message = '') {
        const assertion = {
            type: 'assertEquals',
            actual,
            expected,
            message,
            path: pathTracker.getCurrentPath(),
            passed: false
        };

        try {
            if (actual !== expected) {
                throw new Error(`Assertion failed: ${message || ''}\nExpected: ${expected}\nActual: ${actual}`);
            }
            assertion.passed = true;
        } catch (error) {
            assertion.error = error.message;
            throw error;
        } finally {
            this.assertions.push(assertion);
            this.testResult.assertions.push(assertion);
        }
    }

    /**
     * Path-aware assertion that truthy
     */
    assertTrue(value, message = '') {
        const assertion = {
            type: 'assertTrue',
            value,
            message,
            path: pathTracker.getCurrentPath(),
            passed: false
        };

        try {
            if (!value) {
                throw new Error(`Assertion failed: ${message || ''}\nExpected truthy value, got: ${value}`);
            }
            assertion.passed = true;
        } catch (error) {
            assertion.error = error.message;
            throw error;
        } finally {
            this.assertions.push(assertion);
            this.testResult.assertions.push(assertion);
        }
    }

    /**
     * Path-aware assertion for array contents
     */
    assertArrayEquals(actual, expected, message = '') {
        const assertion = {
            type: 'assertArrayEquals',
            actual,
            expected,
            message,
            path: pathTracker.getCurrentPath(),
            passed: false
        };

        try {
            if (!Array.isArray(actual) || !Array.isArray(expected)) {
                throw new Error('Both values must be arrays');
            }
            
            if (actual.length !== expected.length) {
                throw new Error(`Array lengths differ: expected ${expected.length}, got ${actual.length}`);
            }
            
            for (let i = 0; i < actual.length; i++) {
                if (actual[i] !== expected[i]) {
                    throw new Error(`Arrays differ at index ${i}: expected ${expected[i]}, got ${actual[i]}`);
                }
            }
            
            assertion.passed = true;
        } catch (error) {
            assertion.error = error.message;
            throw new Error(`Assertion failed: ${message || ''}\n${error.message}`);
        } finally {
            this.assertions.push(assertion);
            this.testResult.assertions.push(assertion);
        }
    }

    /**
     * Path-aware async assertion
     */
    async assertAsync(asyncFunction, expectedResult, message = '') {
        const assertion = {
            type: 'assertAsync',
            message,
            path: pathTracker.getCurrentPath(),
            passed: false
        };

        try {
            const result = await asyncFunction();
            if (result !== expectedResult) {
                throw new Error(`Async assertion failed: expected ${expectedResult}, got ${result}`);
            }
            assertion.passed = true;
            assertion.result = result;
        } catch (error) {
            assertion.error = error.message;
            throw new Error(`Async assertion failed: ${message || ''}\n${error.message}`);
        } finally {
            this.assertions.push(assertion);
            this.testResult.assertions.push(assertion);
        }
    }

    /**
     * Path-aware error assertion
     */
    async assertThrows(asyncFunction, expectedErrorType, message = '') {
        const assertion = {
            type: 'assertThrows',
            expectedErrorType: expectedErrorType.name,
            message,
            path: pathTracker.getCurrentPath(),
            passed: false
        };

        try {
            await asyncFunction();
            throw new Error('Expected function to throw an error, but it completed successfully');
        } catch (error) {
            if (!(error instanceof expectedErrorType)) {
                throw new Error(`Expected error of type ${expectedErrorType.name}, got ${error.constructor.name}`);
            }
            assertion.passed = true;
            assertion.actualError = error.constructor.name;
        } finally {
            this.assertions.push(assertion);
            this.testResult.assertions.push(assertion);
        }
    }
}

/**
 * Test runner with comprehensive reporting
 */
export class PathAwareTestRunner {
    constructor(config = {}) {
        this.config = {
            parallel: false,
            maxConcurrency: 4,
            timeout: 30000,
            retries: 0,
            reportFormat: 'json',
            outputPath: './tests/reports',
            ...config
        };
        this.suites = [];
        this.globalSetup = null;
        this.globalTeardown = null;
    }

    /**
     * Add test suite to runner
     */
    addSuite(suite) {
        this.suites.push(suite);
    }

    /**
     * Run all test suites
     */
    async runAll() {
        return pathTracker.executeInPath('test_runner_execution', async () => {
            logger.info('Starting test runner execution', 'test_runner');

            const runResults = {
                startTime: new Date().toISOString(),
                config: this.config,
                suites: [],
                summary: {},
                pathMetrics: {}
            };

            // Path: global-setup
            if (this.globalSetup) {
                await pathTracker.executeInPath('global_setup', async () => {
                    await this.globalSetup();
                });
            }

            try {
                // Path: suite-execution
                if (this.config.parallel) {
                    runResults.suites = await this.runSuitesParallel();
                } else {
                    runResults.suites = await this.runSuitesSequential();
                }

            } finally {
                // Path: global-teardown
                if (this.globalTeardown) {
                    await pathTracker.executeInPath('global_teardown', async () => {
                        await this.globalTeardown();
                    });
                }
            }

            // Path: results-compilation
            runResults.endTime = new Date().toISOString();
            runResults.pathMetrics = pathTracker.getMetrics();
            runResults.summary = this.compileOverallSummary(runResults.suites);

            // Path: report-generation
            await pathTracker.executeInPath('report_generation', async () => {
                await this.generateReports(runResults);
            });

            logger.info('Test runner execution completed', 'test_runner', {
                totalSuites: runResults.suites.length,
                totalTests: runResults.summary.totalTests,
                passed: runResults.summary.totalPassed,
                failed: runResults.summary.totalFailed,
                duration: runResults.summary.totalDuration
            });

            return runResults;
        });
    }

    /**
     * Generate comprehensive test reports
     */
    async generateReports(runResults) {
        const reports = {
            json: this.generateJsonReport(runResults),
            junit: this.generateJunitReport(runResults),
            html: this.generateHtmlReport(runResults),
            pathAnalysis: this.generatePathAnalysisReport(runResults)
        };

        // Write reports to files
        for (const [format, content] of Object.entries(reports)) {
            const filename = `test-results.${format === 'junit' ? 'xml' : format}`;
            const filepath = path.join(this.config.outputPath, filename);
            
            await fs.mkdir(path.dirname(filepath), { recursive: true });
            await fs.writeFile(filepath, content, 'utf8');
            
            logger.info(`Generated ${format} report: ${filepath}`, 'test_runner');
        }
    }
}

// Example usage and test definitions
export const exampleTestSuite = new PathAwareTestSuite('example_suite');

exampleTestSuite.addSetup(async () => {
    // Suite setup code
    logger.info('Setting up example test suite', 'test_setup');
});

exampleTestSuite.addTeardown(async () => {
    // Suite teardown code
    logger.info('Tearing down example test suite', 'test_teardown');
});

// Example test definitions
export const exampleTests = [
    {
        name: 'Path Tracker Basic Functionality',
        description: 'Test that path tracker correctly tracks execution paths',
        async test(context) {
            // Path: path-tracker-initialization
            const initialPath = pathTracker.getCurrentPath();
            context.assertTrue(initialPath, 'Should have an initial path');

            // Path: path-execution-tracking
            let executedPath = null;
            await pathTracker.executeInPath('test_path', async () => {
                executedPath = pathTracker.getCurrentPath();
            });

            context.assertEquals(executedPath, 'test_path', 'Should track executed path correctly');

            // Path: metrics-collection
            const metrics = pathTracker.getMetrics();
            context.assertTrue(metrics.test_path, 'Should have metrics for executed path');
            context.assertTrue(metrics.test_path.executions > 0, 'Should record path executions');
        }
    },
    {
        name: 'Async Path Execution',
        description: 'Test async path execution with proper error handling',
        async test(context) {
            // Path: async-path-execution
            const result = await pathTracker.executeInPath('async_test_path', async () => {
                await new Promise(resolve => setTimeout(resolve, 100));
                return 'async_result';
            });

            context.assertEquals(result, 'async_result', 'Should return async result correctly');

            // Path: error-handling-validation
            await context.assertThrows(async () => {
                await pathTracker.executeInPath('error_path', async () => {
                    throw new Error('Test error');
                });
            }, Error, 'Should propagate errors correctly');
        }
    }
];
```

### Python Testing Framework with Path Awareness

```python
# Path: python-testing-framework
# File: tests/utils/path_aware_testing.py

import asyncio
import pytest
import time
import json
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from pathlib import Path
import logging

from src.utils.path_tracker import PathTracker

# Configure test logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TestAssertion:
    """Represents a test assertion with path context"""
    assertion_type: str
    expected: Any
    actual: Any
    message: str
    path: str
    passed: bool
    error: Optional[str] = None

@dataclass
class TestResult:
    """Comprehensive test result with path tracking"""
    name: str
    description: str
    start_time: str
    end_time: Optional[str] = None
    status: str = 'pending'
    duration_ms: int = 0
    paths_executed: List[str] = field(default_factory=list)
    assertions: List[TestAssertion] = field(default_factory=list)
    errors: List[Dict[str, Any]] = field(default_factory=list)
    path_metrics: Dict[str, Any] = field(default_factory=dict)

class PathAwareTestContext:
    """Test context with path-aware assertions"""
    
    def __init__(self, test_result: TestResult, path_tracker: PathTracker):
        self.test_result = test_result
        self.path_tracker = path_tracker
        self.assertions: List[TestAssertion] = []

    def assert_equals(self, actual: Any, expected: Any, message: str = ""):
        """Path-aware equality assertion"""
        assertion = TestAssertion(
            assertion_type='assert_equals',
            expected=expected,
            actual=actual,
            message=message,
            path=self.path_tracker.get_current_path(),
            passed=False
        )

        try:
            if actual != expected:
                raise AssertionError(
                    f"Assertion failed: {message}\nExpected: {expected}\nActual: {actual}"
                )
            assertion.passed = True
        except Exception as e:
            assertion.error = str(e)
            raise
        finally:
            self.assertions.append(assertion)
            self.test_result.assertions.append(assertion)

    def assert_true(self, value: Any, message: str = ""):
        """Path-aware truthy assertion"""
        assertion = TestAssertion(
            assertion_type='assert_true',
            expected=True,
            actual=value,
            message=message,
            path=self.path_tracker.get_current_path(),
            passed=False
        )

        try:
            if not value:
                raise AssertionError(
                    f"Assertion failed: {message}\nExpected truthy value, got: {value}"
                )
            assertion.passed = True
        except Exception as e:
            assertion.error = str(e)
            raise
        finally:
            self.assertions.append(assertion)
            self.test_result.assertions.append(assertion)

    def assert_in(self, item: Any, container: Any, message: str = ""):
        """Path-aware containment assertion"""
        assertion = TestAssertion(
            assertion_type='assert_in',
            expected=f"{item} in {type(container).__name__}",
            actual=item in container if hasattr(container, '__contains__') else False,
            message=message,
            path=self.path_tracker.get_current_path(),
            passed=False
        )

        try:
            if item not in container:
                raise AssertionError(
                    f"Assertion failed: {message}\n{item} not found in {container}"
                )
            assertion.passed = True
        except Exception as e:
            assertion.error = str(e)
            raise
        finally:
            self.assertions.append(assertion)
            self.test_result.assertions.append(assertion)

    async def assert_async(self, async_func: Callable, expected: Any, message: str = ""):
        """Path-aware async assertion"""
        assertion = TestAssertion(
            assertion_type='assert_async',
            expected=expected,
            actual=None,
            message=message,
            path=self.path_tracker.get_current_path(),
            passed=False
        )

        try:
            result = await async_func()
            assertion.actual = result
            if result != expected:
                raise AssertionError(
                    f"Async assertion failed: {message}\nExpected: {expected}\nActual: {result}"
                )
            assertion.passed = True
        except Exception as e:
            assertion.error = str(e)
            raise
        finally:
            self.assertions.append(assertion)
            self.test_result.assertions.append(assertion)

    def assert_raises(self, exception_type: type, func: Callable, message: str = ""):
        """Path-aware exception assertion"""
        assertion = TestAssertion(
            assertion_type='assert_raises',
            expected=exception_type.__name__,
            actual=None,
            message=message,
            path=self.path_tracker.get_current_path(),
            passed=False
        )

        try:
            func()
            raise AssertionError(f"Expected {exception_type.__name__} to be raised")
        except exception_type as e:
            assertion.actual = type(e).__name__
            assertion.passed = True
        except Exception as e:
            assertion.actual = type(e).__name__
            assertion.error = f"Wrong exception type: expected {exception_type.__name__}, got {type(e).__name__}"
            raise AssertionError(assertion.error)
        finally:
            self.assertions.append(assertion)
            self.test_result.assertions.append(assertion)

class PathAwareTestSuite:
    """Test suite with comprehensive path tracking"""
    
    def __init__(self, suite_name: str):
        self.suite_name = suite_name
        self.path_tracker = PathTracker()
        self.tests: List[Dict[str, Any]] = []
        self.setup_callbacks: List[Callable] = []
        self.teardown_callbacks: List[Callable] = []

    def add_setup(self, callback: Callable):
        """Add suite setup callback"""
        self.setup_callbacks.append(callback)

    def add_teardown(self, callback: Callable):
        """Add suite teardown callback"""
        self.teardown_callbacks.append(callback)

    def add_test(self, name: str, test_func: Callable, description: str = "", 
                 setup: Optional[Callable] = None, teardown: Optional[Callable] = None):
        """Add test to suite"""
        self.tests.append({
            'name': name,
            'description': description,
            'test_func': test_func,
            'setup': setup,
            'teardown': teardown
        })

    async def run_suite(self) -> Dict[str, Any]:
        """Execute entire test suite with path tracking"""
        return await self.path_tracker.execute_in_path(
            f"test_suite_{self.suite_name}",
            self._run_suite_internal
        )

    async def _run_suite_internal(self) -> Dict[str, Any]:
        """Internal suite execution logic"""
        logger.info(f"Starting test suite: {self.suite_name}")

        results = {
            'suite_name': self.suite_name,
            'start_time': time.time(),
            'tests': [],
            'path_metrics': {},
            'summary': {}
        }

        # Path: test-suite-setup
        await self.path_tracker.execute_in_path('test_suite_setup', self._execute_setup_callbacks)

        try:
            # Path: test-execution
            for test_def in self.tests:
                test_result = await self._execute_test(test_def)
                results['tests'].append(test_result)

        finally:
            # Path: test-suite-teardown
            await self.path_tracker.execute_in_path('test_suite_teardown', self._execute_teardown_callbacks)

        # Path: results-compilation
        results['end_time'] = time.time()
        results['duration_ms'] = int((results['end_time'] - results['start_time']) * 1000)
        results['path_metrics'] = self.path_tracker.get_metrics()
        results['summary'] = self._compile_summary(results['tests'])

        logger.info(f"Completed test suite: {self.suite_name}", extra={
            'total_tests': len(results['tests']),
            'passed': results['summary']['passed'],
            'failed': results['summary']['failed'],
            'duration_ms': results['duration_ms']
        })

        return results

    async def _execute_test(self, test_def: Dict[str, Any]) -> TestResult:
        """Execute individual test with comprehensive tracking"""
        test_path = f"test_{test_def['name'].replace(' ', '_').lower()}"
        
        return await self.path_tracker.execute_in_path(test_path, 
            lambda: self._execute_test_internal(test_def, test_path))

    async def _execute_test_internal(self, test_def: Dict[str, Any], test_path: str) -> TestResult:
        """Internal test execution logic"""
        test_result = TestResult(
            name=test_def['name'],
            description=test_def['description'],
            start_time=time.time()
        )

        start_time = time.time()

        try:
            # Path: test-setup
            if test_def['setup']:
                await self.path_tracker.execute_in_path(f"{test_path}_setup", test_def['setup'])

            # Path: test-execution
            context = PathAwareTestContext(test_result, self.path_tracker)
            await self.path_tracker.execute_in_path(f"{test_path}_execution", 
                lambda: test_def['test_func'](context))

            test_result.status = 'passed'

        except Exception as e:
            test_result.status = 'failed'
            test_result.errors.append({
                'message': str(e),
                'type': type(e).__name__,
                'path': self.path_tracker.get_current_path()
            })
            logger.error(f"Test failed: {test_def['name']}", extra={
                'error': str(e),
                'path': self.path_tracker.get_current_path()
            })

        finally:
            # Path: test-teardown
            if test_def['teardown']:
                try:
                    await self.path_tracker.execute_in_path(f"{test_path}_teardown", test_def['teardown'])
                except Exception as teardown_error:
                    test_result.errors.append({
                        'message': f"Teardown failed: {str(teardown_error)}",
                        'type': 'teardown_error',
                        'path': self.path_tracker.get_current_path()
                    })

            test_result.end_time = time.time()
            test_result.duration_ms = int((test_result.end_time - start_time) * 1000)
            test_result.paths_executed = self.path_tracker.get_executed_paths()
            test_result.path_metrics = self.path_tracker.get_path_metrics(test_path)

        return test_result

    async def _execute_setup_callbacks(self):
        """Execute all setup callbacks"""
        for callback in self.setup_callbacks:
            await callback()

    async def _execute_teardown_callbacks(self):
        """Execute all teardown callbacks"""
        for callback in self.teardown_callbacks:
            await callback()

    def _compile_summary(self, test_results: List[TestResult]) -> Dict[str, Any]:
        """Compile test summary statistics"""
        total = len(test_results)
        passed = sum(1 for test in test_results if test.status == 'passed')
        failed = total - passed
        total_duration = sum(test.duration_ms for test in test_results)

        return {
            'total': total,
            'passed': passed,
            'failed': failed,
            'success_rate': (passed / total * 100) if total > 0 else 0,
            'total_duration_ms': total_duration,
            'average_duration_ms': total_duration / total if total > 0 else 0
        }

# Example test suite definition
async def example_path_tracker_test(context: PathAwareTestContext):
    """Example test for path tracker functionality"""
    # Path: path-tracker-initialization
    initial_path = context.path_tracker.get_current_path()
    context.assert_true(initial_path, "Should have an initial path")

    # Path: path-execution-tracking
    executed_path = None
    async def test_path_execution():
        nonlocal executed_path
        executed_path = context.path_tracker.get_current_path()
        return "test_result"

    result = await context.path_tracker.execute_in_path('test_path', test_path_execution)
    context.assert_equals(result, "test_result", "Should return result correctly")
    context.assert_equals(executed_path, "test_path", "Should track executed path correctly")

    # Path: metrics-collection
    metrics = context.path_tracker.get_metrics()
    context.assert_in('test_path', metrics, "Should have metrics for executed path")

# Create example test suite
example_suite = PathAwareTestSuite('example_python_suite')

example_suite.add_setup(lambda: logger.info("Setting up Python test suite"))
example_suite.add_teardown(lambda: logger.info("Tearing down Python test suite"))

example_suite.add_test(
    'Path Tracker Functionality',
    example_path_tracker_test,
    'Test comprehensive path tracker functionality with metrics collection'
)

# Pytest integration
@pytest.mark.asyncio
async def test_path_aware_suite():
    """Pytest integration for path-aware test suite"""
    results = await example_suite.run_suite()
    
    assert results['summary']['total'] > 0, "Should have executed tests"
    assert results['summary']['failed'] == 0, f"All tests should pass, but {results['summary']['failed']} failed"
    assert 'path_metrics' in results, "Should include path metrics"
    
    # Verify path tracking occurred
    assert len(results['path_metrics']) > 0, "Should have collected path metrics"
```

## Automated Test Generation and AI Integration

### AI-Powered Test Case Generation

```javascript
// Path: ai-powered-test-generation
// File: src/utils/ai-test-generator.js

/**
 * AI-powered test case generation system
 */
export class AITestGenerator {
    constructor() {
        this.codeAnalyzer = new CodeAnalyzer();
        this.pathAnalyzer = new PathAnalyzer();
        this.testTemplateEngine = new TestTemplateEngine();
    }

    /**
     * Generate comprehensive test suite for given code
     */
    async generateTestSuite(sourceCode, options = {}) {
        return pathTracker.executeInPath('ai_test_generation', async () => {
            const analysis = await this.analyzeCode(sourceCode);
            const testCases = await this.generateTestCases(analysis, options);
            const testSuite = await this.assembleTestSuite(testCases, options);
            
            return testSuite;
        });
    }

    /**
     * Analyze source code to identify testable components
     */
    async analyzeCode(sourceCode) {
        return pathTracker.executeInPath('code_analysis', async () => {
            const analysis = {
                functions: await this.codeAnalyzer.extractFunctions(sourceCode),
                classes: await this.codeAnalyzer.extractClasses(sourceCode),
                modules: await this.codeAnalyzer.extractModules(sourceCode),
                dependencies: await this.codeAnalyzer.analyzeDependencies(sourceCode),
                paths: await this.pathAnalyzer.identifyExecutionPaths(sourceCode),
                complexity: await this.codeAnalyzer.calculateComplexity(sourceCode)
            };

            return analysis;
        });
    }

    /**
     * Generate test cases based on code analysis
     */
    async generateTestCases(analysis, options) {
        return pathTracker.executeInPath('test_case_generation', async () => {
            const testCases = [];

            // Generate function tests
            for (const func of analysis.functions) {
                const functionTests = await this.generateFunctionTests(func, analysis);
                testCases.push(...functionTests);
            }

            // Generate class tests
            for (const cls of analysis.classes) {
                const classTests = await this.generateClassTests(cls, analysis);
                testCases.push(...classTests);
            }

            // Generate integration tests
            const integrationTests = await this.generateIntegrationTests(analysis);
            testCases.push(...integrationTests);

            // Generate path-specific tests
            const pathTests = await this.generatePathTests(analysis.paths);
            testCases.push(...pathTests);

            return testCases;
        });
    }

    /**
     * Generate test cases for individual functions
     */
    async generateFunctionTests(functionDef, codeAnalysis) {
        const tests = [];

        // Happy path test
        tests.push({
            type: 'unit',
            category: 'happy_path',
            name: `${functionDef.name} - Happy Path`,
            description: `Test normal operation of ${functionDef.name}`,
            setup: this.generateFunctionSetup(functionDef),
            test: this.generateHappyPathTest(functionDef),
            assertions: this.generateHappyPathAssertions(functionDef),
            teardown: this.generateFunctionTeardown(functionDef)
        });

        // Edge case tests
        const edgeCases = this.identifyEdgeCases(functionDef);
        for (const edgeCase of edgeCases) {
            tests.push({
                type: 'unit',
                category: 'edge_case',
                name: `${functionDef.name} - ${edgeCase.name}`,
                description: `Test ${functionDef.name} with ${edgeCase.description}`,
                setup: this.generateEdgeCaseSetup(functionDef, edgeCase),
                test: this.generateEdgeCaseTest(functionDef, edgeCase),
                assertions: this.generateEdgeCaseAssertions(functionDef, edgeCase),
                teardown: this.generateFunctionTeardown(functionDef)
            });
        }

        // Error condition tests
        const errorConditions = this.identifyErrorConditions(functionDef);
        for (const errorCondition of errorConditions) {
            tests.push({
                type: 'unit',
                category: 'error_handling',
                name: `${functionDef.name} - ${errorCondition.name}`,
                description: `Test ${functionDef.name} error handling for ${errorCondition.description}`,
                setup: this.generateErrorSetup(functionDef, errorCondition),
                test: this.generateErrorTest(functionDef, errorCondition),
                assertions: this.generateErrorAssertions(functionDef, errorCondition),
                teardown: this.generateFunctionTeardown(functionDef)
            });
        }

        return tests;
    }

    /**
     * Generate comprehensive integration tests
     */
    async generateIntegrationTests(codeAnalysis) {
        const integrationTests = [];

        // Component interaction tests
        const componentPairs = this.identifyComponentInteractions(codeAnalysis);
        for (const [componentA, componentB] of componentPairs) {
            integrationTests.push({
                type: 'integration',
                category: 'component_interaction',
                name: `Integration: ${componentA.name} → ${componentB.name}`,
                description: `Test interaction between ${componentA.name} and ${componentB.name}`,
                setup: this.generateIntegrationSetup([componentA, componentB]),
                test: this.generateInteractionTest(componentA, componentB),
                assertions: this.generateInteractionAssertions(componentA, componentB),
                teardown: this.generateIntegrationTeardown([componentA, componentB])
            });
        }

        // Data flow tests
        const dataFlows = this.identifyDataFlows(codeAnalysis);
        for (const dataFlow of dataFlows) {
            integrationTests.push({
                type: 'integration',
                category: 'data_flow',
                name: `Data Flow: ${dataFlow.source} → ${dataFlow.destination}`,
                description: `Test data flow from ${dataFlow.source} to ${dataFlow.destination}`,
                setup: this.generateDataFlowSetup(dataFlow),
                test: this.generateDataFlowTest(dataFlow),
                assertions: this.generateDataFlowAssertions(dataFlow),
                teardown: this.generateDataFlowTeardown(dataFlow)
            });
        }

        return integrationTests;
    }

    /**
     * Generate path-specific tests
     */
    async generatePathTests(pathAnalysis) {
        const pathTests = [];

        for (const path of pathAnalysis.criticalPaths) {
            pathTests.push({
                type: 'path',
                category: 'critical_path',
                name: `Critical Path: ${path.name}`,
                description: `Test critical execution path: ${path.description}`,
                setup: this.generatePathSetup(path),
                test: this.generatePathTest(path),
                assertions: this.generatePathAssertions(path),
                teardown: this.generatePathTeardown(path)
            });
        }

        for (const path of pathAnalysis.errorPaths) {
            pathTests.push({
                type: 'path',
                category: 'error_path',
                name: `Error Path: ${path.name}`,
                description: `Test error handling path: ${path.description}`,
                setup: this.generateErrorPathSetup(path),
                test: this.generateErrorPathTest(path),
                assertions: this.generateErrorPathAssertions(path),
                teardown: this.generatePathTeardown(path)
            });
        }

        return pathTests;
    }

    /**
     * Assemble complete test suite from generated test cases
     */
    async assembleTestSuite(testCases, options) {
        const testSuite = {
            name: options.suiteName || 'Generated Test Suite',
            description: options.description || 'AI-generated comprehensive test suite',
            framework: options.framework || 'path-aware',
            configuration: {
                timeout: options.timeout || 30000,
                retries: options.retries || 0,
                parallel: options.parallel || false
            },
            setup: this.generateSuiteSetup(testCases, options),
            teardown: this.generateSuiteTeardown(testCases, options),
            tests: testCases,
            metadata: {
                generatedAt: new Date().toISOString(),
                generator: 'AI Test Generator v1.0',
                totalTests: testCases.length,
                testTypes: this.summarizeTestTypes(testCases)
            }
        };

        return testSuite;
    }
}
```

## Performance and Security Testing

### Performance Testing Framework

```bash
#!/bin/bash
# Path: performance-testing-automation
# File: tests/performance/run-performance-tests.sh

set -euo pipefail

# Path: script-initialization
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../../" && pwd)"
readonly RESULTS_DIR="${SCRIPT_DIR}/results"

# Load libraries
source "${PROJECT_ROOT}/scripts/lib/logging.sh"
source "${PROJECT_ROOT}/scripts/lib/path_management.sh"

# Path: performance-testing-workflow
run_performance_tests() {
    enter_path "performance_testing"
    
    log_info "Starting comprehensive performance testing" "performance_testing"
    
    # Ensure results directory exists
    mkdir -p "$RESULTS_DIR"
    
    # Path: load-testing
    execute_in_path "load_testing" \
        "run_load_tests"
    
    # Path: stress-testing
    execute_in_path "stress_testing" \
        "run_stress_tests"
    
    # Path: spike-testing
    execute_in_path "spike_testing" \
        "run_spike_tests"
    
    # Path: endurance-testing
    execute_in_path "endurance_testing" \
        "run_endurance_tests"
    
    # Path: results-analysis
    execute_in_path "results_analysis" \
        "analyze_performance_results"
    
    exit_path "performance_testing"
    log_info "Performance testing completed successfully" "performance_testing"
}

# Path: load-testing-execution
run_load_tests() {
    log_info "Running load tests" "load_testing"
    
    local load_scenarios=(
        "baseline:10:30s"
        "moderate:50:60s"
        "heavy:100:120s"
        "peak:200:180s"
    )
    
    for scenario in "${load_scenarios[@]}"; do
        IFS=':' read -r name users duration <<< "$scenario"
        
        log_info "Running load test: $name ($users users, $duration)" "load_testing"
        
        # K6 load test
        k6 run \
            --vus "$users" \
            --duration "$duration" \
            --out json="${RESULTS_DIR}/load-test-${name}.json" \
            "${SCRIPT_DIR}/scenarios/load-test.js" \
            || log_error "Load test failed: $name" "load_testing"
        
        # Artillery load test (alternative)
        artillery run \
            --config "${SCRIPT_DIR}/config/artillery-${name}.yml" \
            --output "${RESULTS_DIR}/artillery-${name}.json" \
            "${SCRIPT_DIR}/scenarios/artillery-load.yml" \
            || log_error "Artillery load test failed: $name" "load_testing"
    done
    
    log_info "Load testing completed" "load_testing"
}

# Path: stress-testing-execution
run_stress_tests() {
    log_info "Running stress tests" "stress_testing"
    
    # Gradual stress test
    k6 run \
        --stages "2m:100,5m:100,2m:200,5m:200,2m:300,5m:300,2m:400,5m:400,10m:0" \
        --out json="${RESULTS_DIR}/stress-test-gradual.json" \
        "${SCRIPT_DIR}/scenarios/stress-test.js" \
        || log_error "Gradual stress test failed" "stress_testing"
    
    # Resource exhaustion test
    k6 run \
        --vus 1000 \
        --duration "10m" \
        --out json="${RESULTS_DIR}/stress-test-exhaustion.json" \
        "${SCRIPT_DIR}/scenarios/resource-exhaustion.js" \
        || log_error "Resource exhaustion test failed" "stress_testing"
    
    log_info "Stress testing completed" "stress_testing"
}

# Path: security-testing-execution
run_security_tests() {
    log_info "Running security tests" "security_testing"
    
    # OWASP ZAP security scan
    if command -v docker >/dev/null 2>&1; then
        docker run --rm \
            -v "${RESULTS_DIR}:/zap/wrk" \
            -t owasp/zap2docker-stable zap-baseline.py \
            -t "${APP_URL:-http://localhost:3000}" \
            -J "security-baseline-report.json" \
            -r "security-baseline-report.html" \
            || log_warning "ZAP baseline scan completed with warnings" "security_testing"
    fi
    
    # Snyk vulnerability scan
    if command -v snyk >/dev/null 2>&1; then
        snyk test --json > "${RESULTS_DIR}/snyk-vulnerabilities.json" \
            || log_warning "Snyk scan found vulnerabilities" "security_testing"
    fi
    
    # Retire.js JavaScript vulnerability scan
    if command -v retire >/dev/null 2>&1; then
        retire --js --outputformat json \
            --outputpath "${RESULTS_DIR}/retire-js-scan.json" \
            "${PROJECT_ROOT}" \
            || log_warning "Retire.js found potential issues" "security_testing"
    fi
    
    log_info "Security testing completed" "security_testing"
}

# Path: main-execution
main() {
    local start_time=$(date +%s.%N)
    
    log_info "Starting performance and security testing suite" "main"
    
    # Check prerequisites
    check_testing_tools || {
        log_fatal "Required testing tools are not available" "main"
    }
    
    # Ensure test environment is running
    ensure_test_environment || {
        log_fatal "Could not start test environment" "main"
    }
    
    # Run tests
    run_performance_tests
    run_security_tests
    
    # Generate comprehensive report
    generate_comprehensive_report
    
    local end_time=$(date +%s.%N)
    local total_time=$(echo "$end_time - $start_time" | bc -l)
    
    log_performance_metric "full_test_suite_time" "$total_time" "seconds" "testing"
    log_info "Testing suite completed successfully in ${total_time}s" "main"
}

# Execute main function if script is run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
```

## Integration with Other Instructions

This testing instruction file works in conjunction with:
- **space.instructions.md**: Foundational path-based principles and container-first development
- **project.instructions.md**: AI-seed specific requirements and testing standards
- **python.instructions.md**: Python-specific testing patterns and pytest integration
- **javascript.instructions.md**: JavaScript/Node.js testing frameworks and Jest configuration
- **bash.instructions.md**: Shell script testing and automation requirements
- **docs.instructions.md**: Test documentation and reporting standards
- **ci-cd.instructions.md**: Automated testing integration and pipeline requirements

## Future Evolution

### Advanced Testing Features
- **AI-Driven Test Maintenance**: Automatic test updates based on code changes
- **Predictive Test Selection**: AI-powered test prioritization based on change impact
- **Self-Healing Tests**: Automatic test repair when application interfaces change
- **Intelligent Test Data Generation**: AI-generated realistic test data and scenarios

### Quality Assurance Automation
- **Continuous Quality Monitoring**: Real-time quality metrics collection and analysis
- **Automated Performance Regression Detection**: AI-powered performance change detection
- **Security Testing Integration**: Continuous security testing in development workflows
- **Multi-Environment Test Orchestration**: Automated testing across different environments and configurations
