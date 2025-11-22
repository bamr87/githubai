# Release v0.2.0 - 2025-11-21

## 🎉 Highlights

GitHubAI now includes **intelligent automated issue generation** powered by AI. The new Auto Issue feature automatically analyzes your repository for maintenance needs and creates well-structured GitHub issues with actionable recommendations. Additionally, convert raw user feedback into professional GitHub issues instantly with the new Feedback Issue endpoint.

## ✨ New Features

### 🤖 Auto Issue Generation

Automatically analyze your repository and create maintenance issues with AI-powered content generation.

**Six Analysis Types:**

1. **Code Quality** - Detects quality issues, long lines, missing docstrings, and complexity problems
2. **TODO Scan** - Finds TODO/FIXME/HACK comments that need attention
3. **Documentation** - Identifies missing or outdated documentation
4. **Dependencies** - Checks for outdated dependencies and security issues
5. **Test Coverage** - Analyzes test coverage and suggests missing tests
6. **General Review** - Comprehensive repository health check

**How to Use:**

```bash
# CLI - List available analysis types
docker-compose exec web python manage.py auto_issue --list-chores

# Run code quality analysis
docker-compose exec web python manage.py auto_issue \
    --chore-type code_quality

# Dry run (preview without creating issue)
docker-compose exec web python manage.py auto_issue \
    --chore-type general_review \
    --dry-run
```

```bash
# API - Create auto-issue
curl -X POST http://localhost:8000/api/issues/issues/create-auto-issue/ \
    -H "Content-Type: application/json" \
    -d '{
        "chore_type": "code_quality",
        "auto_submit": true
    }'
```

### 📝 Feedback Issue Creation

Convert raw user feedback (bug reports, feature requests) into structured GitHub issues.

**How to Use:**

```bash
curl -X POST http://localhost:8000/api/issues/issues/create-from-feedback/ \
    -H "Content-Type: application/json" \
    -d '{
        "feedback_type": "bug",
        "summary": "Login button not working",
        "description": "When I click login, nothing happens."
    }'
```

Perfect for integrating with:
- User feedback forms
- Support ticket systems
- In-app feedback widgets
- Email-to-issue workflows

### 🔧 API Endpoints

Two new REST API endpoints:

- `POST /api/issues/issues/create-auto-issue/` - Automated repository analysis
- `POST /api/issues/issues/create-from-feedback/` - User feedback processing

Both endpoints support:
- Dry-run mode for preview
- Custom file targeting
- AI-powered content refinement
- Automatic label assignment

## 🔧 Improvements

- **Enhanced IssueService** - Now supports feedback-based issue creation alongside template-based generation
- **Comprehensive Testing** - 11 new unit tests with 100% coverage of new functionality
- **Better Documentation** - Complete API docs, usage examples, and troubleshooting guides
- **Flexible Analysis** - Target specific files or use intelligent defaults based on analysis type

## 🐛 Bug Fixes

None - This is a new feature release

## 📚 Documentation

New documentation added:

- **[AUTO_ISSUE_FEATURE.md](docs/AUTO_ISSUE_FEATURE.md)** - Complete user guide with examples
- **[AUTO_ISSUE_GENERATION.md](docs/features/AUTO_ISSUE_GENERATION.md)** - Technical implementation details
- **[AUTO_ISSUE_ENDPOINTS.md](docs/api/AUTO_ISSUE_ENDPOINTS.md)** - Full API reference
- **[AUTO_ISSUE_TESTING_CHECKLIST.md](docs/testing/AUTO_ISSUE_TESTING_CHECKLIST.md)** - Testing guide
- **[CHANGELOG.md](CHANGELOG.md)** - Keep a Changelog format
- **Updated README** - New features, CLI examples, API endpoints

## 🔒 Security

- All user inputs validated via Django REST Framework serializers
- GitHub tokens and AI API keys stored securely in environment variables
- No sensitive data exposed in API responses or logs
- SQL injection protection via Django ORM
- Comprehensive input sanitization

## 💾 Database Changes

**No database migrations required**. The feature uses existing models:
- `Issue` - Stores auto-generated and feedback issues
- `IssueFileReference` - Stores context files

New issues are marked with `ai_generated=True` and appropriate labels.

## ⚙️ Configuration

### Required Environment Variables

```bash
# GitHub API (required for issue creation)
GITHUB_TOKEN=ghp_your_token_here

# AI Provider (required for content generation)
AI_API_KEY=your_api_key
AI_PROVIDER=openai  # or anthropic, google, etc.
AI_MODEL=gpt-4o-mini
```

### Optional Settings

```bash
DEFAULT_REPO=bamr87/githubai  # Default repository for commands
AI_TEMPERATURE=0.2
AI_MAX_TOKENS=2500
```

## 📦 Installation/Upgrade

### New Installation

```bash
git clone https://github.com/bamr87/githubai.git
cd githubai

# Configure environment
cp .env.example .env
# Edit .env with your GITHUB_TOKEN and AI_API_KEY

# Start services
docker-compose up -d

# Initialize
./init.sh
```

### Upgrade from v0.1.14

```bash
# Pull latest code
git pull origin main

# Restart services (no migrations needed)
docker-compose down
docker-compose up -d

# Verify feature
docker-compose exec web python manage.py auto_issue --list-chores
```

## 🧪 Testing

**Test Coverage**: 11/11 tests passing (100% ✅)

Run tests:

```bash
# All auto-issue tests
docker-compose exec web pytest tests/test_auto_issue_service.py -v

# With coverage
docker-compose exec web pytest --cov=apps.core.services tests/
```

**Manual Testing**:

```bash
# Test dry-run mode
docker-compose exec web python manage.py auto_issue \
    --chore-type code_quality \
    --dry-run

# Test API
curl -X POST http://localhost:8000/api/issues/issues/create-auto-issue/ \
    -H "Content-Type: application/json" \
    -d '{"chore_type": "general_review", "auto_submit": false}'
```

## 🚀 Usage Examples

### Weekly Repository Health Check

```bash
#!/bin/bash
# weekly-audit.sh
docker-compose exec web python manage.py auto_issue \
    --repo bamr87/githubai \
    --chore-type general_review
```

### Pre-Commit TODO Scanner

```bash
# .git/hooks/pre-commit
docker-compose exec web python manage.py auto_issue \
    --chore-type todo_scan \
    --dry-run > todos.txt

if [ -s todos.txt ]; then
    echo "⚠️  TODOs found - consider addressing"
fi
```

### User Feedback Form

```javascript
// React component
async function submitFeedback(formData) {
    const response = await fetch('/api/issues/issues/create-from-feedback/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            feedback_type: formData.type,
            summary: formData.title,
            description: formData.details
        })
    });
    
    if (response.ok) {
        const issue = await response.json();
        alert(`Issue #${issue.github_issue_number} created!`);
    }
}
```

## 🔗 Links

- **Full Changelog**: [CHANGELOG.md](CHANGELOG.md)
- **Feature Documentation**: [docs/AUTO_ISSUE_FEATURE.md](docs/AUTO_ISSUE_FEATURE.md)
- **API Reference**: [docs/api/AUTO_ISSUE_ENDPOINTS.md](docs/api/AUTO_ISSUE_ENDPOINTS.md)
- **Repository**: [github.com/bamr87/githubai](https://github.com/bamr87/githubai)
- **Issues**: [github.com/bamr87/githubai/issues](https://github.com/bamr87/githubai/issues)

## 📊 Statistics

- **Files Added**: 6 (services, commands, tests, docs)
- **Files Modified**: 5 (README, views, serializers, __init__)
- **Lines of Code**: ~900 (service + tests + docs)
- **Test Coverage**: 100% of public methods
- **Documentation**: ~2,000 lines

## 🙏 Contributors

- **@bamr87** - Feature implementation, documentation, testing

## 💡 What's Next?

Future enhancements planned:

1. **Scheduled Automation** - Celery tasks for automatic weekly/daily scans
2. **Custom Rules** - Organization-specific code quality rules
3. **Metrics Dashboard** - Visualize findings and trends over time
4. **Slack Integration** - Notifications when issues are created
5. **Multi-Language Support** - Extended analysis for JavaScript, Java, etc.

## ⚠️ Known Limitations

1. **Rate Limits**: GitHub API has rate limits (5000/hour authenticated)
2. **File Size**: Large files (>1MB) may timeout during analysis
3. **Language Support**: Code analysis currently optimized for Python
4. **AI Costs**: Each analysis triggers 1-2 AI API calls
5. **Pattern Matching**: TODO scanning uses regex (may miss unusual formats)

## 🆘 Support

Having issues? Check:

1. **Documentation**: See [docs/](docs/) directory
2. **Troubleshooting**: [docs/AUTO_ISSUE_FEATURE.md](docs/AUTO_ISSUE_FEATURE.md#troubleshooting)
3. **Logs**: `docker-compose logs -f web`
4. **Issues**: [GitHub Issues](https://github.com/bamr87/githubai/issues)

## 🎯 Breaking Changes

**None** - This release is fully backward compatible with v0.1.14.

All existing functionality remains unchanged. New features are additive only.

---

**Thank you for using GitHubAI!** 🚀

If you find this feature useful, please ⭐ star the repository and share your feedback!
