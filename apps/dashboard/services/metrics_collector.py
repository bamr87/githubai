"""MetricsCollectorService - ingest DevOps signals into the metrics store.

This is the Phase 1 backbone: for a given repository it pulls the raw signals
that power every dashboard panel (PRs, issues, CI runs, security alerts,
releases) and persists a :class:`RepoMetricSnapshot` so trends can be charted
over time.
"""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any, Dict, Optional

from django.utils import timezone
from django.utils.dateparse import parse_datetime

from core.services import GitHubService
from dashboard.models import Repository, RepoMetricSnapshot

logger = logging.getLogger('githubai')

# A PR is considered "stale" if it has not been updated within this window.
STALE_PR_DAYS = 14


class MetricsCollectorService:
    """Collect and persist a metrics snapshot for a repository."""

    def __init__(self, github_service: Optional[GitHubService] = None) -> None:
        self.github = github_service or GitHubService()

    def collect_snapshot(self, repo: Repository) -> RepoMetricSnapshot:
        """Gather signals for ``repo`` and persist a new snapshot.

        Each signal source degrades gracefully: if one GitHub endpoint fails or
        is unavailable (e.g. code scanning not enabled), the remaining metrics
        are still captured rather than failing the whole ingestion.
        """
        now = timezone.now()
        full = repo.full_name

        pr_metrics = self._collect_pull_requests(full, now)
        issue_metrics = self._collect_issues(full)
        ci_metrics = self._collect_ci(full, repo.default_branch)
        security_metrics = self._collect_security(full)
        release_metrics = self._collect_releases(full)

        snapshot = RepoMetricSnapshot.objects.create(
            repository=repo,
            captured_at=now,
            open_pr_count=pr_metrics['open_pr_count'],
            stale_pr_count=pr_metrics['stale_pr_count'],
            open_issue_count=issue_metrics['open_issue_count'],
            ci_total_runs=ci_metrics['ci_total_runs'],
            ci_success_count=ci_metrics['ci_success_count'],
            ci_failure_count=ci_metrics['ci_failure_count'],
            ci_success_rate=ci_metrics['ci_success_rate'],
            security_alert_count=security_metrics['security_alert_count'],
            last_release_tag=release_metrics['last_release_tag'],
            last_release_at=parse_datetime(release_metrics['last_release_at'])
            if release_metrics.get('last_release_at') else None,
            stars=repo.stars,
            forks=repo.forks,
            data={
                'pull_requests': pr_metrics,
                'issues': issue_metrics,
                'ci': ci_metrics,
                'security': security_metrics,
                'releases': release_metrics,
            },
        )

        repo.last_ingested_at = now
        repo.save(update_fields=['last_ingested_at', 'updated_at'])
        logger.info(f"Collected metrics snapshot for {full}")
        return snapshot

    # ------------------------------------------------------------------
    # Individual signal collectors (each degrades gracefully)
    # ------------------------------------------------------------------
    def _collect_pull_requests(self, full: str, now) -> Dict[str, Any]:
        try:
            prs = self.github.list_pull_requests(full, state='open', max_items=100)
        except Exception as e:  # noqa: BLE001
            logger.warning(f"PR collection failed for {full}: {e}")
            return {'open_pr_count': 0, 'stale_pr_count': 0}

        stale_cutoff = now - timedelta(days=STALE_PR_DAYS)
        stale = 0
        for pr in prs:
            updated = parse_datetime(pr.get('updated_at') or '') if pr.get('updated_at') else None
            if updated and updated < stale_cutoff:
                stale += 1
        return {'open_pr_count': len(prs), 'stale_pr_count': stale}

    def _collect_issues(self, full: str) -> Dict[str, Any]:
        try:
            # Exclude PRs from the issue count using the search API.
            count = self.github.count_search_issues(f"repo:{full} is:issue is:open")
            return {'open_issue_count': count}
        except Exception as e:  # noqa: BLE001
            logger.warning(f"Issue collection failed for {full}: {e}")
            return {'open_issue_count': 0}

    def _collect_ci(self, full: str, branch: str) -> Dict[str, Any]:
        empty = {
            'ci_total_runs': 0, 'ci_success_count': 0,
            'ci_failure_count': 0, 'ci_success_rate': None,
        }
        try:
            runs = self.github.list_workflow_runs(full, branch=branch, per_page=30)
        except Exception as e:  # noqa: BLE001
            logger.warning(f"CI collection failed for {full}: {e}")
            return empty

        completed = [r for r in runs if r.get('status') == 'completed']
        if not completed:
            return {**empty, 'ci_total_runs': len(runs)}

        success = sum(1 for r in completed if r.get('conclusion') == 'success')
        failure = sum(1 for r in completed if r.get('conclusion') in ('failure', 'timed_out'))
        return {
            'ci_total_runs': len(completed),
            'ci_success_count': success,
            'ci_failure_count': failure,
            'ci_success_rate': round(success / len(completed), 4),
        }

    def _collect_security(self, full: str) -> Dict[str, Any]:
        code_alerts = self.github.list_code_scanning_alerts(full, state='open')
        dependabot_alerts = self.github.list_dependabot_alerts(full, state='open')
        return {
            'security_alert_count': len(code_alerts) + len(dependabot_alerts),
            'code_scanning_alerts': len(code_alerts),
            'dependabot_alerts': len(dependabot_alerts),
        }

    def _collect_releases(self, full: str) -> Dict[str, Any]:
        try:
            releases = self.github.list_releases(full, max_items=1)
        except Exception as e:  # noqa: BLE001
            logger.warning(f"Release collection failed for {full}: {e}")
            return {'last_release_tag': '', 'last_release_at': None}

        if not releases:
            return {'last_release_tag': '', 'last_release_at': None}

        latest = releases[0]
        # Store the timestamp as an ISO string so the whole metrics payload
        # remains JSON-serializable; collect_snapshot parses it for the column.
        return {
            'last_release_tag': latest.get('tag_name', ''),
            'last_release_at': latest.get('published_at') or None,
        }
