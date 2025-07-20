# Copilot Instructions

https://code.visualstudio.com/docs/copilot/overview

These instructions guide AI-powered development practices through the fundamental principle of **Paths** - the natural, organic routes that emerge in software development. Like water finding its way through terrain, code and information follow paths of least resistance, creating interconnected networks of knowledge and functionality. AI agents continuously discover, define, and refine these paths, enabling sustainable growth and evolution. The guidelines emphasize container-first development within this path-based framework, ensuring all activities occur within isolated, reproducible environments that can flow seamlessly across different contexts.

## 🌊 The Path Philosophy: Natural Flow in Software Development

### Core Principle: Path of Least Resistance
Software development, like natural systems, inherently follows paths of least resistance. This principle guides every aspect of our work:
- **Code Paths**: Functions naturally flow into one another, creating execution paths that minimize complexity
- **Data Paths**: Information flows through the system via the most efficient routes
- **Knowledge Paths**: Documentation and learning materials connect concepts through intuitive pathways
- **Evolution Paths**: Changes propagate through the codebase following established patterns
- **Collaboration Paths**: Teams interact through well-worn communication channels

### Path Types and Their Interconnections
- **Building Paths**: Code compilation and assembly follow dependency graphs that represent natural build orders
- **Testing Paths**: Test suites traverse the codebase through logical branches, covering critical routes first
- **Evolution Paths**: AI agents identify and follow paths for incremental improvements
- **Patching Paths**: Fixes flow through the system via minimal change routes
- **Deployment Paths**: Applications move from development to production through staged pathways
- **Organization Paths**: File structures emerge organically, creating intuitive navigation routes
- **Programming Paths**: Design patterns create well-traveled routes for solving common problems
- **Orchestration Paths**: Services connect through optimal communication pathways
- **Learning Paths**: Knowledge builds progressively, each concept paving the way for the next
- **Documentation Paths**: Information links create a web of interconnected understanding
- **Branching Paths**: Version control follows natural divergence and convergence patterns

### AI Agents as Path Architects
AI agents serve as intelligent guides that:
- **Discover Paths**: Identify existing patterns and routes within the codebase
- **Design Paths**: Create new pathways for functionality, testing, and deployment
- **Optimize Paths**: Refine routes to reduce friction and improve efficiency
- **Connect Paths**: Build bridges between isolated components
- **Document Paths**: Map the terrain for future travelers
- **Evolve Paths**: Adapt routes based on usage patterns and feedback

### Organic Growth Through Path Networks
Repositories grow like living organisms:
- **Natural Emergence**: Paths form organically through use and need
- **Interconnected Networks**: Information and code build upon each other
- **Adaptive Evolution**: Paths adjust to changing requirements and contexts
- **Collective Intelligence**: Multiple AI agents contribute to path definition
- **Sustainable Expansion**: Growth follows established patterns while allowing innovation

## Path-Driven Development Standards

### Path Discovery in Bash/Shell Scripting

#### Naming Conventions Follow Natural Paths
- Variables: Follow data flow paths (e.g., `input_data` → `processed_data` → `output_result`)
- Functions: Name by their position in execution paths (e.g., `validate_input()` → `process_data()` → `format_output()`)
- Scripts: Indicate their role in workflow paths (e.g., `01_setup.sh`, `02_build.sh`, `03_deploy.sh`)

#### Code Structure Creates Clear Paths
- **Entry Points**: Define clear starting paths with descriptive comments
- **Flow Control**: Use path-based logic that follows natural decision trees
- **Modular Paths**: Break scripts into functions that represent path segments
- **Path Documentation**: Comment each path junction and destination

```bash
#!/bin/bash
# Path: Environment Setup → Validation → Execution → Cleanup

# Define the main execution path
main() {
    # Path segment: Initial validation
    validate_environment || return 1
    
    # Path segment: Core processing
    process_workflow || return 2
    
    # Path segment: Results handling
    handle_results || return 3
    
    # Path segment: Cleanup
    cleanup_resources
}

# Each function represents a segment in the execution path
```

### Path-Aware Error Handling
- **Path Preservation**: Errors maintain context about which path failed
- **Fallback Paths**: Define alternative routes when primary paths fail
- **Path Logging**: Track the journey through the code for debugging

```bash
# Example of path-aware error handling
execute_with_fallback() {
    local primary_path="$1"
    local fallback_path="$2"
    
    # Try primary path
    if ! $primary_path 2>/dev/null; then
        log_path_failure "Primary path failed: $primary_path"
        # Follow fallback path
        $fallback_path || return 1
    fi
}
```

### Python Path Patterns

#### Path-Based Architecture
- **Import Paths**: Organize imports to reflect dependency paths
- **Execution Paths**: Design clear flows from input to output
- **Data Paths**: Create pipelines that transform data along defined routes

```python
# Path: Input Validation → Data Processing → Output Generation

class DataPipeline:
    """Represents a path through data transformation stages."""
    
    def __init__(self):
        self.path_history = []
    
    def follow_path(self, data):
        """Follow the transformation path."""
        # Path segment 1: Validation
        validated = self._validate_input(data)
        self.path_history.append("validation")
        
        # Path segment 2: Processing
        processed = self._process_data(validated)
        self.path_history.append("processing")
        
        # Path segment 3: Output
        result = self._generate_output(processed)
        self.path_history.append("output")
        
        return result
```

### JavaScript/Node.js Path Navigation

#### Asynchronous Path Management
- **Promise Paths**: Chain operations along asynchronous paths
- **Event Paths**: Define clear event flow routes through the application
- **Module Paths**: Organize code to reflect functional pathways

```javascript
// Path: Request → Validation → Processing → Response

class RequestPath {
    constructor() {
        this.pathSegments = [];
    }
    
    async followPath(request) {
        // Define the path through middleware
        const path = [
            this.validateRequest,
            this.authenticateUser,
            this.processRequest,
            this.formatResponse
        ];
        
        // Follow each segment of the path
        let result = request;
        for (const segment of path) {
            result = await segment.call(this, result);
            this.pathSegments.push(segment.name);
        }
        
        return result;
    }
}
```

## Container Paths: Isolated Journey Networks

### Container-First Path Development
- **Build Paths**: Multi-stage Dockerfiles create clear transformation paths
- **Deployment Paths**: Containers flow through development → staging → production
- **Network Paths**: Service discovery creates dynamic communication routes
- **Volume Paths**: Data flows through well-defined storage pathways

```dockerfile
# Path: Source → Dependencies → Build → Runtime

# Path Segment 1: Build Environment
FROM node:18-alpine AS builder
WORKDIR /build-path
COPY package*.json ./
RUN npm ci --only=production

# Path Segment 2: Application Build
COPY . .
RUN npm run build

# Path Segment 3: Runtime Path
FROM node:18-alpine AS runtime
WORKDIR /app-path
COPY --from=builder /build-path/dist ./dist
COPY --from=builder /build-path/node_modules ./node_modules

# Define the execution path
CMD ["node", "dist/index.js"]
```

### Orchestration Paths
- **Service Paths**: Define how services discover and communicate
- **Scaling Paths**: Automatic scaling follows load distribution paths
- **Health Check Paths**: Monitoring follows defined inspection routes

```yaml
# docker-compose.yml - Defining service communication paths
version: '3.8'

services:
  # Path: Client → Gateway → Services → Database
  
  gateway:
    build:
      context: .
      dockerfile: gateway.Dockerfile
    environment:
      - SERVICE_PATHS=api:3000,auth:3001,data:3002
    networks:
      - service-path
  
  api:
    build: ./api
    networks:
      - service-path
    depends_on:
      - database
  
  database:
    image: postgres:15
    networks:
      - service-path
    volumes:
      - data-path:/var/lib/postgresql/data

networks:
  service-path:
    driver: bridge

volumes:
  data-path:
```

## Path-Driven Documentation

### README as Path Maps
- **Navigation Paths**: Structure READMEs to guide readers through natural learning paths
- **Cross-Reference Paths**: Create links that form knowledge networks
- **Example Paths**: Show complete journeys from problem to solution

```markdown
# Project Path Guide

## Quick Start Path
1. **Setup Path**: Clone → Install → Configure
2. **Development Path**: Code → Test → Build
3. **Deployment Path**: Package → Deploy → Monitor

## Learning Paths
- **Beginner Path**: [Concepts](docs/concepts.md) → [Tutorial](docs/tutorial.md) → [First Project](docs/first-project.md)
- **Advanced Path**: [Architecture](docs/architecture.md) → [Patterns](docs/patterns.md) → [Optimization](docs/optimization.md)

## Troubleshooting Paths
- **Error Resolution Path**: [Common Errors](docs/errors.md) → [Debugging Guide](docs/debugging.md) → [Support](docs/support.md)
```

### Documentation Path Networks
- **Hierarchical Paths**: Information flows from general to specific
- **Circular Paths**: Related concepts link back to each other
- **Discovery Paths**: Search and navigation follow intuitive routes

## Testing Along Natural Paths

### Path-Based Test Design
- **Happy Paths**: Test the most common, successful routes
- **Edge Paths**: Explore boundary conditions and unusual routes
- **Error Paths**: Verify failure handling along exception routes

```javascript
describe('User Journey Paths', () => {
    describe('Registration Path', () => {
        test('follows happy path: form → validation → creation → welcome', async () => {
            const journey = new UserJourney();
            const result = await journey.followPath('registration', userData);
            expect(journey.pathHistory).toEqual([
                'form_submission',
                'data_validation',
                'account_creation',
                'welcome_email'
            ]);
        });
        
        test('follows error path: form → validation → error → retry', async () => {
            const journey = new UserJourney();
            const result = await journey.followPath('registration', invalidData);
            expect(journey.pathHistory).toContain('validation_error');
            expect(journey.pathHistory).toContain('retry_prompt');
        });
    });
});
```

### Test Coverage Paths
- **Critical Paths**: Ensure 100% coverage of essential routes
- **Integration Paths**: Test how components connect and communicate
- **Performance Paths**: Measure efficiency along common routes

## Evolution Paths: AI-Guided Growth

### Recursive Path Improvement
- **Path Analysis**: AI agents analyze existing paths for optimization opportunities
- **Path Evolution**: Gradual refinement of routes based on usage patterns
- **Path Prediction**: Anticipate future paths based on current trends

```yaml
# evolution-paths.yml
evolution_cycles:
  - cycle: "path-optimization-2024-01"
    discoveries:
      - inefficient_path: "data_processing → validation → storage"
      - optimized_path: "parallel_validation → data_processing → storage"
      - improvement: "40% reduction in processing time"
    
  - cycle: "path-extension-2024-02"  
    additions:
      - new_path: "data_processing → analytics → insights"
      - connects_to: ["reporting_path", "dashboard_path"]
      - enables: "real-time analytics capabilities"
```

### Path Metrics and Monitoring
- **Path Usage**: Track which routes are most traveled
- **Path Performance**: Measure efficiency of different routes
- **Path Health**: Monitor for broken or degraded paths

## Learning Paths: Progressive Knowledge Building

### Structured Learning Journeys
- **Foundation Paths**: Core concepts that enable further learning
- **Skill Paths**: Progressive routes from beginner to expert
- **Project Paths**: Hands-on journeys through real implementations

```markdown
## Developer Learning Path

### Phase 1: Foundation Path (Week 1-2)
- [ ] Environment Setup → Basic Syntax → First Script
- [ ] Version Control → Branching → Collaboration

### Phase 2: Building Path (Week 3-4)
- [ ] Design Patterns → Implementation → Testing
- [ ] Debugging → Optimization → Deployment

### Phase 3: Advanced Path (Week 5-6)
- [ ] Architecture → Scaling → Monitoring
- [ ] Security → Performance → Maintenance
```

## Path Maintenance and Governance

### Path Lifecycle Management
- **Path Creation**: Document new paths as they emerge
- **Path Validation**: Ensure paths remain functional and efficient
- **Path Deprecation**: Gracefully sunset obsolete routes
- **Path Migration**: Guide transitions from old to new paths

### Path Security
- **Access Paths**: Define and monitor authorization routes
- **Audit Paths**: Track usage for compliance and security
- **Isolation Paths**: Ensure sensitive routes are properly protected

## File Header Standards with Path Context

### Path-Aware Headers
Headers now include path information to show how files connect:

```javascript
/**
 * @file utils/dataProcessor.js
 * @description Utility functions for data transformation along the processing pipeline path
 * @author IT-Journey Team <team@it-journey.org>
 * @created 2025-07-05
 * @lastModified 2025-07-16
 * @version 1.2.0
 * 
 * @pathContext
 *   - incomingPaths: [api/routes/upload.js, queue/consumers/dataConsumer.js]
 *   - outgoingPaths: [storage/repositories/dataRepo.js, analytics/processors/analyzer.js]
 *   - parallelPaths: [validators/dataValidator.js, formatters/dataFormatter.js]
 * 
 * @relatedIssues 
 *   - #145: Optimize data processing path for large files
 *   - #167: Add alternative path for malformed data
 * 
 * ... (rest of standard header)
 */
```

## Integration with Existing Principles

### Path-Enhanced Core Principles
- **DRY**: Reuse established paths instead of creating redundant routes
- **KIS**: Choose the simplest path that accomplishes the goal
- **DFF**: Design multiple paths to handle failures gracefully
- **REnO**: Release along incremental paths, building on previous releases
- **MVP**: Define the minimal path to deliver value
- **COLAB**: Create clear paths for team communication and contribution
- **AIPD**: Let AI agents discover and optimize paths
- **RFD**: READMEs map the paths through the codebase
- **SCD**: Scripts orchestrate journeys along defined paths
- **CFD**: Containers provide consistent paths across environments

### Path-First Development Workflow
1. **Identify Natural Paths**: Before coding, map the natural flow of data and control
2. **Design Path Networks**: Create interconnected routes that build on each other
3. **Implement Along Paths**: Code follows the designed pathways
4. **Test Path Integrity**: Verify all paths function as expected
5. **Document Path Maps**: Create guides for navigating the codebase
6. **Monitor Path Health**: Track usage and performance of different routes
7. **Evolve Path Networks**: Let paths grow and adapt organically

## Conclusion: The Living Path Network

Software repositories are living networks of interconnected paths. Like a garden where footpaths emerge from regular use, our codebases develop natural routes that connect functionality, knowledge, and people. AI agents act as gardeners, tending these paths, creating new connections, and ensuring the network remains healthy and navigable. By embracing the path of least resistance, we create software that flows naturally, scales organically, and evolves sustainably.

Every line of code, every test, every document is both a step on a path and a potential junction for new routes. As paths interconnect and build upon each other, they create a rich ecosystem where information and functionality flow freely, enabling rapid development and continuous evolution.