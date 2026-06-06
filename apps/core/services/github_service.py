"""GitHub Integration services - migrated from github_integration app"""
import base64
import logging
from typing import Dict, List, Optional, Any
from django.conf import settings
import requests
from core.models import APILog

logger = logging.getLogger('githubai')


class GitHubService:
    """Service for GitHub API interactions"""

    def __init__(self) -> None:
        self.token: str = settings.GITHUB_TOKEN
        self.headers: Dict[str, str] = {'Authorization': f'token {self.token}'}
        self.base_url: str = 'https://api.github.com'

    def fetch_issue(self, repo: str, issue_number: int) -> Dict[str, Any]:
        """
        Fetch issue details from GitHub.
        Migrated from github_api_utils.py::fetch_issue
        """
        url = f"{self.base_url}/repos/{repo}/issues/{issue_number}"

        api_log = APILog.objects.create(
            api_type='github',
            endpoint=url,
            method='GET'
        )

        try:
            import time
            start_time = time.time()

            res = requests.get(url, headers=self.headers)
            res.raise_for_status()

            duration_ms = int((time.time() - start_time) * 1000)
            data = res.json()

            api_log.status_code = res.status_code
            api_log.duration_ms = duration_ms
            api_log.response_data = {'issue_number': issue_number, 'title': data.get('title')}
            api_log.save()

            logger.info(f"Fetched GitHub issue #{issue_number} from {repo}")
            return data

        except Exception as e:
            api_log.error_message = str(e)
            api_log.status_code = getattr(e.response, 'status_code', 500) if hasattr(e, 'response') else 500
            api_log.save()

            logger.error(f"Error fetching issue #{issue_number}: {e}")
            raise

    def create_github_issue(
        self,
        repo: str,
        title: str,
        body: str,
        parent_issue_number: Optional[int] = None,
        labels: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a new GitHub issue.
        Migrated from github_api_utils.py::create_github_issue
        """
        labels = labels or []

        if parent_issue_number:
            body += f"\n\n_Parent Issue: #{parent_issue_number}_"

        data = {
            "title": title,
            "body": body,
            "labels": labels
        }

        url = f"{self.base_url}/repos/{repo}/issues"

        api_log = APILog.objects.create(
            api_type='github',
            endpoint=url,
            method='POST',
            request_data=data
        )

        try:
            import time
            start_time = time.time()

            res = requests.post(url, headers=self.headers, json=data)
            res.raise_for_status()

            duration_ms = int((time.time() - start_time) * 1000)
            issue_data = res.json()

            api_log.status_code = res.status_code
            api_log.duration_ms = duration_ms
            api_log.response_data = {
                'issue_number': issue_data.get('number'),
                'html_url': issue_data.get('html_url')
            }
            api_log.save()

            logger.info(f"Created GitHub issue #{issue_data.get('number')} in {repo}")
            return issue_data

        except Exception as e:
            api_log.error_message = str(e)
            api_log.status_code = getattr(e.response, 'status_code', 500) if hasattr(e, 'response') else 500
            api_log.save()

            logger.error(f"Error creating issue in {repo}: {e}")
            raise

    def fetch_file_contents(self, repo: str, filepath: str) -> str:
        """
        Fetch file contents from GitHub repository.
        Migrated from create_issue.py::fetch_file_contents
        """
        url = f"{self.base_url}/repos/{repo}/contents/{filepath}"

        api_log = APILog.objects.create(
            api_type='github',
            endpoint=url,
            method='GET'
        )

        try:
            import time
            start_time = time.time()

            res = requests.get(url, headers=self.headers)
            res.raise_for_status()

            duration_ms = int((time.time() - start_time) * 1000)
            content = base64.b64decode(res.json()['content']).decode('utf-8')

            api_log.status_code = res.status_code
            api_log.duration_ms = duration_ms
            api_log.response_data = {'file': filepath, 'size': len(content)}
            api_log.save()

            logger.debug(f"Fetched file {filepath} from {repo}")
            return content

        except Exception as e:
            api_log.error_message = str(e)
            api_log.status_code = getattr(e.response, 'status_code', 500) if hasattr(e, 'response') else 500
            api_log.save()

            logger.error(f"Error fetching file {filepath}: {e}")
            raise

    # ========================================================================
    # Generic / multi-repo helpers (used by the DevOps cockpit dashboard)
    #
    # These methods add pagination, conditional (ETag) requests, and
    # rate-limit awareness on top of the GitHub REST API so the dashboard can
    # ingest signals from many repositories efficiently. They are additive and
    # do not change the behaviour of the existing single-repo methods above.
    # ========================================================================

    def get_json(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        etag: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Perform a GET request against the GitHub API with ETag support.

        Args:
            path: API path (e.g. ``/repos/owner/repo``) or a full URL.
            params: Optional query string parameters.
            etag: Optional ETag for a conditional request. When the resource is
                unchanged GitHub returns ``304 Not Modified`` and no body, which
                does not count against the primary rate limit.

        Returns:
            Dict with keys:
                ``status_code`` (int),
                ``data`` (parsed JSON or ``None`` when not modified),
                ``etag`` (response ETag, if any),
                ``not_modified`` (bool),
                ``rate_remaining`` (int or ``None``),
                ``link`` (Link header, if any).
        """
        import time

        url = path if path.startswith('http') else f"{self.base_url}{path}"
        headers = dict(self.headers)
        headers.setdefault('Accept', 'application/vnd.github+json')
        if etag:
            headers['If-None-Match'] = etag

        api_log = APILog.objects.create(
            api_type='github', endpoint=url, method='GET', request_data=params or None
        )

        try:
            start_time = time.time()
            res = requests.get(url, headers=headers, params=params, timeout=30)
            duration_ms = int((time.time() - start_time) * 1000)

            rate_remaining = res.headers.get('X-RateLimit-Remaining')
            not_modified = res.status_code == 304
            if not not_modified:
                res.raise_for_status()

            data = None
            if not not_modified and res.content:
                data = res.json()

            api_log.status_code = res.status_code
            api_log.duration_ms = duration_ms
            api_log.response_data = {'not_modified': not_modified}
            api_log.save()

            return {
                'status_code': res.status_code,
                'data': data,
                'etag': res.headers.get('ETag'),
                'not_modified': not_modified,
                'rate_remaining': int(rate_remaining) if rate_remaining is not None else None,
                'link': res.headers.get('Link'),
            }
        except Exception as e:
            api_log.error_message = str(e)
            api_log.status_code = getattr(e.response, 'status_code', 500) if hasattr(e, 'response') else 500
            api_log.save()
            logger.error(f"Error fetching {url}: {e}")
            raise

    def get_paginated(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        max_items: int = 300,
    ) -> List[Dict[str, Any]]:
        """Fetch a list endpoint following ``Link`` pagination headers.

        Args:
            path: API path or full URL for a list endpoint.
            params: Optional query parameters (``per_page`` defaults to 100).
            max_items: Safety cap on the total number of items collected.

        Returns:
            A list of items aggregated across pages (truncated to ``max_items``).
        """
        params = dict(params or {})
        params.setdefault('per_page', 100)

        items: List[Dict[str, Any]] = []
        result = self.get_json(path, params=params)
        while result:
            page = result.get('data') or []
            if isinstance(page, dict):
                # Some endpoints wrap items, e.g. search results
                page = page.get('items', [])
            items.extend(page)
            if len(items) >= max_items:
                return items[:max_items]

            next_url = self._parse_next_link(result.get('link'))
            if not next_url:
                break
            # Query params are already encoded in the next URL.
            result = self.get_json(next_url)

        return items[:max_items]

    @staticmethod
    def _parse_next_link(link_header: Optional[str]) -> Optional[str]:
        """Extract the ``rel="next"`` URL from a GitHub ``Link`` header."""
        if not link_header:
            return None
        for part in link_header.split(','):
            segments = part.split(';')
            if len(segments) < 2:
                continue
            url_segment = segments[0].strip().strip('<>')
            rel_segment = segments[1].strip()
            if rel_segment == 'rel="next"':
                return url_segment
        return None

    def get_rate_limit(self) -> Dict[str, Any]:
        """Return the current GitHub API rate-limit status."""
        result = self.get_json('/rate_limit')
        return result.get('data') or {}

    def fetch_repo(self, repo: str, etag: Optional[str] = None) -> Dict[str, Any]:
        """Fetch repository metadata (stars, forks, language, topics, etc.)."""
        return self.get_json(f"/repos/{repo}", etag=etag)

    def list_repos_for_owner(
        self, owner: str, owner_type: str = 'user', max_items: int = 300
    ) -> List[Dict[str, Any]]:
        """List repositories belonging to a user or organization.

        Args:
            owner: GitHub login of the user or organization.
            owner_type: ``'org'`` to use the organization endpoint, otherwise
                the user endpoint is used.
            max_items: Maximum number of repositories to return.
        """
        base = 'orgs' if owner_type == 'org' else 'users'
        return self.get_paginated(
            f"/{base}/{owner}/repos",
            params={'sort': 'updated', 'type': 'all'},
            max_items=max_items,
        )

    def count_search_issues(self, query: str) -> int:
        """Return ``total_count`` for an issue/PR search query.

        Uses the GitHub search API which reports an accurate total without
        requiring the full result set to be downloaded.
        """
        result = self.get_json('/search/issues', params={'q': query, 'per_page': 1})
        data = result.get('data') or {}
        return int(data.get('total_count', 0))

    def list_pull_requests(
        self, repo: str, state: str = 'open', max_items: int = 100
    ) -> List[Dict[str, Any]]:
        """List pull requests for a repository."""
        return self.get_paginated(
            f"/repos/{repo}/pulls",
            params={'state': state, 'sort': 'updated', 'direction': 'desc'},
            max_items=max_items,
        )

    def list_workflow_runs(
        self, repo: str, branch: Optional[str] = None, per_page: int = 30
    ) -> List[Dict[str, Any]]:
        """List recent GitHub Actions workflow runs for a repository."""
        params: Dict[str, Any] = {'per_page': per_page}
        if branch:
            params['branch'] = branch
        result = self.get_json(f"/repos/{repo}/actions/runs", params=params)
        data = result.get('data') or {}
        return data.get('workflow_runs', []) if isinstance(data, dict) else []

    def list_releases(self, repo: str, max_items: int = 30) -> List[Dict[str, Any]]:
        """List releases for a repository (most recent first)."""
        return self.get_paginated(f"/repos/{repo}/releases", max_items=max_items)

    def list_code_scanning_alerts(
        self, repo: str, state: str = 'open', max_items: int = 100
    ) -> List[Dict[str, Any]]:
        """List code scanning alerts for a repository.

        Returns an empty list when code scanning is not enabled or the token
        lacks permission (GitHub responds ``403``/``404`` in those cases).
        """
        try:
            return self.get_paginated(
                f"/repos/{repo}/code-scanning/alerts",
                params={'state': state},
                max_items=max_items,
            )
        except Exception as e:  # noqa: BLE001 - degrade gracefully for the dashboard
            logger.warning(f"Code scanning alerts unavailable for {repo}: {e}")
            return []

    def list_dependabot_alerts(
        self, repo: str, state: str = 'open', max_items: int = 100
    ) -> List[Dict[str, Any]]:
        """List Dependabot (dependency) alerts, degrading gracefully on errors."""
        try:
            return self.get_paginated(
                f"/repos/{repo}/dependabot/alerts",
                params={'state': state},
                max_items=max_items,
            )
        except Exception as e:  # noqa: BLE001 - degrade gracefully for the dashboard
            logger.warning(f"Dependabot alerts unavailable for {repo}: {e}")
            return []

