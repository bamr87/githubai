"""
This is a configuration file for pytest containing customizations and fixtures.

In VSCode, Code Coverage is recorded in config.xml. Delete this file to reset reporting.
"""

from __future__ import annotations

from typing import List

import pytest
from _pytest.nodes import Item
import unittest.mock as mock  # Added import for MagicMock


def pytest_collection_modifyitems(items: list[Item]):
    for item in items:
        if "spark" in item.nodeid:
            item.add_marker(pytest.mark.spark)
        elif "_int_" in item.nodeid:
            item.add_marker(pytest.mark.integration)


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
                new = mock.MagicMock()  # Create a default MagicMock if no replacement is provided.
            monkeypatch.setattr(target, new)
            return new  # Return the new mock
        def Mock(self, *args, **kwargs):
            return mock.MagicMock(*args, **kwargs)
        # Add more helper methods as needed by your tests
    return Mocker()
