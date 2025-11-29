"""Tests for PRD MACHINE service and management command."""
import hashlib
from unittest.mock import MagicMock, patch

import pytest
from django.core.management import call_command
from django.utils import timezone

from prd_machine.models import PRDState, PRDVersion, PRDConflict, PRDEvent, PRDExport
from prd_machine.services.core import PRDMachineService


# ============================================================================
# Model Tests
# ============================================================================

@pytest.mark.django_db
class TestPRDModels:
    """Test PRD MACHINE model functionality."""

    def test_prd_state_creation(self):
        """Test PRDState model creation and hash computation."""
        state = PRDState.objects.create(
            repo="test/repo",
            file_path="PRD.md",
            content="# Test PRD\n\nThis is a test PRD.",
            version="1.0.0",
        )

        assert state.repo == "test/repo"
        assert state.file_path == "PRD.md"
        assert state.version == "1.0.0"
        # Content hash should be computed automatically
        expected_hash = hashlib.sha256("# Test PRD\n\nThis is a test PRD.".encode()).hexdigest()
        assert state.content_hash == expected_hash

    def test_prd_state_unique_together(self):
        """Test repo+file_path uniqueness constraint."""
        PRDState.objects.create(repo="test/repo", file_path="PRD.md", version="1.0.0")

        with pytest.raises(Exception):  # IntegrityError
            PRDState.objects.create(repo="test/repo", file_path="PRD.md", version="2.0.0")

    def test_prd_state_lock_unlock(self):
        """Test zero-touch mode lock/unlock."""
        state = PRDState.objects.create(repo="test/repo", file_path="PRD.md")

        assert state.is_locked is False

        state.is_locked = True
        state.save()

        state.refresh_from_db()
        assert state.is_locked is True

    def test_prd_version_creation(self):
        """Test PRDVersion model creation."""
        state = PRDState.objects.create(repo="test/repo", file_path="PRD.md", version="1.0.0")
        content = "# PRD v1.0.0"

        version = PRDVersion.objects.create(
            prd_state=state,
            version="1.0.0",
            content=content,
            content_hash=hashlib.sha256(content.encode()).hexdigest(),
            trigger_type="initial",
            trigger_ref="Initial creation",
        )

        assert version.prd_state == state
        assert version.version == "1.0.0"
        assert version.trigger_type == "initial"

    def test_prd_conflict_creation(self):
        """Test PRDConflict model creation."""
        state = PRDState.objects.create(repo="test/repo", file_path="PRD.md")

        conflict = PRDConflict.objects.create(
            prd_state=state,
            conflict_type="version_mismatch",
            severity="medium",
            section_affected="ROAD",
            description="Version number mismatch detected",
            suggested_resolution="Update PRD version",
        )

        assert conflict.severity == "medium"
        assert conflict.resolved is False
        assert "version_mismatch" in str(conflict)

    def test_prd_export_creation(self):
        """Test PRDExport model creation."""
        state = PRDState.objects.create(repo="test/repo", file_path="PRD.md")

        export = PRDExport.objects.create(
            prd_state=state,
            export_type="issues",
            items_created=5,
            github_refs=[1, 2, 3, 4, 5],
            details={"stories_parsed": 5},
        )

        assert export.export_type == "issues"
        assert export.items_created == 5
        assert len(export.github_refs) == 5


# ============================================================================
# Service Tests
# ============================================================================

@pytest.mark.django_db
class TestPRDMachineService:
    """Test PRDMachineService functionality."""

    def test_get_or_create_prd_state(self):
        """Test get_or_create_prd_state method."""
        service = PRDMachineService(repo="test/repo")

        state = service.get_or_create_prd_state("PRD.md")

        assert state.repo == "test/repo"
        assert state.file_path == "PRD.md"
        assert state.version == "1.0.0"
        assert state.auto_evolve is True

        # Calling again should return the same state
        state2 = service.get_or_create_prd_state("PRD.md")
        assert state.id == state2.id

    @patch("prd_machine.services.core.GitHubService")
    def test_sync_from_github(self, mock_github_service_class):
        """Test syncing PRD from GitHub."""
        mock_github = MagicMock()
        mock_github.fetch_file_contents.return_value = "# New PRD\n\nUpdated content"
        mock_github_service_class.return_value = mock_github

        service = PRDMachineService(repo="test/repo")
        service.github_service = mock_github

        state = service.sync_from_github("PRD.md")

        assert state.content == "# New PRD\n\nUpdated content"
        assert state.last_synced_at is not None
        mock_github.fetch_file_contents.assert_called_once_with("test/repo", "PRD.md")

    @patch("prd_machine.services.core.GitHubService")
    @patch("prd_machine.services.core.AIService")
    def test_distill_prd(self, mock_ai_class, mock_github_class):
        """Test PRD distillation with AI."""
        mock_ai = MagicMock()
        mock_ai.call_ai_chat.return_value = "# Evolved PRD\n\nAI-enhanced content"
        mock_ai_class.return_value = mock_ai

        mock_github = MagicMock()
        mock_github.fetch_file_contents.return_value = "README content"
        mock_github_class.return_value = mock_github

        service = PRDMachineService(repo="test/repo")
        service.ai_service = mock_ai
        service.github_service = mock_github

        # Create initial state
        state = PRDState.objects.create(
            repo="test/repo",
            file_path="PRD.md",
            content="# Original PRD\n\nOriginal content",
            version="1.0.0",
        )

        # Distill PRD
        distilled_state = service.distill_prd(
            prd_state=state,
            trigger_type="manual_sync",
            trigger_ref="Test distillation",
        )

        # Version should be incremented
        assert distilled_state.version == "1.0.1"
        assert distilled_state.last_distilled_at is not None

        # Version record should be created
        version = PRDVersion.objects.filter(prd_state=state).first()
        assert version is not None
        assert version.trigger_type == "manual_sync"

    def test_increment_version(self):
        """Test version incrementing logic."""
        service = PRDMachineService(repo="test/repo")

        assert service._increment_version("1.0.0") == "1.0.1"
        assert service._increment_version("1.0.9") == "1.0.10"
        assert service._increment_version("2.5.3") == "2.5.4"

    def test_bump_version(self):
        """Test semantic version bumping."""
        service = PRDMachineService(repo="test/repo")
        state = PRDState.objects.create(
            repo="test/repo",
            file_path="PRD.md",
            version="1.2.3",
        )

        # Patch bump
        new_version = service.bump_version(state, "patch")
        assert new_version == "1.2.4"

        # Minor bump
        state.version = "1.2.4"
        state.save()
        new_version = service.bump_version(state, "minor")
        assert new_version == "1.3.0"

        # Major bump
        state.version = "1.3.0"
        state.save()
        new_version = service.bump_version(state, "major")
        assert new_version == "2.0.0"

    @patch("prd_machine.services.core.AIService")
    @patch("prd_machine.services.core.GitHubService")
    def test_detect_conflicts(self, mock_github_class, mock_ai_class):
        """Test conflict detection."""
        mock_ai = MagicMock()
        mock_ai.call_ai_chat.return_value = (
            "CONFLICT|version_mismatch|medium|ROAD|Version mismatch|Update PRD\n"
            "CONFLICT|missing_feature|low|MVP|Feature missing|Add feature"
        )
        mock_ai_class.return_value = mock_ai

        mock_github = MagicMock()
        mock_github.fetch_file_contents.return_value = "File content"
        mock_github_class.return_value = mock_github

        service = PRDMachineService(repo="test/repo")
        service.ai_service = mock_ai
        service.github_service = mock_github

        state = PRDState.objects.create(
            repo="test/repo",
            file_path="PRD.md",
            content="# PRD\n\nContent here",
            version="1.0.0",
        )

        conflicts = service.detect_conflicts(state)

        assert len(conflicts) == 2
        assert conflicts[0].conflict_type == "version_mismatch"
        assert conflicts[0].severity == "medium"
        assert conflicts[1].conflict_type == "missing_feature"

    @patch("requests.post")
    def test_send_slack_alert(self, mock_post):
        """Test Slack alert sending."""
        mock_response = MagicMock()
        mock_response.ok = True
        mock_post.return_value = mock_response

        state = PRDState.objects.create(
            repo="test/repo",
            file_path="PRD.md",
            slack_webhook="https://hooks.slack.com/test",
        )

        conflict = PRDConflict.objects.create(
            prd_state=state,
            conflict_type="version_mismatch",
            severity="high",
            description="Test conflict",
        )

        service = PRDMachineService(repo="test/repo")
        result = service.send_slack_alert(conflict)

        assert result is True
        conflict.refresh_from_db()
        assert conflict.slack_notified is True
        mock_post.assert_called_once()


# ============================================================================
# Management Command Tests
# ============================================================================

@pytest.mark.django_db
class TestPRDMachineCommand:
    """Test prd_machine management command."""

    @patch("prd_machine.services.core.GitHubService")
    def test_status_command_no_state(self, mock_github_class, capsys):
        """Test status command when no PRD state exists."""
        call_command("prd_machine", "--repo", "test/repo", "--status")

        captured = capsys.readouterr()
        assert "No PRD state found" in captured.out

    @patch("prd_machine.services.core.GitHubService")
    def test_status_command_with_state(self, mock_github_class, capsys):
        """Test status command with existing PRD state."""
        PRDState.objects.create(
            repo="test/repo",
            file_path="PRD.md",
            version="1.2.0",
            is_locked=True,
            auto_evolve=True,
        )

        call_command("prd_machine", "--repo", "test/repo", "--status")

        captured = capsys.readouterr()
        assert "PRD Status: test/repo" in captured.out
        assert "1.2.0" in captured.out  # Version is shown without 'v' prefix
        assert "🔒 Locked" in captured.out

    @patch("prd_machine.services.core.GitHubService")
    def test_lock_command(self, mock_github_class, capsys):
        """Test lock command."""
        PRDState.objects.create(
            repo="test/repo",
            file_path="PRD.md",
            is_locked=False,
        )

        call_command("prd_machine", "--repo", "test/repo", "--lock")

        captured = capsys.readouterr()
        assert "Zero-touch mode ENABLED" in captured.out
        assert "The machine is in control" in captured.out

        state = PRDState.objects.get(repo="test/repo")
        assert state.is_locked is True

    @patch("prd_machine.services.core.GitHubService")
    def test_unlock_command(self, mock_github_class, capsys):
        """Test unlock command."""
        PRDState.objects.create(
            repo="test/repo",
            file_path="PRD.md",
            is_locked=True,
        )

        call_command("prd_machine", "--repo", "test/repo", "--unlock")

        captured = capsys.readouterr()
        assert "Zero-touch mode DISABLED" in captured.out

        state = PRDState.objects.get(repo="test/repo")
        assert state.is_locked is False

    @patch("prd_machine.services.core.GitHubService")
    def test_sync_dry_run(self, mock_github_class, capsys):
        """Test sync with dry-run flag."""
        call_command("prd_machine", "--repo", "test/repo", "--dry-run")

        captured = capsys.readouterr()
        assert "DRY RUN" in captured.out
        assert "Would sync PRD" in captured.out

    @patch("prd_machine.services.core.GitHubService")
    def test_generate_dry_run(self, mock_github_class, capsys):
        """Test generate with dry-run flag."""
        call_command("prd_machine", "--repo", "test/repo", "--generate", "--dry-run")

        captured = capsys.readouterr()
        assert "DRY RUN" in captured.out
        assert "Would generate new PRD" in captured.out

    @patch("prd_machine.services.core.GitHubService")
    def test_bump_version_dry_run(self, mock_github_class, capsys):
        """Test version bump with dry-run flag."""
        call_command("prd_machine", "--repo", "test/repo", "--bump-version", "minor", "--dry-run")

        captured = capsys.readouterr()
        assert "DRY RUN" in captured.out
        assert "Would bump version" in captured.out


# ============================================================================
# Integration Tests (require --run-integration flag)
# ============================================================================

@pytest.mark.integration
@pytest.mark.django_db
class TestPRDMachineIntegration:
    """Integration tests for PRD MACHINE with real API calls."""

    def test_sync_from_real_github(self):
        """Test syncing PRD from real GitHub repo."""
        service = PRDMachineService(repo="bamr87/githubai")

        state = service.sync_from_github("PRD.md")

        assert state.content is not None
        assert len(state.content) > 0
        assert state.last_synced_at is not None

    def test_detect_real_conflicts(self, load_test_config):
        """Test conflict detection with real AI."""
        service = PRDMachineService(repo="bamr87/githubai")
        state = service.sync_from_github("PRD.md")

        conflicts = service.detect_conflicts(state)

        # Should return a list (may or may not have conflicts)
        assert isinstance(conflicts, list)
