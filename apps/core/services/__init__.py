"""Core services - merged from all apps"""
from .ai_service import AIService
from .github_service import GitHubService
from .issue_service import IssueService
from .doc_service import DocGenerationService, ChangelogService
from .versioning_service import VersioningService

__all__ = [
    'AIService',
    'GitHubService',
    'IssueService',
    'DocGenerationService',
    'ChangelogService',
    'VersioningService',
]

