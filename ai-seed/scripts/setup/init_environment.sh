#!/bin/bash
# AI-Seed Environment Initialization Script
# Path: Environment Setup → Validation → Initialization → Configuration

set -euo pipefail

# Path: Script initialization and library loading
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../../" && pwd)"
readonly LOG_DIR="${PROJECT_ROOT}/logs"

# Create logs directory
mkdir -p "${LOG_DIR}"

# Path: Utility functions for logging and path management
log_info() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [INFO] $1" | tee -a "${LOG_DIR}/init.log"
}

log_error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [ERROR] $1" | tee -a "${LOG_DIR}/init.log" >&2
}

log_success() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [SUCCESS] $1" | tee -a "${LOG_DIR}/init.log"
}

# Path: Environment validation
validate_environment() {
    log_info "Validating environment prerequisites..."
    
    # Check for required tools
    local required_tools=("docker" "git" "curl")
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            log_error "Required tool not found: $tool"
            echo "Please install $tool and try again."
            return 1
        fi
        log_info "✓ Found required tool: $tool"
    done
    
    # Check for docker compose (v2 or legacy)
    if docker compose version &> /dev/null; then
        log_info "✓ Found Docker Compose v2"
    elif command -v docker-compose &> /dev/null; then
        log_info "✓ Found Docker Compose (legacy)"
    else
        log_error "Docker Compose not found"
        echo "Please install Docker Compose and try again."
        return 1
    fi
    
    # Check Docker daemon
    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running"
        echo "Please start Docker and try again."
        return 1
    fi
    log_info "✓ Docker daemon is running"
    
    # Check available disk space (at least 2GB)
    local available_space_gb
    available_space_gb=$(df "${PROJECT_ROOT}" | awk 'NR==2 {print int($4/1024/1024)}')
    
    if [[ $available_space_gb -lt 2 ]]; then
        log_error "Insufficient disk space: ${available_space_gb}GB available (minimum: 2GB)"
        return 1
    fi
    log_info "✓ Sufficient disk space: ${available_space_gb}GB available"
    
    log_success "Environment validation completed"
}

# Path: Project structure initialization
initialize_project_structure() {
    log_info "Initializing AI-Seed project structure..."
    
    local required_dirs=(
        "${PROJECT_ROOT}/src"
        "${PROJECT_ROOT}/src/frontend"
        "${PROJECT_ROOT}/src/api"
        "${PROJECT_ROOT}/src/ai"
        "${PROJECT_ROOT}/src/data"
        "${PROJECT_ROOT}/tests"
        "${PROJECT_ROOT}/tests/unit"
        "${PROJECT_ROOT}/tests/integration"
        "${PROJECT_ROOT}/tests/e2e"
        "${PROJECT_ROOT}/docs"
        "${PROJECT_ROOT}/docs/architecture"
        "${PROJECT_ROOT}/docs/guides"
        "${PROJECT_ROOT}/docs/api"
        "${PROJECT_ROOT}/config"
        "${PROJECT_ROOT}/config/environments"
        "${PROJECT_ROOT}/logs"
        "${PROJECT_ROOT}/scripts/build"
        "${PROJECT_ROOT}/scripts/deploy"
        "${PROJECT_ROOT}/scripts/maintenance"
    )
    
    for dir in "${required_dirs[@]}"; do
        if [[ ! -d "$dir" ]]; then
            mkdir -p "$dir"
            log_info "✓ Created directory: $dir"
        fi
    done
    
    log_success "Project structure initialization completed"
}

# Path: Configuration file generation
create_default_configurations() {
    log_info "Creating default configuration files..."
    
    # Environment configuration
    if [[ ! -f "${PROJECT_ROOT}/config/.env.development" ]]; then
        cat > "${PROJECT_ROOT}/config/.env.development" << 'EOF'
# AI-Seed Development Environment Configuration
AI_SEED_ENV=development
AI_SEED_LOG_LEVEL=DEBUG
AI_SEED_CONTAINER_REGISTRY=localhost:5000
AI_SEED_PATH_MONITORING=true

# Database Configuration
DATABASE_URL=postgresql://ai_seed:ai_seed_pass@localhost:5432/ai_seed_dev
REDIS_URL=redis://localhost:6379/0

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=true

# AI Engine Configuration
AI_ENGINE_HOST=0.0.0.0
AI_ENGINE_PORT=5000
AI_MODEL_PATH=/app/models

# Frontend Configuration
FRONTEND_PORT=3000
FRONTEND_API_URL=http://localhost:8000
EOF
        log_info "✓ Created development environment configuration"
    fi
    
    # Docker Compose override for development
    if [[ ! -f "${PROJECT_ROOT}/docker-compose.override.yml" ]]; then
        cat > "${PROJECT_ROOT}/docker-compose.override.yml" << 'EOF'
# AI-Seed Development Environment Overrides
version: '3.8'

services:
  frontend:
    environment:
      - LOG_LEVEL=DEBUG
      - HOT_RELOAD=true
    volumes:
      - ./src/frontend:/app/src/frontend:rw
    command: ["npm", "run", "dev", "--prefix", "src/frontend"]

  api:
    environment:
      - LOG_LEVEL=DEBUG
      - API_DEBUG=true
    volumes:
      - ./src/api:/app/src/api:rw
    command: ["npm", "run", "dev", "--prefix", "src/api"]

  ai-engine:
    environment:
      - LOG_LEVEL=DEBUG
      - FLASK_DEBUG=true
    volumes:
      - ./src/ai:/app:rw
    command: ["python", "main.py", "--debug"]
EOF
        log_info "✓ Created Docker Compose development override"
    fi
    
    # Nginx configuration for path monitoring
    if [[ ! -f "${PROJECT_ROOT}/config/nginx.conf" ]]; then
        cat > "${PROJECT_ROOT}/config/nginx.conf" << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream frontend {
        server frontend:3000;
    }
    
    upstream api {
        server api:8000;
    }
    
    upstream ai-engine {
        server ai-engine:5000;
    }
    
    server {
        listen 80;
        server_name localhost;
        
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
        
        location /api/ {
            proxy_pass http://api/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
        
        location /ai/ {
            proxy_pass http://ai-engine/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
        
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
    }
}
EOF
        log_info "✓ Created Nginx configuration for path monitoring"
    fi
    
    log_success "Configuration files created successfully"
}

# Path: Git hooks and automation setup
setup_git_hooks() {
    log_info "Setting up Git hooks for path-based development..."
    
    local hooks_dir="${PROJECT_ROOT}/.git/hooks"
    
    # Pre-commit hook for path validation
    cat > "${hooks_dir}/pre-commit" << 'EOF'
#!/bin/bash
# AI-Seed Path Validation Pre-commit Hook

set -euo pipefail

echo "🌱 AI-Seed: Validating paths before commit..."

# Run linting if lint script exists
if [[ -f "./scripts/maintenance/lint.sh" ]]; then
    ./scripts/maintenance/lint.sh
fi

# Run tests if test script exists
if [[ -f "./scripts/test/run_tests.sh" ]]; then
    ./scripts/test/run_tests.sh --quick
fi

echo "✅ Path validation completed successfully"
EOF
    
    chmod +x "${hooks_dir}/pre-commit"
    log_info "✓ Created pre-commit hook for path validation"
    
    log_success "Git hooks setup completed"
}

# Path: Health check and verification
verify_installation() {
    log_info "Verifying AI-Seed installation..."
    
    # Check directory structure
    local key_dirs=("src" "scripts" "config" "docs" "tests")
    for dir in "${key_dirs[@]}"; do
        if [[ -d "${PROJECT_ROOT}/${dir}" ]]; then
            log_info "✓ Directory structure: $dir"
        else
            log_error "✗ Missing directory: $dir"
            return 1
        fi
    done
    
    # Check configuration files
    local key_configs=("config/.env.development" "docker/docker-compose.yml" "config/nginx.conf")
    for config in "${key_configs[@]}"; do
        if [[ -f "${PROJECT_ROOT}/${config}" ]]; then
            log_info "✓ Configuration file: $config"
        else
            log_error "✗ Missing configuration: $config"
            return 1
        fi
    done
    
    log_success "Installation verification completed successfully"
    
    # Display next steps
    cat << 'EOF'

🌱 AI-Seed Environment Initialized Successfully! 🌱

Next steps to grow your seed:

1. 📦 Build the containers:
   docker compose -f docker/docker-compose.yml build

2. 🚀 Start the ecosystem:
   docker compose -f docker/docker-compose.yml up

3. 🌐 Access your applications:
   - Frontend: http://localhost:3000
   - API: http://localhost:8000
   - AI Engine: http://localhost:5000
   - Monitor: http://localhost:8080

4. 📚 Explore the documentation:
   - Architecture: docs/architecture/
   - Guides: docs/guides/
   - API Docs: docs/api/

5. 🛠️ Start developing:
   - Add your code to src/
   - Write tests in tests/
   - Use scripts/ for automation

The path of least resistance awaits! 🛤️✨

EOF
}

# Path: Main execution workflow
main() {
    local start_time=$(date +%s)
    
    echo "🌱 Welcome to AI-Seed Environment Initialization 🌱"
    echo "Following the path of least resistance to set up your development environment..."
    echo ""
    
    # Execute initialization paths
    validate_environment || {
        log_error "Environment validation failed"
        exit 1
    }
    
    initialize_project_structure || {
        log_error "Project structure initialization failed"
        exit 1
    }
    
    create_default_configurations || {
        log_error "Configuration creation failed"
        exit 1
    }
    
    setup_git_hooks || {
        log_error "Git hooks setup failed"
        exit 1
    }
    
    verify_installation || {
        log_error "Installation verification failed"
        exit 1
    }
    
    local end_time=$(date +%s)
    local total_time=$((end_time - start_time))
    
    log_success "AI-Seed environment initialized successfully in ${total_time} seconds"
}

# Execute main function if script is run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi