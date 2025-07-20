---
file: bash.instructions.md
description: Bash/Shell scripting instructions for path-based automation and container-first development
applyTo: "**/*.sh,**/*.bash"
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
    - alpine:3.18
    - ubuntu:22.04
  exposedPorts: null
  volumes:
    - /scripts:ro
    - /workspace:rw
    - /logs:rw
  environment:
    SHELL: /bin/bash
    PATH: /usr/local/bin:/usr/bin:/bin
  resources:
    cpu: 0.1-0.5
    memory: 128MiB-512MiB
  healthCheck: /bin/bash --version
paths:
  script-execution-path: Environment setup → validation → execution → cleanup
  automation-workflow-path: Init → build → test → deploy → monitor
  error-recovery-path: Error detection → logging → fallback → notification
changelog:
  - date: 2025-07-19
    change: Initial creation
    author: AI-Seed Team
usage: Reference for all Bash/Shell scripting within container environments
notes: Emphasizes path-based automation and container-first execution
---

# Bash/Shell Instructions

Apply the [general coding guidelines](../copilot-instructions.md) to all code.

These instructions provide comprehensive guidance for Bash and Shell scripting within the AI-seed ecosystem, emphasizing path-based automation, container-first execution, and reliable script development practices.

## Shell Environment and Setup

### Container-First Shell Scripting

#### Base Container Configuration
```dockerfile
# Multi-stage shell script environment
FROM alpine:3.18 AS base
RUN apk add --no-cache \
    bash \
    curl \
    jq \
    git \
    docker-cli \
    && rm -rf /var/cache/apk/*

# Development stage
FROM base AS development
RUN apk add --no-cache \
    shellcheck \
    bats \
    make \
    && rm -rf /var/cache/apk/*

WORKDIR /workspace
COPY scripts/ /scripts/
RUN chmod +x /scripts/*.sh

# Production stage
FROM base AS production
COPY scripts/ /scripts/
RUN chmod +x /scripts/*.sh
USER 1000:1000
ENTRYPOINT ["/scripts/entrypoint.sh"]
```

#### Shell Environment Path Setup
```bash
#!/bin/bash
# Path: environment-initialization

# Script header template
set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Path: environment-variable-setup
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../" && pwd)"
readonly LOG_DIR="${PROJECT_ROOT}/logs"
readonly CONFIG_DIR="${PROJECT_ROOT}/config"

# Path: logging-initialization
readonly LOG_FILE="${LOG_DIR}/$(basename "${0%.*}").log"
mkdir -p "${LOG_DIR}"

# Path: utility-function-loading
source "${SCRIPT_DIR}/lib/logging.sh"
source "${SCRIPT_DIR}/lib/utils.sh"
source "${SCRIPT_DIR}/lib/path_management.sh"
```

### Path-Based Script Organization

#### Directory Structure
```
scripts/
├── lib/                    # Shared library path
│   ├── logging.sh         # Centralized logging functions
│   ├── utils.sh           # General utility functions
│   ├── path_management.sh # Path execution and tracking
│   ├── container_ops.sh   # Container operation helpers
│   └── error_handling.sh  # Error management functions
├── setup/                  # Environment setup path
│   ├── init_environment.sh
│   ├── install_dependencies.sh
│   └── configure_containers.sh
├── build/                  # Build automation path
│   ├── build_images.sh
│   ├── run_tests.sh
│   └── package_artifacts.sh
├── deploy/                 # Deployment orchestration path
│   ├── deploy_development.sh
│   ├── deploy_staging.sh
│   └── deploy_production.sh
├── maintenance/            # System maintenance path
│   ├── cleanup_containers.sh
│   ├── backup_data.sh
│   └── monitor_health.sh
└── entrypoint.sh          # Container entry point
```

## Path-Aware Function Library

### Core Path Management Functions
```bash
#!/bin/bash
# Path: core-path-management-library
# File: scripts/lib/path_management.sh

# Global path tracking variables
declare -a EXECUTION_PATH_STACK=()
declare -A PATH_METRICS=()
declare -A PATH_START_TIMES=()

# Path: execution-path-tracking
enter_path() {
    local path_name="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    EXECUTION_PATH_STACK+=("$path_name")
    PATH_START_TIMES["$path_name"]=$(date +%s.%N)
    
    log_info "Entering path: $path_name" "path_tracking"
    log_debug "Current path stack: ${EXECUTION_PATH_STACK[*]}" "path_tracking"
}

exit_path() {
    local path_name="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    if [[ ${#EXECUTION_PATH_STACK[@]} -eq 0 ]]; then
        log_warning "Attempting to exit path '$path_name' but stack is empty" "path_tracking"
        return 1
    fi
    
    local current_path="${EXECUTION_PATH_STACK[-1]}"
    if [[ "$current_path" != "$path_name" ]]; then
        log_warning "Path mismatch: expected '$current_path', got '$path_name'" "path_tracking"
    fi
    
    # Calculate execution time
    local start_time="${PATH_START_TIMES[$path_name]}"
    local end_time=$(date +%s.%N)
    local execution_time=$(echo "$end_time - $start_time" | bc -l)
    
    # Update metrics
    if [[ -z "${PATH_METRICS[$path_name]:-}" ]]; then
        PATH_METRICS["$path_name"]="1:$execution_time"
    else
        local current_metrics="${PATH_METRICS[$path_name]}"
        local count=$(echo "$current_metrics" | cut -d: -f1)
        local total_time=$(echo "$current_metrics" | cut -d: -f2)
        local new_count=$((count + 1))
        local new_total=$(echo "$total_time + $execution_time" | bc -l)
        PATH_METRICS["$path_name"]="$new_count:$new_total"
    fi
    
    # Remove from stack
    unset 'EXECUTION_PATH_STACK[-1]'
    
    log_info "Exiting path: $path_name (${execution_time}s)" "path_tracking"
}

# Path: execution-context-management
execute_in_path() {
    local path_name="$1"
    shift
    local command="$@"
    
    enter_path "$path_name"
    
    local exit_code=0
    if ! eval "$command"; then
        exit_code=$?
        log_error "Command failed in path '$path_name': $command" "path_execution"
    fi
    
    exit_path "$path_name"
    return $exit_code
}

# Path: parallel-execution-management
execute_paths_parallel() {
    local -a pids=()
    local -a path_names=()
    
    while [[ $# -gt 0 ]]; do
        local path_name="$1"
        local command="$2"
        shift 2
        
        path_names+=("$path_name")
        (
            execute_in_path "$path_name" "$command"
        ) &
        pids+=($!)
    done
    
    # Wait for all paths to complete
    local overall_success=true
    for i in "${!pids[@]}"; do
        local pid="${pids[$i]}"
        local path_name="${path_names[$i]}"
        
        if wait "$pid"; then
            log_info "Parallel path '$path_name' completed successfully" "parallel_execution"
        else
            log_error "Parallel path '$path_name' failed" "parallel_execution"
            overall_success=false
        fi
    done
    
    if [[ "$overall_success" = true ]]; then
        return 0
    else
        return 1
    fi
}
```

### Error Handling and Recovery Paths
```bash
#!/bin/bash
# Path: error-handling-and-recovery
# File: scripts/lib/error_handling.sh

# Path: error-classification
readonly ERROR_RECOVERABLE=1
readonly ERROR_FATAL=2
readonly ERROR_USER=3
readonly ERROR_SYSTEM=4

# Path: error-context-capture
capture_error_context() {
    local error_code="$1"
    local error_message="$2"
    local current_path="${EXECUTION_PATH_STACK[-1]:-unknown}"
    
    cat << EOF > "${LOG_DIR}/error_context_$(date +%s).json"
{
    "timestamp": "$(date -Iseconds)",
    "error_code": $error_code,
    "error_message": "$error_message",
    "current_path": "$current_path",
    "path_stack": [$(printf '"%s",' "${EXECUTION_PATH_STACK[@]}" | sed 's/,$//')],
    "environment": {
        "script": "${BASH_SOURCE[1]}",
        "function": "${FUNCNAME[1]}",
        "line": "${BASH_LINENO[0]}",
        "pwd": "$(pwd)",
        "user": "$(whoami)",
        "pid": $$
    },
    "system_info": {
        "hostname": "$(hostname)",
        "os": "$(uname -s)",
        "kernel": "$(uname -r)",
        "arch": "$(uname -m)"
    }
}
EOF
}

# Path: error-recovery-strategies
attempt_error_recovery() {
    local error_type="$1"
    local error_context="$2"
    local current_path="${EXECUTION_PATH_STACK[-1]:-unknown}"
    
    case "$error_type" in
        "$ERROR_RECOVERABLE")
            log_info "Attempting recovery for recoverable error in path: $current_path" "error_recovery"
            
            # Path: retry-mechanism
            if retry_with_backoff "$error_context"; then
                log_info "Error recovery successful" "error_recovery"
                return 0
            else
                log_error "Error recovery failed, escalating" "error_recovery"
                return $ERROR_FATAL
            fi
            ;;
        
        "$ERROR_USER")
            log_warning "User error detected, providing guidance" "error_recovery"
            display_user_help "$error_context"
            return $ERROR_USER
            ;;
        
        "$ERROR_SYSTEM")
            log_error "System error detected, checking environment" "error_recovery"
            if check_system_health; then
                log_info "System appears healthy, retrying operation" "error_recovery"
                return $ERROR_RECOVERABLE
            else
                log_error "System health check failed" "error_recovery"
                return $ERROR_FATAL
            fi
            ;;
        
        *)
            log_error "Unknown error type: $error_type" "error_recovery"
            return $ERROR_FATAL
            ;;
    esac
}

# Path: retry-with-exponential-backoff
retry_with_backoff() {
    local command="$1"
    local max_attempts="${2:-3}"
    local initial_delay="${3:-1}"
    
    local attempt=1
    local delay="$initial_delay"
    
    while [[ $attempt -le $max_attempts ]]; do
        log_info "Retry attempt $attempt/$max_attempts (delay: ${delay}s)" "retry_backoff"
        
        if eval "$command"; then
            log_info "Retry successful on attempt $attempt" "retry_backoff"
            return 0
        fi
        
        if [[ $attempt -lt $max_attempts ]]; then
            log_warning "Attempt $attempt failed, waiting ${delay}s before retry" "retry_backoff"
            sleep "$delay"
            delay=$((delay * 2))  # Exponential backoff
        fi
        
        ((attempt++))
    done
    
    log_error "All retry attempts failed" "retry_backoff"
    return 1
}

# Path: graceful-error-handling
handle_script_error() {
    local exit_code=$?
    local line_number=${BASH_LINENO[0]}
    local command="${BASH_COMMAND}"
    
    capture_error_context "$exit_code" "Command failed: $command (line $line_number)"
    
    # Determine error type based on exit code
    local error_type
    case $exit_code in
        1) error_type=$ERROR_RECOVERABLE ;;
        2) error_type=$ERROR_USER ;;
        126|127) error_type=$ERROR_SYSTEM ;;
        *) error_type=$ERROR_FATAL ;;
    esac
    
    # Attempt recovery
    if [[ $error_type -ne $ERROR_FATAL ]]; then
        if attempt_error_recovery "$error_type" "$command"; then
            return 0  # Recovery successful
        fi
    fi
    
    # Cleanup and exit
    cleanup_on_error
    exit $exit_code
}

# Set error trap
trap 'handle_script_error' ERR
```

### Logging System with Path Context
```bash
#!/bin/bash
# Path: centralized-logging-system
# File: scripts/lib/logging.sh

# Path: log-level-definitions
readonly LOG_LEVEL_DEBUG=0
readonly LOG_LEVEL_INFO=1
readonly LOG_LEVEL_WARNING=2
readonly LOG_LEVEL_ERROR=3
readonly LOG_LEVEL_FATAL=4

# Current log level (can be overridden by environment)
LOG_LEVEL=${LOG_LEVEL:-$LOG_LEVEL_INFO}

# Path: log-formatting
format_log_message() {
    local level="$1"
    local message="$2"
    local context="${3:-general}"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local current_path="${EXECUTION_PATH_STACK[-1]:-main}"
    
    echo "[$timestamp] [$level] [$context] [$current_path] $message"
}

# Path: core-logging-functions
log_debug() {
    local message="$1"
    local context="${2:-debug}"
    
    if [[ $LOG_LEVEL -le $LOG_LEVEL_DEBUG ]]; then
        format_log_message "DEBUG" "$message" "$context" >&2
        [[ -n "${LOG_FILE:-}" ]] && format_log_message "DEBUG" "$message" "$context" >> "$LOG_FILE"
    fi
}

log_info() {
    local message="$1"
    local context="${2:-info}"
    
    if [[ $LOG_LEVEL -le $LOG_LEVEL_INFO ]]; then
        format_log_message "INFO" "$message" "$context"
        [[ -n "${LOG_FILE:-}" ]] && format_log_message "INFO" "$message" "$context" >> "$LOG_FILE"
    fi
}

log_warning() {
    local message="$1"
    local context="${2:-warning}"
    
    if [[ $LOG_LEVEL -le $LOG_LEVEL_WARNING ]]; then
        format_log_message "WARNING" "$message" "$context" >&2
        [[ -n "${LOG_FILE:-}" ]] && format_log_message "WARNING" "$message" "$context" >> "$LOG_FILE"
    fi
}

log_error() {
    local message="$1"
    local context="${2:-error}"
    
    if [[ $LOG_LEVEL -le $LOG_LEVEL_ERROR ]]; then
        format_log_message "ERROR" "$message" "$context" >&2
        [[ -n "${LOG_FILE:-}" ]] && format_log_message "ERROR" "$message" "$context" >> "$LOG_FILE"
    fi
}

log_fatal() {
    local message="$1"
    local context="${2:-fatal}"
    
    format_log_message "FATAL" "$message" "$context" >&2
    [[ -n "${LOG_FILE:-}" ]] && format_log_message "FATAL" "$message" "$context" >> "$LOG_FILE"
    
    # Capture system state for fatal errors
    capture_system_state_on_fatal "$message"
    exit 1
}

# Path: structured-logging
log_json() {
    local level="$1"
    local message="$2"
    local context="${3:-general}"
    local extra_data="${4:-{}}"
    
    local timestamp=$(date -Iseconds)
    local current_path="${EXECUTION_PATH_STACK[-1]:-main}"
    
    local json_log=$(jq -n \
        --arg timestamp "$timestamp" \
        --arg level "$level" \
        --arg message "$message" \
        --arg context "$context" \
        --arg path "$current_path" \
        --argjson extra "$extra_data" \
        '{
            timestamp: $timestamp,
            level: $level,
            message: $message,
            context: $context,
            path: $path,
            extra: $extra
        }')
    
    echo "$json_log" >> "${LOG_DIR}/structured.log"
}

# Path: performance-logging
log_performance_metric() {
    local metric_name="$1"
    local metric_value="$2"
    local metric_unit="${3:-ms}"
    local context="${4:-performance}"
    
    log_json "INFO" "Performance metric recorded" "$context" \
        "{\"metric_name\": \"$metric_name\", \"value\": $metric_value, \"unit\": \"$metric_unit\"}"
}
```

## Container Operations and Orchestration

### Container Lifecycle Management
```bash
#!/bin/bash
# Path: container-lifecycle-management
# File: scripts/lib/container_ops.sh

# Path: container-image-management
build_container_image() {
    local image_name="$1"
    local dockerfile_path="${2:-Dockerfile}"
    local build_context="${3:-.}"
    local target_stage="${4:-production}"
    
    execute_in_path "container_build" \
        "docker build \
            --file '$dockerfile_path' \
            --target '$target_stage' \
            --tag '$image_name' \
            '$build_context'"
}

# Path: container-execution-with-monitoring
run_container_with_monitoring() {
    local container_name="$1"
    local image_name="$2"
    shift 2
    local docker_args="$@"
    
    enter_path "container_execution"
    
    # Start container
    log_info "Starting container: $container_name" "container_ops"
    local container_id
    container_id=$(docker run --detach --name "$container_name" $docker_args "$image_name")
    
    if [[ -z "$container_id" ]]; then
        log_error "Failed to start container: $container_name" "container_ops"
        exit_path "container_execution"
        return 1
    fi
    
    # Monitor container health
    monitor_container_health "$container_id" &
    local monitor_pid=$!
    
    # Wait for container completion
    docker wait "$container_id"
    local exit_code=$?
    
    # Stop monitoring
    kill $monitor_pid 2>/dev/null || true
    
    # Collect logs
    log_info "Container execution completed with exit code: $exit_code" "container_ops"
    docker logs "$container_id" > "${LOG_DIR}/${container_name}.log" 2>&1
    
    # Cleanup
    docker rm "$container_id" >/dev/null 2>&1 || true
    
    exit_path "container_execution"
    return $exit_code
}

# Path: container-health-monitoring
monitor_container_health() {
    local container_id="$1"
    local check_interval="${2:-10}"
    
    while docker ps --quiet --filter "id=$container_id" | grep -q "$container_id"; do
        local health_status
        health_status=$(docker inspect "$container_id" --format '{{.State.Health.Status}}' 2>/dev/null || echo "no-health-check")
        
        case "$health_status" in
            "healthy")
                log_debug "Container $container_id is healthy" "health_monitoring"
                ;;
            "unhealthy")
                log_warning "Container $container_id is unhealthy" "health_monitoring"
                ;;
            "starting")
                log_info "Container $container_id health check starting" "health_monitoring"
                ;;
            "no-health-check")
                log_debug "Container $container_id has no health check configured" "health_monitoring"
                ;;
        esac
        
        sleep "$check_interval"
    done
}

# Path: multi-container-orchestration
orchestrate_multi_container_deployment() {
    local compose_file="$1"
    local environment="${2:-development}"
    local scale_config="${3:-}"
    
    execute_in_path "multi_container_orchestration" \
        "docker-compose \
            --file '$compose_file' \
            --project-name 'ai-seed-$environment' \
            up --detach $scale_config"
    
    # Verify all services are healthy
    verify_services_health "$compose_file" "ai-seed-$environment"
}

verify_services_health() {
    local compose_file="$1"
    local project_name="$2"
    local max_wait_time="${3:-300}"  # 5 minutes
    
    enter_path "service_health_verification"
    
    local start_time=$(date +%s)
    local services
    services=$(docker-compose --file "$compose_file" config --services)
    
    for service in $services; do
        log_info "Verifying health of service: $service" "health_verification"
        
        while true; do
            local current_time=$(date +%s)
            local elapsed_time=$((current_time - start_time))
            
            if [[ $elapsed_time -gt $max_wait_time ]]; then
                log_error "Health check timeout for service: $service" "health_verification"
                exit_path "service_health_verification"
                return 1
            fi
            
            local container_id
            container_id=$(docker-compose --file "$compose_file" --project-name "$project_name" ps --quiet "$service")
            
            if [[ -n "$container_id" ]]; then
                local health_status
                health_status=$(docker inspect "$container_id" --format '{{.State.Health.Status}}' 2>/dev/null || echo "running")
                
                if [[ "$health_status" = "healthy" ]] || [[ "$health_status" = "running" ]]; then
                    log_info "Service $service is healthy" "health_verification"
                    break
                fi
            fi
            
            sleep 5
        done
    done
    
    exit_path "service_health_verification"
    log_info "All services are healthy" "health_verification"
}
```

### Automation Workflow Scripts

#### Environment Setup Script
```bash
#!/bin/bash
# Path: environment-initialization-automation
# File: scripts/setup/init_environment.sh

set -euo pipefail

# Path: script-initialization
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../../" && pwd)"

# Load libraries
source "${SCRIPT_DIR}/../lib/logging.sh"
source "${SCRIPT_DIR}/../lib/path_management.sh"
source "${SCRIPT_DIR}/../lib/utils.sh"

# Path: environment-validation
validate_environment() {
    enter_path "environment_validation"
    
    log_info "Validating environment prerequisites" "setup"
    
    # Check required tools
    local required_tools=("docker" "docker-compose" "git" "curl" "jq")
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            log_error "Required tool not found: $tool" "setup"
            exit_path "environment_validation"
            return 1
        fi
        log_debug "Found required tool: $tool" "setup"
    done
    
    # Check Docker daemon
    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running" "setup"
        exit_path "environment_validation"
        return 1
    fi
    
    # Check available disk space
    local available_space_gb
    available_space_gb=$(df "${PROJECT_ROOT}" | awk 'NR==2 {print int($4/1024/1024)}')
    
    if [[ $available_space_gb -lt 5 ]]; then
        log_warning "Low disk space: ${available_space_gb}GB available (recommended: 5GB+)" "setup"
    fi
    
    exit_path "environment_validation"
    log_info "Environment validation completed successfully" "setup"
}

# Path: project-structure-initialization
initialize_project_structure() {
    enter_path "project_structure_initialization"
    
    log_info "Initializing project directory structure" "setup"
    
    local required_dirs=(
        "${PROJECT_ROOT}/logs"
        "${PROJECT_ROOT}/data"
        "${PROJECT_ROOT}/config"
        "${PROJECT_ROOT}/tmp"
        "${PROJECT_ROOT}/docker/volumes"
    )
    
    for dir in "${required_dirs[@]}"; do
        if [[ ! -d "$dir" ]]; then
            mkdir -p "$dir"
            log_debug "Created directory: $dir" "setup"
        fi
    done
    
    # Create default configuration files
    create_default_configs
    
    exit_path "project_structure_initialization"
    log_info "Project structure initialization completed" "setup"
}

# Path: configuration-file-generation
create_default_configs() {
    local config_dir="${PROJECT_ROOT}/config"
    
    # Environment configuration
    if [[ ! -f "${config_dir}/.env.development" ]]; then
        cat > "${config_dir}/.env.development" << 'EOF'
# AI-Seed Development Environment Configuration
AI_SEED_ENV=development
AI_SEED_LOG_LEVEL=DEBUG
AI_SEED_CONTAINER_REGISTRY=localhost:5000
AI_SEED_PATH_MONITORING=true

# Database Configuration
DATABASE_URL=postgresql://user:pass@localhost:5432/ai_seed_dev
REDIS_URL=redis://localhost:6379/0

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=true
EOF
        log_debug "Created development environment configuration" "setup"
    fi
    
    # Docker Compose override for development
    if [[ ! -f "${PROJECT_ROOT}/docker-compose.override.yml" ]]; then
        cat > "${PROJECT_ROOT}/docker-compose.override.yml" << 'EOF'
version: '3.8'

services:
  app:
    environment:
      - LOG_LEVEL=DEBUG
    volumes:
      - ./src:/app/src:rw
      - ./logs:/app/logs:rw
    ports:
      - "8000:8000"
    command: ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
EOF
        log_debug "Created Docker Compose development override" "setup"
    fi
}

# Path: main-execution-workflow
main() {
    local start_time=$(date +%s.%N)
    
    log_info "Starting environment initialization" "setup"
    
    # Execute initialization paths
    validate_environment || {
        log_fatal "Environment validation failed" "setup"
    }
    
    initialize_project_structure || {
        log_fatal "Project structure initialization failed" "setup"
    }
    
    # Calculate total execution time
    local end_time=$(date +%s.%N)
    local total_time=$(echo "$end_time - $start_time" | bc -l)
    
    log_performance_metric "environment_init_time" "$total_time" "seconds" "setup"
    log_info "Environment initialization completed successfully in ${total_time}s" "setup"
}

# Execute main function if script is run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
```

#### Build Automation Script
```bash
#!/bin/bash
# Path: build-automation-workflow
# File: scripts/build/build_images.sh

set -euo pipefail

# Path: script-initialization
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../../" && pwd)"

# Load libraries
source "${SCRIPT_DIR}/../lib/logging.sh"
source "${SCRIPT_DIR}/../lib/path_management.sh"
source "${SCRIPT_DIR}/../lib/container_ops.sh"

# Path: build-configuration
readonly BUILD_CONTEXT="${PROJECT_ROOT}"
readonly DOCKERFILE_PATH="${BUILD_CONTEXT}/Dockerfile"
readonly IMAGE_BASE_NAME="ai-seed"
readonly BUILD_TIMESTAMP=$(date +%Y%m%d-%H%M%S)
readonly GIT_COMMIT_HASH=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")

# Path: image-tagging-strategy
generate_image_tags() {
    local stage="$1"
    local environment="${2:-development}"
    
    echo "${IMAGE_BASE_NAME}:${stage}-${environment}"
    echo "${IMAGE_BASE_NAME}:${stage}-${BUILD_TIMESTAMP}"
    echo "${IMAGE_BASE_NAME}:${stage}-${GIT_COMMIT_HASH}"
    
    if [[ "$environment" = "production" ]]; then
        echo "${IMAGE_BASE_NAME}:${stage}-latest"
    fi
}

# Path: multi-stage-build-execution
build_container_images() {
    local environment="${1:-development}"
    local push_to_registry="${2:-false}"
    
    enter_path "container_image_build"
    
    local stages=("base" "development" "production")
    
    for stage in "${stages[@]}"; do
        # Skip production stage in development builds
        if [[ "$environment" = "development" && "$stage" = "production" ]]; then
            continue
        fi
        
        # Skip development stage in production builds
        if [[ "$environment" = "production" && "$stage" = "development" ]]; then
            continue
        fi
        
        log_info "Building $stage stage for $environment environment" "build"
        
        local primary_tag="${IMAGE_BASE_NAME}:${stage}-${environment}"
        
        # Build with primary tag
        if ! build_container_image "$primary_tag" "$DOCKERFILE_PATH" "$BUILD_CONTEXT" "$stage"; then
            log_error "Failed to build $stage stage" "build"
            exit_path "container_image_build"
            return 1
        fi
        
        # Add additional tags
        local additional_tags
        additional_tags=$(generate_image_tags "$stage" "$environment" | grep -v "$primary_tag")
        
        for tag in $additional_tags; do
            docker tag "$primary_tag" "$tag"
            log_debug "Tagged image with: $tag" "build"
        done
        
        # Push to registry if requested
        if [[ "$push_to_registry" = "true" ]]; then
            push_images_to_registry "$stage" "$environment"
        fi
    done
    
    exit_path "container_image_build"
    log_info "Container image build completed successfully" "build"
}

# Path: registry-operations
push_images_to_registry() {
    local stage="$1"
    local environment="$2"
    
    enter_path "registry_push"
    
    local tags_to_push
    tags_to_push=$(generate_image_tags "$stage" "$environment")
    
    for tag in $tags_to_push; do
        log_info "Pushing image to registry: $tag" "registry"
        
        if docker push "$tag"; then
            log_info "Successfully pushed: $tag" "registry"
        else
            log_error "Failed to push: $tag" "registry"
            exit_path "registry_push"
            return 1
        fi
    done
    
    exit_path "registry_push"
}

# Path: build-validation
validate_built_images() {
    local environment="${1:-development}"
    
    enter_path "build_validation"
    
    local primary_tag="${IMAGE_BASE_NAME}:production-${environment}"
    
    log_info "Validating built image: $primary_tag" "validation"
    
    # Run basic container validation
    if ! docker run --rm --entrypoint="" "$primary_tag" /bin/sh -c "echo 'Container validation successful'"; then
        log_error "Container validation failed for: $primary_tag" "validation"
        exit_path "build_validation"
        return 1
    fi
    
    # Check image size
    local image_size_mb
    image_size_mb=$(docker images "$primary_tag" --format "table {{.Size}}" | tail -n +2 | sed 's/MB//' | awk '{print int($1)}')
    
    log_performance_metric "image_size_mb" "$image_size_mb" "MB" "build"
    
    # Warn if image is too large
    if [[ $image_size_mb -gt 1000 ]]; then
        log_warning "Image size is large: ${image_size_mb}MB (consider optimization)" "validation"
    fi
    
    exit_path "build_validation"
    log_info "Image validation completed successfully" "validation"
}

# Path: main-build-workflow
main() {
    local environment="${1:-development}"
    local push_registry="${2:-false}"
    local validate_only="${3:-false}"
    
    local start_time=$(date +%s.%N)
    
    log_info "Starting container build process for $environment environment" "build"
    
    if [[ "$validate_only" = "true" ]]; then
        validate_built_images "$environment"
    else
        # Execute build workflow
        build_container_images "$environment" "$push_registry" || {
            log_fatal "Container build failed" "build"
        }
        
        validate_built_images "$environment" || {
            log_fatal "Container validation failed" "build"
        }
    fi
    
    # Calculate and log performance metrics
    local end_time=$(date +%s.%N)
    local total_time=$(echo "$end_time - $start_time" | bc -l)
    
    log_performance_metric "build_total_time" "$total_time" "seconds" "build"
    log_info "Build process completed successfully in ${total_time}s" "build"
}

# Path: script-argument-parsing
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    # Parse command line arguments
    environment="development"
    push_registry="false"
    validate_only="false"
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --environment|-e)
                environment="$2"
                shift 2
                ;;
            --push-registry|-p)
                push_registry="true"
                shift
                ;;
            --validate-only|-v)
                validate_only="true"
                shift
                ;;
            --help|-h)
                cat << EOF
Usage: $0 [OPTIONS]

Options:
    --environment, -e    Target environment (development|staging|production)
    --push-registry, -p  Push images to container registry
    --validate-only, -v  Only validate existing images, don't build
    --help, -h          Show this help message

Examples:
    $0 --environment production --push-registry
    $0 --validate-only --environment staging
EOF
                exit 0
                ;;
            *)
                log_error "Unknown option: $1" "args"
                exit 1
                ;;
        esac
    done
    
    main "$environment" "$push_registry" "$validate_only"
fi
```

## Integration with Other Instructions

This Bash instruction file works in conjunction with:
- **space.instructions.md**: Foundational path-based principles and container-first development
- **project.instructions.md**: AI-seed specific requirements and conventions
- **python.instructions.md**: Language interoperability for mixed codebases
- **ci-cd.instructions.md**: Automated pipeline integration and deployment
- **test.instructions.md**: Automated testing and validation scripts

## Future Evolution

### Advanced Bash Patterns
- **AI-Generated Scripts**: Automated script generation based on path analysis
- **Dynamic Path Optimization**: Runtime path selection based on system conditions
- **Cross-Platform Compatibility**: Enhanced portability across different container environments
- **Performance Profiling**: Detailed execution time analysis and optimization

### Container Integration Enhancements
- **Orchestration Patterns**: Advanced multi-container coordination strategies
- **Resource Management**: Dynamic resource allocation and optimization
- **Security Hardening**: Enhanced security practices for script execution
- **Monitoring Integration**: Real-time script execution monitoring and alerting
