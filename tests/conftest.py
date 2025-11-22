"""
Pytest configuration file for GitHubAI Django tests.

Provides fixtures and configuration for testing Django apps.
"""

from __future__ import annotations

import unittest.mock as mock
import pytest
from _pytest.nodes import Item


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
