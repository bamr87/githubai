"""
Pytest configuration file for GitHubAI Django tests.

Provides fixtures and configuration for testing Django apps.
"""

from __future__ import annotations

import unittest.mock as mock
import pytest
from _pytest.nodes import Item
from django.core.management import call_command


def pytest_addoption(parser):
	"""Add custom command line options."""
	parser.addoption(
		"--run-integration",
		action="store_true",
		default=False,
		help="Run integration tests that require API keys"
	)


def pytest_configure(config):
	"""Register custom markers."""
	config.addinivalue_line(
		"markers", "integration: mark test as integration test requiring external APIs"
	)
	config.addinivalue_line(
		"markers", "spark: mark test as spark-related"
	)


def pytest_collection_modifyitems(config, items: list[Item]):
	"""Modify test collection to add markers automatically."""
	skip_integration = pytest.mark.skip(reason="need --run-integration option to run")

	for item in items:
		if "spark" in item.nodeid:
			item.add_marker(pytest.mark.spark)
		elif "_int_" in item.nodeid or "integration" in item.nodeid:
			item.add_marker(pytest.mark.integration)
			if not config.getoption("--run-integration"):
				item.add_marker(skip_integration)


@pytest.fixture
def unit_test_mocks(monkeypatch: None):
    """Include Mocks here to execute all commands offline and fast."""
    pass


@pytest.fixture
def mocker(monkeypatch):
    # Minimal implementation for tests
    class Mocker:
        def patch(self, target, new=None):
            if new is None:
                new = (
                    mock.MagicMock()
                )  # Create a default MagicMock if no replacement is provided.
            monkeypatch.setattr(target, new)
            return new  # Return the new mock

        def Mock(self, *args, **kwargs):
            return mock.MagicMock(*args, **kwargs)

        # Add more helper methods as needed by your tests

    return Mocker()


# ============================================================================
# Data Loading Fixtures (Two-Tier Strategy)
# ============================================================================

@pytest.fixture(scope='session')
def load_test_config(django_db_setup, django_db_blocker):
    """
    Load critical technical configuration (Category 1 data).

    Loads AIProvider and AIModel test configuration once per test session.
    This runs before any tests and provides the foundation for AI operations.

    Usage:
        @pytest.mark.django_db
        def test_my_feature(load_test_config):
            # AI providers are now configured
            from core.models import AIProvider
            provider = AIProvider.objects.get(name='openai')
            assert provider.has_api_key
    """
    with django_db_blocker.unblock():
        # Load test configuration fixture
        call_command('loaddata', 'apps/core/fixtures/test_config.json', verbosity=0)


@pytest.fixture
def sample_content_data(db, load_test_config):
    """
    Load sample content data (Category 2 data).

    Loads PromptTemplates, IssueTemplates, and sample Issues.
    This fixture depends on load_test_config being loaded first.

    Usage:
        @pytest.mark.django_db
        def test_prompts(sample_content_data):
            from core.models import PromptTemplate
            templates = PromptTemplate.objects.all()
            assert templates.count() >= 2
    """
    # Load content fixture
    call_command('loaddata', 'apps/core/fixtures/test_content.json', verbosity=0)


@pytest.fixture
def ai_provider_config(db, load_test_config):
    """
    Provides access to test AI provider configuration.

    Returns a dictionary with configured test providers and models.

    Usage:
        def test_ai_service(ai_provider_config):
            assert 'openai' in ai_provider_config['providers']
            assert ai_provider_config['default_provider'].name == 'openai'
    """
    from core.models import AIProvider, AIModel

    providers = {p.name: p for p in AIProvider.objects.all()}
    default_provider = AIProvider.objects.filter(is_active=True).first()
    default_model = AIModel.objects.filter(is_default=True, is_active=True).first()

    return {
        'providers': providers,
        'default_provider': default_provider,
        'default_model': default_model,
        'models': list(AIModel.objects.all()),
    }


@pytest.fixture
def test_prompt_templates(db, sample_content_data):
    """
    Provides quick access to test prompt templates.

    Returns a dictionary of prompt templates by category.

    Usage:
        def test_chat(test_prompt_templates):
            chat_template = test_prompt_templates['chat']
            assert chat_template is not None
    """
    from core.models import PromptTemplate

    templates = {}
    for template in PromptTemplate.objects.all():
        templates[template.category] = template

    return templates


@pytest.fixture
def test_issues(db, sample_content_data):
    """
    Provides access to sample test issues.

    Returns a list of test Issue objects.

    Usage:
        def test_issue_service(test_issues):
            assert len(test_issues) >= 2
            assert test_issues[0].github_repo == 'test/repo'
    """
    from core.models import Issue

    return list(Issue.objects.all())
