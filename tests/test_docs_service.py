"""Tests for docs app services."""

from unittest.mock import Mock, patch

import pytest
from core.models import ChangelogEntry, DocumentationFile
from core.services import ChangelogService, DocGenerationService
from django.test import TestCase


@pytest.mark.django_db
class TestChangelogService:
    """Test cases for ChangelogService."""

    def setup_method(self):
        """Setup test fixtures."""
        self.service = ChangelogService()
        self.repo = "owner/repo"

    def test_service_initialization(self):
        """Test ChangelogService can be instantiated."""
        assert self.service is not None
        assert hasattr(self.service, "ai_service")

    @patch("core.services.doc_service.Repo")
    @patch("core.services.doc_service.OpenAIService")
    def test_generate_from_commit(self, mock_ai_class, mock_repo_class):
        """Test changelog generation from commit."""
        # Mock git Repo
        mock_repo = Mock()
        mock_commit = Mock()
        mock_commit.hexsha = "abc123"
        mock_commit.message = "Add new feature"
        mock_commit.diff.return_value = []
        mock_repo.head.commit = mock_commit
        mock_repo_class.return_value = mock_repo

        # Mock OpenAI service
        mock_openai_instance = Mock()
        mock_openai_instance.call_openai_chat.return_value = (
            "## Features\n- Added new feature"
        )
        mock_openai_class.return_value = mock_openai_instance

        service = ChangelogService()
        result = service.generate_from_commit(repo_path="/tmp/test_repo")

        assert result is not None
        assert hasattr(result, "commit_sha")
        assert result.commit_sha == "abc123"
        assert result.entry_type == "commit"

    @patch("core.services.doc_service.Github")
    @patch("core.services.doc_service.AIService")
    def test_generate_from_pr(self, mock_ai_class, mock_github_class):
        """Test changelog generation from pull request."""
        # Mock GitHub
        mock_github = Mock()
        mock_repo = Mock()
        mock_pr = Mock()
        mock_pr.get_files.return_value = []
        mock_repo.get_pull.return_value = mock_pr
        mock_github.get_repo.return_value = mock_repo
        mock_github_class.return_value = mock_github

        # Mock AI service
        mock_ai_instance = Mock()
        mock_ai_instance.call_ai_chat.return_value = (
            "## Changes\n- New feature added"
        )
        mock_ai_class.return_value = mock_ai_instance

        service = ChangelogService()
        result = service.generate_from_pr(pr_number=10, repo_name="owner/repo")

        assert result is not None
        assert result.pr_number == 10
        assert result.entry_type == "pr"

    @pytest.mark.django_db
    def test_changelog_entry_model_creation(self):
        """Test ChangelogEntry model creation."""
        entry = ChangelogEntry.objects.create(
            entry_type="commit",
            commit_sha="abc123",
            commit_message="Add new feature",
            ai_generated_content="## Features\n- New feature",
        )

        assert entry.id is not None
        assert entry.commit_sha == "abc123"
        assert entry.entry_type == "commit"

    @pytest.mark.django_db
    def test_changelog_entry_pr_reference(self):
        """Test ChangelogEntry with PR reference."""
        entry = ChangelogEntry.objects.create(
            entry_type="pr", pr_number=10, ai_generated_content="## Changes from PR #10"
        )

        assert entry.pr_number == 10
        assert entry.entry_type == "pr"


@pytest.mark.django_db
class TestDocGenerationService:
    """Test cases for DocGenerationService."""

    def setup_method(self):
        """Setup test fixtures."""
        self.service = DocGenerationService()

    def test_service_initialization(self):
        """Test DocGenerationService can be instantiated."""
        assert self.service is not None

    @patch("builtins.open", create=True)
    def test_parse_python_file(self, mock_open):
        """Test parsing Python file and extracting docstrings."""
        python_code = '''
def test_function():
	"""This is a test function."""
	pass

class TestClass:
	"""This is a test class."""

	def method(self):
		"""This is a method."""
		pass
'''
        mock_open.return_value.__enter__.return_value.read.return_value = python_code

        result = self.service.parse_python_file("test.py")

        assert result is not None
        assert "docstrings" in result
        assert "comments" in result
        assert len(result["docstrings"]) > 0

    @patch("builtins.open", create=True)
    def test_parse_python_file_no_docs(self, mock_open):
        """Test parsing Python file without docstrings."""
        python_code = """
def no_docs():
	pass
"""
        mock_open.return_value.__enter__.return_value.read.return_value = python_code

        result = self.service.parse_python_file("test.py")

        # Should still return structure even with no docstrings
        assert result is not None
        assert "docstrings" in result
        assert "comments" in result

    def test_generate_markdown_documentation(self):
        """Test generating markdown documentation."""
        parsed_data = {
            "docstrings": [("test_function", "This is a test function.")],
            "comments": [],
        }

        result = self.service.generate_markdown_documentation(parsed_data)

        assert result is not None
        assert "# Documentation" in result
        assert "test_function" in result

    @pytest.mark.django_db
    def test_documentation_file_model(self):
        """Test DocumentationFile model creation."""
        import hashlib

        content = "# Module Documentation\n\n## Functions"
        content_hash = hashlib.sha256(content.encode()).hexdigest()

        doc = DocumentationFile.objects.create(
            file_path="test/module.py",
            markdown_content=content,
            language="python",
            content_hash=content_hash,
            docstrings={},
            comments=[],
        )

        assert doc.id is not None
        assert doc.file_path == "test/module.py"
        assert doc.language == "python"
        assert doc.markdown_content == content


class TestDocServiceIntegration(TestCase):
    """Integration tests for doc services."""

    @pytest.mark.django_db
    def test_full_changelog_workflow(self):
        """Test complete changelog generation workflow."""
        # Create a changelog entry
        entry = ChangelogEntry.objects.create(
            entry_type="commit",
            commit_sha="test123",
            commit_message="Test commit",
            ai_generated_content="## Test\n- Test change",
        )

        # Verify it was created
        assert ChangelogEntry.objects.filter(commit_sha="test123").exists()

        # Verify we can retrieve it
        retrieved = ChangelogEntry.objects.get(commit_sha="test123")
        assert retrieved.ai_generated_content == entry.ai_generated_content
        assert retrieved.ai_generated_content == entry.ai_generated_content
        assert retrieved.ai_generated_content == entry.ai_generated_content
