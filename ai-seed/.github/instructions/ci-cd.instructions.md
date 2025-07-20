---
file: ci-cd.instructions.md
description: Comprehensive CI/CD pipeline instructions for automated build, test, and deployment workflows
author: AI-Seed Team <team@ai-seed.org>
created: 2025-07-19
lastModified: 2025-07-19
version: 1.0.0
relatedIssues: []
relatedEvolutions: []
dependencies:
  - space.instructions.md: Foundation principles and path-based development
  - project.instructions.md: Project-specific context and requirements
  - test.instructions.md: Testing standards and automation requirements
  - docs.instructions.md: Documentation generation and deployment
containerRequirements:
  baseImage: 
    - ubuntu:22.04
    - node:18-alpine
    - python:3.11-slim
  exposedPorts: null
  volumes:
    - /workspace:rw
    - /cache:rw
    - /artifacts:rw
  environment:
    CI: true
    NODE_ENV: production
    PYTHON_ENV: production
  resources:
    cpu: 2.0-8.0
    memory: 4GiB-16GiB
  healthCheck: null
paths:
  ci-pipeline-path: Trigger → checkout → build → test → package → deploy
  cd-pipeline-path: Package → staging → approval → production → monitoring
  quality-gate-path: Static analysis → security scan → performance test → approval
changelog:
  - date: 2025-07-19
    change: Initial creation
    author: AI-Seed Team
usage: Reference for all CI/CD pipeline configurations, automation, and deployment strategies
notes: Emphasizes path-based deployments, container-first pipelines, and AI-assisted quality gates
---

# CI/CD Instructions

These instructions provide comprehensive guidance for implementing robust, path-aware CI/CD pipelines within the AI-seed ecosystem, emphasizing container-first deployments, automated quality gates, and AI-assisted pipeline optimization.

## CI/CD Philosophy and Strategy

### Path-Based Pipeline Architecture

CI/CD pipelines should follow natural development and deployment paths, ensuring reliable, traceable, and efficient software delivery while maintaining quality and security standards.

#### Core Pipeline Paths
- **Integration Path**: Code commit → build → test → quality gates → integration
- **Deployment Path**: Package → staging → testing → approval → production
- **Monitoring Path**: Deployment → health checks → metrics → alerts → feedback
- **Rollback Path**: Issue detection → automated rollback → investigation → fix → redeploy
- **Security Path**: Code scan → dependency check → compliance → approval
- **Performance Path**: Build → performance test → optimization → validation

### Pipeline Organization Structure

```
.github/
├── workflows/                   # GitHub Actions workflows
│   ├── ci.yml                  # Continuous integration pipeline
│   ├── cd-staging.yml          # Continuous deployment to staging
│   ├── cd-production.yml       # Production deployment pipeline
│   ├── security.yml            # Security scanning and compliance
│   ├── performance.yml         # Performance testing pipeline
│   ├── documentation.yml       # Documentation generation and deployment
│   └── maintenance.yml         # Maintenance and cleanup tasks
├── actions/                     # Custom GitHub Actions
│   ├── setup-environment/      # Environment setup action
│   ├── build-container/        # Container build action
│   ├── run-tests/              # Test execution action
│   ├── security-scan/          # Security scanning action
│   └── deploy-application/     # Deployment action
└── templates/                   # Pipeline templates
    ├── ci-template.yml         # CI pipeline template
    ├── cd-template.yml         # CD pipeline template
    └── security-template.yml   # Security pipeline template

ci/
├── config/                      # CI/CD configuration files
│   ├── docker/                 # Docker configurations for CI/CD
│   ├── terraform/              # Infrastructure as Code
│   ├── ansible/                # Configuration management
│   └── scripts/                # CI/CD utility scripts
├── environments/               # Environment-specific configurations
│   ├── development/            # Development environment config
│   ├── staging/                # Staging environment config
│   ├── production/             # Production environment config
│   └── testing/                # Test environment config
├── pipelines/                  # Pipeline definitions
│   ├── jenkins/                # Jenkins pipeline files
│   ├── azure-devops/          # Azure DevOps pipeline files
│   ├── gitlab-ci/             # GitLab CI configuration
│   └── circleci/              # CircleCI configuration
└── monitoring/                 # Pipeline monitoring and metrics
    ├── dashboards/             # Monitoring dashboards
    ├── alerts/                 # Alert configurations
    └── metrics/                # Custom metrics definitions
```

## Container-First CI/CD Pipeline

### GitHub Actions Workflows

#### Comprehensive CI Pipeline
```yaml
# Path: continuous-integration-pipeline
# File: .github/workflows/ci.yml

name: Continuous Integration

on:
  push:
    branches: [ main, develop, 'feature/*', 'hotfix/*' ]
  pull_request:
    branches: [ main, develop ]
  workflow_dispatch:
    inputs:
      environment:
        description: 'Target environment'
        required: true
        default: 'development'
        type: choice
        options:
          - development
          - staging

env:
  NODE_VERSION: '18'
  PYTHON_VERSION: '3.11'
  DOCKER_BUILDKIT: 1
  COMPOSE_DOCKER_CLI_BUILD: 1

jobs:
  # Path: pipeline-initialization
  setup:
    name: Setup Pipeline Environment
    runs-on: ubuntu-latest
    outputs:
      cache-key: ${{ steps.cache-key.outputs.key }}
      should-run-tests: ${{ steps.changes.outputs.should-run-tests }}
      should-build: ${{ steps.changes.outputs.should-build }}
      environment: ${{ steps.env.outputs.environment }}
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for proper change detection

      - name: Detect changes
        id: changes
        uses: dorny/paths-filter@v2
        with:
          filters: |
            should-run-tests:
              - 'src/**'
              - 'tests/**'
              - 'package*.json'
              - 'requirements*.txt'
              - 'Dockerfile*'
              - 'docker-compose*.yml'
            should-build:
              - 'src/**'
              - 'package*.json'
              - 'requirements*.txt'
              - 'Dockerfile*'

      - name: Determine environment
        id: env
        run: |
          if [[ "${{ github.ref }}" == "refs/heads/main" ]]; then
            echo "environment=production" >> $GITHUB_OUTPUT
          elif [[ "${{ github.ref }}" == "refs/heads/develop" ]]; then
            echo "environment=staging" >> $GITHUB_OUTPUT
          else
            echo "environment=development" >> $GITHUB_OUTPUT
          fi

      - name: Generate cache key
        id: cache-key
        run: |
          echo "key=deps-${{ runner.os }}-node${{ env.NODE_VERSION }}-python${{ env.PYTHON_VERSION }}-${{ hashFiles('package-lock.json', 'requirements*.txt') }}" >> $GITHUB_OUTPUT

  # Path: dependency-management
  dependencies:
    name: Install Dependencies
    runs-on: ubuntu-latest
    needs: setup
    if: needs.setup.outputs.should-run-tests == 'true' || needs.setup.outputs.should-build == 'true'
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Cache dependencies
        uses: actions/cache@v3
        with:
          path: |
            ~/.npm
            ~/.cache/pip
            node_modules
            .venv
          key: ${{ needs.setup.outputs.cache-key }}
          restore-keys: |
            deps-${{ runner.os }}-node${{ env.NODE_VERSION }}-python${{ env.PYTHON_VERSION }}-

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Install Node.js dependencies
        run: |
          npm ci --prefer-offline --no-audit
          echo "Node.js dependencies installed successfully"

      - name: Install Python dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          if [ -f requirements-dev.txt ]; then
            pip install -r requirements-dev.txt
          fi
          echo "Python dependencies installed successfully"

  # Path: code-quality-analysis
  code-quality:
    name: Code Quality Analysis
    runs-on: ubuntu-latest
    needs: [setup, dependencies]
    if: needs.setup.outputs.should-run-tests == 'true'
    strategy:
      matrix:
        tool: [eslint, prettier, pylint, black, mypy]
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Restore dependencies
        uses: actions/cache@v3
        with:
          path: |
            ~/.npm
            ~/.cache/pip
            node_modules
            .venv
          key: ${{ needs.setup.outputs.cache-key }}

      - name: Setup environments
        run: |
          # Setup Node.js environment
          export PATH="./node_modules/.bin:$PATH"
          
          # Setup Python environment
          if [ -d ".venv" ]; then
            source .venv/bin/activate
          fi

      - name: Run ESLint
        if: matrix.tool == 'eslint'
        run: |
          npm run lint:js
          echo "ESLint analysis completed"

      - name: Run Prettier
        if: matrix.tool == 'prettier'
        run: |
          npm run format:check
          echo "Prettier format check completed"

      - name: Run Pylint
        if: matrix.tool == 'pylint'
        run: |
          pylint src/ --output-format=github
          echo "Pylint analysis completed"

      - name: Run Black
        if: matrix.tool == 'black'
        run: |
          black --check src/
          echo "Black format check completed"

      - name: Run MyPy
        if: matrix.tool == 'mypy'
        run: |
          mypy src/ --strict
          echo "MyPy type checking completed"

      - name: Upload quality results
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: code-quality-${{ matrix.tool }}
          path: |
            reports/lint/
            reports/format/
            reports/type-check/

  # Path: security-scanning
  security:
    name: Security Scanning
    runs-on: ubuntu-latest
    needs: [setup, dependencies]
    if: needs.setup.outputs.should-run-tests == 'true'
    permissions:
      security-events: write
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Restore dependencies
        uses: actions/cache@v3
        with:
          path: |
            ~/.npm
            ~/.cache/pip
            node_modules
            .venv
          key: ${{ needs.setup.outputs.cache-key }}

      - name: Run npm audit
        run: |
          npm audit --audit-level moderate --output json > reports/npm-audit.json || true
          echo "NPM security audit completed"

      - name: Run Snyk test
        uses: snyk/actions/node@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          args: --severity-threshold=high --json > reports/snyk-report.json

      - name: Run Bandit security scan
        run: |
          bandit -r src/ -f json -o reports/bandit-report.json || true
          echo "Bandit security scan completed"

      - name: Run Safety check
        run: |
          safety check --json --output reports/safety-report.json || true
          echo "Safety dependency check completed"

      - name: Initialize CodeQL
        uses: github/codeql-action/init@v2
        with:
          languages: javascript, python

      - name: Autobuild
        uses: github/codeql-action/autobuild@v2

      - name: Perform CodeQL Analysis
        uses: github/codeql-action/analyze@v2

      - name: Upload security results
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: security-reports
          path: reports/

  # Path: unit-testing
  unit-tests:
    name: Unit Tests
    runs-on: ubuntu-latest
    needs: [setup, dependencies]
    if: needs.setup.outputs.should-run-tests == 'true'
    strategy:
      matrix:
        test-suite: [javascript, python]
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Restore dependencies
        uses: actions/cache@v3
        with:
          path: |
            ~/.npm
            ~/.cache/pip
            node_modules
            .venv
          key: ${{ needs.setup.outputs.cache-key }}

      - name: Run JavaScript tests
        if: matrix.test-suite == 'javascript'
        run: |
          npm run test:unit:coverage
          echo "JavaScript unit tests completed"

      - name: Run Python tests
        if: matrix.test-suite == 'python'
        run: |
          python -m pytest tests/unit/python/ \
            --cov=src \
            --cov-report=xml \
            --cov-report=html \
            --junitxml=reports/pytest-results.xml
          echo "Python unit tests completed"

      - name: Upload test results
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: test-results-${{ matrix.test-suite }}
          path: |
            reports/
            coverage/

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage/lcov.info,./coverage.xml
          flags: ${{ matrix.test-suite }}
          name: codecov-${{ matrix.test-suite }}

  # Path: integration-testing
  integration-tests:
    name: Integration Tests
    runs-on: ubuntu-latest
    needs: [setup, dependencies]
    if: needs.setup.outputs.should-run-tests == 'true'
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: test_db
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: test_password
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 3s
          --health-retries 5
        ports:
          - 6379:6379

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Restore dependencies
        uses: actions/cache@v3
        with:
          path: |
            ~/.npm
            ~/.cache/pip
            node_modules
            .venv
          key: ${{ needs.setup.outputs.cache-key }}

      - name: Setup test environment
        env:
          DATABASE_URL: postgresql://test_user:test_password@localhost:5432/test_db
          REDIS_URL: redis://localhost:6379
        run: |
          npm run db:migrate:test
          npm run db:seed:test
          echo "Test environment setup completed"

      - name: Run integration tests
        env:
          DATABASE_URL: postgresql://test_user:test_password@localhost:5432/test_db
          REDIS_URL: redis://localhost:6379
          NODE_ENV: test
        run: |
          npm run test:integration
          echo "Integration tests completed"

      - name: Upload integration test results
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: integration-test-results
          path: reports/integration/

  # Path: container-building
  build:
    name: Build Container Images
    runs-on: ubuntu-latest
    needs: [setup, code-quality, security, unit-tests]
    if: needs.setup.outputs.should-build == 'true'
    strategy:
      matrix:
        component: [api, worker, frontend]
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ghcr.io/${{ github.repository }}/${{ matrix.component }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=sha,prefix={{branch}}-
            type=raw,value=latest,enable={{is_default_branch}}

      - name: Build and push container image
        uses: docker/build-push-action@v5
        with:
          context: .
          file: ./docker/${{ matrix.component }}/Dockerfile
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          build-args: |
            BUILDKIT_INLINE_CACHE=1
            COMPONENT=${{ matrix.component }}
            VERSION=${{ github.sha }}

      - name: Generate SBOM
        uses: anchore/sbom-action@v0
        with:
          image: ghcr.io/${{ github.repository }}/${{ matrix.component }}:${{ github.sha }}
          format: spdx-json
          output-file: sbom-${{ matrix.component }}.json

      - name: Upload SBOM
        uses: actions/upload-artifact@v3
        with:
          name: sbom-${{ matrix.component }}
          path: sbom-${{ matrix.component }}.json

  # Path: end-to-end-testing
  e2e-tests:
    name: End-to-End Tests
    runs-on: ubuntu-latest
    needs: [build, integration-tests]
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup test environment
        run: |
          docker-compose -f docker-compose.test.yml up -d
          
          # Wait for services to be ready
          timeout 300 bash -c 'until docker-compose -f docker-compose.test.yml exec -T app curl -f http://localhost:3000/health; do sleep 10; done'
          echo "Test environment is ready"

      - name: Run E2E tests
        run: |
          npm run test:e2e
          echo "End-to-end tests completed"

      - name: Cleanup test environment
        if: always()
        run: |
          docker-compose -f docker-compose.test.yml down -v
          docker system prune -f

      - name: Upload E2E test results
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: e2e-test-results
          path: |
            reports/e2e/
            screenshots/
            videos/

  # Path: pipeline-results
  results:
    name: Pipeline Results
    runs-on: ubuntu-latest
    needs: [setup, code-quality, security, unit-tests, integration-tests, build, e2e-tests]
    if: always()
    steps:
      - name: Download all artifacts
        uses: actions/download-artifact@v3

      - name: Generate pipeline report
        run: |
          echo "# CI Pipeline Report" > pipeline-report.md
          echo "**Date:** $(date)" >> pipeline-report.md
          echo "**Commit:** ${{ github.sha }}" >> pipeline-report.md
          echo "**Branch:** ${{ github.ref_name }}" >> pipeline-report.md
          echo "" >> pipeline-report.md
          
          echo "## Job Results" >> pipeline-report.md
          echo "- Code Quality: ${{ needs.code-quality.result }}" >> pipeline-report.md
          echo "- Security: ${{ needs.security.result }}" >> pipeline-report.md
          echo "- Unit Tests: ${{ needs.unit-tests.result }}" >> pipeline-report.md
          echo "- Integration Tests: ${{ needs.integration-tests.result }}" >> pipeline-report.md
          echo "- Build: ${{ needs.build.result }}" >> pipeline-report.md
          echo "- E2E Tests: ${{ needs.e2e-tests.result }}" >> pipeline-report.md

      - name: Upload pipeline report
        uses: actions/upload-artifact@v3
        with:
          name: pipeline-report
          path: pipeline-report.md

      - name: Comment on PR
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const report = fs.readFileSync('pipeline-report.md', 'utf8');
            
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: report
            });
```

#### Continuous Deployment Pipeline
```yaml
# Path: continuous-deployment-pipeline
# File: .github/workflows/cd-production.yml

name: Production Deployment

on:
  workflow_run:
    workflows: ["Continuous Integration"]
    types:
      - completed
    branches: [main]
  workflow_dispatch:
    inputs:
      version:
        description: 'Version to deploy'
        required: true
        type: string
      environment:
        description: 'Target environment'
        required: true
        default: 'production'
        type: choice
        options:
          - staging
          - production

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  # Path: deployment-preparation
  prepare:
    name: Prepare Deployment
    runs-on: ubuntu-latest
    if: github.event.workflow_run.conclusion == 'success' || github.event_name == 'workflow_dispatch'
    outputs:
      version: ${{ steps.version.outputs.version }}
      environment: ${{ steps.env.outputs.environment }}
      should-deploy: ${{ steps.check.outputs.should-deploy }}
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Determine version
        id: version
        run: |
          if [[ "${{ github.event_name }}" == "workflow_dispatch" ]]; then
            echo "version=${{ github.event.inputs.version }}" >> $GITHUB_OUTPUT
          else
            echo "version=${{ github.sha }}" >> $GITHUB_OUTPUT
          fi

      - name: Determine environment
        id: env
        run: |
          if [[ "${{ github.event_name }}" == "workflow_dispatch" ]]; then
            echo "environment=${{ github.event.inputs.environment }}" >> $GITHUB_OUTPUT
          else
            echo "environment=production" >> $GITHUB_OUTPUT
          fi

      - name: Check deployment conditions
        id: check
        run: |
          # Check if deployment should proceed based on conditions
          # (e.g., business hours, feature flags, etc.)
          echo "should-deploy=true" >> $GITHUB_OUTPUT

  # Path: pre-deployment-validation
  pre-deployment:
    name: Pre-deployment Validation
    runs-on: ubuntu-latest
    needs: prepare
    if: needs.prepare.outputs.should-deploy == 'true'
    environment:
      name: ${{ needs.prepare.outputs.environment }}-validation
      url: https://${{ needs.prepare.outputs.environment }}.example.com
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Validate container images
        run: |
          # Verify that all required container images exist
          docker manifest inspect ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/api:${{ needs.prepare.outputs.version }}
          docker manifest inspect ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/worker:${{ needs.prepare.outputs.version }}
          docker manifest inspect ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/frontend:${{ needs.prepare.outputs.version }}
          echo "Container images validated"

      - name: Run deployment readiness checks
        run: |
          # Check infrastructure readiness
          curl -f https://${{ needs.prepare.outputs.environment }}.example.com/health
          
          # Check database connectivity
          # Check external service dependencies
          # Verify configuration
          echo "Pre-deployment validation completed"

      - name: Security scan of deployment artifacts
        run: |
          # Scan container images for vulnerabilities
          docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
            -v $(pwd):/workspace \
            aquasec/trivy image ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/api:${{ needs.prepare.outputs.version }}
          echo "Security scan completed"

  # Path: staging-deployment
  deploy-staging:
    name: Deploy to Staging
    runs-on: ubuntu-latest
    needs: [prepare, pre-deployment]
    if: needs.prepare.outputs.environment == 'production'
    environment:
      name: staging
      url: https://staging.example.com
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup kubectl
        uses: azure/setup-kubectl@v3
        with:
          version: 'v1.28.0'

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      - name: Update kubeconfig
        run: |
          aws eks update-kubeconfig --name staging-cluster --region us-east-1

      - name: Deploy to staging
        run: |
          # Update Kubernetes manifests with new image tags
          sed -i "s|image: .*api:.*|image: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/api:${{ needs.prepare.outputs.version }}|g" k8s/staging/api-deployment.yml
          sed -i "s|image: .*worker:.*|image: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/worker:${{ needs.prepare.outputs.version }}|g" k8s/staging/worker-deployment.yml
          sed -i "s|image: .*frontend:.*|image: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/frontend:${{ needs.prepare.outputs.version }}|g" k8s/staging/frontend-deployment.yml
          
          # Apply Kubernetes manifests
          kubectl apply -f k8s/staging/
          
          # Wait for rollout to complete
          kubectl rollout status deployment/api -n staging
          kubectl rollout status deployment/worker -n staging
          kubectl rollout status deployment/frontend -n staging
          
          echo "Staging deployment completed"

      - name: Run staging tests
        run: |
          # Run smoke tests against staging environment
          npm run test:staging
          echo "Staging tests completed"

  # Path: production-deployment
  deploy-production:
    name: Deploy to Production
    runs-on: ubuntu-latest
    needs: [prepare, pre-deployment, deploy-staging]
    environment:
      name: production
      url: https://production.example.com
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup kubectl
        uses: azure/setup-kubectl@v3
        with:
          version: 'v1.28.0'

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      - name: Update kubeconfig
        run: |
          aws eks update-kubeconfig --name production-cluster --region us-east-1

      - name: Create deployment backup
        run: |
          # Backup current deployment configuration
          kubectl get deployment api -n production -o yaml > backup/api-deployment-$(date +%Y%m%d-%H%M%S).yml
          kubectl get deployment worker -n production -o yaml > backup/worker-deployment-$(date +%Y%m%d-%H%M%S).yml
          kubectl get deployment frontend -n production -o yaml > backup/frontend-deployment-$(date +%Y%m%d-%H%M%S).yml
          echo "Deployment backup created"

      - name: Deploy to production
        run: |
          # Blue-green deployment strategy
          
          # Update deployment manifests
          sed -i "s|image: .*api:.*|image: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/api:${{ needs.prepare.outputs.version }}|g" k8s/production/api-deployment.yml
          sed -i "s|image: .*worker:.*|image: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/worker:${{ needs.prepare.outputs.version }}|g" k8s/production/worker-deployment.yml
          sed -i "s|image: .*frontend:.*|image: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/frontend:${{ needs.prepare.outputs.version }}|g" k8s/production/frontend-deployment.yml
          
          # Apply manifests with rolling update
          kubectl apply -f k8s/production/
          
          # Wait for rollout to complete
          kubectl rollout status deployment/api -n production --timeout=600s
          kubectl rollout status deployment/worker -n production --timeout=600s
          kubectl rollout status deployment/frontend -n production --timeout=600s
          
          echo "Production deployment completed"

      - name: Run production health checks
        run: |
          # Comprehensive health checks
          curl -f https://production.example.com/health
          curl -f https://production.example.com/api/health
          
          # Run production smoke tests
          npm run test:production:smoke
          
          echo "Production health checks passed"

      - name: Update monitoring and alerting
        run: |
          # Update monitoring dashboards
          # Configure alerts for new deployment
          # Update service discovery
          echo "Monitoring and alerting updated"

  # Path: post-deployment-validation
  post-deployment:
    name: Post-deployment Validation
    runs-on: ubuntu-latest
    needs: [prepare, deploy-production]
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Run comprehensive tests
        run: |
          # Run full test suite against production
          npm run test:production:full
          echo "Comprehensive tests completed"

      - name: Performance baseline validation
        run: |
          # Run performance tests to establish baseline
          npm run test:performance:production
          echo "Performance validation completed"

      - name: Security validation
        run: |
          # Run security tests against production
          npm run test:security:production
          echo "Security validation completed"

      - name: Generate deployment report
        run: |
          echo "# Production Deployment Report" > deployment-report.md
          echo "**Version:** ${{ needs.prepare.outputs.version }}" >> deployment-report.md
          echo "**Date:** $(date)" >> deployment-report.md
          echo "**Environment:** ${{ needs.prepare.outputs.environment }}" >> deployment-report.md
          echo "" >> deployment-report.md
          
          # Add metrics and status information
          echo "## Deployment Metrics" >> deployment-report.md
          echo "- Deployment Duration: $(($(date +%s) - ${{ github.event.created_at }})) seconds" >> deployment-report.md
          echo "- Health Status: ✅ Healthy" >> deployment-report.md
          echo "- Performance: ✅ Within baseline" >> deployment-report.md
          echo "- Security: ✅ No issues detected" >> deployment-report.md

      - name: Upload deployment report
        uses: actions/upload-artifact@v3
        with:
          name: deployment-report
          path: deployment-report.md

      - name: Notify teams
        run: |
          # Send notifications to relevant teams
          # Update status pages
          # Log deployment in tracking systems
          echo "Teams notified of successful deployment"
```

### Infrastructure as Code Integration

#### Terraform Configuration
```hcl
# Path: infrastructure-as-code
# File: ci/config/terraform/main.tf

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }
  }

  backend "s3" {
    bucket         = "ai-seed-terraform-state"
    key            = "infrastructure/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-locks"
  }
}

provider "aws" {
  region = var.aws_region
}

# Local values for common tags and naming
locals {
  common_tags = {
    Project     = "ai-seed"
    Environment = var.environment
    ManagedBy   = "terraform"
    CreatedBy   = "ci-cd-pipeline"
    Path        = "infrastructure"
  }

  name_prefix = "${var.project_name}-${var.environment}"
}

# Path: vpc-infrastructure
module "vpc" {
  source = "./modules/vpc"

  name_prefix = local.name_prefix
  environment = var.environment
  
  vpc_cidr             = var.vpc_cidr
  availability_zones   = var.availability_zones
  private_subnet_cidrs = var.private_subnet_cidrs
  public_subnet_cidrs  = var.public_subnet_cidrs
  
  enable_nat_gateway = true
  enable_vpn_gateway = false
  
  tags = local.common_tags
}

# Path: eks-cluster-infrastructure
module "eks" {
  source = "./modules/eks"

  cluster_name    = "${local.name_prefix}-cluster"
  cluster_version = var.kubernetes_version
  
  vpc_id              = module.vpc.vpc_id
  subnet_ids          = module.vpc.private_subnet_ids
  control_plane_subnet_ids = module.vpc.public_subnet_ids
  
  node_groups = {
    main = {
      instance_types = ["t3.medium", "t3.large"]
      min_size       = 2
      max_size       = 10
      desired_size   = 3
      
      labels = {
        Environment = var.environment
        NodeGroup   = "main"
      }
      
      taints = []
    }
    
    compute = {
      instance_types = ["c5.large", "c5.xlarge"]
      min_size       = 0
      max_size       = 20
      desired_size   = 0
      
      labels = {
        Environment = var.environment
        NodeGroup   = "compute"
        Workload    = "compute-intensive"
      }
      
      taints = [
        {
          key    = "workload"
          value  = "compute"
          effect = "NO_SCHEDULE"
        }
      ]
    }
  }
  
  tags = local.common_tags
}

# Path: database-infrastructure
module "rds" {
  source = "./modules/rds"

  identifier = "${local.name_prefix}-database"
  
  engine               = "postgres"
  engine_version       = "15.4"
  instance_class       = var.db_instance_class
  allocated_storage    = var.db_allocated_storage
  max_allocated_storage = var.db_max_allocated_storage
  
  database_name = var.database_name
  username      = var.database_username
  password      = random_password.database_password.result
  
  vpc_security_group_ids = [module.security_groups.database_sg_id]
  db_subnet_group_name   = module.vpc.database_subnet_group_name
  
  backup_retention_period = var.environment == "production" ? 30 : 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  enabled_cloudwatch_logs_exports = ["postgresql"]
  monitoring_interval            = 60
  performance_insights_enabled   = true
  
  deletion_protection = var.environment == "production"
  skip_final_snapshot = var.environment != "production"
  
  tags = local.common_tags
}

# Path: cache-infrastructure
module "redis" {
  source = "./modules/redis"

  cluster_id = "${local.name_prefix}-cache"
  
  node_type               = var.redis_node_type
  num_cache_nodes         = var.redis_num_nodes
  parameter_group_name    = "default.redis7"
  port                    = 6379
  
  subnet_group_name       = module.vpc.cache_subnet_group_name
  security_group_ids      = [module.security_groups.cache_sg_id]
  
  maintenance_window      = "sun:05:00-sun:06:00"
  snapshot_retention_limit = var.environment == "production" ? 7 : 1
  snapshot_window         = "06:00-07:00"
  
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  
  tags = local.common_tags
}

# Path: monitoring-infrastructure
module "monitoring" {
  source = "./modules/monitoring"

  cluster_name = module.eks.cluster_name
  environment  = var.environment
  
  # CloudWatch Log Groups
  log_groups = {
    application = {
      name              = "/aws/eks/${module.eks.cluster_name}/application"
      retention_in_days = var.environment == "production" ? 90 : 30
    }
    
    performance = {
      name              = "/aws/eks/${module.eks.cluster_name}/performance"
      retention_in_days = var.environment == "production" ? 30 : 7
    }
    
    security = {
      name              = "/aws/eks/${module.eks.cluster_name}/security"
      retention_in_days = var.environment == "production" ? 365 : 90
    }
  }
  
  # Prometheus and Grafana
  enable_prometheus = true
  enable_grafana    = true
  
  # Alertmanager configuration
  alertmanager_config = {
    global = {
      smtp_smarthost = var.smtp_server
      smtp_from      = var.alert_email_from
    }
    
    route = {
      group_by        = ["alertname", "cluster", "service"]
      group_wait      = "10s"
      group_interval  = "10s"
      repeat_interval = "1h"
      receiver        = "default"
    }
    
    receivers = [
      {
        name = "default"
        email_configs = [
          {
            to      = var.alert_email_to
            subject = "{{ .GroupLabels.alertname }} - {{ .GroupLabels.cluster }}"
          }
        ]
      }
    ]
  }
  
  tags = local.common_tags
}

# Security Groups Module
module "security_groups" {
  source = "./modules/security-groups"

  vpc_id      = module.vpc.vpc_id
  name_prefix = local.name_prefix
  
  tags = local.common_tags
}

# Random password for database
resource "random_password" "database_password" {
  length  = 32
  special = true
}

# Store database password in AWS Secrets Manager
resource "aws_secretsmanager_secret" "database_password" {
  name                    = "${local.name_prefix}-database-password"
  description             = "Database password for ${var.environment} environment"
  recovery_window_in_days = var.environment == "production" ? 30 : 0
  
  tags = local.common_tags
}

resource "aws_secretsmanager_secret_version" "database_password" {
  secret_id     = aws_secretsmanager_secret.database_password.id
  secret_string = jsonencode({
    username = var.database_username
    password = random_password.database_password.result
    engine   = "postgres"
    host     = module.rds.db_instance_endpoint
    port     = 5432
    dbname   = var.database_name
  })
}

# Outputs
output "cluster_endpoint" {
  description = "EKS cluster endpoint"
  value       = module.eks.cluster_endpoint
  sensitive   = true
}

output "cluster_name" {
  description = "EKS cluster name"
  value       = module.eks.cluster_name
}

output "database_endpoint" {
  description = "RDS database endpoint"
  value       = module.rds.db_instance_endpoint
  sensitive   = true
}

output "redis_endpoint" {
  description = "Redis cache endpoint"
  value       = module.redis.cache_cluster_address
  sensitive   = true
}

output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}
```

### Monitoring and Observability

#### Comprehensive Monitoring Stack
```yaml
# Path: monitoring-configuration
# File: ci/monitoring/prometheus-config.yml

global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "/etc/prometheus/rules/*.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  # Kubernetes API Server
  - job_name: 'kubernetes-apiservers'
    kubernetes_sd_configs:
      - role: endpoints
    scheme: https
    tls_config:
      ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
    bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token
    relabel_configs:
      - source_labels: [__meta_kubernetes_namespace, __meta_kubernetes_service_name, __meta_kubernetes_endpoint_port_name]
        action: keep
        regex: default;kubernetes;https

  # Kubernetes Nodes
  - job_name: 'kubernetes-nodes'
    kubernetes_sd_configs:
      - role: node
    scheme: https
    tls_config:
      ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
    bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token
    relabel_configs:
      - action: labelmap
        regex: __meta_kubernetes_node_label_(.+)

  # Kubernetes Pods
  - job_name: 'kubernetes-pods'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
      - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
        action: replace
        regex: ([^:]+)(?::\d+)?;(\d+)
        replacement: $1:$2
        target_label: __address__
      - action: labelmap
        regex: __meta_kubernetes_pod_label_(.+)
      - source_labels: [__meta_kubernetes_namespace]
        action: replace
        target_label: kubernetes_namespace
      - source_labels: [__meta_kubernetes_pod_name]
        action: replace
        target_label: kubernetes_pod_name

  # Application Metrics
  - job_name: 'ai-seed-api'
    static_configs:
      - targets: ['ai-seed-api:3000']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'ai-seed-worker'
    static_configs:
      - targets: ['ai-seed-worker:3001']
    metrics_path: '/metrics'
    scrape_interval: 10s

  # Database Metrics
  - job_name: 'postgres-exporter'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'redis-exporter'
    static_configs:
      - targets: ['redis-exporter:9121']

  # Path-specific metrics
  - job_name: 'path-metrics'
    static_configs:
      - targets: ['ai-seed-api:3000']
    metrics_path: '/metrics/paths'
    scrape_interval: 30s
```

### Custom Actions and Scripts

#### Path-Aware Deployment Action
```typescript
// Path: custom-deployment-action
// File: .github/actions/deploy-application/action.ts

import * as core from '@actions/core';
import * as exec from '@actions/exec';
import * as io from '@actions/io';
import { PathTracker } from '../../../src/utils/path-tracker';

/**
 * Custom GitHub Action for path-aware application deployment
 */
class DeploymentAction {
    private pathTracker: PathTracker;
    private environment: string;
    private version: string;
    private namespace: string;

    constructor() {
        this.pathTracker = new PathTracker();
        this.environment = core.getInput('environment', { required: true });
        this.version = core.getInput('version', { required: true });
        this.namespace = core.getInput('namespace') || this.environment;
    }

    /**
     * Execute deployment with comprehensive path tracking
     */
    async run(): Promise<void> {
        try {
            await this.pathTracker.executeInPath('github_action_deployment', async () => {
                core.info(`Starting deployment to ${this.environment}`);
                
                // Path: pre-deployment-validation
                await this.pathTracker.executeInPath('pre_deployment_validation', 
                    () => this.validatePreDeployment());

                // Path: deployment-execution
                await this.pathTracker.executeInPath('deployment_execution', 
                    () => this.executeDeployment());

                // Path: post-deployment-validation
                await this.pathTracker.executeInPath('post_deployment_validation', 
                    () => this.validatePostDeployment());

                // Path: deployment-reporting
                await this.pathTracker.executeInPath('deployment_reporting', 
                    () => this.generateDeploymentReport());

                core.info('Deployment completed successfully');
            });
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : String(error);
            core.setFailed(`Deployment failed: ${errorMessage}`);
            throw error;
        }
    }

    /**
     * Validate pre-deployment conditions
     */
    private async validatePreDeployment(): Promise<void> {
        core.info('Validating pre-deployment conditions');

        // Check if kubectl is available
        await exec.exec('kubectl', ['version', '--client']);

        // Verify cluster connectivity
        await exec.exec('kubectl', ['cluster-info']);

        // Check namespace exists
        try {
            await exec.exec('kubectl', ['get', 'namespace', this.namespace]);
        } catch (error) {
            core.info(`Creating namespace: ${this.namespace}`);
            await exec.exec('kubectl', ['create', 'namespace', this.namespace]);
        }

        // Validate container images exist
        const images = await this.getContainerImages();
        for (const image of images) {
            await exec.exec('docker', ['manifest', 'inspect', image]);
            core.info(`Validated image: ${image}`);
        }

        core.info('Pre-deployment validation completed');
    }

    /**
     * Execute the actual deployment
     */
    private async executeDeployment(): Promise<void> {
        core.info(`Deploying version ${this.version} to ${this.environment}`);

        // Update deployment manifests
        await this.updateDeploymentManifests();

        // Apply Kubernetes manifests
        await exec.exec('kubectl', ['apply', '-f', 'k8s/', '-n', this.namespace]);

        // Wait for rollout to complete
        const deployments = await this.getDeploymentNames();
        for (const deployment of deployments) {
            core.info(`Waiting for rollout: ${deployment}`);
            await exec.exec('kubectl', [
                'rollout', 'status', 
                `deployment/${deployment}`, 
                '-n', this.namespace,
                '--timeout=600s'
            ]);
        }

        core.info('Deployment execution completed');
    }

    /**
     * Validate post-deployment conditions
     */
    private async validatePostDeployment(): Promise<void> {
        core.info('Validating post-deployment conditions');

        // Check pod health
        await exec.exec('kubectl', [
            'get', 'pods', 
            '-n', this.namespace,
            '-l', `version=${this.version}`
        ]);

        // Run health checks
        const healthEndpoint = core.getInput('health-endpoint') || '/health';
        const serviceUrl = await this.getServiceUrl();
        
        if (serviceUrl) {
            await exec.exec('curl', [
                '-f',
                '--max-time', '30',
                '--retry', '5',
                '--retry-delay', '10',
                `${serviceUrl}${healthEndpoint}`
            ]);
        }

        // Run smoke tests if configured
        const smokeTestCommand = core.getInput('smoke-test-command');
        if (smokeTestCommand) {
            await exec.exec('bash', ['-c', smokeTestCommand]);
        }

        core.info('Post-deployment validation completed');
    }

    /**
     * Generate comprehensive deployment report
     */
    private async generateDeploymentReport(): Promise<void> {
        const pathMetrics = this.pathTracker.getMetrics();
        const deploymentDuration = this.pathTracker.getPathDuration('github_action_deployment');

        const report = {
            deployment: {
                environment: this.environment,
                version: this.version,
                namespace: this.namespace,
                timestamp: new Date().toISOString(),
                duration: deploymentDuration
            },
            pathMetrics,
            validation: {
                preDeployment: 'success',
                deployment: 'success',
                postDeployment: 'success'
            }
        };

        // Set outputs
        core.setOutput('deployment-report', JSON.stringify(report));
        core.setOutput('deployment-duration', deploymentDuration.toString());
        core.setOutput('deployment-status', 'success');

        core.info('Deployment report generated');
    }

    /**
     * Get container images for validation
     */
    private async getContainerImages(): Promise<string[]> {
        const registry = core.getInput('registry') || 'ghcr.io';
        const repository = core.getInput('repository', { required: true });
        
        const components = ['api', 'worker', 'frontend'];
        return components.map(component => 
            `${registry}/${repository}/${component}:${this.version}`
        );
    }

    /**
     * Update deployment manifests with new version
     */
    private async updateDeploymentManifests(): Promise<void> {
        const images = await this.getContainerImages();
        
        for (let i = 0; i < images.length; i++) {
            const component = ['api', 'worker', 'frontend'][i];
            const image = images[i];
            
            await exec.exec('sed', [
                '-i',
                `s|image: .*${component}:.*|image: ${image}|g`,
                `k8s/${this.environment}/${component}-deployment.yml`
            ]);
        }
    }

    /**
     * Get deployment names from manifests
     */
    private async getDeploymentNames(): Promise<string[]> {
        // This would parse Kubernetes manifests to extract deployment names
        // For simplicity, returning common deployment names
        return ['api', 'worker', 'frontend'];
    }

    /**
     * Get service URL for health checks
     */
    private async getServiceUrl(): Promise<string | null> {
        try {
            let output = '';
            await exec.exec('kubectl', [
                'get', 'service', 'api',
                '-n', this.namespace,
                '-o', 'jsonpath={.status.loadBalancer.ingress[0].hostname}'
            ], {
                listeners: {
                    stdout: (data: Buffer) => {
                        output += data.toString();
                    }
                }
            });
            
            return output.trim() ? `http://${output.trim()}` : null;
        } catch (error) {
            core.warning('Could not get service URL for health checks');
            return null;
        }
    }
}

// Action entry point
async function run(): Promise<void> {
    const deployment = new DeploymentAction();
    await deployment.run();
}

// Execute if this is the main module
if (require.main === module) {
    run().catch(error => {
        console.error('Action failed:', error);
        process.exit(1);
    });
}

export { DeploymentAction };
```

## Integration with Other Instructions

This CI/CD instruction file works in conjunction with:
- **space.instructions.md**: Foundational path-based principles and container-first development
- **project.instructions.md**: AI-seed specific requirements and pipeline configurations
- **test.instructions.md**: Testing standards and automation integration
- **docs.instructions.md**: Documentation generation and deployment
- **python.instructions.md**: Python-specific build and deployment patterns
- **javascript.instructions.md**: JavaScript/Node.js build and deployment requirements
- **bash.instructions.md**: Shell script automation and deployment utilities

## Future Evolution

### Advanced CI/CD Features
- **AI-Powered Pipeline Optimization**: Machine learning-driven pipeline performance optimization
- **Predictive Quality Gates**: AI-powered prediction of build and deployment success
- **Intelligent Resource Allocation**: Dynamic resource allocation based on pipeline requirements
- **Automated Rollback Intelligence**: AI-driven automatic rollback decision making
- **Multi-Cloud Deployment Orchestration**: Seamless deployment across multiple cloud providers
- **Continuous Security Integration**: Real-time security scanning and compliance validation
