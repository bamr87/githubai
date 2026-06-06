"""Tests for the DevOps cockpit dashboard app.

Covers the multi-repo registry, metrics ingestion, AI digests, and the cockpit
REST API. External GitHub/AI calls are mocked so the suite runs offline.
"""
from __future__ import annotations

from datetime import timedelta
from unittest.mock import MagicMock, patch

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from dashboard.models import (
    Organization,
    Repository,
    RepoConnection,
    RepoMetricSnapshot,
    RepoDigest,
)
from dashboard.services import (
    RepositoryService,
    MetricsCollectorService,
    FleetDigestService,
)


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------
def _make_repo(full_name='owner/repo', tracked=True, archived=False):
    org, _ = Organization.objects.get_or_create(login=full_name.split('/')[0])
    return Repository.objects.create(
        organization=org,
        full_name=full_name,
        owner=full_name.split('/')[0],
        name=full_name.split('/')[1],
        is_tracked=tracked,
        is_archived=archived,
        stars=5,
        forks=2,
    )


def _make_snapshot(repo, **kwargs):
    defaults = dict(
        captured_at=timezone.now(),
        open_pr_count=2,
        stale_pr_count=1,
        open_issue_count=3,
        ci_total_runs=10,
        ci_success_count=9,
        ci_failure_count=1,
        ci_success_rate=0.9,
        security_alert_count=0,
    )
    defaults.update(kwargs)
    return RepoMetricSnapshot.objects.create(repository=repo, **defaults)


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestModels:
    def test_repository_str(self):
        repo = _make_repo()
        assert str(repo) == 'owner/repo'

    def test_health_score_perfect(self):
        repo = _make_repo()
        snap = _make_snapshot(repo, ci_success_rate=1.0, stale_pr_count=0, security_alert_count=0)
        assert snap.health_score == 100

    def test_health_score_penalised(self):
        repo = _make_repo()
        snap = _make_snapshot(repo, ci_success_rate=0.5, stale_pr_count=2, security_alert_count=1)
        # 100 - 20 (ci) - 10 (security) - 6 (stale) = 64
        assert snap.health_score == 64

    def test_digest_str_fleet(self):
        digest = RepoDigest.objects.create(
            scope='fleet', title='Fleet', summary='x', severity='high'
        )
        assert 'FLEET' in str(digest)


# ---------------------------------------------------------------------------
# RepositoryService tests
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestRepositoryService:
    def test_register_repository_creates_records(self):
        gh = MagicMock()
        gh.fetch_repo.return_value = {
            'not_modified': False,
            'etag': 'etag-1',
            'data': {
                'name': 'repo', 'description': 'desc', 'default_branch': 'main',
                'private': False, 'archived': False, 'fork': False,
                'language': 'Python', 'topics': ['ai'], 'html_url': 'https://x',
                'stargazers_count': 42, 'forks_count': 7, 'open_issues_count': 3,
            },
        }
        service = RepositoryService(github_service=gh)
        repo = service.register_repository('owner/repo')

        assert repo.full_name == 'owner/repo'
        assert repo.language == 'Python'
        assert repo.stars == 42
        assert repo.metadata_etag == 'etag-1'
        assert Organization.objects.filter(login='owner').exists()

    def test_register_invalid_name_raises(self):
        with pytest.raises(ValueError):
            RepositoryService(github_service=MagicMock()).register_repository('no-slash')

    def test_sync_metadata_not_modified_keeps_values(self):
        repo = _make_repo()
        repo.language = 'Go'
        repo.save()
        gh = MagicMock()
        gh.fetch_repo.return_value = {'not_modified': True, 'data': None}
        service = RepositoryService(github_service=gh)
        result = service.sync_repository_metadata(repo)
        assert result.language == 'Go'

    def test_discover_flags_registered(self):
        _make_repo('owner/known')
        gh = MagicMock()
        gh.list_repos_for_owner.return_value = [
            {'full_name': 'owner/known', 'description': 'd', 'language': 'Py',
             'private': False, 'archived': False, 'stargazers_count': 1},
            {'full_name': 'owner/new', 'description': 'd2', 'language': 'JS',
             'private': False, 'archived': False, 'stargazers_count': 0},
        ]
        out = RepositoryService(github_service=gh).discover_repositories('owner')
        by_name = {r['full_name']: r for r in out}
        assert by_name['owner/known']['is_registered'] is True
        assert by_name['owner/new']['is_registered'] is False

    def test_set_tracked_toggle(self):
        repo = _make_repo(tracked=True)
        service = RepositoryService(github_service=MagicMock())
        service.set_tracked(repo.full_name, False)
        repo.refresh_from_db()
        assert repo.is_tracked is False

    def test_tracked_repositories_excludes_archived(self):
        _make_repo('owner/active', tracked=True, archived=False)
        _make_repo('owner/archived', tracked=True, archived=True)
        names = set(RepositoryService.tracked_repositories().values_list('full_name', flat=True))
        assert names == {'owner/active'}


# ---------------------------------------------------------------------------
# MetricsCollectorService tests
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestMetricsCollector:
    def _github_mock(self):
        gh = MagicMock()
        now = timezone.now()
        recent = now.isoformat()
        old = (now - timedelta(days=30)).isoformat()
        gh.list_pull_requests.return_value = [
            {'updated_at': recent}, {'updated_at': old},
        ]
        gh.count_search_issues.return_value = 4
        gh.list_workflow_runs.return_value = [
            {'status': 'completed', 'conclusion': 'success'},
            {'status': 'completed', 'conclusion': 'failure'},
            {'status': 'in_progress', 'conclusion': None},
        ]
        gh.list_code_scanning_alerts.return_value = [{'number': 1}]
        gh.list_dependabot_alerts.return_value = [{'number': 2}, {'number': 3}]
        gh.list_releases.return_value = [
            {'tag_name': 'v1.2.3', 'published_at': recent},
        ]
        return gh

    def test_collect_snapshot_persists_metrics(self):
        repo = _make_repo()
        collector = MetricsCollectorService(github_service=self._github_mock())
        snap = collector.collect_snapshot(repo)

        assert snap.open_pr_count == 2
        assert snap.stale_pr_count == 1
        assert snap.open_issue_count == 4
        assert snap.ci_total_runs == 2  # only completed runs counted
        assert snap.ci_success_rate == 0.5
        assert snap.security_alert_count == 3  # 1 code scanning + 2 dependabot
        assert snap.last_release_tag == 'v1.2.3'
        repo.refresh_from_db()
        assert repo.last_ingested_at is not None

    def test_collect_degrades_on_pr_failure(self):
        repo = _make_repo()
        gh = self._github_mock()
        gh.list_pull_requests.side_effect = Exception('boom')
        collector = MetricsCollectorService(github_service=gh)
        snap = collector.collect_snapshot(repo)
        assert snap.open_pr_count == 0  # degraded gracefully
        assert snap.open_issue_count == 4  # other metrics still collected


# ---------------------------------------------------------------------------
# FleetDigestService tests
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestDigestService:
    def test_repo_digest_uses_ai(self):
        repo = _make_repo()
        _make_snapshot(repo, security_alert_count=2, ci_success_rate=0.4)
        ai = MagicMock()
        ai.call_ai_chat.return_value = 'AI summary text'
        digest = FleetDigestService(ai_service=ai).generate_repo_digest(repo, use_ai=True)
        assert digest.summary == 'AI summary text'
        assert digest.severity == 'critical'  # alerts + low CI
        ai.call_ai_chat.assert_called_once()

    def test_repo_digest_fallback_without_ai(self):
        repo = _make_repo()
        _make_snapshot(repo, ci_failure_count=2, security_alert_count=1, stale_pr_count=3)
        digest = FleetDigestService().generate_repo_digest(repo, use_ai=False)
        assert 'Health score' in digest.summary
        assert digest.generated_by_model == 'rule-based'

    def test_repo_digest_ai_failure_falls_back(self):
        repo = _make_repo()
        _make_snapshot(repo)
        ai = MagicMock()
        ai.call_ai_chat.side_effect = Exception('ai down')
        digest = FleetDigestService(ai_service=ai).generate_repo_digest(repo, use_ai=True)
        assert 'Health score' in digest.summary  # fell back

    def test_fleet_digest_ranks_repositories(self):
        bad = _make_repo('owner/bad')
        _make_snapshot(bad, security_alert_count=5, ci_failure_count=3)
        good = _make_repo('owner/good')
        _make_snapshot(good, security_alert_count=0, ci_success_rate=1.0,
                       ci_failure_count=0, stale_pr_count=0)
        digest = FleetDigestService().generate_fleet_digest(use_ai=False)
        assert digest.scope == 'fleet'
        assert digest.severity in ('high', 'critical')
        # The worst repo should appear in the ranked summary.
        assert 'owner/bad' in digest.summary


# ---------------------------------------------------------------------------
# API tests
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestDashboardAPI:
    def setup_method(self):
        self.client = APIClient()

    def _auth(self):
        """Authenticate the client; write actions require auth (gated by design)."""
        from django.contrib.auth import get_user_model
        user = get_user_model().objects.create_user(username='cockpit', password='x')
        self.client.force_authenticate(user=user)
        return user

    def test_register_endpoint(self):
        self._auth()
        with patch('dashboard.services.repository_service.GitHubService') as gh_cls:
            gh = gh_cls.return_value
            gh.fetch_repo.return_value = {
                'not_modified': False, 'etag': 'e',
                'data': {'name': 'repo', 'language': 'Python', 'topics': [],
                         'stargazers_count': 1, 'forks_count': 0, 'open_issues_count': 0},
            }
            resp = self.client.post(
                '/api/dashboard/repositories/register/',
                {'full_name': 'owner/repo'}, format='json',
            )
        assert resp.status_code == 201
        assert resp.data['full_name'] == 'owner/repo'

    def test_register_endpoint_validates_format(self):
        self._auth()
        resp = self.client.post(
            '/api/dashboard/repositories/register/',
            {'full_name': 'invalid'}, format='json',
        )
        assert resp.status_code == 400

    def test_fleet_overview(self):
        repo = _make_repo()
        _make_snapshot(repo, security_alert_count=2)
        resp = self.client.get('/api/dashboard/fleet/overview/')
        assert resp.status_code == 200
        assert resp.data['totals']['repositories'] == 1
        assert resp.data['totals']['security_alerts'] == 2
        assert resp.data['repositories'][0]['full_name'] == 'owner/repo'

    def test_fleet_attention(self):
        repo = _make_repo()
        _make_snapshot(repo, ci_success_rate=0.5, security_alert_count=1, stale_pr_count=2)
        resp = self.client.get('/api/dashboard/fleet/attention/')
        assert resp.status_code == 200
        assert len(resp.data['failing_ci']) == 1
        assert len(resp.data['open_security_alerts']) == 1
        assert len(resp.data['stale_pull_requests']) == 1

    def test_collect_action(self):
        self._auth()
        repo = _make_repo()
        with patch('dashboard.views.MetricsCollectorService') as collector_cls:
            snap = _make_snapshot(repo)
            collector_cls.return_value.collect_snapshot.return_value = snap
            resp = self.client.post(f'/api/dashboard/repositories/{repo.id}/collect/')
        assert resp.status_code == 201

    def test_fleet_digest_endpoint(self):
        repo = _make_repo()
        _make_snapshot(repo)
        resp = self.client.post('/api/dashboard/fleet/digest/', {'use_ai': False}, format='json')
        assert resp.status_code == 201
        assert resp.data['scope'] == 'fleet'
