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

