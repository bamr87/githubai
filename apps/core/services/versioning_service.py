"""Versioning services - migrated from scripts/versioning.py"""
import subprocess
import logging
from pathlib import Path
from django.conf import settings
from django.utils import timezone
from core.models import Version

logger = logging.getLogger('githubai')


class VersioningService:
    """Service for semantic versioning - migrated from scripts/versioning.py"""

    def __init__(self):
        self.version_file = settings.BASE_DIR / 'VERSION'
        self.init_file = settings.BASE_DIR / 'src' / 'githubai' / '__init__.py'

    def run(self, cmd):
        """Execute shell command"""
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip()

    def get_latest_tag(self):
        """Get latest git tag"""
        try:
            return self.run("git describe --tags $(git rev-list --tags --max-count=1)").lstrip('v')
        except subprocess.CalledProcessError:
            return None

    def read_version(self):
        """Read version from VERSION file"""
        if self.version_file.exists():
            return self.version_file.read_text().strip()
        return "0.0.0"

    def write_version(self, version):
        """Write version to VERSION file and __init__.py"""
        self.version_file.write_text(version)

        if self.init_file.exists():
            import re
            init_content = self.init_file.read_text()
            init_content = re.sub(
                r'__version__ = ".*"',
                f'__version__ = "{version}"',
                init_content
            )
            self.init_file.write_text(init_content)

        logger.info(f"Updated version to {version}")

    def determine_bump(self, commit_msg):
        """Determine bump type from commit message"""
        if "[major]" in commit_msg:
            return "major"
        elif "[minor]" in commit_msg:
            return "minor"
        else:
            return "patch"

    def bump_version(self, current_version, bump_type):
        """Calculate new version"""
        major, minor, patch = map(int, current_version.split('.'))
        if bump_type == "major":
            return f"{major + 1}.0.0"
        elif bump_type == "minor":
            return f"{major}.{minor + 1}.0"
        else:
            return f"{major}.{minor}.{patch + 1}"

    def process_version_bump(self):
        """Main version bump process"""
        commit_msg = self.run("git log -1 --pretty=%B")
        commit_sha = self.run("git log -1 --pretty=%H")
        bump_type = self.determine_bump(commit_msg)

        latest_tag = self.get_latest_tag()
        current_version = self.read_version()

        # Sync with tag if there's a conflict
        if latest_tag and current_version != latest_tag:
            logger.warning(f"Version conflict: {current_version} != {latest_tag}. Syncing...")
            current_version = latest_tag
            self.write_version(current_version)

        new_version = self.bump_version(current_version, bump_type)
        self.write_version(new_version)

        # Save to database
        major, minor, patch = map(int, new_version.split('.'))
        version = Version.objects.create(
            version_number=new_version,
            major=major,
            minor=minor,
            patch=patch,
            bump_type=bump_type,
            commit_sha=commit_sha,
            commit_message=commit_msg,
            git_tag=f"v{new_version}"
        )

        logger.info(f"Bumped version from {current_version} to {new_version} ({bump_type})")
        return version

    def create_git_tag(self, version):
        """Create and push git tag"""
        tag = f"v{version.version_number}"
        self.run("git config --global user.name 'github-actions[bot]'")
        self.run("git config --global user.email 'github-actions[bot]@users.noreply.github.com'")
        self.run("git add .")
        self.run(f'git commit -m "Bump version to {version.version_number}"')
        self.run("git push")
        self.run(f"git tag {tag}")
        self.run(f"git push origin {tag}")

        version.git_tag = tag
        version.save()

        logger.info(f"Created and pushed git tag: {tag}")
