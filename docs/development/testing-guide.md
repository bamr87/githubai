# Testing Guide

## Overview

This guide covers testing strategies, tools, and best practices for GitHubAI.

## Test Structure

```
tests/
├── test_ai_services.py          # AI service tests
├── test_auto_issue_service.py   # Auto-issue feature tests
├── test_docs_service.py         # Documentation generation tests
├── test_github_integration.py   # GitHub API tests
├── test_issues_service.py       # Issue service tests
└── test_versioning_service.py   # Version management tests
```

## Running Tests

### All Tests

```bash
docker-compose exec web pytest
```

### Specific Test File

```bash
docker-compose exec web pytest tests/test_auto_issue_service.py
```

### Specific Test

```bash
docker-compose exec web pytest tests/test_auto_issue_service.py::TestAutoIssueService::test_scan_for_todos
```

### With Coverage

```bash
docker-compose exec web pytest --cov=apps.core.services tests/
```

### With Verbose Output

```bash
docker-compose exec web pytest -v
```

## Test Categories

### Unit Tests

Test individual components in isolation.

**Example**:

```python
@pytest.mark.django_db
def test_scan_for_todos():
    service = AutoIssueService()
    content = "# TODO: Fix this\n# FIXME: Bug here"
    findings = service._scan_for_todos(content)
    assert len(findings) == 2
```

### Integration Tests

Test interactions between components.

**Example**:

```python
@pytest.mark.django_db
def test_create_issue_end_to_end(mocker):
    # Mock external services
    mock_github = mocker.patch('core.services.GitHubService')
    mock_ai = mocker.patch('core.services.AIService')

    service = AutoIssueService()
    issue = service.analyze_repo_and_create_issue(...)

    assert issue.github_issue_number is not None
```

### API Tests

Test REST API endpoints.

**Example**:

```python
@pytest.mark.django_db
def test_create_auto_issue_endpoint(client):
    response = client.post(
        '/api/issues/issues/create-auto-issue/',
        data={'chore_type': 'code_quality', 'auto_submit': false},
        content_type='application/json'
    )
    assert response.status_code == 200
```

## Feature-Specific Testing

### Auto Issue Generation

See complete testing guide: [Auto Issue Testing](../testing/AUTO_ISSUE_TESTING_CHECKLIST.md)

**Quick Test**:

```bash
# Run all auto-issue tests
docker-compose exec web pytest tests/test_auto_issue_service.py -v

# Test dry-run mode
docker-compose exec web python manage.py auto_issue --chore-type code_quality --dry-run
```

### AI Chat Frontend

See complete testing guide: [Chat Testing](../testing/AI_CHAT_TESTING.md)

**Manual Test**:

```bash
# Test API endpoint
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'

# Test frontend
open http://localhost:5173
```

## Mocking External Services

### Mocking GitHub API

```python
@pytest.mark.django_db
def test_with_mocked_github(mocker):
    mock_github = mocker.patch('core.services.github_service.GitHubService')
    mock_instance = mock_github.return_value
    mock_instance.create_github_issue.return_value = MagicMock(
        number=123,
        html_url='https://github.com/repo/issues/123'
    )

    # Test code that uses GitHubService
```

### Mocking AI Service

```python
@pytest.mark.django_db
def test_with_mocked_ai(mocker):
    mock_ai = mocker.patch('core.services.ai_service.AIService')
    mock_instance = mock_ai.return_value
    mock_instance.call_ai_chat.return_value = "Mocked AI response"

    # Test code that uses AIService
```

## Test Configuration

### pytest.ini

Located at project root:

```ini
[pytest]
DJANGO_SETTINGS_MODULE = githubai.settings
python_files = tests.py test_*.py *_tests.py
```

### conftest.py

Located in `tests/` directory for shared fixtures.

### Coverage Configuration

In `pyproject.toml`:

```toml
[tool.pytest.ini_options]
addopts = "--cov=apps --cov-report=html --cov-report=term"
```

## Continuous Integration

Tests run automatically on:

- Pull requests
- Pushes to main branch
- Scheduled nightly builds

See `.github/workflows/` for CI configuration.

## Writing New Tests

### Test Naming Convention

- Test files: `test_<feature>.py`
- Test functions: `test_<what_it_tests>`
- Test classes: `Test<FeatureName>`

### Example Test Template

```python
import pytest
from core.services import MyService

@pytest.mark.django_db
class TestMyFeature:
    def test_basic_functionality(self):
        """Test that basic functionality works."""
        service = MyService()
        result = service.do_something()
        assert result is not None

    def test_error_handling(self):
        """Test that errors are handled gracefully."""
        service = MyService()
        with pytest.raises(ValueError):
            service.do_something_invalid()

    def test_with_mocked_dependency(self, mocker):
        """Test with mocked external service."""
        mock_service = mocker.patch('core.services.ExternalService')
        mock_service.return_value.call.return_value = "mocked"

        service = MyService()
        result = service.use_external_service()

        assert result == "mocked"
        mock_service.return_value.call.assert_called_once()
```

## Test Data Management

### Using Fixtures

```python
@pytest.fixture
def sample_issue():
    """Create a sample issue for testing."""
    return Issue.objects.create(
        github_repo='test/repo',
        github_issue_number=1,
        title='Test Issue',
        body='Test body'
    )

def test_with_fixture(sample_issue):
    assert sample_issue.title == 'Test Issue'
```

### Factory Pattern

```python
from factory.django import DjangoModelFactory

class IssueFactory(DjangoModelFactory):
    class Meta:
        model = Issue

    github_repo = 'test/repo'
    title = 'Test Issue'
```

## Performance Testing

### Load Testing with Locust

```python
from locust import HttpUser, task, between

class GitHubAIUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def create_auto_issue(self):
        self.client.post(
            "/api/issues/issues/create-auto-issue/",
            json={"chore_type": "code_quality", "auto_submit": false}
        )
```

Run with:

```bash
locust -f tests/locustfile.py --host=http://localhost:8000
```

## Debugging Tests

### Run with PDB

```bash
docker-compose exec web pytest --pdb
```

### Print Debug Output

```bash
docker-compose exec web pytest -s
```

### Specific Test with Verbose

```bash
docker-compose exec web pytest tests/test_file.py::test_name -vv
```

## Best Practices

1. **Test in Isolation**: Use mocks for external services
2. **Keep Tests Fast**: Mock slow operations
3. **Test Edge Cases**: Don't just test happy paths
4. **Use Descriptive Names**: Test names should explain what they test
5. **One Assert Per Test**: When possible, test one thing at a time
6. **Clean Up After Tests**: Use fixtures and teardown
7. **Mock External APIs**: Don't make real API calls in tests
8. **Test Documentation**: Include docstrings in test functions

## Coverage Goals

- **Overall**: 80% minimum
- **New Features**: 100% of public methods
- **Critical Paths**: 100% coverage

Check coverage report:

```bash
docker-compose exec web pytest --cov=apps --cov-report=html
open htmlcov/index.html
```

## Related Documentation

- [Auto Issue Testing Checklist](../testing/AUTO_ISSUE_TESTING_CHECKLIST.md)
- [AI Chat Testing Guide](../testing/AI_CHAT_TESTING.md)
- [Contributing Guide](contributing.md)

## Support

For testing questions:

- Check existing test files in `tests/`
- Review pytest documentation: <https://docs.pytest.org>
- Ask in GitHub discussions
