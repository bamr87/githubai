# API Endpoint: Create Auto Issue

## Method: POST

## Endpoint

```
POST /api/issues/issues/create-auto-issue/
```

## Description

Automatically analyzes a repository and creates a GitHub issue for maintenance tasks. The system performs intelligent analysis based on the selected chore type (code quality, TODO scanning, documentation gaps, etc.) and generates a comprehensive, AI-refined issue with actionable recommendations.

## Authentication

Uses Django's default authentication. No special permissions required beyond standard API access.

## Request

### Headers

```http
Content-Type: application/json
Accept: application/json
```

### Path Parameters

None

### Query Parameters

None

### Request Body

```json
{
    "chore_type": "code_quality",
    "repo": "bamr87/githubai",
    "context_files": [
        "apps/core/services/issue_service.py",
        "apps/core/views.py"
    ],
    "auto_submit": true
}
```

#### Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `chore_type` | string | Yes | - | Type of analysis to perform. Choices: `code_quality`, `todo_scan`, `documentation`, `dependencies`, `test_coverage`, `general_review` |
| `repo` | string | No | `bamr87/githubai` | Repository in format `owner/repo` |
| `context_files` | array[string] | No | Auto-selected | List of specific file paths to analyze (relative to repo root) |
| `auto_submit` | boolean | No | `true` | If `true`, creates GitHub issue. If `false`, returns analysis only (dry-run) |

#### Chore Types

| Chore Type | Description |
|------------|-------------|
| `code_quality` | Analyzes code for quality issues, complexity, and best practices. Checks line lengths, docstring presence, code complexity. |
| `todo_scan` | Finds TODO/FIXME/HACK comments in code that need attention. Catalogs technical debt. |
| `documentation` | Identifies missing or outdated documentation. Checks for standard README sections. |
| `dependencies` | Checks for outdated dependencies and security issues in requirements files. |
| `test_coverage` | Analyzes test coverage and suggests missing tests. |
| `general_review` | Performs a comprehensive repository health check across multiple areas. |

## Response

### Success Response (201 Created)

When `auto_submit: true` and issue is created successfully:

```json
{
    "id": 42,
    "github_repo": "bamr87/githubai",
    "github_issue_number": 123,
    "title": "[Auto] Code Quality Review - 5 items found",
    "body": "# Code Quality Analysis\n\n## Summary\n...",
    "html_url": "https://github.com/bamr87/githubai/issues/123",
    "state": "open",
    "issue_type": "other",
    "labels": [
        "auto-generated",
        "maintenance",
        "code-quality",
        "refactor"
    ],
    "parent_issue": null,
    "ai_generated": true,
    "template": null,
    "file_references": [],
    "sub_issues_count": 0,
    "created_at": "2025-11-21T10:30:00Z",
    "updated_at": "2025-11-21T10:30:00Z"
}
```

### Dry Run Response (200 OK)

When `auto_submit: false` (preview mode):

```json
{
    "analysis": "# Code Quality Issue: Repository Analysis\n\n## Summary of Findings\n\nDuring the recent code quality analysis of the repository `bamr87/githubai`, several areas were identified that could benefit from attention...\n\n## Specific Recommendations\n\n1. **Line Length Issues** - Multiple files contain lines exceeding 120 characters\n2. **Missing Docstrings** - Several functions lack documentation\n\n## Prioritized Action Items\n\n1. High Priority: Address line length violations in `apps/core/services/issue_service.py`\n2. Medium Priority: Add docstrings to public methods\n\n## Expected Benefits\n\n- Improved code readability\n- Better maintainability\n- Enhanced developer onboarding",
    "message": "Dry run - no issue created"
}
```

### Error Responses

#### 400 Bad Request

Invalid chore type or request data:

```json
{
    "error": "Invalid chore_type. Must be one of: code_quality, todo_scan, documentation, dependencies, test_coverage, general_review"
}
```

Missing required fields:

```json
{
    "chore_type": [
        "This field is required."
    ]
}
```

#### 401 Unauthorized

Missing or invalid authentication credentials.

#### 500 Internal Server Error

GitHub API failure, AI service error, or other server-side issues:

```json
{
    "error": "GitHub API error: Repository not found"
}
```

## Examples

### cURL

**Create Code Quality Issue:**

```bash
curl -X POST http://localhost:8000/api/issues/issues/create-auto-issue/ \
    -H "Content-Type: application/json" \
    -d '{
        "chore_type": "code_quality",
        "repo": "bamr87/githubai",
        "auto_submit": true
    }'
```

**TODO Scan with Specific Files:**

```bash
curl -X POST http://localhost:8000/api/issues/issues/create-auto-issue/ \
    -H "Content-Type: application/json" \
    -d '{
        "chore_type": "todo_scan",
        "repo": "bamr87/githubai",
        "context_files": [
            "apps/core/services/issue_service.py",
            "apps/core/services/ai_service.py"
        ],
        "auto_submit": true
    }'
```

**Dry Run (Preview Only):**

```bash
curl -X POST http://localhost:8000/api/issues/issues/create-auto-issue/ \
    -H "Content-Type: application/json" \
    -d '{
        "chore_type": "general_review",
        "repo": "bamr87/githubai",
        "auto_submit": false
    }'
```

### Python

**Using requests library:**

```python
import requests

url = "http://localhost:8000/api/issues/issues/create-auto-issue/"

# Create issue
response = requests.post(url, json={
    "chore_type": "code_quality",
    "repo": "bamr87/githubai",
    "auto_submit": True
})

if response.status_code == 201:
    issue = response.json()
    print(f"Created issue #{issue['github_issue_number']}")
    print(f"URL: {issue['html_url']}")
else:
    print(f"Error: {response.json()}")
```

**Dry run preview:**

```python
import requests

response = requests.post(
    "http://localhost:8000/api/issues/issues/create-auto-issue/",
    json={
        "chore_type": "todo_scan",
        "auto_submit": False
    }
)

if response.status_code == 200:
    print("Analysis preview:")
    print(response.json()["analysis"])
```

### JavaScript/TypeScript

**Using fetch:**

```javascript
const response = await fetch('/api/issues/issues/create-auto-issue/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        chore_type: 'documentation',
        repo: 'bamr87/githubai',
        auto_submit: true
    })
});

if (response.ok) {
    const issue = await response.json();
    console.log(`Created issue #${issue.github_issue_number}`);
} else {
    const error = await response.json();
    console.error('Error:', error);
}
```

## Notes

### Performance

- **Response Time**: 10-30 seconds depending on analysis scope
- **Rate Limits**: Subject to GitHub API rate limits (5000/hour authenticated)
- **AI API Calls**: Each request triggers 1-2 AI API calls

### Best Practices

1. **Use Dry Run First**: Test with `auto_submit: false` before creating actual issues
2. **Specify Context Files**: Narrow scope for faster, more focused analysis
3. **Monitor Costs**: AI API calls incur costs; use judiciously
4. **Schedule Wisely**: Avoid concurrent requests to prevent rate limiting

### Related Endpoints

- `POST /api/issues/issues/create-from-feedback/` - Create issue from user feedback
- `POST /api/issues/issues/create-sub-issue/` - Create template-based sub-issue
- `POST /api/issues/issues/create-readme-update/` - Generate README update issue
- `GET /api/issues/issues/` - List all issues

### Configuration Requirements

Before using this endpoint, ensure:

- `GITHUB_TOKEN` is set in environment variables
- `AI_API_KEY` is configured
- `AI_PROVIDER` is specified (openai, anthropic, etc.)

### Labels Applied

Auto-generated issues include:

- Base: `auto-generated`, `maintenance`
- Chore-specific:
  - `code_quality`: `code-quality`, `refactor`
  - `todo_scan`: `technical-debt`
  - `documentation`: `documentation`
  - `dependencies`: `dependencies`, `security`
  - `test_coverage`: `testing`
  - `general_review`: `health-check`

---

# API Endpoint: Create Feedback Issue

## Method: POST

## Endpoint

```
POST /api/issues/issues/create-from-feedback/
```

## Description

Converts raw user feedback (bug reports or feature requests) into a well-structured GitHub issue using AI refinement. This endpoint is designed for user-facing feedback forms, support tickets, or any scenario where unstructured feedback needs to be transformed into actionable GitHub issues.

## Authentication

Uses Django's default authentication. No special permissions required beyond standard API access.

## Request

### Headers

```http
Content-Type: application/json
Accept: application/json
```

### Path Parameters

None

### Query Parameters

None

### Request Body

```json
{
    "feedback_type": "bug",
    "summary": "Login button not working on mobile",
    "description": "When I tap the login button on my iPhone, nothing happens. I've tried restarting the app and clearing cache, but the issue persists. This started happening after the last update.",
    "repo": "bamr87/githubai",
    "context_files": [
        "README.md",
        "docs/TROUBLESHOOTING.md"
    ]
}
```

#### Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `feedback_type` | string | Yes | - | Type of feedback. Choices: `bug`, `feature` |
| `summary` | string | Yes | - | Short summary of the issue (becomes issue title). Max 200 characters. |
| `description` | string | Yes | - | Detailed description of the issue or feature request. |
| `repo` | string | No | `bamr87/githubai` | Repository in format `owner/repo` |
| `context_files` | array[string] | No | `[]` | Optional list of repository files to provide context for AI refinement |

## Response

### Success Response (201 Created)

```json
{
    "id": 43,
    "github_repo": "bamr87/githubai",
    "github_issue_number": 124,
    "title": "Login button not working on mobile",
    "body": "## Summary\n\nUser reports that the login button is unresponsive on mobile devices (iOS).\n\n## Details\n\nWhen tapping the login button on iPhone, no action occurs. The issue began after the most recent application update.\n\n## Steps to Reproduce\n\n1. Open the application on an iPhone\n2. Navigate to the login screen\n3. Tap the login button\n\n## Expected Behavior\n\nThe login form should appear or authentication should proceed.\n\n## Actual Behavior\n\nNo response when button is tapped. No error messages displayed.\n\n## User-Attempted Solutions\n\n- Restarted the application\n- Cleared cache\n\nIssue persists after these attempts.\n\n## Environment\n\n- Device: iPhone\n- Version: Latest update\n\n## Priority\n\nHigh - blocks user authentication on mobile platform",
    "html_url": "https://github.com/bamr87/githubai/issues/124",
    "state": "open",
    "issue_type": "bug",
    "labels": [
        "ai-generated",
        "bug"
    ],
    "parent_issue": null,
    "ai_generated": true,
    "template": null,
    "file_references": [
        {
            "id": 1,
            "file_path": "README.md",
            "content": "# GitHubAI...",
            "created_at": "2025-11-21T10:35:00Z"
        }
    ],
    "sub_issues_count": 0,
    "created_at": "2025-11-21T10:35:00Z",
    "updated_at": "2025-11-21T10:35:00Z"
}
```

### Error Responses

#### 400 Bad Request

Missing required fields:

```json
{
    "feedback_type": [
        "This field is required."
    ],
    "summary": [
        "This field is required."
    ]
}
```

Invalid feedback type:

```json
{
    "feedback_type": [
        "\"invalid\" is not a valid choice."
    ]
}
```

#### 401 Unauthorized

Missing or invalid authentication credentials.

#### 500 Internal Server Error

GitHub API failure or AI service error:

```json
{
    "error": "GitHub API error: Unable to create issue"
}
```

## Examples

### cURL

**Bug Report:**

```bash
curl -X POST http://localhost:8000/api/issues/issues/create-from-feedback/ \
    -H "Content-Type: application/json" \
    -d '{
        "feedback_type": "bug",
        "summary": "Login button not working",
        "description": "When I click the login button, nothing happens.",
        "repo": "bamr87/githubai"
    }'
```

**Feature Request with Context:**

```bash
curl -X POST http://localhost:8000/api/issues/issues/create-from-feedback/ \
    -H "Content-Type: application/json" \
    -d '{
        "feedback_type": "feature",
        "summary": "Add dark mode support",
        "description": "I would love to see a dark theme option for the application. It would be easier on the eyes during night-time use.",
        "repo": "bamr87/githubai",
        "context_files": ["README.md"]
    }'
```

### Python

```python
import requests

url = "http://localhost:8000/api/issues/issues/create-from-feedback/"

response = requests.post(url, json={
    "feedback_type": "bug",
    "summary": "Search not returning results",
    "description": "The search function returns no results even when I know matching issues exist.",
    "repo": "bamr87/githubai"
})

if response.status_code == 201:
    issue = response.json()
    print(f"Created issue #{issue['github_issue_number']}")
    print(f"URL: {issue['html_url']}")
```

### JavaScript/TypeScript

**React feedback form integration:**

```javascript
async function submitFeedback(formData) {
    const response = await fetch('/api/issues/issues/create-from-feedback/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            feedback_type: formData.type,
            summary: formData.title,
            description: formData.details,
            repo: 'bamr87/githubai'
        })
    });

    if (response.ok) {
        const issue = await response.json();
        return {
            success: true,
            issueNumber: issue.github_issue_number,
            url: issue.html_url
        };
    } else {
        const error = await response.json();
        return {
            success: false,
            error: error.error
        };
    }
}
```

## Notes

### Performance

- **Response Time**: 5-10 seconds (faster than auto-issue endpoint)
- **AI Processing**: Single AI API call for content refinement
- **Rate Limits**: Subject to GitHub API limits

### Best Practices

1. **Validate Input**: Ensure summary is concise (< 200 chars)
2. **Detailed Descriptions**: More context yields better AI refinement
3. **Use Context Files**: Include relevant documentation for better results
4. **User Attribution**: Consider adding user info in description

### AI Refinement Process

The AI transforms raw feedback into structured issues with:

- **Bug Reports**:
  - Summary section
  - Steps to Reproduce
  - Expected vs Actual Behavior
  - Environment information
  - Priority assessment

- **Feature Requests**:
  - Clear feature description
  - Motivation and use case
  - Proposed solution
  - Acceptance criteria
  - Implementation considerations

### Labels Applied

- Base: `ai-generated`
- Type-specific: `bug` or `feature`

### Configuration Requirements

Ensure environment variables are set:

- `GITHUB_TOKEN` - For issue creation
- `AI_API_KEY` - For content refinement
- `AI_PROVIDER` - AI service configuration

### Integration Scenarios

**1. Support Ticket System:**
```python
# Convert support ticket to GitHub issue
ticket = get_support_ticket(ticket_id)
create_feedback_issue(
    feedback_type='bug' if ticket.is_bug else 'feature',
    summary=ticket.subject,
    description=ticket.body,
    context_files=['docs/TROUBLESHOOTING.md']
)
```

**2. In-App Feedback Form:**
```javascript
// User feedback button handler
document.querySelector('#feedback-btn').addEventListener('click', () => {
    showFeedbackModal({
        onSubmit: async (data) => {
            const result = await submitFeedback(data);
            if (result.success) {
                showSuccess(`Issue #${result.issueNumber} created!`);
            }
        }
    });
});
```

**3. Email-to-Issue:**
```python
# Parse email and create issue
def process_feedback_email(email):
    issue = create_feedback_issue(
        feedback_type='bug',
        summary=email.subject,
        description=email.body,
        repo='bamr87/githubai'
    )
    send_confirmation_email(email.sender, issue.html_url)
```

### Related Endpoints

- `POST /api/issues/issues/create-auto-issue/` - Automated repository analysis
- `POST /api/issues/issues/create-sub-issue/` - Template-based issue creation
- `GET /api/issues/issues/` - List all issues
- `GET /api/issues/issues/{id}/` - Get specific issue

---

## General API Information

### Base URL

```
http://localhost:8000/api/issues/issues/
```

Production: `https://yourdomain.com/api/issues/issues/`

### Authentication

Both endpoints use Django's default authentication system. In production, consider:

- Token authentication
- Session authentication
- OAuth2

### Rate Limiting

- Not implemented by default
- Recommended: 100 requests/hour per user
- Consider throttling in `settings.py`

### Error Handling

All endpoints return consistent error structures:

```json
{
    "error": "Human-readable error message",
    "details": {
        "field_name": ["Validation error message"]
    }
}
```

### Versioning

Current API version: `v1` (implicit)

Future versions may use path-based versioning: `/api/v2/issues/`

### Support

- Documentation: See [docs/](../../../docs/)
- Issues: [GitHub Issues](https://github.com/bamr87/githubai/issues)
- Tests: `tests/test_issues_service.py`
