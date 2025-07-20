# Copilot Instructions

Most current documentation is here: https://code.visualstudio.com/docs/copilot/overview

These instructions guide AI-powered development practices, focusing on programming standards, design patterns, and best practices across various technology stacks. The guidelines emphasize container-first development, ensuring all activities occur within isolated, reproducible environments. We prioritize Bash/Shell scripting due to its prevalence in the codebase, followed by Python and JavaScript/Node.js as accessible, open-source frameworks. For other languages or frameworks, extend these patterns analogously while adhering to core principles.

## Paths: Organic Growth Pathways in Software Development

### Core Concept of Paths
Drawing from the metaphor of seeds, plants, evolution, and sustainable growth, "Paths" represent the organic, evolving workflows, processes, and decision trees that guide every aspect of software development within the repository. Paths are dynamically defined, designed, and refined through collaborative efforts between humans and various AI agents, ensuring recursive self-improvement and adaptability. 

- **Organic Growth**: Paths emerge naturally from usage patterns, feedback loops, and evolution cycles, allowing the repository to grow like a living ecosystem. AI agents analyze existing structures, identify bottlenecks, and propose new paths that build upon previous ones, fostering interconnected knowledge and capabilities.
- **Path of Least Resistance**: This is the foundational principle—always prioritize workflows that minimize friction, complexity, and effort while maximizing efficiency, reusability, and sustainability. Paths should flow smoothly, avoiding unnecessary detours, and evolve to incorporate lessons from prior iterations.
- **AI Agent Integration**: Multiple AI agents (e.g., for code generation, testing, documentation, and orchestration) collaboratively define and design paths. Each agent contributes by analyzing data, simulating outcomes, and propagating improvements across the system, ensuring all information builds off one another in a cohesive, self-reinforcing manner.
- **Interconnectedness**: Paths are not isolated; they interconnect across building, testing, evolving, patching, deploying, organizing, programming, orchestrating, learning, documenting, branching, and other processes. Changes in one path trigger recursive updates in related paths, maintaining system-wide harmony.
- **Documentation and Evolution**: Every path must be documented in README.md files and headers, with AI agents simulating and validating path efficiency during evolution cycles. Paths evolve through daily automated checks, incorporating feedback to solidify successful routes and deprecate inefficient ones.

Paths overlay all existing guidelines, enhancing them with this organic, low-resistance framework. For instance, in code structure, functions define clear execution paths; in deployment, orchestration follows optimized deployment paths.

## Bash/Shell Scripting Standards and Design Patterns

### Naming Conventions
- Variables: Use lowercase with underscores (e.g., `my_variable`) to enhance readability and avoid conflicts, ensuring smooth data flow along execution paths.
- Constants: Use uppercase letters (e.g., `readonly MY_CONSTANT=value`) to signal immutability and provide stable anchors in evolving paths.
- Functions: Lowercase with underscores, descriptive of purpose (e.g., `process_input_data()`), clearly marking entry and exit points in workflow paths.
- Script Files: End with `.sh` extension; use meaningful, descriptive names (e.g., `deploy_application.sh`) that reflect the path they orchestrate.

### Code Structure
- Shebang: Always start with `#!/bin/bash` or `#!/usr/bin/env bash` for portability, initiating a clear starting point for the script's path.
- Strict Mode: Enable with `set -euo pipefail` to exit on errors, treat unset variables as errors, and prevent pipeline failures from derailing paths.
- Modularization: Break code into functions; keep scripts under 200 lines where possible. Source reusable functions from a `lib/` directory (e.g., `source lib/utils.sh`), creating interconnected paths that AI agents can evolve organically.
- Comments and Headers: Include comprehensive inline comments documenting paths (e.g., "This function defines the primary data processing path"). Adhere to file header standards (detailed in the Documentation Standards section) for every script, ensuring consistent metadata and path evolution tracking.

### Error Handling
- Traps: Use `trap cleanup_function ERR EXIT` for resource cleanup on errors or termination, ensuring paths can recover or rollback gracefully.
- Exit Status Checks: Explicitly check statuses (e.g., `command || { echo "Error: command failed"; exit 1; }`), redirecting to fallback paths when needed.
- Messages and Logging: Provide user-friendly error messages (e.g., `echo "Error: File not found at $path" >&2`). Log to stderr for errors and use a centralized logging function to track path deviations, allowing AI agents to analyze and refine them.

### Design Patterns
- **Modular Functions**: Encapsulate logic in reusable functions sourced from shared libraries to promote reuse across scripts, forming branching paths that merge efficiently.
- **Configuration Management**: Use associative arrays (e.g., `declare -A config`) or external config files (e.g., `.env` files loaded via `source`) for dynamic settings, enabling paths to adapt based on context.
- **Logging Pattern**: Create a centralized logger function supporting levels (e.g., `log_info()`, `log_error()`) with timestamps and optional file output, documenting path traversal for AI evolution.
- **Idempotency**: Ensure scripts can run multiple times without side effects (e.g., check if a file exists before creating it), supporting repeatable, low-resistance paths.
- **Dependency Injection**: Pass paths, commands, or tools as parameters (e.g., `function process { local tool=$1; ... }`) instead of hardcoding, allowing AI agents to inject optimized routes.

### Best Practices
- Variables: Avoid globals; use `local` for function-scoped variables. Declare constants with `readonly`, maintaining clear, uncluttered paths.
- Quoting: Always quote expansions (e.g., `"$variable"`) to prevent word splitting and globbing, ensuring data integrity along paths.
- Data Structures: Use arrays for lists (e.g., `files=(file1 file2)`) over space-separated strings, facilitating parallel or sequential path processing.
- Portability: Adhere to POSIX standards; test on multiple shells (e.g., bash, sh), ensuring paths are cross-platform.
- Security: Avoid `eval`; use secure practices like input sanitization, preventing vulnerabilities from blocking paths.

## Python Standards and Design Patterns

### Naming Conventions
- Variables/Functions: snake_case (e.g., `process_data()`), guiding clear navigation through code paths.
- Classes: CamelCase (e.g., `DataProcessor`), serving as hubs for multiple intersecting paths.
- Constants: UPPER_CASE (e.g., `MAX_RETRIES = 5`), providing fixed points in dynamic paths.
- Compliance: Follow PEP 8 for style, including line length (79 characters) and indentation (4 spaces), to minimize reading resistance.

### Code Structure
- Entry Point: Use `if __name__ == '__main__':` for executable scripts to allow module imports, defining a primary execution path while enabling modular reuse.
- Organization: Structure into modules/packages (e.g., `src/utils/data.py`); use relative imports to connect paths organically.
- Documentation: Include docstrings (Google or NumPy style) for functions, classes, and modules, describing parameters, returns, examples, and path flows. Adhere to file header standards for consistent metadata and path tracking.

### Error Handling
- Exceptions: Use `try-except` for specific exceptions (e.g., `except ValueError as e:`); avoid bare `except`, redirecting to recovery paths.
- Custom Exceptions: Define classes like `class AppError(Exception): pass` for domain-specific errors, signaling path branches.
- Logging: Use `logging` module with tracebacks (e.g., `logging.exception("Error occurred")`); configure levels to monitor path health.

### Design Patterns
- **Singleton**: Use metaclasses or modules for single instances (e.g., configuration managers), centralizing shared paths.
- **Factory**: Abstract object creation (e.g., `def create_processor(type): return ProcessorA() if type == 'A' else ProcessorB()`), dynamically selecting optimal paths.
- **Decorator**: Enhance functions (e.g., `@cache` for memoization), smoothing performance along frequent paths.
- **MVC**: Separate concerns in apps (Model for data paths, View for UI paths, Controller for logic orchestration), ensuring modular evolution.
- **Observer**: Implement event systems (e.g., using callbacks or `asyncio` for async notifications), creating reactive paths that AI agents can refine.

### Best Practices
- Environments: Use `venv` or `poetry` for isolation; pin dependencies in `requirements.txt`, containerizing paths for reproducibility.
- Typing: Add type hints (e.g., `def func(x: int) -> str:`); validate with `mypy`, clarifying data flows in paths.
- Testing: Write unit tests with `pytest`; aim for >80% coverage of critical paths.
- Output: Use `logging` over `print`; format logs consistently to trace path execution.
- Philosophy: Adhere to PEP 20 (e.g., "Simple is better than complex"), favoring paths of least resistance.

## JavaScript/Node.js Standards and Design Patterns

### Naming Conventions
- Variables/Functions: camelCase (e.g., `processData()`), facilitating intuitive path following.
- Classes/Constructors: PascalCase (e.g., `DataProcessor`), as key nodes in path networks.
- Constants: UPPER_CASE (e.g., `MAX_RETRIES = 5`), anchoring stable paths.

### Code Structure
- Modules: Use ES modules with `import/export`; organize into logical directories (e.g., `src/utils/`, `src/services/`), linking paths modularly.
- Documentation: Add JSDoc comments (e.g., `/** @param {string} input - The input data */`), describing paths. Adhere to file header standards for consistent metadata.

### Error Handling
- Synchronous: Use `try-catch` (e.g., `try { ... } catch (err) { console.error(err); }`), handling path interruptions.
- Asynchronous: Handle promises with `.catch()` or `async/await` in `try-catch`; propagate errors along fallback paths.
- Custom Errors: Extend `Error` (e.g., `class AppError extends Error { constructor(msg) { super(msg); } }`), for path-specific signaling.

### Design Patterns
- **Module Pattern**: Encapsulate code with IIFEs for private scopes, protecting internal paths.
- **Singleton**: Use modules or classes for singletons (e.g., exported object), centralizing global paths.
- **Factory**: Dynamic object creation (e.g., `function create(type) { return type === 'A' ? new A() : new B(); }`), branching paths efficiently.
- **Observer/Pub-Sub**: Use `EventEmitter` for events, enabling event-driven paths.
- **Middleware**: In Express.js, chain functions (e.g., `app.use(loggerMiddleware)`), sequencing request paths.

### Best Practices
- Linting: Use ESLint with standard configs (e.g., Airbnb style), enforcing clean paths.
- Async: Prefer `async/await` for readability; avoid callback hell, smoothing asynchronous paths.
- Packages: Manage with `npm` or `yarn`; lock versions in `package-lock.json`, containerizing dependency paths.
- Testing: Use Jest/Mocha for unit/integration tests; mock dependencies to isolate paths.
- Performance: Avoid blocking operations; use streams for large data, optimizing path throughput.

## General Guidelines Across Stacks

Follow core principles: DRY (Don't Repeat Yourself), KIS (Keep It Simple), DFF (Design for Failure), REnO (Release Early and Often), MVP (Minimum Viable Product), COLAB (Collaboration), AIPD (AI-Powered Development), RFD (README-First Development), and SCD (Script-Centric Development). Ensure container-first development for all activities, with paths guiding organic evolution.

### Container-First Development (CFD)
- **Ephemeral Environments**: Run all development, testing, and deployment in containers for reproducible paths.
- **Cross-Platform Compatibility**: Design for container portability; avoid OS-specific accommodations, ensuring universal paths.
- **Local Machine Isolation**: Execute no scripts/tests directly on host; use Docker wrappers to encapsulate paths.
- **Infrastructure as Code**: Define environments via Dockerfiles, Compose, or Kubernetes manifests, codifying deployment paths.
- **Stateless Operations**: Make processes stateless; use volumes for persistence, allowing paths to restart seamlessly.
- **Multi-Stage Builds**: Optimize images (e.g., build stage for dependencies, runtime for minimal footprint), reducing build path resistance.
- **Orchestration**: Use Docker Compose for local, Kubernetes for production, orchestrating multi-container paths.
- **Volume Management**: Employ named volumes/bind mounts; document data paths for persistence.
- **Network Isolation**: Secure networks; use policies for communication, protecting inter-container paths.
- **Resource Constraints**: Set CPU/memory limits/requests, allocating resources to high-traffic paths.
- **Health Checks**: Implement probes (e.g., HTTP endpoints or commands), monitoring path vitality.
- **Logging Strategy**: Centralize logs (e.g., via ELK stack or container stdout), tracing path executions for AI analysis.

### Design for Failure (DFF)
- Implement error handling, try-catch, and meaningful messages, with fallback paths for resilience.
- Add redundancy (e.g., retries), fallbacks, and logging/monitoring to reroute failed paths.
- Consider edge cases; include container resilience (auto-restarts) and health monitoring to heal paths organically.

### Don't Repeat Yourself (DRY)
- Extract reusable code into functions/modules, merging duplicate paths into shared routes.
- Refactor duplicates; use configs for constants, centralizing configuration paths.
- Employ templates for similar structures, templating common paths.

### Keep It Simple (KIS)
- Prioritize readable code; use descriptive names to illuminate paths.
- Break down complex logic; avoid over-abstraction, favoring straightforward paths.

### Release Early and Often (REnO)
- Use incremental development, feature flags, and versioning to evolve release paths iteratively.
- Integrate CI/CD in containers; use registries for artifacts, automating deployment paths.

### Minimum Viable Product (MVP)
- Focus on core features; iterate later, starting with minimal paths and expanding organically.
- Start with simple containers, evolve to complex architectures along proven paths.

### Collaboration (COLAB)
- Write self-documenting code; follow standards, documenting collaborative paths.
- Include READMEs; use semantic commits/PRs to branch and merge paths.

### AI-Powered Development (AIPD)
- Use AI for generation/review; balance with human oversight, with AI agents designing optimal paths.
- Integrate AI for testing/documentation; document usage, evolving AI paths recursively.

### README-First Development (RFD)
- Use README.md as primary context for AI/development, outlining directory paths.
- Document directories comprehensively; distinguish implemented vs. future features, planning path evolutions.
- Update before changes; optimize for AI comprehension, ensuring paths build on documented foundations.

### Script-Centric Development (SCD)
- Scripts in `scripts/` orchestrate workflows, relying on `src/` for functions, defining high-level paths.
- Design for container execution; provide Docker wrappers, containerizing script paths.

## Technology-Specific Guidelines

### Container Infrastructure Requirements
- **Docker Foundation**: Include Dockerfiles with multi-stage builds for dev/test/prod, optimizing build paths.
- **Composition**: Use Docker Compose for multi-service apps, composing service paths.
- **Cross-Platform**: Build multi-arch images (AMD64/ARM64), ensuring portable paths.
- **Security**: Scan images; use minimal bases (e.g., Alpine), securing container paths.
- **Dependencies**: Manage in images; use registries, resolving dependency paths.

### Containerized Development Workflows
- **Devcontainers**: Configure for VS Code/Codespaces with hot reload/debug, enabling live development paths.
- **Parity**: Ensure identical envs across stages, aligning paths from dev to prod.

### @azure Rule - Use Azure Best Practices
Invoke `azure_development-get_best_practices` tool for Azure-related operations.
- Integrate Azure Container Instances/Apps/Kubernetes; use Azure Container Registry, defining cloud-native paths.

### GitHub Models Prompt Format
- Use `.prompt.yml` files with structure: name, description, model (e.g., gpt-4o-mini), parameters, messages, testData, evaluators.
- Placeholders: `{{variable}}`, templating prompt paths.
- Reference: GitHub Models Documentation.

### Open Source Development
- Follow licensing; include attributions, encouraging community-defined paths.
- Use standard structures; encourage contributions to evolve paths collectively.

## Documentation Standards
- **Container-First**: Provide container-specific guidance; assume containerized envs, documenting container paths.
- **Directory-Level**: Every directory must contain a README.md file that:
  - Purpose: Explains the directory's role in the project and its paths.
  - Contents: Lists and describes all files and subdirectories, mapping their paths.
  - Usage: Provides examples of how to interact with the directory, following low-resistance paths.
  - Features: Details implemented functionality and active paths.
  - Future Enhancements: Lists planned features with status (e.g., "Planned", "In Progress"), outlining evolving paths.
  - Integration: Describes how it connects to other parts of the project, linking paths.
  - Container Context: Includes setup, ports, volumes, networks, and examples, containerizing documentation paths.
- **Organization**: Non-README.md/CHANGELOG.md Markdown files must be in `docs/` subdirectories (e.g., `docs/guides/`, `docs/reference/api/`). Use consistent naming (lowercase with hyphens) and cross-references to connect documentation paths.
- **Synchronization**: Update documentation concurrently with code changes. Use sections for technical accuracy and validation, ensuring docs evolve along code paths.
- **General Standards**: Include installation (container-based), usage, contribution guidelines. Add inline comments for logic; generate API/user guides documenting paths. Maintain CHANGELOG.md at root with semantic versioning, logging path evolutions.
- **Container-Specific**: Document ports (e.g., "Exposed: 8080/tcp for API paths"), volumes (e.g., "/app/data: persistent data paths"), environment variables, networks, resources (e.g., "Min CPU: 1 vCPU, Memory: 512MiB for path execution"), security, and health checks (e.g., "CMD: curl -f /health to verify path health").

### Automatic Documentation Generation
- Run tools (e.g., JSDoc, shdoc) in containers to generate MD from comments, automating doc paths.
- Store in `docs/`; validate for completeness/bidirectionality, syncing code and doc paths.
- Generate for configs/orchestration; ensure examples container-agnostic, following universal paths.

## Testing Approaches

### Container-Based Testing Strategy
- Run tests in isolated containers; create dedicated images for test paths.
- Orchestrate integration/E2E; manage data via volumes, testing end-to-end paths.
- Parallelize; ensure cross-platform, validating multiple path branches.

### Testing Framework Integration
- Unit/integration/E2E/performance/security tests in containers matching prod, covering critical paths.

### Test Execution and Reporting
- Orchestrate runs; generate reports tracing test paths; integrate into CI/CD; cleanup to reset paths.

## Code Quality Standards

### Container Security Best Practices
- Secure bases; scan vulnerabilities; run as non-root; manage secrets; secure networks; sign images; monitor runtime, protecting security paths.

### Performance Considerations
- Optimize readability; use caching; monitor; minimize layers/resources, tuning performance paths.

### Accessibility & Inclusivity
- Follow WCAG; inclusive language; i18n/l10n; test assistive tech, ensuring accessible paths.

## Learning & Education Focus

### Beginner-Friendly Approach
- Explain simply; steps/resources/exercises, guiding learners along introductory paths.
- Introduce containers early; hands-on, building foundational paths.

### Real-World Applications
- Practical examples; theory/practice, demonstrating real-world paths.
- Containerized projects; prod patterns, evolving learning paths.

### Community Learning
- Reviews/forums; share container configs, collaboratively refining community paths.

## AI Integration Guidelines

### AI-Assisted Container Development
- AI for configs/optimization/security, with agents designing container paths.
- Run tools in containers; constraint-aware, evolving AI-assisted paths.

### Best Practices for AI Tools
- Clear context; review; document, using AI to simulate and select least-resistance paths.
- Templates/feedback, recursively improving AI paths.

### Post-AI Prompt Cycle Validation
- Run `post-ai-validation.sh`; check configs/docs/paths.
- Address errors; refine, validating path integrity.

## Container Development Workflows

### Development Environment Setup
- Devcontainers/Compose; hot reload/ports/envs/tools, enabling fluid development paths.

### Container Lifecycle Management
- Automate builds/tagging/cleanup/scanning/updates, managing lifecycle paths.

### Monitoring and Observability
- Metrics/logs/tracing; health/alerting, observing path flows.

## File Header Standards

### Universal File Header Requirements
Every file MUST begin with a commented header containing standardized metadata. This applies to all types: source code (e.g., .py, .js, .sh), configuration (e.g., .yaml, .json), documentation (e.g., .md), scripts, templates, and others. 

**Exceptions**: 
- `.prompt.yml` or `.prompt.yaml` files follow GitHub Models format without custom headers.
- Binary files (e.g., images, executables) are exempt.

Headers use language-appropriate comment syntax (e.g., `/** */` for JS, `""" """` for Python, `#` for Shell/YAML). All fields are required unless marked optional; use "N/A" or "TBD" if not applicable. Fields must appear in the specified order. Lists (e.g., @relatedIssues) use bullet points with "- " prefix. Dates use YYYY-MM-DD format. Versions follow semantic versioning (major.minor.patch) or iteration number (e.g., v1.0.0).

Include a new field for paths:

### Header Template Structure
```
/**
 * @file [filename.ext] - Exact file name including extension.
 * @description [Brief one-sentence description of the file's purpose and primary functionality. Be concise yet informative.]
 * @author [Full Name or Team] <[email@domain.com]> - Creator or maintaining team; use consistent format.
 * @created [YYYY-MM-DD] - Date of initial creation.
 * @lastModified [YYYY-MM-DD] - Date of last update; update on every change.
 * @version [semantic.version or iteration.number] - Current version; increment on changes (e.g., 1.0.0 for initial, 1.0.1 for patches).
 * 
 * @relatedIssues 
 *   - #[issue-number]: [Brief description of related GitHub issue or ticket.]
 *   - #[issue-number]: [Another description.] (List at least one if applicable; use "N/A" if none.)
 * 
 * @relatedEvolutions
 *   - [evolution-cycle or version]: [Description of changes in AI/evolution cycles or major updates.]
 *   - [evolution-cycle]: [Another description.] (Document iterative improvements; "N/A" if none.)
 * 
 * @dependencies
 *   - [dependency-name]: [version or brief description, e.g., lodash: ^4.17.21.]
 *   - [dependency-name]: [Another.] (List external libraries/tools; "N/A" if none.)
 * 
 * @containerRequirements
 *   - baseImage: [Base container image and tag, e.g., node:18-alpine.]
 *   - exposedPorts: [Comma-separated list, e.g., 3000/tcp, 8080.]
 *   - volumes: [List of mounts, e.g., /app/data:rw.]
 *   - environment: [Required vars, e.g., NODE_ENV=production, LOG_LEVEL=info.]
 *   - resources: [Limits/requests, e.g., CPU: 0.5, Memory: 512MiB.]
 *   - healthCheck: [Command or endpoint, e.g., GET /health or curl -f http://localhost/health.] (All subfields required; "N/A" if not container-relevant.)
 * 
 * @paths
 *   - [path-name]: [Description of primary execution/learning/deployment/etc. path this file defines or contributes to, e.g., data-processing-path: Handles input validation to output transformation with fallback error path.]
 *   - [path-name]: [Another path description.] (Document key paths; "N/A" if none; emphasize least resistance.)
 * 
 * @changelog
 *   - [YYYY-MM-DD]: [Description of change] - [Author initials or name.]
 *   - [YYYY-MM-DD]: [Another change] - [Initials.]
 *   - [YYYY-MM-DD]: Initial creation - [Initials.] (At least one entry; add new at top.)
 * 
 * @usage [Brief example of how to use/invoke the file, e.g., node script.js --input file.txt. Include container context if applicable, and reference paths.]
 * @notes [Optional additional info, warnings, or TODOs. Use "N/A" if empty.]
 */
```

### Language-Specific Header Examples
[Examples updated similarly, adding @paths section, e.g., 
@paths
  - main-processing: Validates input, transforms data, with retry on failure.
  - error-recovery: Logs errors and falls back to default output.
]

### Header Maintenance Requirements

#### Creation Standards
- Include complete header in every new file before content, defining initial paths.
- Required fields mandatory; lists require at least "N/A" entry if empty.
- Use consistent formatting: Indent sub-items with 2-4 spaces; no trailing spaces.

#### Update Obligations
- Update @lastModified on any change (content or header).
- Increment @version: Patch for minor, minor for features, major for breaking.
- Add @changelog entry at top: Date, description (start with verb, e.g., "Added..."), initials.
- Link new @relatedIssues/@relatedEvolutions as relevant.
- Review @description/@usage/@paths for accuracy post-change, evolving path definitions.

#### Validation and Compliance
- Pre-commit hooks validate header presence/format/completeness, including paths.
- CI/CD pipelines fail on missing/invalid headers or undocumented paths.
- Code reviews check accuracy (e.g., dates match commits, paths reflect logic).
- Automated tools (e.g., scripts in containers) assist updates/audits of paths.
- Quarterly audits ensure currency and path interconnections.

### Integration with AI Evolution Engine
- Document @relatedEvolutions and @paths for AI cycles (e.g., "cycle-3: AI-refactored data path for least resistance").
- AI agents auto-update headers on modifications, refining paths.
- Maintain cross-file relationships in headers, mapping path networks.
- Use headers as context for AI-generated code/docs, simulating path efficiencies.

## Deployment Guidelines

### Container-First Deployment
- Orchestration for immutable/blue-green/canary/rollback; service mesh/auto-scaling, following optimized deployment paths.

### Environment Management
- Parity via configs/vars/resources/networks/monitoring, aligning environment paths.

### Infrastructure as Code
- Define/version configs; automate pipelines, codifying IaC paths.

## Migration and Legacy System Integration

### Container Migration Strategy
- Gradual; wrap legacies; data/config/testing/rollback, migrating along transitional paths.

### Hybrid Environment Management
- Gateways/discovery/security/monitoring; gradual replacement, integrating hybrid paths.