"""Shared fixtures for the GitHubAI self-tests."""

import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent

# Make the load-config module importable as a unit under test.
sys.path.insert(0, str(REPO_ROOT / "actions" / "load-config"))


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture(scope="session")
def profiles_dir(repo_root) -> Path:
    return repo_root / "profiles"


@pytest.fixture(scope="session")
def workflow_files(repo_root):
    return sorted((repo_root / ".github" / "workflows").glob("*.yml"))


@pytest.fixture(scope="session")
def claude_workflow_files(workflow_files):
    return [p for p in workflow_files if p.name.startswith("claude")]


@pytest.fixture(scope="session")
def template_stub_files(repo_root):
    return sorted((repo_root / "template" / "workflows").glob("*.yml"))


def load_yaml(path: Path):
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)
