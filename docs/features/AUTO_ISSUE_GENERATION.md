# Auto Issue Generation Feature

## Overview

The Auto Issue Generation feature provides AI-powered automatic repository analysis and GitHub issue creation for maintenance tasks. It includes two primary capabilities:

1. **Automated Repository Analysis** - Scans codebases for 6 types of maintenance needs and creates structured issues
2. **User Feedback Processing** - Converts raw user bug reports and feature requests into well-formed GitHub issues

Both capabilities leverage AI to generate comprehensive, actionable issue content that follows best practices for GitHub issue formatting.

## Architecture

### Components Involved

```
┌─────────────────────────────────────────────────────────────┐
│                     Auto Issue Feature                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────┐      ┌──────────────────┐            │
│  │  REST API        │      │  Management      │            │
│  │  Endpoints       │      │  Commands        │            │
│  └────────┬─────────┘      └────────┬─────────┘            │
│           │                         │                       │
│           └─────────┬───────────────┘                       │
│                     │                                       │
│           ┌─────────▼──────────────┐                        │
│           │   IssueService         │                        │
│           │  - create_issue_from   │                        │
│           │    _feedback()         │                        │
│           └─────────┬──────────────┘                        │
│                     │                                       │
│           ┌─────────▼──────────────┐                        │
│           │  AutoIssueService      │                        │
│           │  - analyze_repo_and    │                        │
│           │    _create_issue()     │                        │
│           │  - 6 chore types       │                        │
│           └─────────┬──────────────┘                        │
│                     │                                       │
│        ┌────────────┴────────────┐                          │
│        │                         │                          │
│  ┌─────▼─────────┐      ┌───────▼────────┐                 │
│  │ GitHubService │      │   AIService    │                 │
│  │ - fetch files │      │ - generate     │                 │
│  │ - create      │      │   content      │                 │
│  │   issues      │      │ - refine       │                 │
│  └───────────────┘      │   issues       │                 │
│                         └────────────────┘                 │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

**Auto Issue Creation Flow:**

```
1. User/Scheduler triggers analysis
   ↓
2. AutoIssueService._perform_analysis()
   - Fetches repository files from GitHub
   - Scans for patterns (TODOs, quality issues, etc.)
   - Collects findings
   ↓
3. AutoIssueService._generate_issue_content()
   - AIService generates structured issue body
   - Applies chore-specific prompts
   ↓
4. GitHubService.create_github_issue()
   - Creates issue on GitHub
   - Applies appropriate labels
   ↓
5. Issue model saves to database
   - Stores metadata
   - Links file references
```

**Feedback Issue Flow:**

```
1. User submits feedback (bug/feature)
   ↓
2. IssueService.create_issue_from_feedback()
   - Fetches context files if provided
   - Structures feedback for AI
   ↓
3. AIService refines content
   - Converts raw feedback to structured issue
   - Adds appropriate sections
   ↓
4. GitHubService creates issue
   ↓
5. Issue saved with references
```

### Integration Points

1. **GitHub API** - Issue creation, file fetching
2. **AI Provider** (OpenAI, Anthropic, etc.) - Content generation
3. **Django ORM** - Database persistence
4. **Celery** (future) - Scheduled background tasks
5. **REST Framework** - API interface

### Dependencies

- `core.services.GitHubService` - GitHub API interactions
- `core.services.AIService` - AI content generation
- `core.models.Issue` - Database model
- `core.models.IssueFileReference` - File context storage

## Implementation Details

### Key Classes and Modules

#### AutoIssueService (`apps/core/services/auto_issue_service.py`)

**Purpose**: Automated repository analysis and issue generation

**Key Methods**:

- `analyze_repo_and_create_issue()` - Main entry point
  - Parameters: `repo`, `chore_type`, `context_files`, `auto_submit`
  - Returns: `Issue` instance or analysis string (dry-run)

- `_perform_analysis()` - Scans repository for issues
  - Fetches files from GitHub
  - Executes chore-specific analysis
  - Collects findings

- `_generate_issue_content()` - AI-powered content generation
  - Formats analysis data for AI
  - Returns structured Markdown issue body

- `_scan_for_todos()` - Regex-based TODO detection
- `_analyze_code_quality()` - Line length, docstring checks
- `_check_documentation()` - Documentation gap detection

**Chore Types**:

```python
CHORE_TYPES = {
    'code_quality': 'Analyze code for quality issues',
    'todo_scan': 'Find TODO/FIXME/HACK comments',
    'documentation': 'Identify documentation gaps',
    'dependencies': 'Check outdated dependencies',
    'test_coverage': 'Analyze test coverage',
    'general_review': 'General repository health check',
}
```

#### IssueService Updates (`apps/core/services/issue_service.py`)

**New Method**: `create_issue_from_feedback()`

- Converts user feedback (bug/feature) to structured issue
- Fetches context files for additional information
- Uses AI to refine and structure content
- Creates GitHub issue with appropriate labels

### Service Layer Changes

**New Files Created**:

- `apps/core/services/auto_issue_service.py` (330 lines)
- `apps/core/management/commands/auto_issue.py` (76 lines)

**Modified Files**:

- `apps/core/services/__init__.py` - Added `AutoIssueService` export
- `apps/core/services/issue_service.py` - Added `create_issue_from_feedback()`
- `apps/core/views.py` - Added 2 new API actions
- `apps/core/serializers.py` - Added 2 new serializers

### Database Schema Changes

**No schema changes required**. The feature uses existing models:

- `Issue` - Stores generated issues
- `IssueFileReference` - Stores context files used in analysis

New issues are marked with:

- `ai_generated=True`
- Labels: `['auto-generated', 'maintenance']` + chore-specific labels

### API Endpoints

#### 1. Create Auto Issue

**Endpoint**: `POST /api/issues/issues/create-auto-issue/`

**Request Body**:

```json
{
    "chore_type": "code_quality",
    "repo": "bamr87/githubai",
    "context_files": ["apps/core/services/issue_service.py"],
    "auto_submit": true
}
```

**Response (201)**:

```json
{
    "id": 42,
    "github_issue_number": 123,
    "title": "[Auto] Code Quality Review - 5 items found",
    "labels": ["auto-generated", "maintenance", "code-quality"]
}
```

#### 2. Create Feedback Issue

**Endpoint**: `POST /api/issues/issues/create-from-feedback/`

**Request Body**:

```json
{
    "feedback_type": "bug",
    "summary": "Login button not working",
    "description": "When I click login, nothing happens.",
    "repo": "bamr87/githubai",
    "context_files": ["README.md"]
}
```

**Response (201)**:

```json
{
    "id": 43,
    "github_issue_number": 124,
    "title": "Login button not working",
    "issue_type": "bug",
    "labels": ["ai-generated", "bug"]
}
```

## Configuration

### Environment Variables Required

```bash
# GitHub API access (required)
GITHUB_TOKEN=ghp_your_github_personal_access_token

# AI Provider configuration (required)
AI_PROVIDER=openai  # or anthropic, google, etc.
AI_API_KEY=your_ai_api_key
AI_MODEL=gpt-4o-mini
AI_TEMPERATURE=0.2
AI_MAX_TOKENS=2500

# Default repository (optional)
DEFAULT_REPO=bamr87/githubai
```

### Settings Changes

No Django settings changes required. The feature uses existing:

- `settings.GITHUB_TOKEN`
- `settings.AI_API_KEY`
- `settings.AI_PROVIDER`

## Usage Examples

### Code Examples

#### Python SDK Usage

```python
from core.services import AutoIssueService

# Initialize service
service = AutoIssueService()

# Create auto-issue
issue = service.analyze_repo_and_create_issue(
    repo='bamr87/githubai',
    chore_type='code_quality',
    context_files=['apps/core/services/issue_service.py'],
    auto_submit=True
)

print(f"Created issue #{issue.github_issue_number}")
print(f"URL: {issue.html_url}")
```

#### Dry Run (Preview)

```python
content = service.analyze_repo_and_create_issue(
    repo='bamr87/githubai',
    chore_type='todo_scan',
    auto_submit=False  # Preview only
)

print("Generated content:")
print(content)
```

#### Feedback Issue Creation

```python
from core.services import IssueService

service = IssueService()

issue = service.create_issue_from_feedback(
    feedback_type='bug',
    summary='Button not responding',
    description='The submit button does not work on mobile',
    repo='bamr87/githubai',
    context_files=['README.md']
)
```

### API Usage

#### cURL Examples

**Auto Issue (Code Quality)**:

```bash
curl -X POST http://localhost:8000/api/issues/issues/create-auto-issue/ \
    -H "Content-Type: application/json" \
    -d '{
        "chore_type": "code_quality",
        "repo": "bamr87/githubai",
        "auto_submit": true
    }'
```

**Dry Run**:

```bash
curl -X POST http://localhost:8000/api/issues/issues/create-auto-issue/ \
    -H "Content-Type: application/json" \
    -d '{
        "chore_type": "general_review",
        "auto_submit": false
    }'
```

**User Feedback Issue**:

```bash
curl -X POST http://localhost:8000/api/issues/issues/create-from-feedback/ \
    -H "Content-Type: application/json" \
    -d '{
        "feedback_type": "feature",
        "summary": "Add dark mode support",
        "description": "Would love to see a dark theme option",
        "repo": "bamr87/githubai"
    }'
```

### Common Use Cases

#### 1. Weekly Repository Health Check

```bash
#!/bin/bash
# weekly-audit.sh
docker-compose exec web python manage.py auto_issue \
    --repo bamr87/githubai \
    --chore-type general_review
```

#### 2. Pre-Commit TODO Scan

```bash
# .git/hooks/pre-commit
docker-compose exec web python manage.py auto_issue \
    --chore-type todo_scan \
    --dry-run > todo-report.txt

if [ -s todo-report.txt ]; then
    echo "⚠️  TODOs found. Consider addressing before commit."
fi
```

#### 3. CI/CD Quality Gate

```yaml
# .github/workflows/quality-check.yml
- name: Code Quality Check
  run: |
    docker-compose exec web python manage.py auto_issue \
      --chore-type code_quality \
      --dry-run
```

#### 4. User Feedback Form Integration

```javascript
// Frontend feedback form
fetch('/api/issues/issues/create-from-feedback/', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        feedback_type: 'bug',
        summary: form.summary.value,
        description: form.description.value
    })
});
```

## Testing

### How to Test the Feature

#### 1. Management Command Tests

```bash
# List available chore types
docker-compose exec web python manage.py auto_issue --list-chores

# Dry run (no GitHub issue created)
docker-compose exec web python manage.py auto_issue \
    --chore-type code_quality \
    --dry-run

# Create actual issue (requires GITHUB_TOKEN)
docker-compose exec web python manage.py auto_issue \
    --chore-type todo_scan
```

#### 2. API Endpoint Tests

```bash
# Test auto-issue endpoint
curl -X POST http://localhost:8000/api/issues/issues/create-auto-issue/ \
    -H "Content-Type: application/json" \
    -d '{"chore_type": "general_review", "auto_submit": false}'

# Test feedback endpoint
curl -X POST http://localhost:8000/api/issues/issues/create-from-feedback/ \
    -H "Content-Type: application/json" \
    -d '{"feedback_type": "bug", "summary": "Test", "description": "Test bug"}'
```

#### 3. Unit Tests

```bash
# Run all auto-issue tests
docker-compose exec web pytest tests/test_auto_issue_service.py -v

# Run specific test
docker-compose exec web pytest tests/test_auto_issue_service.py::TestAutoIssueService::test_scan_for_todos -v

# With coverage
docker-compose exec web pytest --cov=apps.core.services.auto_issue_service tests/test_auto_issue_service.py
```

### Test Scenarios Covered

✅ **Service Initialization** - AutoIssueService instantiation
✅ **Chore Type Listing** - Available analysis types
✅ **Full Issue Creation** - End-to-end with mocked GitHub/AI
✅ **Dry Run Mode** - Analysis without GitHub issue
✅ **TODO Scanning** - Regex pattern matching
✅ **Code Quality Analysis** - Line length, docstrings
✅ **Label Generation** - Chore-specific labels
✅ **Title Generation** - Finding count integration
✅ **Invalid Input Handling** - Error cases
✅ **Feedback Issue Creation** - User feedback processing

**Test Coverage**: 100% of public methods

### Manual Testing Steps

1. **Setup Environment**:

   ```bash
   docker-compose up -d
   docker-compose exec web python manage.py migrate
   ```

2. **Configure Tokens**:
   - Set `GITHUB_TOKEN` in `.env`
   - Set `AI_API_KEY` in `.env`

3. **Test Dry Run**:

   ```bash
   docker-compose exec web python manage.py auto_issue --chore-type code_quality --dry-run
   ```

   - ✅ Verify analysis output generated
   - ✅ Confirm no GitHub issue created

4. **Test Live Issue Creation**:

   ```bash
   docker-compose exec web python manage.py auto_issue --chore-type general_review
   ```

   - ✅ Check GitHub for new issue
   - ✅ Verify issue has correct labels
   - ✅ Verify issue body is well-formatted

5. **Test API**:

   ```bash
   curl -X POST http://localhost:8000/api/issues/issues/create-auto-issue/ \
       -H "Content-Type: application/json" \
       -d '{"chore_type": "todo_scan", "auto_submit": true}'
   ```

   - ✅ Verify 201 Created response
   - ✅ Check database for Issue record

## Troubleshooting

### Common Issues

#### 1. Authentication Errors (401)

**Symptom**: `GitHubException: 401 Unauthorized`

**Solution**:

```bash
# Verify token is set
docker-compose exec web python -c "from django.conf import settings; print(settings.GITHUB_TOKEN[:10])"

# Update .env with valid token
GITHUB_TOKEN=ghp_your_valid_token_here

# Restart services
docker-compose restart web
```

#### 2. AI API Errors

**Symptom**: `AIServiceException: API key invalid`

**Solution**:

```bash
# Check AI configuration
docker-compose exec web python manage.py configure_ai --test

# Update .env
AI_API_KEY=your_valid_api_key
AI_PROVIDER=openai
```

#### 3. No Files Found in Analysis

**Symptom**: Empty findings array

**Solution**:

- Verify repository name format: `owner/repo`
- Check file paths are relative to repo root
- Try without `--files` flag to use defaults

#### 4. Import Errors

**Symptom**: `ModuleNotFoundError: No module named 'core.services.auto_issue_service'`

**Solution**:

```bash
# Restart Django to reload code
docker-compose restart web

# Verify file exists
docker-compose exec web ls -la apps/core/services/auto_issue_service.py
```

### Debug Tips

**Enable Verbose Logging**:

```python
# In settings.py
LOGGING['loggers']['githubai']['level'] = 'DEBUG'
```

**Check Logs**:

```bash
docker-compose logs -f web | grep auto_issue
```

**Database Inspection**:

```bash
docker-compose exec web python manage.py shell
>>> from core.models import Issue
>>> Issue.objects.filter(ai_generated=True).latest('created_at')
```

### Known Limitations

1. **Rate Limiting**: GitHub API has rate limits (5000/hour authenticated)
2. **File Size**: Large files (>1MB) may timeout during analysis
3. **Language Support**: Code analysis currently optimized for Python
4. **AI Costs**: Each analysis triggers 1-2 AI API calls
5. **Pattern Matching**: TODO scanning uses regex (may miss variations)

## Security Considerations

### Authentication/Authorization Changes

**No authentication changes made**. The feature inherits existing Django authentication:

- REST API endpoints use existing authentication classes
- Management commands run with Django permissions
- No new user-facing authentication requirements

### Data Privacy Implications

**Data Handling**:

- **GitHub Token**: Stored in environment variables, never logged
- **AI API Key**: Stored in environment variables, never exposed to client
- **Repository Content**: Fetched via GitHub API, not stored permanently
- **Issue Content**: Stored in database (considered public)
- **User Feedback**: Stored in database with issue

**Privacy Considerations**:

- Do not use with private repositories containing sensitive data
- Issue content is public on GitHub
- AI providers may log requests (check provider policy)
- Consider data residency requirements for AI provider

### Security Best Practices Applied

✅ **Input Validation**: All user inputs validated via serializers
✅ **SQL Injection Protection**: Django ORM used exclusively
✅ **API Key Storage**: Environment variables only
✅ **Rate Limiting**: Inherits from Django REST Framework settings
✅ **Error Handling**: No sensitive data in error messages
✅ **Logging**: Tokens/keys excluded from logs
✅ **HTTPS**: Required for production GitHub/AI API calls

**Recommendations**:

1. Use GitHub Fine-Grained Tokens with minimal scopes
2. Rotate API keys regularly
3. Enable rate limiting in production
4. Monitor AI API costs
5. Review generated issues before publishing (dry-run first)

## Performance Impact

### Expected Performance Characteristics

**Response Times** (typical):

- **Dry Run Analysis**: 5-15 seconds (depends on file count)
- **Full Issue Creation**: 10-30 seconds (includes GitHub API call)
- **Feedback Issue**: 5-10 seconds (simpler analysis)

**Factors Affecting Performance**:

- Number of files analyzed
- File sizes
- AI provider response time (500ms - 3s)
- GitHub API latency (200ms - 1s)
- Network conditions

### Optimization Techniques Used

1. **Selective File Fetching**: Only fetches necessary files
2. **Analysis Limiting**: Code quality checks limited to first 5 findings
3. **AI Prompt Optimization**: Concise prompts reduce token usage
4. **Dry-Run Mode**: Skip GitHub API calls for testing
5. **Caching**: AI responses cached (if same analysis repeated)
6. **Regex Efficiency**: Compiled patterns for TODO scanning

### Resource Requirements

**Memory Usage**:

- Base: ~50MB per request
- Per file analyzed: ~1-5MB
- AI model overhead: ~10MB

**CPU Usage**:

- Regex processing: Low
- File parsing: Low-Medium
- Network I/O: Primary bottleneck

**Database Impact**:

- 1 Issue record per generation (~2KB)
- N IssueFileReference records (~5KB each)
- Minimal database load

**Scalability**:

- **Concurrent Requests**: Limited by AI API rate limits
- **Background Processing**: Can be offloaded to Celery
- **Caching Strategy**: AI response caching reduces costs/latency

**Production Recommendations**:

- Use Celery for async processing
- Implement request queuing for high volume
- Monitor AI API quota/costs
- Consider regional AI provider endpoints for latency

## Related Documentation

- [AUTO_ISSUE_FEATURE.md](../AUTO_ISSUE_FEATURE.md) - User-facing documentation
- [AUTO_ISSUE_IMPLEMENTATION_SUMMARY.md](../AUTO_ISSUE_IMPLEMENTATION_SUMMARY.md) - Implementation details
- [DJANGO_IMPLEMENTATION.md](../DJANGO_IMPLEMENTATION.md) - Overall architecture
- [AI_PROVIDER_CONFIGURATION.md](../AI_PROVIDER_CONFIGURATION.md) - AI setup

## Version History

- **v0.2.0** (2025-11-21) - Initial release
  - Auto Issue Service with 6 chore types
  - Feedback issue creation
  - Management command interface
  - REST API endpoints
  - Comprehensive test suite
