---
agent: agent
mode: agent
description: "Review changes, run tests, update documentation, bump version, and publish for GitHubAI"
---

# GitHubAI Commit & Publish Workflow

Review open changes, run appropriate tests, create/update documentation, update the changelog, bump the version according to semantic versioning, and prepare for publication.

## Task Overview

Execute the complete release pipeline for the current changes in the GitHubAI repository.

## Project Context

- **Architecture**: Single-app Django (apps/core/) with service layer pattern
- **Stack**: Django 5.x, PostgreSQL, Redis, Celery, React frontend (Vite)
- **Version File**: `VERSION` (root) - dynamic version in pyproject.toml
- **Changelog**: `docs/releases/CHANGELOG.md`
- **Docker**: `infra/docker/docker-compose.yml` with dev/test overlays

## Step 1: Review Open Changes

1. **Analyze Git Changes**:
   - Run `git status` to identify all modified, added, and deleted files
   - Run `git diff --cached` for staged changes and `git diff` for unstaged changes
   - Categorize changes by type:
     - **Features**: New functionality (services, views, API endpoints)
     - **Bug Fixes**: Issues resolved
     - **Breaking Changes**: Changes that break backward compatibility
     - **Documentation**: Documentation updates
     - **Refactoring**: Code improvements without functionality changes
     - **Dependencies**: Package version updates (requirements*.txt, pyproject.toml)
     - **Tests**: Test additions or modifications (tests/)
     - **Frontend**: React components, Vite config (frontend/)
     - **AI/Services**: AI service, prompts, providers (apps/core/services/)
     - **Infrastructure**: Docker, nginx, Celery configs (infra/)

2. **Summarize Changes**:
   - Create a concise summary of all changes
   - Identify the impact level (major, minor, patch)
   - Note any breaking changes that require migration

## Step 2: Run Appropriate Tests

1. **Identify Test Requirements**:
   - Based on changed files, determine which tests to run:
     - `apps/core/models.py` → run all model tests
     - `apps/core/services/` → run service-specific tests
     - `apps/core/views.py` → run API tests
     - `frontend/` → frontend tests (if configured)
     - General changes → run full test suite

2. **Execute Tests via Docker** (Required):
   ```bash
   # Start services if not running
   docker-compose -f infra/docker/docker-compose.yml up -d
   
   # Run full pytest suite (excludes integration tests by default)
   docker-compose -f infra/docker/docker-compose.yml exec web pytest
   
   # Run with coverage report
   docker-compose -f infra/docker/docker-compose.yml exec web pytest --cov
   
   # Run specific test file
   docker-compose -f infra/docker/docker-compose.yml exec web pytest tests/test_ai_services.py
   
   # Run integration tests (requires external APIs)
   docker-compose -f infra/docker/docker-compose.yml exec web pytest -m integration --run-integration
   ```

3. **Verify Test Results**:
   - Ensure all tests pass before proceeding
   - If tests fail, stop and report the failures
   - Document test coverage percentage (target: 80%+)

## Step 3: Create/Update Documentation

1. **Update Affected Documentation**:
   - `README.md` - Main project readme
   - `docs/` - Feature and API documentation
   - `docs/features/` - Feature-specific docs
   - `docs/guides/` - User guides
   - `docs/api/` - API endpoint documentation
   - `frontend/README.md` - Frontend documentation
   - `frontend/FRONTEND_ARCHITECTURE.md` - Frontend architecture

2. **Update Docstrings**:
   - Verify all new/modified functions have proper docstrings
   - Use Google-style docstrings format
   - Include Args, Returns, Raises, and Examples sections

3. **Update API Reference** (if applicable):
   ```bash
   # Rebuild Sphinx documentation
   docker-compose -f infra/docker/docker-compose.yml exec docs make html
   ```

## Step 4: Update CHANGELOG.md

1. **Changelog Location**: `docs/releases/CHANGELOG.md`

2. **Determine Version Type** based on changes:
   - **MAJOR** (X.0.0): Breaking changes, API incompatibilities
   - **MINOR** (0.X.0): New features, backward-compatible
   - **PATCH** (0.0.X): Bug fixes, minor improvements

3. **Add Changelog Entry** following Keep a Changelog format:
   ```markdown
   ## [X.Y.Z] - YYYY-MM-DD
   
   ### Added
   - New features (services, endpoints, components)
   
   ### Changed
   - Changes to existing functionality
   
   ### Deprecated
   - Features marked for removal
   
   ### Removed
   - Removed features
   
   ### Fixed
   - Bug fixes
   
   ### Security
   - Security updates
   
   ### Dependencies
   - Package updates
   ```

4. **Reference Issues/PRs** if applicable

## Step 5: Bump Version

1. **Update VERSION file** (root):
   ```bash
   echo "X.Y.Z" > VERSION
   ```
   
   Note: `pyproject.toml` uses dynamic versioning - no manual update needed.

2. **Alternative: Use Management Command**:
   ```bash
   # Auto-bump based on commit message markers [major], [minor], or default patch
   docker-compose -f infra/docker/docker-compose.yml exec web python manage.py bump_version --type minor
   ```

3. **Verify Version Consistency**:
   - Ensure VERSION file is updated
   - Check CHANGELOG.md has entry for new version
   - Verify apps/VERSION matches (if present)

## Step 6: Prepare for Publication

1. **Stage All Changes**:
   ```bash
   git add -A
   ```

2. **Create Semantic Commit Message**:
   Format: `<type>(<scope>): <description>`
   
   Types:
   - `feat`: New feature
   - `fix`: Bug fix
   - `docs`: Documentation changes
   - `style`: Code style changes (Black formatting)
   - `refactor`: Code refactoring
   - `test`: Test additions/changes
   - `chore`: Maintenance tasks
   - `ci`: CI/CD changes
   - `breaking`: Breaking changes

   Scopes (GitHubAI-specific):
   - `core`: apps/core changes
   - `ai`: AI service, providers, prompts
   - `github`: GitHub integration
   - `api`: REST API endpoints
   - `frontend`: React frontend
   - `docker`: Infrastructure/Docker
   - `celery`: Async tasks

3. **Commit Changes**:
   ```bash
   git commit -m "<type>(<scope>): <description>

   <detailed description of changes>

   - Change 1
   - Change 2
   - Change 3

   Closes #<issue-number> (if applicable)"
   ```

4. **Create Git Tag** (for releases):
   ```bash
   git tag -a v<X.Y.Z> -m "Release v<X.Y.Z>: <summary>"
   ```

5. **Push Changes**:
   ```bash
   git push origin main
   git push origin --tags
   ```

## Success Criteria

- [ ] All tests pass with no failures
- [ ] Test coverage maintained at 80%+ or improved
- [ ] All changed code has proper documentation
- [ ] `docs/releases/CHANGELOG.md` updated with new version entry
- [ ] `VERSION` file updated to new version
- [ ] Git commit follows semantic commit format
- [ ] Changes pushed to remote repository
- [ ] Git tag created for releases (optional)

## Output Format

After completing all steps, provide a summary:

```markdown
## Release Summary

**Version**: X.Y.Z (from X.Y.Z)
**Type**: MAJOR | MINOR | PATCH
**Date**: YYYY-MM-DD

### Changes Included
- [ ] Feature 1
- [ ] Fix 1
- [ ] etc.

### Test Results
- Total Tests: X
- Passed: X
- Failed: X
- Coverage: X%

### Files Modified
- apps/core/...
- frontend/src/...
- docs/...

### Documentation Updated
- [ ] README.md
- [ ] docs/releases/CHANGELOG.md
- [ ] docs/features/...
- [ ] API docs

### Commit Information
- Hash: <commit-hash>
- Message: <commit-message>
- Tag: v<version> (if created)
```

## Rollback Procedure

If issues are discovered after publication:

1. Revert the commit:
   ```bash
   git revert <commit-hash>
   ```

2. Delete the tag (if created):
   ```bash
   git tag -d v<version>
   git push origin :refs/tags/v<version>
   ```

3. Create a patch release with the fix

## Key File Locations

| Purpose | Path |
|---------|------|
| Version | `VERSION` |
| Changelog | `docs/releases/CHANGELOG.md` |
| Tests | `tests/` |
| Services | `apps/core/services/` |
| Models | `apps/core/models.py` |
| API Views | `apps/core/views.py` |
| Frontend | `frontend/src/` |
| Docker | `infra/docker/docker-compose.yml` |

---

**Note**: Always run tests in the Docker container to ensure environment consistency. Never publish without passing tests. Use `docker-compose -f infra/docker/docker-compose.yml exec web <command>` for all Django/Python commands.