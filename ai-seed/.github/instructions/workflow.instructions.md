---
file: workflow.instructions.md
description: GitHub Actions workflow standards and AI instructions for automated CI/CD pipeline development
applyTo: "**/.github/workflows/*.yml,**/.github/workflows/*.yaml"
author: "AI-Seed Team <team@ai-seed.org>"
created: "2025-07-20"
lastModified: "2025-07-20"
version: "0.3.0"

relatedIssues:
  - "N/A"

relatedEvolutions:
  - "v0.3.0: Initial conversion from WORKFLOW_STANDARDS.md to instructions format"

dependencies:
  - file: ci-cd.instructions.md
    description: General CI/CD pipeline instructions and automation strategies
  - file: bash.instructions.md
    description: Shell scripting standards for workflow execution
  - file: project.instructions.md
    description: Project-specific context and requirements

containerRequirements:
  baseImage: ubuntu-latest
  description: for GitHub Actions runner environment
  exposedPorts: []
  portDescription: N/A
  volumes: []
  environment:
    EVOLUTION_VERSION: "0.3.0"
  resources:
    cpu: "2-4 cores"
    memory: "7GB"
  healthCheck: "GitHub Actions runner health check"

paths:
  workflow_execution_path:
    - trigger
    - checkout
    - environment_setup
    - script_execution
    - validation
    - cleanup
  evolution_workflow_path:
    - manual_dispatch
    - environment_preparation
    - context_collection
    - ai_evolution
    - change_application
    - pull_request_creation
  testing_workflow_path:
    - trigger
    - setup
    - test_execution
    - result_validation
    - artifact_storage

changelog:
  - date: "2025-07-20"
    description: "Initial creation from WORKFLOW_STANDARDS.md"
    author: "AI-Seed Team"

usage: "Reference for all GitHub Actions workflow development and AI Evolution Engine automation"
notes: "Emphasizes path-based workflow design, standardized patterns, and evolution-focused automation"
---

# GitHub Actions Workflow Instructions

These instructions provide comprehensive guidance for creating and maintaining GitHub Actions workflows within the AI-seed ecosystem, emphasizing standardized patterns, path-based execution, and AI Evolution Engine integration.

## Workflow Philosophy and Standards

### Path-Based Workflow Design

GitHub Actions workflows should follow natural execution paths that minimize complexity while ensuring reliability, consistency, and maintainability. Each workflow represents a defined path through the CI/CD pipeline.

#### Core Workflow Principles
- **Standardization**: Use consistent patterns across all workflows
- **Path Optimization**: Design workflows to follow the most efficient execution routes
- **Error Resilience**: Include robust error handling and recovery mechanisms
- **Evolution Integration**: Support AI-driven workflow improvements
- **Container-First**: Execute all operations within isolated environments

## Standard Workflow Structure

### Required Workflow Elements

#### Universal Environment Variables
All workflows MUST include these standard environment variables:

```yaml
env:
  EVOLUTION_VERSION: "0.3.0"
  WORKFLOW_TYPE: "descriptive_name"  # e.g., "manual_evolution", "scheduled_evolution", "testing_automation"
```

#### Standard Permissions
Use these permissions consistently across all workflows:

```yaml
permissions:
  contents: write
  pull-requests: write
  issues: write
```

#### Standardized Checkout Configuration
Always use this checkout pattern for consistency:

```yaml
- name: 🌱 Prepare Evolution Environment
  uses: actions/checkout@v4
  with:
    fetch-depth: 0
    token: ${{ secrets.PAT_TOKEN_TOKEN }}
```

### Common Input Parameters

#### Growth Modes for Evolution Workflows
Define these input options for AI evolution workflows:

```yaml
inputs:
  growth_mode:
    description: 'Evolution approach and risk level'
    required: false
    default: 'adaptive'
    type: choice
    options:
      - 'conservative'     # Safe, minimal changes with thorough validation
      - 'adaptive'         # Balanced approach with moderate changes and validation
      - 'experimental'     # Advanced features and experimental changes
      - 'test-automation'  # Focus on testing improvements and automation
      - 'build-optimization' # Focus on build and CI/CD improvements
      - 'error-resilience' # Focus on error handling and recovery patterns
      - 'ci-cd-enhancement' # Focus on CI/CD pipeline improvements
```

#### Evolution Types for Daily Automation
Include these evolution types for automated workflows:

```yaml
inputs:
  evolution_type:
    description: 'Type of evolution to perform'
    required: false
    default: 'consistency'
    type: choice
    options:
      - 'consistency'      # Fix inconsistencies across files and configurations
      - 'error_fixing'     # Resolve errors, bugs, and issues
      - 'documentation'    # Improve documentation quality and coverage
      - 'code_quality'     # Enhance code quality, patterns, and standards
      - 'security_updates' # Apply security improvements and updates
```

#### Intensity Levels
Define intensity levels for change scope:

```yaml
inputs:
  intensity:
    description: 'Scope and impact level of changes'
    required: false
    default: 'moderate'
    type: choice
    options:
      - 'minimal'         # Small, safe changes with low risk
      - 'moderate'        # Medium-sized improvements with moderate risk
      - 'comprehensive'   # Large-scale improvements with higher impact
```

#### Dry Run Support
ALL evolution workflows MUST include dry run capability:

```yaml
inputs:
  dry_run:
    description: 'Run in simulation mode without making actual changes'
    required: false
    default: false
    type: boolean
```

## Standard Workflow Patterns

### Environment Setup Pattern
All workflows should follow this environment setup pattern:

```yaml
- name: 🛠️ Setup Environment
  run: |
    set -euo pipefail
    if [ ! -f "./scripts/setup-environment.sh" ]; then
      echo "❌ Setup script not found!"
      exit 1
    fi
    chmod +x ./scripts/setup-environment.sh
    ./scripts/setup-environment.sh
```

### Script Execution Pattern
Always make scripts executable and include error handling:

```yaml
- name: 🧬 Execute Script
  run: |
    set -euo pipefail
    script_path="./scripts/script-name.sh"
    
    if [ ! -f "$script_path" ]; then
      echo "❌ Script not found: $script_path"
      exit 1
    fi
    
    chmod +x "$script_path"
    "$script_path" arg1 arg2
```

### Dry Run Implementation Pattern
Include dry run support in all evolution workflows:

```yaml
- name: 🔍 Dry Run - Preview Changes
  if: env.DRY_RUN == 'true' || inputs.dry_run == true
  run: |
    set -euo pipefail
    echo "🔍 DRY RUN MODE - Changes that would be applied:"
    
    if [ -f "/tmp/evolution_response.json" ]; then
      if command -v jq >/dev/null 2>&1; then
        cat "/tmp/evolution_response.json" | jq -r '.changes[] | "\(.type): \(.file)"' 2>/dev/null || echo "No changes preview available"
      else
        echo "Preview data available in /tmp/evolution_response.json"
      fi
    else
      echo "No preview data available"
    fi
```

### Error Validation Pattern
Include validation steps before critical operations:

```yaml
- name: 🔍 Validate Prerequisites
  run: |
    set -euo pipefail
    
    # Validate required files exist
    required_files=("./scripts/setup-environment.sh" "./scripts/evolution-engine.sh")
    for file in "${required_files[@]}"; do
      if [ ! -f "$file" ]; then
        echo "❌ Required file missing: $file"
        exit 1
      fi
    done
    
    # Validate environment variables
    required_vars=("EVOLUTION_VERSION" "WORKFLOW_TYPE")
    for var in "${required_vars[@]}"; do
      if [ -z "${!var:-}" ]; then
        echo "❌ Required environment variable missing: $var"
        exit 1
      fi
    done
    
    echo "✅ All prerequisites validated"
```

## Naming Conventions and Standards

### Step Naming Standards
- **Use Emojis**: Include descriptive emojis for improved readability
  - 🌱 for environment preparation
  - 🛠️ for setup and configuration
  - 🧬 for core evolution/processing
  - 🔍 for validation and dry runs
  - 📝 for documentation and reporting
  - 🚀 for deployment and release
  - 🧹 for cleanup operations

### Variable Naming Standards
- **Environment Variables**: Use UPPER_CASE (e.g., `EVOLUTION_VERSION`)
- **Local Variables**: Use lowercase with underscores (e.g., `script_path`)
- **Input Parameters**: Use lowercase with underscores (e.g., `dry_run`)

### File Path Standards
- **Temporary Files**: Use `/tmp/` for temporary workflow outputs
- **Scripts**: Use relative paths `./scripts/` for script execution
- **Configurations**: Store in predictable, documented locations
- **Artifacts**: Use workflow-specific directories under `/tmp/`

## Error Handling and Resilience

### Required Error Handling Patterns
- **Set Strict Mode**: Always use `set -euo pipefail` in multi-line scripts
- **Validate Inputs**: Check for required files, variables, and conditions
- **Meaningful Messages**: Provide actionable error messages with context
- **Graceful Degradation**: Include fallback mechanisms where appropriate

### Error Recovery Strategies
```yaml
- name: 🔧 Error Recovery
  if: failure()
  run: |
    set -euo pipefail
    
    echo "❌ Workflow failed - attempting recovery"
    
    # Log error context
    echo "Current directory: $(pwd)"
    echo "Available files: $(ls -la)"
    echo "Environment variables: $(env | grep -E '^(EVOLUTION|WORKFLOW)_')"
    
    # Attempt cleanup
    if [ -d "/tmp" ]; then
      echo "Cleaning temporary files..."
      find /tmp -name "*evolution*" -type f -delete 2>/dev/null || true
    fi
    
    # Store failure artifacts
    mkdir -p /tmp/failure-artifacts
    cp -r logs/* /tmp/failure-artifacts/ 2>/dev/null || true
```

## Token Management and Security

### Standard Token Usage
- **Primary Token**: Use `${{ secrets.PAT_TOKEN_TOKEN }}` for most operations
- **Custom Tokens**: Only use custom tokens when additional permissions required
- **Documentation**: Document any special token requirements in workflow comments

### Security Best Practices
```yaml
# Example of secure token usage
- name: 🔐 Secure Operation
  env:
    # Use least-privilege tokens
    GITHUB_TOKEN: ${{ secrets.PAT_TOKEN_TOKEN }}
  run: |
    # Never echo sensitive values
    echo "Performing operation with secured token"
    
    # Validate token permissions before use
    if ! gh auth status >/dev/null 2>&1; then
      echo "❌ GitHub token authentication failed"
      exit 1
    fi
```

## Version Management

### Version Consistency
- Update `EVOLUTION_VERSION` consistently across all workflows
- Document version changes in workflow comments
- Maintain backward compatibility when possible

### Version Header Template
```yaml
# AI Evolution Workflow - [Workflow Name]
# Version: 0.3.0
# Last Updated: 2025-07-20
# 
# Breaking Changes:
# - [List any breaking changes]
# 
# New Features:
# - [List new features]
```

## Testing and Validation

### Workflow Testing Standards
- **Independent Testing**: Test scripts independently before workflow integration
- **Validation Steps**: Include comprehensive validation at each stage
- **Debug Output**: Provide meaningful output for troubleshooting
- **Rollback Procedures**: Include rollback mechanisms for critical operations

### Test Execution Pattern
```yaml
- name: 🧪 Test Workflow Components
  run: |
    set -euo pipefail
    
    echo "🧪 Testing workflow components..."
    
    # Test script syntax
    for script in ./scripts/*.sh; do
      if [ -f "$script" ]; then
        echo "Checking syntax: $script"
        bash -n "$script" || {
          echo "❌ Syntax error in $script"
          exit 1
        }
      fi
    done
    
    # Test required tools
    required_tools=("jq" "gh" "git")
    for tool in "${required_tools[@]}"; do
      if ! command -v "$tool" >/dev/null 2>&1; then
        echo "❌ Required tool missing: $tool"
        exit 1
      fi
    done
    
    echo "✅ All tests passed"
```

## Workflow Template Examples

### Basic Evolution Workflow Template
```yaml
name: AI Evolution - [Purpose]

on:
  workflow_dispatch:
    inputs:
      growth_mode:
        description: 'Evolution approach and risk level'
        required: false
        default: 'adaptive'
        type: choice
        options:
          - 'conservative'
          - 'adaptive'
          - 'experimental'
      dry_run:
        description: 'Run in simulation mode'
        required: false
        default: false
        type: boolean

env:
  EVOLUTION_VERSION: "0.3.0"
  WORKFLOW_TYPE: "manual_evolution"

permissions:
  contents: write
  pull-requests: write
  issues: write

jobs:
  evolve:
    runs-on: ubuntu-latest
    
    steps:
    - name: 🌱 Prepare Evolution Environment
      uses: actions/checkout@v4
      with:
        fetch-depth: 0
        token: ${{ secrets.PAT_TOKEN_TOKEN }}
    
    - name: 🛠️ Setup Environment
      run: |
        set -euo pipefail
        chmod +x ./scripts/setup-environment.sh
        ./scripts/setup-environment.sh
    
    - name: 🔍 Validate Prerequisites
      run: |
        set -euo pipefail
        # Add validation logic here
    
    - name: 🧬 Execute Evolution
      run: |
        set -euo pipefail
        chmod +x ./scripts/evolution-engine.sh
        ./scripts/evolution-engine.sh "${{ inputs.growth_mode }}"
    
    - name: 🔍 Dry Run - Preview Changes
      if: inputs.dry_run == true
      run: |
        echo "🔍 DRY RUN MODE - Preview only"
        # Add dry run logic here
```

### Scheduled Maintenance Workflow Template
```yaml
name: Daily Evolution Maintenance

on:
  schedule:
    - cron: '0 3 * * *'  # Daily at 3 AM UTC
  workflow_dispatch:
    inputs:
      evolution_type:
        description: 'Type of evolution to perform'
        required: false
        default: 'consistency'
        type: choice
        options:
          - 'consistency'
          - 'error_fixing'
          - 'documentation'
          - 'code_quality'
          - 'security_updates'

env:
  EVOLUTION_VERSION: "0.3.0"
  WORKFLOW_TYPE: "scheduled_evolution"

permissions:
  contents: write
  pull-requests: write
  issues: write

jobs:
  daily-evolution:
    runs-on: ubuntu-latest
    
    steps:
    - name: 🌱 Prepare Evolution Environment
      uses: actions/checkout@v4
      with:
        fetch-depth: 0
        token: ${{ secrets.PAT_TOKEN_TOKEN }}
    
    # Add standard workflow steps here
```

## Integration with AI Evolution Engine

### Evolution Context Collection
```yaml
- name: 📊 Collect Evolution Context
  run: |
    set -euo pipefail
    
    echo "📊 Collecting repository context for evolution..."
    
    # Collect repository metrics
    ./scripts/collect-context.sh > /tmp/evolution-context.json
    
    # Validate context data
    if ! jq empty /tmp/evolution-context.json 2>/dev/null; then
      echo "❌ Invalid context data generated"
      exit 1
    fi
    
    echo "✅ Context collection completed"
```

### Change Application Pattern
```yaml
- name: 🔄 Apply Evolution Changes
  if: inputs.dry_run != true
  run: |
    set -euo pipefail
    
    echo "🔄 Applying evolution changes..."
    
    # Apply changes with validation
    ./scripts/apply-changes.sh /tmp/evolution_response.json
    
    # Validate applied changes
    if ! git diff --exit-code HEAD^ HEAD; then
      echo "✅ Changes successfully applied"
    else
      echo "⚠️ No changes were applied"
    fi
```

## Best Practices and Guidelines

### Performance Optimization
- Use GitHub Actions caching for dependencies and build artifacts
- Minimize checkout depth when full history isn't needed
- Parallel job execution for independent operations
- Efficient artifact storage and retrieval

### Maintainability
- Keep workflows focused on single responsibilities
- Use reusable composite actions for common patterns
- Document complex logic with inline comments
- Regular review and cleanup of unused workflows

### Monitoring and Observability
- Include timing information for performance tracking
- Log key decision points and execution paths
- Store artifacts for debugging and analysis
- Implement health checks for critical operations

---

*These instructions should be referenced when creating or modifying any GitHub Actions workflows in the AI-seed ecosystem.*
