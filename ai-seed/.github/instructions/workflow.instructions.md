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
  - file: mcp.instructions.md
    description: Model Context Protocol integration and server automation

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
  mcp_integration_path:
    - server_discovery
    - capability_analysis
    - configuration_generation
    - integration_testing
    - deployment_validation

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

## MCP Integration Workflows

### MCP Server Deployment and Testing Workflow

#### Automated MCP Server Discovery
```yaml
name: MCP Server Discovery and Configuration

on:
  schedule:
    - cron: '0 6 * * *'  # Daily at 6 AM UTC
  workflow_dispatch:
    inputs:
      force_reconfiguration:
        description: 'Force reconfiguration of all MCP servers'
        required: false
        default: false
        type: boolean
      server_filter:
        description: 'Filter servers by type (filesystem, database, api, all)'
        required: false
        default: 'all'
        type: choice
        options:
          - 'all'
          - 'filesystem'
          - 'database'
          - 'api'

env:
  EVOLUTION_VERSION: "0.3.0"
  WORKFLOW_TYPE: "mcp_integration"

permissions:
  contents: write
  pull-requests: write
  issues: write

jobs:
  mcp-discovery:
    runs-on: ubuntu-latest
    
    steps:
    - name: 🌱 Prepare MCP Environment
      uses: actions/checkout@v4
      with:
        fetch-depth: 0
        token: ${{ secrets.PAT_TOKEN_TOKEN }}
    
    - name: 🛠️ Setup Environment
      run: |
        set -euo pipefail
        chmod +x ./scripts/setup-environment.sh
        ./scripts/setup-environment.sh
    
    - name: 🔍 Validate MCP Prerequisites
      run: |
        set -euo pipefail
        
        # Validate required tools
        required_tools=("docker" "docker-compose" "jq" "python3")
        for tool in "${required_tools[@]}"; do
          if ! command -v "$tool" >/dev/null 2>&1; then
            echo "❌ Required tool missing: $tool"
            exit 1
          fi
        done
        
        # Validate MCP server containers are available
        if ! docker-compose -f docker-compose.mcp.yml config >/dev/null 2>&1; then
          echo "❌ MCP Docker Compose configuration is invalid"
          exit 1
        fi
        
        echo "✅ All MCP prerequisites validated"
    
    - name: 🚀 Deploy MCP Servers
      run: |
        set -euo pipefail
        
        echo "🚀 Deploying MCP servers..."
        
        # Start MCP server infrastructure
        docker-compose -f docker-compose.mcp.yml up -d
        
        # Wait for servers to be ready
        sleep 30
        
        # Verify server health
        ./scripts/mcp/monitor-servers.sh --health-check-all
    
    - name: 🧬 Discover and Configure MCP Servers
      run: |
        set -euo pipefail
        
        chmod +x ./scripts/mcp/discover-servers.sh
        ./scripts/mcp/discover-servers.sh
        
        # Validate configuration files were generated
        if [ ! -f "config/mcp/client_config.json" ]; then
          echo "❌ MCP client configuration not generated"
          exit 1
        fi
        
        if [ ! -f "config/mcp/validation_report.json" ]; then
          echo "❌ MCP validation report not generated"
          exit 1
        fi
    
    - name: 🧪 Test MCP Integrations
      run: |
        set -euo pipefail
        
        echo "🧪 Testing MCP integrations..."
        
        # Run comprehensive integration tests
        chmod +x ./scripts/mcp/test-integrations.sh
        ./scripts/mcp/test-integrations.sh --comprehensive
        
        # Generate test results summary
        python3 -c "
        import json
        with open('config/mcp/validation_report.json', 'r') as f:
            report = json.load(f)
        
        success_rate = report['summary']['success_rate']
        total_servers = report['summary']['total_servers']
        healthy_servers = report['summary']['healthy_servers']
        
        print(f'MCP Integration Test Results:')
        print(f'- Total Servers: {total_servers}')
        print(f'- Healthy Servers: {healthy_servers}')
        print(f'- Success Rate: {success_rate}%')
        
        if success_rate < 80:
            print('❌ MCP integration test failed - success rate below 80%')
            exit(1)
        else:
            print('✅ MCP integration test passed')
        "
    
    - name: 📝 Generate MCP Documentation
      run: |
        set -euo pipefail
        
        echo "📝 Generating MCP integration documentation..."
        
        # Generate updated documentation
        python3 scripts/generate-mcp-docs.py
        
        # Validate documentation was generated
        if [ ! -f "docs/mcp-integration-guide.md" ]; then
          echo "❌ MCP documentation not generated"
          exit 1
        fi
    
    - name: 🔄 Create Configuration Update PR
      if: github.event_name == 'schedule' || inputs.force_reconfiguration == true
      run: |
        set -euo pipefail
        
        # Check if there are changes to commit
        if git diff --quiet && git diff --cached --quiet; then
          echo "No MCP configuration changes to commit"
          exit 0
        fi
        
        # Create branch for MCP updates
        branch_name="automated/mcp-config-update-$(date +%Y%m%d-%H%M%S)"
        git checkout -b "$branch_name"
        
        # Stage and commit changes
        git add config/mcp/ docs/mcp-*.md
        git commit -m "feat: automated MCP server configuration update
        
        - Updated MCP server discovery and configuration
        - Refreshed client configuration
        - Updated integration documentation
        - Validated server health and capabilities
        
        Generated by: ${{ github.workflow }} workflow
        Trigger: ${{ github.event_name }}
        Timestamp: $(date -Iseconds)"
        
        # Push branch and create PR
        git push origin "$branch_name"
        
        gh pr create \
          --title "Automated MCP Configuration Update" \
          --body "This PR contains automated updates to MCP server configurations and documentation.
        
        ## Changes Include:
        - 🔄 Updated MCP server discovery results
        - ⚙️ Refreshed client configuration files
        - 📚 Updated integration documentation
        - ✅ Validated server health and capabilities
        
        ## Test Results:
        $(cat config/mcp/validation_report.json | jq -r '.summary | \"- Total Servers: \" + (.total_servers | tostring) + \"\n- Healthy Servers: \" + (.healthy_servers | tostring) + \"\n- Success Rate: \" + (.success_rate | tostring) + \"%\"')
        
        This PR was automatically generated by the MCP Discovery workflow." \
          --assignee "${{ github.actor }}" \
          --label "automated,mcp,configuration"
      env:
        GITHUB_TOKEN: ${{ secrets.PAT_TOKEN_TOKEN }}
    
    - name: 🧹 Cleanup MCP Test Environment
      if: always()
      run: |
        set -euo pipefail
        
        echo "🧹 Cleaning up MCP test environment..."
        
        # Stop MCP servers if running
        docker-compose -f docker-compose.mcp.yml down --remove-orphans || true
        
        # Clean up temporary files
        rm -rf tmp/mcp-* || true
        rm -rf tmp/test_mcp_* || true
        
        echo "✅ Cleanup completed"
```

#### MCP Server Health Monitoring Workflow
```yaml
name: MCP Server Health Monitoring

on:
  schedule:
    - cron: '*/15 * * * *'  # Every 15 minutes
  workflow_dispatch:

env:
  EVOLUTION_VERSION: "0.3.0"
  WORKFLOW_TYPE: "mcp_monitoring"

permissions:
  contents: read
  issues: write

jobs:
  health-monitoring:
    runs-on: ubuntu-latest
    
    steps:
    - name: 🌱 Prepare Monitoring Environment
      uses: actions/checkout@v4
      with:
        fetch-depth: 1
        token: ${{ secrets.PAT_TOKEN_TOKEN }}
    
    - name: 🛠️ Setup Monitoring Tools
      run: |
        set -euo pipefail
        chmod +x ./scripts/setup-environment.sh
        ./scripts/setup-environment.sh --monitoring-only
    
    - name: 🔍 Monitor MCP Server Health
      run: |
        set -euo pipefail
        
        echo "🔍 Monitoring MCP server health..."
        
        # Run health checks
        chmod +x ./scripts/mcp/monitor-servers.sh
        ./scripts/mcp/monitor-servers.sh --health-check-all --output-json > /tmp/health_report.json
        
        # Analyze health report
        python3 -c "
        import json
        import sys
        
        with open('/tmp/health_report.json', 'r') as f:
            health_data = json.load(f)
        
        unhealthy_servers = [
            server for server, status in health_data.get('servers', {}).items()
            if status.get('status') != 'healthy'
        ]
        
        if unhealthy_servers:
            print(f'❌ Unhealthy MCP servers detected: {unhealthy_servers}')
            
            # Create or update GitHub issue
            import subprocess
            import os
            
            issue_title = f'MCP Server Health Alert - {len(unhealthy_servers)} server(s) unhealthy'
            issue_body = f'''
# MCP Server Health Alert

**Alert Time:** {health_data.get('timestamp', 'unknown')}
**Unhealthy Servers:** {len(unhealthy_servers)}

## Server Status Details:

'''
            
            for server in unhealthy_servers:
                status = health_data['servers'][server]
                issue_body += f'''
### {server}
- **Status:** {status.get('status', 'unknown')}
- **Error:** {status.get('error', 'No error details')}
- **Last Check:** {status.get('last_check', 'unknown')}
'''
            
            issue_body += '''
## Recommended Actions:
1. Check server container logs: `docker logs mcp-{server_name}`
2. Restart unhealthy servers: `docker-compose -f docker-compose.mcp.yml restart`
3. Review server configuration and dependencies
4. Monitor for recovery in next health check cycle

This issue was automatically generated by the MCP Health Monitoring workflow.
'''
            
            # Check if existing health alert issue exists
            result = subprocess.run([
                'gh', 'issue', 'list', 
                '--label', 'mcp-health-alert',
                '--state', 'open',
                '--json', 'number,title'
            ], capture_output=True, text=True, env=dict(os.environ, GITHUB_TOKEN='${{ secrets.PAT_TOKEN_TOKEN }}'))
            
            if result.returncode == 0:
                issues = json.loads(result.stdout)
                if issues:
                    # Update existing issue
                    issue_number = issues[0]['number']
                    subprocess.run([
                        'gh', 'issue', 'edit', str(issue_number),
                        '--title', issue_title,
                        '--body', issue_body
                    ], env=dict(os.environ, GITHUB_TOKEN='${{ secrets.PAT_TOKEN_TOKEN }}'))
                    print(f'Updated existing health alert issue #{issue_number}')
                else:
                    # Create new issue
                    subprocess.run([
                        'gh', 'issue', 'create',
                        '--title', issue_title,
                        '--body', issue_body,
                        '--label', 'mcp-health-alert,bug,automated'
                    ], env=dict(os.environ, GITHUB_TOKEN='${{ secrets.PAT_TOKEN_TOKEN }}'))
                    print('Created new health alert issue')
            
            sys.exit(1)
        else:
            print('✅ All MCP servers are healthy')
            
            # Close any existing health alert issues
            result = subprocess.run([
                'gh', 'issue', 'list', 
                '--label', 'mcp-health-alert',
                '--state', 'open',
                '--json', 'number'
            ], capture_output=True, text=True, env=dict(os.environ, GITHUB_TOKEN='${{ secrets.PAT_TOKEN_TOKEN }}'))
            
            if result.returncode == 0:
                issues = json.loads(result.stdout)
                for issue in issues:
                    subprocess.run([
                        'gh', 'issue', 'close', str(issue['number']),
                        '--comment', 'MCP servers have recovered. All servers are now healthy. Auto-closing this alert.'
                    ], env=dict(os.environ, GITHUB_TOKEN='${{ secrets.PAT_TOKEN_TOKEN }}'))
                    print(f'Closed resolved health alert issue #{issue[\"number\"]}')
        "
      env:
        GITHUB_TOKEN: ${{ secrets.PAT_TOKEN_TOKEN }}
```

### MCP-Enhanced Evolution Workflows

#### Context-Aware Evolution with MCP
```yaml
name: MCP-Enhanced AI Evolution

on:
  workflow_dispatch:
    inputs:
      evolution_focus:
        description: 'Focus area for evolution'
        required: false
        default: 'mcp_integration'
        type: choice
        options:
          - 'mcp_integration'
          - 'context_optimization'
          - 'server_capabilities'
          - 'client_improvements'
      mcp_context_sources:
        description: 'MCP context sources to utilize'
        required: false
        default: 'all'
        type: choice
        options:
          - 'all'
          - 'filesystem'
          - 'database'
          - 'api'
          - 'git'

env:
  EVOLUTION_VERSION: "0.3.0"
  WORKFLOW_TYPE: "mcp_enhanced_evolution"

permissions:
  contents: write
  pull-requests: write
  issues: write

jobs:
  mcp-enhanced-evolution:
    runs-on: ubuntu-latest
    
    steps:
    - name: 🌱 Prepare MCP-Enhanced Evolution Environment
      uses: actions/checkout@v4
      with:
        fetch-depth: 0
        token: ${{ secrets.PAT_TOKEN_TOKEN }}
    
    - name: 🛠️ Setup MCP Environment
      run: |
        set -euo pipefail
        chmod +x ./scripts/setup-environment.sh
        ./scripts/setup-environment.sh --with-mcp
        
        # Start MCP servers for context collection
        docker-compose -f docker-compose.mcp.yml up -d
        sleep 30  # Allow servers to initialize
    
    - name: 📊 Collect MCP Context
      run: |
        set -euo pipefail
        
        echo "📊 Collecting comprehensive context via MCP servers..."
        
        # Collect context from specified sources
        mkdir -p /tmp/mcp-context
        
        context_sources="${{ inputs.mcp_context_sources }}"
        if [ "$context_sources" = "all" ]; then
          context_sources="filesystem git docker"
        fi
        
        for source in $context_sources; do
          echo "Collecting $source context..."
          ./scripts/lib/mcp_context.sh collect_mcp_context "$source" "/tmp/mcp-context/${source}_context.json"
        done
        
        # Aggregate all context into comprehensive dataset
        python3 -c "
        import json
        import glob
        import os
        
        aggregated_context = {
            'collection_timestamp': '$(date -Iseconds)',
            'evolution_focus': '${{ inputs.evolution_focus }}',
            'context_sources': '$context_sources'.split(),
            'contexts': {}
        }
        
        for context_file in glob.glob('/tmp/mcp-context/*_context.json'):
            context_type = os.path.basename(context_file).replace('_context.json', '')
            try:
                with open(context_file, 'r') as f:
                    context_data = json.load(f)
                aggregated_context['contexts'][context_type] = context_data
                print(f'✅ Loaded {context_type} context')
            except Exception as e:
                print(f'❌ Failed to load {context_type} context: {e}')
        
        with open('/tmp/mcp-evolution-context.json', 'w') as f:
            json.dump(aggregated_context, f, indent=2)
        
        print(f'📋 Aggregated context from {len(aggregated_context[\"contexts\"])} sources')
        "
    
    - name: 🧬 Execute MCP-Enhanced Evolution
      run: |
        set -euo pipefail
        
        echo "🧬 Executing MCP-enhanced evolution..."
        
        # Use MCP context for enhanced evolution
        chmod +x ./scripts/evolution-engine.sh
        
        # Pass MCP context to evolution engine
        export MCP_CONTEXT_FILE="/tmp/mcp-evolution-context.json"
        export EVOLUTION_FOCUS="${{ inputs.evolution_focus }}"
        
        ./scripts/evolution-engine.sh \
          --mode "mcp-enhanced" \
          --focus "${{ inputs.evolution_focus }}" \
          --context-file "/tmp/mcp-evolution-context.json"
    
    - name: 🔍 Validate MCP Integration Improvements
      run: |
        set -euo pipefail
        
        echo "🔍 Validating MCP integration improvements..."
        
        # Test that MCP integrations still work after evolution
        ./scripts/mcp/test-integrations.sh --post-evolution
        
        # Validate any new MCP-related code
        if find . -name "*.py" -path "*/mcp/*" -newer /tmp/evolution_start_time 2>/dev/null | head -1; then
          echo "Found new MCP-related Python code, running validation..."
          python3 -m py_compile $(find . -name "*.py" -path "*/mcp/*" -newer /tmp/evolution_start_time)
        fi
        
        if find . -name "*.ts" -path "*/mcp/*" -newer /tmp/evolution_start_time 2>/dev/null | head -1; then
          echo "Found new MCP-related TypeScript code, running validation..."
          npx tsc --noEmit $(find . -name "*.ts" -path "*/mcp/*" -newer /tmp/evolution_start_time)
        fi
    
    - name: 📈 Generate MCP Evolution Report
      run: |
        set -euo pipefail
        
        echo "📈 Generating MCP evolution report..."
        
        # Generate comprehensive evolution report
        python3 -c "
        import json
        import os
        from datetime import datetime
        
        # Load evolution results if available
        evolution_results = {}
        if os.path.exists('/tmp/evolution_response.json'):
            with open('/tmp/evolution_response.json', 'r') as f:
                evolution_results = json.load(f)
        
        # Load MCP context
        mcp_context = {}
        if os.path.exists('/tmp/mcp-evolution-context.json'):
            with open('/tmp/mcp-evolution-context.json', 'r') as f:
                mcp_context = json.load(f)
        
        # Generate report
        report = {
            'report_timestamp': datetime.now().isoformat(),
            'evolution_focus': '${{ inputs.evolution_focus }}',
            'mcp_context_sources': mcp_context.get('context_sources', []),
            'evolution_summary': {
                'total_changes': len(evolution_results.get('changes', [])),
                'mcp_related_changes': len([
                    change for change in evolution_results.get('changes', [])
                    if 'mcp' in change.get('file', '').lower() or 'mcp' in change.get('description', '').lower()
                ]),
                'context_sources_used': len(mcp_context.get('contexts', {})),
                'enhancement_areas': evolution_results.get('enhancement_areas', [])
            },
            'mcp_integration_status': 'enhanced' if evolution_results else 'unchanged',
            'recommendations': evolution_results.get('recommendations', [])
        }
        
        with open('/tmp/mcp-evolution-report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print('📋 MCP evolution report generated')
        print(f'- Total changes: {report[\"evolution_summary\"][\"total_changes\"]}')
        print(f'- MCP-related changes: {report[\"evolution_summary\"][\"mcp_related_changes\"]}')
        print(f'- Context sources used: {report[\"evolution_summary\"][\"context_sources_used\"]}')
        "
    
    - name: 🧹 Cleanup MCP Evolution Environment
      if: always()
      run: |
        set -euo pipefail
        
        echo "🧹 Cleaning up MCP evolution environment..."
        
        # Archive evolution artifacts
        mkdir -p artifacts/mcp-evolution
        cp /tmp/mcp-evolution-context.json artifacts/mcp-evolution/ 2>/dev/null || true
        cp /tmp/mcp-evolution-report.json artifacts/mcp-evolution/ 2>/dev/null || true
        cp /tmp/evolution_response.json artifacts/mcp-evolution/ 2>/dev/null || true
        
        # Stop MCP servers
        docker-compose -f docker-compose.mcp.yml down --remove-orphans || true
        
        # Clean temporary files
        rm -rf /tmp/mcp-* || true
        
        echo "✅ MCP evolution cleanup completed"
```

---

*These instructions should be referenced when creating or modifying any GitHub Actions workflows in the AI-seed ecosystem.*
