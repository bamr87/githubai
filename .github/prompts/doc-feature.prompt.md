---
agent: agent
description: Comprehensive feature documentation and release preparation prompt
---

# Feature Documentation and Release Preparation Prompt

You are an expert technical documentation specialist and release engineer. Your task is to analyze a newly developed feature and generate comprehensive documentation, changelogs, tests, and release artifacts following industry best practices.

## Context Analysis

First, analyze the current state of the feature:

1. **Code Changes Review**
   - Review all modified, added, and deleted files
   - Identify the feature's scope, purpose, and implementation
   - Map dependencies and integration points
   - Identify affected components and services

2. **Git History Analysis**
   - Examine recent commits related to this feature
   - Identify the feature branch name and base branch
   - Review commit messages for context
   - Check for any referenced issues or PRs

## Documentation Requirements

Generate the following documentation artifacts:

### 1. Feature Documentation (`docs/features/FEATURE_NAME.md`)

Create comprehensive feature documentation including:

```markdown
# Feature Name

## Overview
Brief description of what the feature does and why it was implemented.

## Architecture
- Components involved
- Data flow diagrams (describe in text)
- Integration points
- Dependencies

## Implementation Details
- Key classes and modules
- Service layer changes
- Database schema changes (if any)
- API endpoints (if any)

## Configuration
- Environment variables required
- Settings changes
- Third-party service setup

## Usage Examples
- Code examples
- API usage
- Common use cases

## Testing
- How to test the feature
- Test scenarios covered
- Manual testing steps

## Troubleshooting
- Common issues
- Debug tips
- Known limitations

## Security Considerations
- Authentication/Authorization changes
- Data privacy implications
- Security best practices applied

## Performance Impact
- Expected performance characteristics
- Optimization techniques used
- Resource requirements
```

### 2. Changelog Entry (`CHANGELOG.md`)

Add an entry following Keep a Changelog format:

```markdown
## [VERSION] - YYYY-MM-DD

### Added
- New features, endpoints, or capabilities
- New configuration options
- New dependencies

### Changed
- Modifications to existing functionality
- API changes
- Behavior changes

### Deprecated
- Features marked for removal
- APIs scheduled for deprecation

### Removed
- Deleted features or code
- Removed dependencies

### Fixed
- Bug fixes related to this feature
- Issues resolved

### Security
- Security improvements or fixes
```

### 3. API Documentation (`docs/api/ENDPOINT.md`)

If the feature includes API endpoints:

```markdown
# API Endpoint: /api/path

## Method: GET/POST/PUT/DELETE

## Description
What this endpoint does.

## Authentication
Required authentication type and permissions.

## Request

### Headers
```
Content-Type: application/json
Authorization: Bearer <token>
```

### Path Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|

### Query Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|

### Request Body
```json
{
  "field": "value"
}
```

## Response

### Success Response (200)
```json
{
  "status": "success",
  "data": {}
}
```

### Error Responses
- 400 Bad Request
- 401 Unauthorized
- 404 Not Found
- 500 Internal Server Error

## Examples

### cURL
```bash
curl -X GET "http://api.example.com/api/path" \
  -H "Authorization: Bearer token"
```

### Python
```python
import requests
response = requests.get("http://api.example.com/api/path")
```
```

### 4. Test Documentation (`tests/README_FEATURE.md`)

```markdown
# Testing: Feature Name

## Test Coverage
- Unit tests: X%
- Integration tests: Y%
- E2E tests: Z%

## Running Tests

### All Tests
```bash
docker-compose exec web pytest tests/test_feature.py
```

### Specific Test
```bash
docker-compose exec web pytest tests/test_feature.py::test_name
```

### With Coverage
```bash
docker-compose exec web pytest --cov=apps.feature tests/test_feature.py
```

## Test Scenarios

### 1. Scenario Name
**Purpose**: What this test validates
**Steps**: How to reproduce
**Expected**: What should happen

## Manual Testing Checklist
- [ ] Step 1
- [ ] Step 2
- [ ] Step 3

## Test Data Requirements
- Required fixtures
- Environment setup
- Mock data needed
```

### 5. Migration Guide (if breaking changes)

```markdown
# Migration Guide: Version X to Version Y

## Breaking Changes
List of breaking changes and their impact.

## Migration Steps

### 1. Database Migrations
```bash
docker-compose exec web python manage.py migrate
```

### 2. Configuration Updates
Update the following settings...

### 3. Code Changes Required
If integrating systems need updates...

## Rollback Plan
How to revert if needed.
```

## Versioning Strategy

Analyze the changes and recommend version bump following Semantic Versioning (SemVer):

### Version Bump Decision Tree

1. **MAJOR version (X.0.0)** - Increment when:
   - Breaking API changes
   - Incompatible database schema changes
   - Removed features or endpoints
   - Changed authentication/authorization model
   - Changed core behavior that breaks existing integrations

2. **MINOR version (0.X.0)** - Increment when:
   - New features added (backward compatible)
   - New API endpoints
   - New optional configuration options
   - Deprecated features (but still functional)
   - Enhanced functionality without breaking changes

3. **PATCH version (0.0.X)** - Increment when:
   - Bug fixes
   - Performance improvements
   - Documentation updates
   - Security patches
   - Refactoring without behavior changes

### Version Bump Command
```bash
# Automatic version bump based on analysis
docker-compose exec web python manage.py bump_version --type [major|minor|patch]

# Manual version specification
docker-compose exec web python manage.py bump_version --version X.Y.Z
```

## Git Branching Strategy

### Branch Naming Convention

```
feature/short-feature-description
bugfix/issue-number-bug-description
hotfix/critical-issue-description
release/version-number
```

### Release Workflow

1. **Feature Development**
   ```bash
   # Create feature branch from main
   git checkout main
   git pull origin main
   git checkout -b feature/feature-name

   # Commit changes
   git add .
   git commit -m "feat: add feature description"

   # Push feature branch
   git push origin feature/feature-name
   ```

2. **Pre-Release Checklist**
   - [ ] All tests passing
   - [ ] Documentation updated
   - [ ] CHANGELOG.md updated
   - [ ] Version bumped appropriately
   - [ ] Migration scripts tested
   - [ ] Security review completed
   - [ ] Performance testing done
   - [ ] Code review approved

3. **Create Release Branch**
   ```bash
   # Create release branch
   git checkout main
   git pull origin main
   git checkout -b release/vX.Y.Z

   # Bump version
   docker-compose exec web python manage.py bump_version --type [major|minor|patch]

   # Commit version bump
   git add VERSION apps/VERSION
   git commit -m "chore: bump version to X.Y.Z"

   # Push release branch
   git push origin release/vX.Y.Z
   ```

4. **Create Pull Request**
   - Title: `Release vX.Y.Z: Feature Name`
   - Description should include:
     - Summary of changes
     - Link to feature documentation
     - Testing completed
     - Migration notes (if any)
     - Rollback plan

5. **Tag Release**
   ```bash
   # After merging to main
   git checkout main
   git pull origin main

   # Create annotated tag
   git tag -a vX.Y.Z -m "Release version X.Y.Z

   Features:
   - Feature 1
   - Feature 2

   Changes:
   - Change 1

   Fixes:
   - Fix 1"

   # Push tag
   git push origin vX.Y.Z
   ```

6. **Post-Release**
   ```bash
   # Merge back to develop (if using GitFlow)
   git checkout develop
   git merge main
   git push origin develop

   # Delete feature branch
   git branch -d feature/feature-name
   git push origin --delete feature/feature-name
   ```

## Commit Message Convention

Follow Conventional Commits specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `perf`: Performance improvement
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `ci`: CI/CD changes
- `build`: Build system changes

### Examples
```bash
feat(issues): add auto-issue generation service

Implemented AI-powered automatic issue generation with:
- Template-based issue creation
- GitHub API integration
- Celery async task support
- Comprehensive error handling

Closes #123

---

fix(auth): resolve token expiration handling

Fixed issue where expired tokens weren't properly refreshed,
causing 401 errors for long-running sessions.

Fixes #456

---

docs(api): add comprehensive endpoint documentation

Added detailed API documentation for all issue-related
endpoints including request/response examples.
```

## Release Notes Template

Generate user-facing release notes:

```markdown
# Release vX.Y.Z - YYYY-MM-DD

## 🎉 Highlights
Brief, user-friendly description of major changes.

## ✨ New Features
- **Feature Name**: What it does and why it's useful

## 🔧 Improvements
- Enhancement 1
- Enhancement 2

## 🐛 Bug Fixes
- Fix description

## ⚠️ Breaking Changes
**IMPORTANT**: List any breaking changes and migration steps

## 📚 Documentation
- New documentation added
- Updated guides

## 🔒 Security
- Security improvements

## 🙏 Contributors
Thanks to @username for contributions!

## 📦 Installation/Upgrade

### New Installation
```bash
git clone https://github.com/bamr87/githubai.git
cd githubai
docker-compose up
```

### Upgrade from Previous Version
```bash
git pull origin main
docker-compose down
docker-compose build
docker-compose up
```

## 🔗 Links
- Full Changelog (see docs/CHANGELOG.md or generate during release)
- [Documentation](../../docs/)
- [Issues](https://github.com/bamr87/githubai/issues)
```

## Testing Checklist

Generate comprehensive testing checklist:

```markdown
# Feature Testing Checklist

## Unit Tests
- [ ] All service methods tested
- [ ] Edge cases covered
- [ ] Error handling validated
- [ ] Mock objects properly configured

## Integration Tests
- [ ] Database interactions tested
- [ ] API integrations verified
- [ ] Service layer integration validated
- [ ] External service mocks working

## API Tests
- [ ] All endpoints tested (GET, POST, PUT, DELETE)
- [ ] Authentication/Authorization validated
- [ ] Request validation working
- [ ] Response format correct
- [ ] Error responses appropriate

## Functional Tests
- [ ] Feature works end-to-end
- [ ] User workflows complete successfully
- [ ] Data persists correctly
- [ ] UI updates reflect changes (if applicable)

## Performance Tests
- [ ] Response times acceptable
- [ ] No N+1 queries
- [ ] Caching working properly
- [ ] Resource usage reasonable

## Security Tests
- [ ] Authentication required where needed
- [ ] Authorization rules enforced
- [ ] Input validation prevents injection
- [ ] Sensitive data protected
- [ ] Rate limiting (if applicable)

## Compatibility Tests
- [ ] Works in Docker environment
- [ ] Database migrations successful
- [ ] Celery tasks execute properly
- [ ] Redis integration functional

## Manual Testing
- [ ] Feature works in development environment
- [ ] Feature works in staging environment
- [ ] Documentation accurate
- [ ] Error messages helpful
```

## Output Format

Provide your analysis and documentation in the following structure:

1. **Executive Summary**: 2-3 sentence overview of the feature
2. **Recommended Version Bump**: [MAJOR|MINOR|PATCH] with justification
3. **Documentation Artifacts**: All generated documentation files
4. **Git Commands**: Complete sequence of commands for release
5. **Testing Summary**: Coverage report and testing recommendations
6. **Risk Assessment**: Potential issues and mitigation strategies
7. **Post-Release Monitoring**: Metrics to watch and alerts to configure

## Additional Considerations

- **Database Migrations**: Check for schema changes and document migration steps
- **Environment Variables**: Document any new configuration requirements
- **Dependencies**: Note new or updated dependencies in requirements.txt
- **Backward Compatibility**: Assess impact on existing integrations
- **Performance Impact**: Estimate resource usage and scalability
- **Monitoring**: Suggest metrics and logging for the new feature
- **Rollback Strategy**: Document how to safely revert if issues arise

---

## How to Use This Prompt

1. Review current git diff and changes
2. Analyze the feature scope and impact
3. Generate all required documentation
4. Recommend appropriate version bump
5. Provide complete git workflow commands
6. Create testing checklist
7. Prepare release notes

This prompt ensures comprehensive, production-ready documentation for every feature release.

