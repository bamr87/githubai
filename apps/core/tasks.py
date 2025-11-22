"""Celery tasks - merged from all apps"""
from celery import shared_task
from django.conf import settings
import logging

logger = logging.getLogger('githubai')


# ============================================================================
# Issue Tasks
# ============================================================================

@shared_task(bind=True, max_retries=3)
def create_sub_issue_task(self, repo, parent_issue_number, file_refs=None):
    """Async task to create sub-issue"""
    try:
        from core.services import IssueService
        service = IssueService()
        issue = service.create_sub_issue_from_template(
            repo=repo,
            parent_issue_number=parent_issue_number,
            file_refs=file_refs or []
        )
        logger.info(f"Created sub-issue #{issue.github_issue_number}")
        return {
            'success': True,
            'issue_id': issue.id,
            'github_issue_number': issue.github_issue_number,
            'html_url': issue.html_url
        }
    except Exception as exc:
        logger.error(f"Error creating sub-issue: {exc}")
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def create_readme_update_task(self, repo, issue_number, additional_files=None):
    """Async task to create README update issue"""
    try:
        from core.services import IssueService
        service = IssueService()
        issue = service.create_readme_update_issue(
            repo=repo,
            issue_number=issue_number,
            additional_files=additional_files or []
        )
        logger.info(f"Created README update issue #{issue.github_issue_number}")
        return {
            'success': True,
            'issue_id': issue.id,
            'github_issue_number': issue.github_issue_number,
            'html_url': issue.html_url
        }
    except Exception as exc:
        logger.error(f"Error creating README update: {exc}")
        raise self.retry(exc=exc, countdown=60)


# ============================================================================
# Documentation Tasks
# ============================================================================

@shared_task(bind=True)
def generate_changelog_from_commit_task(self, repo_path=None):
    """Async task to generate changelog from commit"""
    try:
        from core.services import ChangelogService
        service = ChangelogService()
        entry = service.generate_from_commit(repo_path)
        logger.info(f"Generated changelog for commit {entry.commit_sha[:7]}")
        return {
            'success': True,
            'entry_id': entry.id,
            'commit_sha': entry.commit_sha
        }
    except Exception as exc:
        logger.error(f"Error generating changelog: {exc}")
        raise


@shared_task(bind=True)
def generate_changelog_from_pr_task(self, pr_number, repo_name=None):
    """Async task to generate changelog from PR"""
    try:
        from core.services import ChangelogService
        service = ChangelogService()
        entry = service.generate_from_pr(pr_number, repo_name)
        logger.info(f"Generated changelog for PR #{pr_number}")
        return {
            'success': True,
            'entry_id': entry.id,
            'pr_number': pr_number
        }
    except Exception as exc:
        logger.error(f"Error generating PR changelog: {exc}")
        raise


@shared_task(bind=True)
def process_file_documentation_task(self, file_path):
    """Async task to process file documentation"""
    try:
        from core.services import DocGenerationService
        service = DocGenerationService()
        doc_file = service.process_file(file_path)
        logger.info(f"Processed documentation for {file_path}")
        return {
            'success': True,
            'doc_file_id': doc_file.id,
            'file_path': file_path
        }
    except Exception as exc:
        logger.error(f"Error processing file docs: {exc}")
        raise


# ============================================================================
# Versioning Tasks
# ============================================================================

@shared_task(bind=True)
def process_version_bump_task(self):
    """Async task to process version bump"""
    try:
        from core.services import VersioningService
        service = VersioningService()
        version = service.process_version_bump()
        logger.info(f"Bumped version to {version.version_number}")
        return {
            'success': True,
            'version_id': version.id,
            'version_number': version.version_number
        }
    except Exception as exc:
        logger.error(f"Error bumping version: {exc}")
        raise


@shared_task(bind=True)
def create_git_tag_task(self, version_id):
    """Async task to create git tag"""
    try:
        from core.models import Version
        from core.services import VersioningService

        version = Version.objects.get(id=version_id)
        service = VersioningService()
        service.create_git_tag(version)
        logger.info(f"Created git tag {version.git_tag}")
        return {
            'success': True,
            'version_id': version.id,
            'git_tag': version.git_tag
        }
    except Exception as exc:
        logger.error(f"Error creating git tag: {exc}")
        raise

