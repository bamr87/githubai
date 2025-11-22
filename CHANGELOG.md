# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
