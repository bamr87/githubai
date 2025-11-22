# Contributing to GitHubAI

Thank you for your interest in contributing to GitHubAI! This guide will help you get started.

## Quick Start

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Set up development environment**
4. **Create a feature branch**
5. **Make your changes**
6. **Test thoroughly**
7. **Submit a pull request**

## Development Setup

### Prerequisites

- Docker and Docker Compose
- Git
- Python 3.11+ (for local development)
- Node.js 20+ (for frontend development)

### Initial Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/githubai.git
cd githubai

# Add upstream remote
git remote add upstream https://github.com/bamr87/githubai.git

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Start services
docker-compose -f infra/docker/docker-compose.yml up -d

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser
```

## Development Workflow

### Creating a Feature Branch

```bash
# Update your main branch
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/your-feature-name
```

### Making Changes

1. **Follow coding standards** (see below)
2. **Write tests** for new features
3. **Update documentation** as needed
4. **Test your changes** thoroughly

### Testing Changes

```bash
# Run all tests
docker-compose exec web pytest

# Run specific tests
docker-compose exec web pytest tests/test_your_feature.py

# Check coverage
docker-compose exec web pytest --cov
```

### Submitting Changes

```bash
# Stage your changes
git add .

# Commit with descriptive message
git commit -m "feat: add new feature X

Detailed description of what this commit does.

Closes #123"

# Push to your fork
git push origin feature/your-feature-name
```

Then create a pull request on GitHub.

## Coding Standards

### Python Style

- Follow **PEP 8**
- Use **black** for formatting (120 line length)
- Use **snake_case** for functions/variables
- Use **PascalCase** for classes
- Add **docstrings** to all public modules, classes, and functions

### Example

```python
def create_github_issue(repo: str, title: str, body: str) -> Issue:
    """Create a new GitHub issue.

    Args:
        repo: Repository in format 'owner/repo'
        title: Issue title
        body: Issue body content

    Returns:
        Issue instance with GitHub details

    Raises:
        GitHubException: If issue creation fails
    """
    # Implementation here
    pass
```

### Django Conventions

- **Service Layer Pattern**: Business logic in `services.py`, not views
- **Use Django ORM**: No raw SQL
- **Serializers**: Validate all API inputs
- **Logging**: Use project logger

Example:

```python
# Good
from core.services import AIService

ai_service = AIService()
response = ai_service.call_ai_chat(system_prompt, user_prompt)

# Bad - don't call AI APIs directly
import openai
response = openai.chat.completions.create(...)
```

### Frontend Standards

- Use **React functional components**
- Follow **Airbnb React style guide**
- Use **Ant Design** components when possible
- Handle errors gracefully

### Commit Messages

Follow **Conventional Commits** format:

```
type(scope): short description

Longer description if needed.

Closes #issue-number
```

**Types**:

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding/updating tests
- `chore`: Maintenance tasks

**Examples**:

```
feat(auto-issue): add dependency analysis chore type
fix(chat): handle API timeout errors gracefully
docs(readme): update installation instructions
```

## Testing Guidelines

### Writing Tests

- **Test file naming**: `test_<feature>.py`
- **Test function naming**: `test_<what_it_tests>`
- **One test per behavior**: Test one thing at a time
- **Use mocks**: Don't call external APIs in tests
- **Clean test data**: Use fixtures and factories

### Example Test

```python
import pytest
from core.services import AutoIssueService

@pytest.mark.django_db
def test_scan_for_todos_finds_todo_comments():
    """Test that TODO comments are detected correctly."""
    service = AutoIssueService()
    content = "# TODO: Fix this bug\ndef my_function():\n    pass"

    findings = service._scan_for_todos(content)

    assert len(findings) == 1
    assert 'TODO: Fix this bug' in findings[0]
```

See [Testing Guide](testing-guide.md) for more details.

## Documentation

### When to Update Documentation

- Adding new features
- Changing API endpoints
- Modifying configuration requirements
- Fixing bugs that affect user workflows

### Documentation Structure

```
docs/
├── README.md                    # Documentation index
├── GETTING_STARTED.md          # Quickstart guide
├── guides/                     # User guides
├── api/                        # API reference
├── development/                # Developer docs
└── releases/                   # Release notes
```

### Writing Documentation

- Use **clear, concise language**
- Include **code examples**
- Add **troubleshooting tips**
- Keep **up to date** with code changes

## Pull Request Process

### Before Submitting

- [ ] Tests pass: `docker-compose exec web pytest`
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] Commit messages follow conventions
- [ ] Branch is up to date with main

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings generated
```

### Review Process

1. **Automated checks** run (tests, linting)
2. **Maintainer review** (may request changes)
3. **Address feedback** if needed
4. **Merge** once approved

## Project Structure

Understanding the codebase:

```
githubai/
├── apps/                      # Django applications
│   ├── core/                 # Core functionality
│   │   ├── services/        # Business logic
│   │   ├── models.py        # Database models
│   │   ├── views.py         # API endpoints
│   │   └── serializers.py   # API serializers
│   └── githubai/            # Project settings
├── frontend/                 # React application
│   ├── src/
│   │   ├── App.jsx         # Main component
│   │   └── App.css         # Styles
│   └── package.json        # Dependencies
├── docs/                    # Documentation
├── infra/                   # Infrastructure
│   ├── docker/             # Docker configuration
│   └── scripts/            # Utility scripts
└── tests/                  # Test files
```

## Common Tasks

### Adding a New API Endpoint

1. Create serializer in `apps/core/serializers.py`
2. Add view action in `apps/core/views.py`
3. Add tests in `tests/test_*.py`
4. Update API documentation in `docs/api/`

### Adding a New Service Method

1. Add method to service class in `apps/core/services/`
2. Add tests in `tests/test_*_service.py`
3. Update relevant documentation

### Adding a New Management Command

1. Create command file in `apps/core/management/commands/`
2. Implement `handle()` method
3. Add tests
4. Document usage in guides

## Getting Help

- **Questions**: Open a GitHub Discussion
- **Bugs**: Create an issue with reproduction steps
- **Security**: Email <security@example.com> (not public issues)
- **Chat**: Join our community chat (link)

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Follow GitHub's Community Guidelines

## License

By contributing, you agree that your contributions will be licensed under the project's license (see LICENSE file).

## Recognition

Contributors will be recognized in:

- Release notes
- CONTRIBUTORS.md file
- Git commit history

Thank you for contributing to GitHubAI! 🚀
