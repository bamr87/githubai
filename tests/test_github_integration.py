"""Tests for GitHub integration services."""

from unittest.mock import Mock, patch

import pytest
from core.models import APILog
from core.services import GitHubService
from django.test import TestCase


@pytest.mark.django_db
class TestGitHubService:
    """Test cases for GitHubService."""

    def setup_method(self):
        """Setup test fixtures."""
        self.service = GitHubService()
        self.repo = "owner/repo"

    def test_service_initialization(self):
        """Test GitHubService can be instantiated."""
        assert self.service is not None

    @patch("core.services.github_service.requests")
    def test_fetch_issue_success(self, mock_requests):
        """Test successful issue retrieval."""
        # Mock requests response
        mock_response = Mock()
        mock_response.json.return_value = {
            "number": 123,
            "title": "Test Issue",
            "body": "Test body",
            "html_url": "https://github.com/owner/repo/issues/123",
            "state": "open",
        }
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_requests.get.return_value = mock_response

        service = GitHubService()
        result = service.fetch_issue(self.repo, 123)

        assert result is not None
        assert result["number"] == 123
        assert result["title"] == "Test Issue"

    @patch("core.services.github_service.requests")
    def test_fetch_issue_not_found(self, mock_requests):
        """Test handling of non-existent issue."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("Issue not found")
        mock_requests.get.return_value = mock_response

        service = GitHubService()

        with pytest.raises(Exception) as exc_info:
            service.fetch_issue(self.repo, 999)

        assert "Issue not found" in str(exc_info.value)

    @patch("core.services.github_service.requests")
    def test_create_github_issue_success(self, mock_requests):
        """Test successful issue creation."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "number": 124,
            "html_url": "https://github.com/owner/repo/issues/124",
            "title": "New Issue",
        }
        mock_response.status_code = 201
        mock_response.raise_for_status = Mock()
        mock_requests.post.return_value = mock_response

        service = GitHubService()
        result = service.create_github_issue(
            repo=self.repo, title="New Issue", body="Issue body"
        )

        assert result is not None
        assert result["number"] == 124

    @patch("core.services.github_service.requests")
    def test_fetch_file_contents(self, mock_requests):
        """Test retrieving file contents from repository."""
        import base64

        content = "# README\nTest content"
        encoded_content = base64.b64encode(content.encode()).decode()

        mock_response = Mock()
        mock_response.json.return_value = {"content": encoded_content}
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_requests.get.return_value = mock_response

        service = GitHubService()
        result = service.fetch_file_contents(self.repo, "README.md")

        assert result is not None
        assert "README" in result
        assert result == content

    @pytest.mark.django_db
    @patch("core.services.github_service.requests")
    def test_api_logging(self, mock_requests):
        """Test that API calls are logged."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "number": 123,
            "title": "Test",
            "body": "Test",
            "html_url": "https://github.com/owner/repo/issues/123",
            "state": "open",
        }
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_requests.get.return_value = mock_response

        service = GitHubService()
        service.fetch_issue(self.repo, 123)

        # Verify API log was created
        logs = APILog.objects.filter(api_type="github")
        assert logs.count() > 0
        log = logs.first()
        assert log.api_type == "github"
        assert log.method == "GET"

    @patch("core.services.github_service.requests")
    def test_invalid_repo_format(self, mock_requests):
        """Test handling invalid repository format."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("Invalid repository")
        mock_requests.get.return_value = mock_response

        service = GitHubService()

        with pytest.raises(Exception) as exc_info:
            service.fetch_issue("invalid-repo-format", 123)

        assert "Invalid repository" in str(exc_info.value)

    @patch("core.services.github_service.requests")
    def test_rate_limit_handling(self, mock_requests):
        """Test handling GitHub rate limits."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception(
            "API rate limit exceeded"
        )
        mock_requests.get.return_value = mock_response

        service = GitHubService()

        with pytest.raises(Exception) as exc_info:
            service.fetch_issue(self.repo, 123)

        assert "rate limit" in str(exc_info.value).lower()


class TestGitHubServiceIntegration(TestCase):
    """Integration tests for GitHub service."""

    @pytest.mark.django_db
    def test_api_log_model(self):
        """Test APILog model for GitHub calls."""
        log = APILog.objects.create(
            api_type="github",
            endpoint="/repos/owner/repo/issues/123",
            method="GET",
            request_data={"repo": "owner/repo"},
            response_data={"number": 123},
            status_code=200,
            duration_ms=150,
        )

        assert log.id is not None
        assert log.api_type == "github"
        assert log.status_code == 200

    @pytest.mark.skipif(
        True,  # Skip by default, use --run-integration to run
        reason="Integration tests require --run-integration flag",
    )
    @patch.dict("os.environ", {"GITHUB_TOKEN": "test_token"})
    def test_real_github_api_call(self):
        """Test real GitHub API call (requires valid token)."""
        # This test would make a real API call
        # Only run when explicitly testing with real credentials
        pass
        pass
        pass
