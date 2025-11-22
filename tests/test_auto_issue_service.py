"""Tests for auto-issue service"""
from unittest.mock import Mock, patch, MagicMock
import pytest
from core.models import Issue
from core.services import AutoIssueService
from django.test import TestCase


@pytest.mark.django_db
class TestAutoIssueService:
    """Test cases for AutoIssueService."""

    def setup_method(self):
        """Setup test fixtures."""
        self.service = AutoIssueService()
        self.repo = "bamr87/githubai"

    def test_service_initialization(self):
        """Test AutoIssueService can be instantiated."""
        assert self.service is not None
        assert hasattr(self.service, "github_service")
        assert hasattr(self.service, "ai_service")

    def test_list_chore_types(self):
        """Test listing available chore types."""
        chore_types = AutoIssueService.list_chore_types()
        assert isinstance(chore_types, dict)
        assert 'general_review' in chore_types
        assert 'code_quality' in chore_types
        assert 'todo_scan' in chore_types

    @patch("core.services.auto_issue_service.GitHubService")
    @patch("core.services.auto_issue_service.AIService")
    def test_analyze_repo_and_create_issue_success(
        self, mock_ai_class, mock_github_class
    ):
        """Test successful auto-issue creation."""
        # Mock GitHub service
        mock_github_instance = Mock()
        mock_github_instance.fetch_file_contents.return_value = "# README\nTest content"
        mock_github_instance.create_github_issue.return_value = {
            "number": 300,
            "html_url": "https://github.com/bamr87/githubai/issues/300",
        }
        mock_github_class.return_value = mock_github_instance

        # Mock AI service
        mock_ai_instance = Mock()
        mock_ai_instance.call_ai_chat.return_value = (
            "# Auto-Generated Issue\n\n## Summary\nTest analysis results"
        )
        mock_ai_class.return_value = mock_ai_instance

        service = AutoIssueService()
        issue = service.analyze_repo_and_create_issue(
            repo=self.repo,
            chore_type='general_review',
            auto_submit=True,
        )

        assert issue is not None
        assert issue.github_issue_number == 300
        assert issue.ai_generated is True
        assert 'auto-generated' in issue.labels
        mock_github_instance.create_github_issue.assert_called_once()
        mock_ai_instance.call_ai_chat.assert_called_once()

    @patch("core.services.auto_issue_service.GitHubService")
    @patch("core.services.auto_issue_service.AIService")
    def test_analyze_repo_dry_run(self, mock_ai_class, mock_github_class):
        """Test dry run mode (no GitHub issue creation)."""
        mock_github_instance = Mock()
        mock_github_instance.fetch_file_contents.return_value = "content"
        mock_github_class.return_value = mock_github_instance

        mock_ai_instance = Mock()
        mock_ai_instance.call_ai_chat.return_value = "Issue content"
        mock_ai_class.return_value = mock_ai_instance

        service = AutoIssueService()
        result = service.analyze_repo_and_create_issue(
            repo=self.repo,
            chore_type='general_review',
            auto_submit=False,
        )

        # Should return content but not create GitHub issue
        assert isinstance(result, str)
        mock_github_instance.create_github_issue.assert_not_called()

    def test_scan_for_todos(self):
        """Test TODO scanning functionality."""
        test_content = """
# Sample Python code
def my_function():
    # TODO: Implement this feature
    # FIXME: Fix this bug
    # HACK: Temporary workaround
    pass
"""
        findings = self.service._scan_for_todos(test_content, "test.py")
        assert len(findings) == 3
        assert any(f['type'] == 'TODO' for f in findings)
        assert any(f['type'] == 'FIXME' for f in findings)
        assert any(f['type'] == 'HACK' for f in findings)

    def test_analyze_code_quality(self):
        """Test code quality analysis."""
        # Test long line detection
        long_line = "x = " + "a" * 150
        findings = self.service._analyze_code_quality(long_line, "test.py")
        assert any(f['type'] == 'line_length' for f in findings)

    def test_get_default_files_for_chore(self):
        """Test getting default files for different chore types."""
        files = self.service._get_default_files_for_chore('code_quality')
        assert isinstance(files, list)
        assert len(files) > 0

    def test_get_labels_for_chore(self):
        """Test label generation for chore types."""
        labels = self.service._get_labels_for_chore('code_quality')
        assert 'auto-generated' in labels
        assert 'maintenance' in labels
        assert 'code-quality' in labels

    def test_generate_title(self):
        """Test title generation."""
        analysis_data = {'findings': [{'message': 'test1'}, {'message': 'test2'}]}
        title = self.service._generate_title('todo_scan', analysis_data)
        assert '[Auto]' in title
        assert '2 items' in title

    def test_invalid_chore_type(self):
        """Test error handling for invalid chore type."""
        with pytest.raises(ValueError) as exc_info:
            self.service.analyze_repo_and_create_issue(
                repo=self.repo,
                chore_type='invalid_type',
            )
        assert 'Invalid chore_type' in str(exc_info.value)
