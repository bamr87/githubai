"""Tests for issues app services."""

from unittest.mock import Mock, patch

import pytest
from core.models import Issue, IssueFileReference, IssueTemplate
from core.services import IssueService
from django.test import TestCase


@pytest.mark.django_db
class TestIssueService:
    """Test cases for IssueService."""

    def setup_method(self):
        """Setup test fixtures."""
        self.service = IssueService()
        self.repo = "owner/repo"

        # Create test template
        self.template = IssueTemplate.objects.create(
            name="Test Template.md",
            about="Test template description",
            title_prefix="[Test]: ",
            prompt="Test prompt",
            template_body="Test body template",
            labels=["test"],
            include_files=[],
        )

    def test_service_initialization(self):
        """Test IssueService can be instantiated."""
        assert self.service is not None
        assert hasattr(self.service, "github_service")
        assert hasattr(self.service, "ai_service")

    @patch("core.services.issue_service.GitHubService")
    @patch("core.services.issue_service.AIService")
    def test_create_sub_issue_from_template_success(
        self, mock_ai_class, mock_github_class
    ):
        """Test successful sub-issue creation."""
        # Mock GitHub service
        mock_github_instance = Mock()
        mock_github_instance.fetch_issue.return_value = {
            "number": 123,
            "title": "Parent Issue",
            "body": "Parent issue body <!-- template: Test Template.md -->",
            "html_url": "https://github.com/owner/repo/issues/123",
        }
        mock_github_instance.create_github_issue.return_value = {
            "number": 124,
            "title": "Sub Issue",
            "html_url": "https://github.com/owner/repo/issues/124",
        }
        mock_github_instance.fetch_file_contents.return_value = "file content"
        mock_github_class.return_value = mock_github_instance

        # Mock AI service
        mock_ai_instance = Mock()
        mock_ai_instance.call_ai_chat.return_value = (
            "# Generated content\nTest content"
        )
        mock_ai_class.return_value = mock_ai_instance

        service = IssueService()
        result = service.create_sub_issue_from_template(
            repo=self.repo, parent_issue_number=123
        )

        assert result is not None
        assert hasattr(result, "github_issue_number")
        assert result.github_issue_number == 124
        mock_github_instance.create_github_issue.assert_called_once()

    @patch("core.services.issue_service.GitHubService")
    def test_create_sub_issue_invalid_repo(self, mock_github_class):
        """Test sub-issue creation with invalid repo."""
        mock_github_instance = Mock()
        mock_github_instance.fetch_issue.side_effect = Exception("Repository not found")
        mock_github_class.return_value = mock_github_instance

        service = IssueService()

        with pytest.raises(Exception) as exc_info:
            service.create_sub_issue_from_template(
                repo="invalid/repo", parent_issue_number=999
            )

        assert "Repository not found" in str(exc_info.value)

    def test_get_template_by_name(self):
        """Test retrieving template by name."""
        template = IssueTemplate.objects.get(name="Test Template.md")
        assert template is not None
        assert template.name == "Test Template.md"

    def test_get_template_not_found(self):
        """Test retrieving non-existent template."""
        with pytest.raises(IssueTemplate.DoesNotExist):
            IssueTemplate.objects.get(name="Nonexistent Template")

    @pytest.mark.django_db
    def test_issue_model_creation(self):
        """Test Issue model creation."""
        issue = Issue.objects.create(
            github_repo=self.repo,
            github_issue_number=123,
            title="Test Issue",
            body="Test body",
            html_url="https://github.com/owner/repo/issues/123",
            state="open",
        )

        assert issue.id is not None
        assert issue.github_repo == self.repo
        assert issue.github_issue_number == 123
        assert str(issue) == "#123: Test Issue"
        assert issue.full_issue_identifier == f"{self.repo}#123"

    @pytest.mark.django_db
    def test_issue_parent_child_relationship(self):
        """Test parent-child relationship between issues."""
        parent = Issue.objects.create(
            github_repo=self.repo,
            github_issue_number=100,
            title="Parent Issue",
            html_url="https://github.com/owner/repo/issues/100",
        )

        child = Issue.objects.create(
            github_repo=self.repo,
            github_issue_number=101,
            title="Child Issue",
            html_url="https://github.com/owner/repo/issues/101",
            parent_issue=parent,
        )

        assert child.parent_issue == parent
        assert child in parent.sub_issues.all()

    @pytest.mark.django_db
    def test_issue_file_reference(self):
        """Test IssueFileReference model."""
        issue = Issue.objects.create(
            github_repo=self.repo,
            github_issue_number=123,
            title="Test Issue",
            html_url="https://github.com/owner/repo/issues/123",
        )

        file_ref = IssueFileReference.objects.create(
            issue=issue, file_path="README.md", content="# Test content"
        )

        assert file_ref.issue == issue
        assert file_ref.file_path == "README.md"
        assert issue.file_references.count() == 1

    @patch("core.services.issue_service.GitHubService")
    @patch("core.services.issue_service.AIService")
    def test_create_issue_from_feedback_creates_github_and_db_issue(
        self, mock_ai_class, mock_github_class
    ):
        """IssueService.create_issue_from_feedback should call AI and GitHub and persist issue."""

        mock_github_instance = Mock()
        mock_github_instance.fetch_file_contents.return_value = "# README content"
        mock_github_instance.create_github_issue.return_value = {
            "number": 200,
            "html_url": "https://github.com/owner/repo/issues/200",
        }
        mock_github_class.return_value = mock_github_instance

        mock_ai_instance = Mock()
        mock_ai_instance.call_ai_chat.return_value = "# Refined issue body"
        mock_ai_class.return_value = mock_ai_instance

        service = IssueService()
        issue = service.create_issue_from_feedback(
            feedback_type="bug",
            summary="Login button not working",
            description="When I click login, nothing happens.",
            repo=self.repo,
            context_files=["README.md"],
        )

        assert issue.github_issue_number == 200
        assert issue.issue_type == "bug"
        assert issue.ai_generated is True
        assert Issue.objects.filter(github_issue_number=200).exists()
        mock_ai_instance.call_ai_chat.assert_called_once()
        mock_github_instance.create_github_issue.assert_called_once()

        # Context file should be stored on IssueFileReference
        assert issue.file_references.count() == 1


class TestIssueServiceIntegration(TestCase):
    """Integration tests for IssueService (requires API keys)."""

    @pytest.mark.skipif(
        True,  # Skip by default, use --run-integration to run
        reason="Integration tests require --run-integration flag",
    )
    @patch.dict(
        "os.environ", {"GITHUB_TOKEN": "test_token", "AI_API_KEY": "test_key"}
    )
    def test_end_to_end_issue_creation(self):
        """End-to-end test for issue creation (mocked APIs)."""
        # This would test the full workflow with mocked external APIs
        pass
        pass
        pass
