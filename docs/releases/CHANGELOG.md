# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.5.0] - 2025-11-29

### Added

- **PRD MACHINE** - AI-powered Product Requirements Document automation system
  - New Django app `apps/prd_machine/` with complete service layer architecture
  - **Models**: `PRDState`, `PRDVersion`, `PRDEvent`, `PRDConflict`, `PRDExport` for full PRD lifecycle tracking
  - **Core Service**: `PRDMachineService` with AI-powered capabilities:
    - PRD synchronization from GitHub repositories
    - AI-driven PRD distillation and evolution from repository signals
    - PRD generation from scratch via repository analysis
    - Conflict detection between PRD and actual code state
    - Export to GitHub issues, changelog generation
    - Zero-touch mode for fully automated PRD management
  - **Celery Tasks**: 10 async tasks for GitHub webhook processing and scheduled operations
    - `process_github_push_event` - Auto-distill PRD on commits
    - `process_github_pr_event` - Update PRD on PR merges
    - `process_github_issue_event` - Track issue lifecycle
    - `scheduled_prd_distillation` - Periodic PRD refresh
    - `scheduled_conflict_detection` - Automated conflict monitoring
  - **REST API**: ViewSets and endpoints for PRD state, versions, events, conflicts
    - GitHub webhook endpoint (`/api/prd-machine/webhook/github/`)
    - Manual trigger endpoints for sync, distill, generate, export
  - **Admin Panel**: Custom admin with actions for sync, distill, detect conflicts, export, toggle lock
  - **Management Command**: `python manage.py prd_machine` with options:
    - `--sync` / `--distill` / `--generate` / `--detect-conflicts`
    - `--export-issues` / `--export-changelog` / `--bump-version`
    - `--lock` / `--unlock` for zero-touch mode
    - `--status` / `--dry-run` for inspection

- **Implementation Plan Documentation**
  - New `IP.md` documenting the PRD MACHINE implementation plan with status tracking

### Changed

- **Django Settings**: Added `prd_machine.apps.PrdMachineConfig` to `INSTALLED_APPS`
- **URL Configuration**: Added `api/prd-machine/` URL namespace for PRD MACHINE API

### Infrastructure

- **Docker**: Updated docker-compose configurations with correct build contexts
  - Fixed `docker-compose.dev.yml` context paths for all services
  - Added `name: githubai` to docker-compose.yml
  - Added `PATH=/root/.local/bin:$PATH` to Dockerfile builder stage

### Dependencies

- Updated `openai>=1.56.0` for httpx 0.28+ compatibility (from `~=1.54.0`)

### Tests

- Added comprehensive test suite in `tests/test_prd_machine.py`
  - Model tests for all 5 PRD models
  - Service tests for PRDMachineService methods
  - Management command tests
  - Integration tests (marked with `@pytest.mark.integration`)

## [0.4.1] - 2025-11-26

### Added

- **VS Code Remote Debugging Support** - Full debugging integration for Docker development environment
  - Docker Compose debug overlay (`infra/docker/docker-compose.debug.yml`) with debugpy configuration
  - VS Code launch configurations for Django, Celery Worker, and Celery Beat containers
  - Compound debug configuration for simultaneous Django + Celery debugging
  - VS Code tasks (`.vscode/tasks.json`) for common Docker operations

- **Documentation**
  - `docs/development/debugging-guide.md` - Comprehensive VS Code remote debugging guide

### Dependencies

- Added `debugpy~=1.8.0` for remote debugging support

## [0.4.0] - 2025-11-26

### Added

- **Complete Frontend Application Rebuild** - Production-ready React SPA with full navigation and features
  - React Router 7 for client-side routing with 8 distinct pages
  - Modern AppLayout component with collapsible sidebar navigation
  - Responsive design with full-width content layout
  - Ant Design 6 ConfigProvider for consistent theming

- **New Pages & Routes**
  - `HomePage` (`/`) - Landing page with feature cards, quick stats, and quick actions
  - `ChatPage` (`/chat`) - AI chat interface with dynamic provider/model selection
  - `IssuesPage` (`/issues`) - Issue dashboard with filtering, search, and pagination
  - `IssueDetailPage` (`/issues/:id`) - Single issue view with full details
  - `CreateIssuePage` (`/issues/create`) - Manual issue creation with template support
  - `AutoIssuePage` (`/issues/auto`) - AI-powered automatic issue generation
  - `TemplatesPage` (`/templates`) - Template browser with preview modal
  - `SettingsPage` (`/settings`) - Settings placeholder page

- **Chat Components** - Refactored modular chat components
  - `ChatContainer` - Main chat state management with AI provider integration
  - `ChatMessage` - Individual message rendering with role-based styling
  - `MessageList` - Message list with empty state
  - `MessageInput` - Input field with keyboard shortcuts and loading state

- **Layout Components**
  - `AppLayout` - Fixed sidebar navigation, sticky header, footer
  - Menu with icons: Home, AI Chat, Issues, Templates, Settings
  - Collapsible sidebar with responsive breakpoint
  - GitHub link and connection status indicator

- **API Client Layer** - Centralized API abstraction
  - `src/services/api.js` with organized endpoint methods
  - `chatApi` - Send messages with optional provider/model override
  - `issueApi` - Full CRUD, auto-issue, feedback, README update
  - `templateApi` - Template CRUD operations
  - `providerApi` - List and get AI providers
  - `modelApi` - List and get AI models
  - `healthApi` - Health check endpoint
  - Error interceptor with user-friendly messages

- **Backend API Enhancements**
  - `AIProviderSerializer` - Read-only provider serialization (excludes API keys)
  - `AIModelSerializer` - Model serialization with provider info
  - `AIProviderViewSet` - Read-only provider endpoints at `/api/providers/`
  - `AIModelViewSet` - Read-only model endpoints at `/api/models/`
  - Custom `by_provider` action for filtering models by provider name

- **Frontend Documentation**
  - `.github/instructions/frontend.instructions.md` - Copilot guidelines for frontend
  - `frontend/FRONTEND_ARCHITECTURE.md` - Comprehensive architecture document
  - Component patterns, API usage, and best practices

### Changed

- **CSS Reset** - Replaced Vite default template styles
  - `index.css` - Clean reset with full-width body/root
  - `App.css` - Application-specific styles for Ant Design overrides
  - Removed `place-items: center` causing narrow layout
  - Added chat message, dashboard card, and utility styles

- **App.jsx** - Complete rewrite with routing
  - Replaced monolithic chat app with React Router setup
  - ConfigProvider wrapper for Ant Design theming
  - AppLayout wrapper for consistent navigation

- **URL Structure** - Organized API endpoints
  - `/api/providers/` - AI provider list/detail
  - `/api/models/` - AI model list/detail with provider filter
  - `/api/models/by-provider/<name>/` - Models by provider name

### Fixed

- **Layout Width Issue** - Content no longer narrow and left-aligned
  - Removed restrictive `body { display: flex; place-items: center }` from Vite template
  - Fixed sidebar margin transitions
  - Content now uses full available width

### Dependencies

- Added `react-router-dom: ^7.9.6` for client-side routing

## [0.3.0] - 2025-11-22

### Added

- **AI Chat Frontend** - Modern React-based web interface for conversational AI interaction
  - React 19 application with Vite 7 build system
  - Ant Design 6 UI component library for professional interface
  - Real-time chat with message history and provider information display
  - Keyboard shortcuts: Enter to send, Shift+Enter for new line
  - Responsive layout optimized for desktop and mobile
  - Error notifications and loading states for better UX

- **Chat REST API Endpoint** - Backend integration for frontend chat interface
  - `POST /api/chat/` endpoint for conversational AI interactions
  - `ChatView` API view with Django REST Framework
  - `ChatMessageSerializer` and `ChatResponseSerializer` for request/response validation
  - Integration with existing `AIService` for multi-provider support
  - Automatic caching via existing `AIResponse` model
  - Comprehensive logging via existing `APILog` model

- **Docker Configuration** - Frontend containerization and orchestration
  - Frontend service added to `docker-compose.yml`
  - Node.js 20 Alpine-based Dockerfile for frontend
  - Hot module replacement (HMR) enabled for development
  - Volume mounting for live code updates
  - Network configuration for frontend-backend communication

- **Frontend Dependencies**
  - `react: ^19.2.0` - React framework
  - `react-dom: ^19.2.0` - React DOM rendering
  - `antd: ^6.0.0` - Ant Design component library
  - `axios: ^1.13.2` - HTTP client for API communication
  - `vite: ^7.2.4` - Next generation frontend tooling

- **Documentation**
  - `docs/features/AI_CHAT_FRONTEND.md` - Comprehensive feature documentation
  - `docs/FRONTEND_QUICKSTART.md` - Quick start guide for users
  - `docs/FRONTEND_IMPLEMENTATION.md` - Implementation details and summary
  - Frontend README with setup and usage instructions

- **Superuser Management** - Enhanced admin account creation
  - `create_superuser` management command for automated admin account creation
  - Environment variable configuration for superuser credentials
  - `DJANGO_SUPERUSER_USERNAME`, `DJANGO_SUPERUSER_EMAIL`, `DJANGO_SUPERUSER_PASSWORD` in `.env`
  - Idempotent execution (skips if user already exists)

### Changed

- **CORS Configuration** - Extended to support frontend development
  - Added `http://localhost:5173` to `CORS_ALLOWED_ORIGINS`
  - Maintained backward compatibility with existing origins

- **URL Configuration** - New chat endpoint routing
  - Added `/api/chat/` route to `apps/core/urls.py`
  - Imported `ChatView` in core URL configuration

### Fixed

- None (new feature release)

### Security

- **CORS**: Properly configured for local development (production requires domain restriction)
- **Input Validation**: All chat inputs validated via DRF serializers
- **Error Handling**: Generic error messages prevent information disclosure
- **API Keys**: Securely stored in environment variables, not in code
- **Note**: Authentication not yet implemented (required for production deployment)

### Performance

- **Caching**: Leverages existing `AIResponse` caching to reduce API calls and costs
- **Efficient Rendering**: React state management minimizes unnecessary re-renders
- **Code Splitting**: Vite provides optimized bundle splitting
- **Resource Usage**: Frontend container ~50MB, minimal CPU impact

## [0.2.0] - 2025-11-21

### Added

- **Auto Issue Generation Service** - Automated repository analysis and GitHub issue creation
  - Six analysis types: `code_quality`, `todo_scan`, `documentation`, `dependencies`, `test_coverage`, `general_review`
  - AI-powered issue content generation with structured Markdown formatting
  - `AutoIssueService` class with comprehensive analysis capabilities
  - Pattern-based scanning for TODOs, FIXMEs, HACKs, and code quality issues
  - Dry-run mode for previewing analysis without creating GitHub issues
  - Automatic label assignment based on chore type
  - File-specific analysis targeting

- **User Feedback Issue Creation** - Convert raw user feedback into structured GitHub issues
  - `create_issue_from_feedback()` method in `IssueService`
  - Support for bug reports and feature requests
  - Context file inclusion for better issue quality
  - AI refinement of user-submitted content

- **REST API Endpoints**
  - `POST /api/issues/issues/create-auto-issue/` - Automated repository analysis endpoint
  - `POST /api/issues/issues/create-from-feedback/` - User feedback processing endpoint
  - Request validation via Django REST Framework serializers
  - Comprehensive error handling and status codes

- **Management Commands**
  - `python manage.py auto_issue` - CLI interface for automated issue generation
  - `--list-chores` flag to display available analysis types
  - `--dry-run` flag for analysis preview without issue creation
  - `--chore-type` parameter for analysis type selection
  - `--files` parameter for targeted file analysis
  - `--repo` parameter for repository specification

- **Serializers**
  - `CreateAutoIssueSerializer` - Validates auto-issue API requests
  - `CreateFeedbackIssueSerializer` - Validates feedback issue requests
  - Supports chore type choices, file lists, and dry-run options

- **Test Suite**
  - 10 comprehensive unit tests for `AutoIssueService` (100% passing)
  - 1 additional test for feedback issue creation
  - Mocked GitHub and AI service interactions
  - Test coverage for all public methods
  - Edge case and error handling validation

- **Documentation**
  - `docs/AUTO_ISSUE_FEATURE.md` - User-facing feature documentation
  - `docs/AUTO_ISSUE_IMPLEMENTATION_SUMMARY.md` - Implementation details
  - `docs/features/AUTO_ISSUE_GENERATION.md` - Comprehensive technical documentation
  - README updates with usage examples and API documentation
  - Demo script `demo_auto_issue.py` for feature validation

### Changed

- **README.md** - Updated features section with Auto Issue capabilities
  - Added CLI examples for auto-issue commands
  - Added API endpoint documentation for new endpoints
  - Updated usage section with feedback issue examples

- **IssueService** - Extended with feedback processing capability
  - New method integrates with existing issue creation workflow
  - Maintains consistency with template-based issue generation

### Fixed

- None (new feature release)

### Security

- All user inputs validated via Django REST Framework serializers
- GitHub tokens and AI API keys stored securely in environment variables
- No sensitive data exposed in API responses or logs
- SQL injection protection via Django ORM usage

## [0.1.14] - 2025-11-20

### Previous Release

(See `docs/CHANGELOG_AI.md` for historical changes)

---

## Version Numbering

This project follows [Semantic Versioning](https://semver.org/):

- **MAJOR** version (X.0.0) - Incompatible API changes
- **MINOR** version (0.X.0) - New features (backward compatible)
- **PATCH** version (0.0.X) - Bug fixes (backward compatible)

## Links

- [Repository](https://github.com/bamr87/githubai)
- [Issue Tracker](https://github.com/bamr87/githubai/issues)
- [Documentation](docs/)
