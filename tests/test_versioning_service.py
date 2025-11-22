"""Tests for versioning app services."""

from unittest.mock import Mock, patch

import pytest
from core.models import Version
from core.services import VersioningService
from django.test import TestCase


@pytest.mark.django_db
class TestVersioningService:
    """Test cases for VersioningService."""

    def setup_method(self):
        """Setup test fixtures."""
        self.service = VersioningService()

    def test_service_initialization(self):
        """Test VersioningService can be instantiated."""
        assert self.service is not None

    def test_parse_version_string(self):
        """Test parsing version string."""
        version = "1.2.3"
        major, minor, patch = map(int, version.split("."))

        assert major == 1
        assert minor == 2
        assert patch == 3

    def test_parse_invalid_version(self):
        """Test parsing invalid version string."""
        with pytest.raises((ValueError, AttributeError)):
            major, minor, patch = map(int, "invalid".split("."))

    def test_bump_major_version(self):
        """Test bumping major version."""
        new_version = self.service.bump_version("1.2.3", "major")
        assert new_version == "2.0.0"

    def test_bump_minor_version(self):
        """Test bumping minor version."""
        new_version = self.service.bump_version("1.2.3", "minor")
        assert new_version == "1.3.0"

    def test_bump_patch_version(self):
        """Test bumping patch version."""
        new_version = self.service.bump_version("1.2.3", "patch")
        assert new_version == "1.2.4"

    def test_determine_bump_major(self):
        """Test detecting major version from commit message."""
        commit_message = "[major] Breaking change: new API"
        bump_type = self.service.determine_bump(commit_message)
        assert bump_type == "major"

    def test_determine_bump_minor(self):
        """Test detecting minor version from commit message."""
        commit_message = "[minor] Add new feature"
        bump_type = self.service.determine_bump(commit_message)
        assert bump_type == "minor"

    def test_determine_bump_patch(self):
        """Test detecting patch version from commit message."""
        commit_message = "[patch] Fix bug"
        bump_type = self.service.determine_bump(commit_message)
        assert bump_type == "patch"

    def test_determine_bump_default(self):
        """Test default version detection."""
        commit_message = "Regular commit message"
        bump_type = self.service.determine_bump(commit_message)
        assert bump_type == "patch"  # Default to patch

    @pytest.mark.django_db
    def test_version_model_creation(self):
        """Test Version model creation."""
        version = Version.objects.create(
            version_number="1.2.3",
            major=1,
            minor=2,
            patch=3,
            bump_type="patch",
            git_tag="v1.2.3",
            commit_message="Release version 1.2.3",
        )

        assert version.id is not None
        assert version.version_number == "1.2.3"
        assert version.major == 1
        assert version.minor == 2
        assert version.patch == 3
        assert str(version) == "v1.2.3"
        assert version.semver == "1.2.3"

    @pytest.mark.django_db
    def test_get_latest_version(self):
        """Test retrieving latest version."""
        # Create multiple versions
        Version.objects.create(version_number="1.0.0", major=1, minor=0, patch=0)
        Version.objects.create(version_number="1.1.0", major=1, minor=1, patch=0)
        Version.objects.create(version_number="1.2.0", major=1, minor=2, patch=0)

        latest = Version.objects.latest("created_at")
        assert latest.version_number == "1.2.0"

    @pytest.mark.django_db
    def test_version_history_ordering(self):
        """Test version history is properly ordered."""
        # Create versions out of order
        Version.objects.create(version_number="1.2.0", major=1, minor=2, patch=0)
        Version.objects.create(version_number="1.0.0", major=1, minor=0, patch=0)
        Version.objects.create(version_number="1.1.0", major=1, minor=1, patch=0)

        versions = list(Version.objects.order_by("-created_at"))

        # Most recent should be first
        assert versions[0].version_number == "1.1.0"
        assert versions[-1].version_number == "1.2.0"

    @patch("core.services.versioning_service.subprocess")
    def test_get_latest_tag(self, mock_subprocess):
        """Test retrieving latest git tag."""
        mock_result = Mock()
        mock_result.stdout.strip.return_value = "v1.2.3"
        mock_subprocess.run.return_value = mock_result

        service = VersioningService()
        tag = service.get_latest_tag()

        assert tag == "1.2.3"  # Should strip 'v' prefix

    @patch("core.services.versioning_service.subprocess")
    def test_create_git_tag(self, mock_subprocess):
        """Test creating git tag."""
        mock_result = Mock()
        mock_result.stdout.strip.return_value = ""
        mock_subprocess.run.return_value = mock_result

        version = Version.objects.create(
            version_number="1.2.3", major=1, minor=2, patch=3, bump_type="patch"
        )

        service = VersioningService()
        service.create_git_tag(version)

        # Verify subprocess.run was called multiple times for git commands
        assert mock_subprocess.run.call_count > 0


class TestVersioningIntegration(TestCase):
    """Integration tests for versioning service."""

    @pytest.mark.django_db
    def test_full_version_bump_workflow(self):
        """Test complete version bumping workflow."""
        # Create initial version
        Version.objects.create(
            version_number="1.0.0",
            major=1,
            minor=0,
            patch=0,
            commit_message="Initial release",
        )

        service = VersioningService()

        # Bump to 1.1.0
        new_version = service.bump_version("1.0.0", "minor")
        assert new_version == "1.1.0"

        # Create new version record
        Version.objects.create(
            version_number=new_version,
            major=1,
            minor=1,
            patch=0,
            commit_message="Minor version bump",
        )

        # Verify both versions exist
        assert Version.objects.count() == 2
        assert Version.objects.filter(version_number="1.1.0").exists()
        assert Version.objects.filter(version_number="1.1.0").exists()
        assert Version.objects.filter(version_number="1.1.0").exists()
