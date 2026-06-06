"""RepositoryService - discover and register repositories in the cockpit.

This is the Phase 0 entry point: it turns the loose ``owner/repo`` strings used
elsewhere in the app into first-class, managed :class:`Repository` records that
all metrics and digests reference.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from django.utils import timezone

from core.services import GitHubService
from dashboard.models import Organization, Repository

logger = logging.getLogger('githubai')


class RepositoryService:
    """Register repositories and keep their metadata in sync with GitHub."""

    def __init__(self, github_service: Optional[GitHubService] = None) -> None:
        self.github = github_service or GitHubService()

    # ------------------------------------------------------------------
    # Organization helpers
    # ------------------------------------------------------------------
    def get_or_create_organization(
        self, login: str, org_type: str = 'org', **extra: Any
    ) -> Organization:
        """Return the :class:`Organization` for ``login``, creating it if needed."""
        defaults = {'org_type': org_type}
        defaults.update({k: v for k, v in extra.items() if v is not None})
        org, created = Organization.objects.get_or_create(login=login, defaults=defaults)
        if created:
            logger.info(f"Registered organization '{login}'")
        return org

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------
    def register_repository(self, full_name: str, is_tracked: bool = True) -> Repository:
        """Register a single repository by ``owner/repo`` and sync its metadata.

        Args:
            full_name: Repository in ``owner/repo`` format.
            is_tracked: Whether to add the repo to the active watchlist.

        Returns:
            The created or updated :class:`Repository`.
        """
        if '/' not in full_name:
            raise ValueError(f"Invalid repository name '{full_name}', expected 'owner/repo'")

        owner = full_name.split('/', 1)[0]
        org = self.get_or_create_organization(owner)

        repo, _ = Repository.objects.get_or_create(
            full_name=full_name,
            defaults={
                'organization': org,
                'owner': owner,
                'name': full_name.split('/', 1)[1],
                'is_tracked': is_tracked,
            },
        )
        repo.is_tracked = is_tracked
        repo.save(update_fields=['is_tracked', 'updated_at'])

        try:
            self.sync_repository_metadata(repo)
        except Exception as e:  # noqa: BLE001 - registration should not hard-fail on API issues
            logger.warning(f"Metadata sync failed for {full_name}: {e}")

        return repo

    def sync_repository_metadata(self, repo: Repository) -> Repository:
        """Refresh a repository's cached metadata from the GitHub API.

        Uses a conditional (ETag) request so unchanged repos don't consume the
        primary rate limit.
        """
        result = self.github.fetch_repo(repo.full_name, etag=repo.metadata_etag or None)

        if result.get('not_modified'):
            logger.debug(f"Metadata unchanged for {repo.full_name}")
            return repo

        data = result.get('data') or {}
        repo.name = data.get('name', repo.name)
        repo.description = data.get('description') or ''
        repo.default_branch = data.get('default_branch') or repo.default_branch
        repo.is_private = bool(data.get('private', repo.is_private))
        repo.is_archived = bool(data.get('archived', repo.is_archived))
        repo.is_fork = bool(data.get('fork', repo.is_fork))
        repo.language = data.get('language') or ''
        repo.topics = data.get('topics') or []
        repo.html_url = data.get('html_url') or ''
        repo.stars = data.get('stargazers_count', repo.stars)
        repo.forks = data.get('forks_count', repo.forks)
        repo.open_issues_count = data.get('open_issues_count', repo.open_issues_count)
        if result.get('etag'):
            repo.metadata_etag = result['etag']
        repo.save()
        logger.info(f"Synced metadata for {repo.full_name}")
        return repo

    # ------------------------------------------------------------------
    # Discovery
    # ------------------------------------------------------------------
    def discover_repositories(
        self, owner: str, owner_type: str = 'org', max_items: int = 300
    ) -> List[Dict[str, Any]]:
        """List repositories accessible for an owner without registering them.

        Returns a lightweight list of dicts the UI can present as a "select
        which repos to track" picker. Already-registered repos are flagged.
        """
        raw = self.github.list_repos_for_owner(owner, owner_type=owner_type, max_items=max_items)
        registered = set(
            Repository.objects.filter(full_name__in=[r.get('full_name') for r in raw])
            .values_list('full_name', flat=True)
        )
        return [
            {
                'full_name': r.get('full_name'),
                'description': r.get('description'),
                'language': r.get('language'),
                'private': r.get('private'),
                'archived': r.get('archived'),
                'stars': r.get('stargazers_count', 0),
                'is_registered': r.get('full_name') in registered,
            }
            for r in raw
        ]

    def set_tracked(self, full_name: str, tracked: bool) -> Repository:
        """Toggle a repository on/off the active ingestion watchlist."""
        repo = Repository.objects.get(full_name=full_name)
        repo.is_tracked = tracked
        repo.save(update_fields=['is_tracked', 'updated_at'])
        return repo

    @staticmethod
    def tracked_repositories():
        """Return the queryset of repositories on the active watchlist."""
        return Repository.objects.filter(is_tracked=True, is_archived=False)
