"""Dashboard views - the cockpit REST API.

Exposes the multi-repo registry, the time-series metrics store, AI digests, and
cross-cutting "fleet" views (e.g. all failing CI, all open security alerts) that
make the dashboard a single place to manage many repositories.
"""
from __future__ import annotations

import logging

from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from dashboard.models import (
    Organization,
    Repository,
    RepoConnection,
    RepoMetricSnapshot,
    RepoDigest,
)
from dashboard.serializers import (
    OrganizationSerializer,
    RepositorySerializer,
    RepoConnectionSerializer,
    RepoMetricSnapshotSerializer,
    RepoDigestSerializer,
    RegisterRepositorySerializer,
    DiscoverRepositoriesSerializer,
)
from dashboard.services import (
    RepositoryService,
    MetricsCollectorService,
    FleetDigestService,
)

logger = logging.getLogger('githubai')


class OrganizationViewSet(viewsets.ModelViewSet):
    """CRUD for organizations/owners tracked in the cockpit."""
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['org_type', 'is_active']


class RepoConnectionViewSet(viewsets.ModelViewSet):
    """CRUD for repository connections (credential references, not secrets)."""
    queryset = RepoConnection.objects.all()
    serializer_class = RepoConnectionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['organization', 'connection_type', 'is_active']


class RepositoryViewSet(viewsets.ModelViewSet):
    """Manage registered repositories and trigger per-repo actions."""
    queryset = Repository.objects.select_related('organization').all()
    serializer_class = RepositorySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['organization', 'is_tracked', 'is_archived', 'language', 'owner']
    lookup_field = 'pk'

    @action(detail=False, methods=['post'], url_path='register')
    def register(self, request: Request) -> Response:
        """Register a repository by ``owner/repo`` and sync its metadata."""
        serializer = RegisterRepositorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        repo = RepositoryService().register_repository(
            serializer.validated_data['full_name'],
            is_tracked=serializer.validated_data['is_tracked'],
        )
        return Response(RepositorySerializer(repo).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='discover')
    def discover(self, request: Request) -> Response:
        """List repositories available for an owner (without registering them)."""
        serializer = DiscoverRepositoriesSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        repos = RepositoryService().discover_repositories(
            serializer.validated_data['owner'],
            owner_type=serializer.validated_data['owner_type'],
        )
        return Response({'repositories': repos, 'count': len(repos)})

    @action(detail=True, methods=['post'], url_path='track')
    def track(self, request: Request, pk=None) -> Response:
        """Add this repository to the active ingestion watchlist."""
        repo = self.get_object()
        repo = RepositoryService().set_tracked(repo.full_name, True)
        return Response(RepositorySerializer(repo).data)

    @action(detail=True, methods=['post'], url_path='untrack')
    def untrack(self, request: Request, pk=None) -> Response:
        """Remove this repository from the active ingestion watchlist."""
        repo = self.get_object()
        repo = RepositoryService().set_tracked(repo.full_name, False)
        return Response(RepositorySerializer(repo).data)

    @action(detail=True, methods=['post'], url_path='sync')
    def sync(self, request: Request, pk=None) -> Response:
        """Refresh this repository's metadata from GitHub."""
        repo = self.get_object()
        repo = RepositoryService().sync_repository_metadata(repo)
        return Response(RepositorySerializer(repo).data)

    @action(detail=True, methods=['post'], url_path='collect')
    def collect(self, request: Request, pk=None) -> Response:
        """Collect a fresh metrics snapshot for this repository now."""
        repo = self.get_object()
        snapshot = MetricsCollectorService().collect_snapshot(repo)
        return Response(RepoMetricSnapshotSerializer(snapshot).data,
                        status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], url_path='snapshots')
    def snapshots(self, request: Request, pk=None) -> Response:
        """Return the time-series snapshots for this repository."""
        repo = self.get_object()
        qs = repo.snapshots.order_by('-captured_at')[:100]
        return Response(RepoMetricSnapshotSerializer(qs, many=True).data)

    @action(detail=True, methods=['post'], url_path='digest')
    def digest(self, request: Request, pk=None) -> Response:
        """Generate an AI "what needs attention" digest for this repository."""
        repo = self.get_object()
        use_ai = request.data.get('use_ai', True)
        digest = FleetDigestService().generate_repo_digest(repo, use_ai=use_ai)
        return Response(RepoDigestSerializer(digest).data, status=status.HTTP_201_CREATED)


class RepoMetricSnapshotViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only access to the time-series metrics store."""
    queryset = RepoMetricSnapshot.objects.select_related('repository').all()
    serializer_class = RepoMetricSnapshotSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['repository']


class RepoDigestViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only access to AI digests (per-repo and fleet)."""
    queryset = RepoDigest.objects.select_related('repository').all()
    serializer_class = RepoDigestSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['scope', 'severity', 'repository']


class FleetOverviewView(APIView):
    """One-glance triage of the whole portfolio.

    Returns each tracked repository with its latest snapshot summary plus
    aggregate fleet KPIs, powering the cockpit's "fleet view" grid.
    """
    permission_classes = [AllowAny]

    def get(self, request: Request) -> Response:
        repos = (
            Repository.objects.filter(is_archived=False)
            .select_related('organization')
            .order_by('full_name')
        )
        only_tracked = request.query_params.get('tracked')
        if only_tracked is not None:
            repos = repos.filter(is_tracked=only_tracked.lower() in ('1', 'true', 'yes'))

        rows = []
        totals = {
            'repositories': 0, 'open_prs': 0, 'stale_prs': 0,
            'open_issues': 0, 'security_alerts': 0, 'failing_ci': 0,
        }
        for repo in repos:
            snapshot = repo.snapshots.order_by('-captured_at').first()
            row = {
                'id': repo.id,
                'full_name': repo.full_name,
                'language': repo.language,
                'is_tracked': repo.is_tracked,
                'html_url': repo.html_url,
                'stars': repo.stars,
                'last_ingested_at': repo.last_ingested_at,
                'has_metrics': snapshot is not None,
            }
            if snapshot:
                ci_failing = (
                    snapshot.ci_success_rate is not None and snapshot.ci_success_rate < 1.0
                )
                row.update({
                    'health_score': snapshot.health_score,
                    'open_prs': snapshot.open_pr_count,
                    'stale_prs': snapshot.stale_pr_count,
                    'open_issues': snapshot.open_issue_count,
                    'ci_success_rate': snapshot.ci_success_rate,
                    'security_alerts': snapshot.security_alert_count,
                    'last_release_tag': snapshot.last_release_tag,
                    'captured_at': snapshot.captured_at,
                })
                totals['open_prs'] += snapshot.open_pr_count
                totals['stale_prs'] += snapshot.stale_pr_count
                totals['open_issues'] += snapshot.open_issue_count
                totals['security_alerts'] += snapshot.security_alert_count
                if ci_failing:
                    totals['failing_ci'] += 1
            totals['repositories'] += 1
            rows.append(row)

        return Response({'totals': totals, 'repositories': rows})


@api_view(['GET'])
@permission_classes([AllowAny])
def fleet_attention(request: Request) -> Response:
    """Cross-cutting view: repositories that need attention, ranked.

    Surfaces failing CI, open security alerts, and stale PRs across the fleet -
    the "all red items in one place" view.
    """
    repos = Repository.objects.filter(is_archived=False, is_tracked=True)
    failing_ci, security, stale = [], [], []
    for repo in repos:
        snapshot = repo.snapshots.order_by('-captured_at').first()
        if not snapshot:
            continue
        if snapshot.ci_success_rate is not None and snapshot.ci_success_rate < 1.0:
            failing_ci.append({
                'full_name': repo.full_name,
                'ci_success_rate': snapshot.ci_success_rate,
                'ci_failures': snapshot.ci_failure_count,
            })
        if snapshot.security_alert_count > 0:
            security.append({
                'full_name': repo.full_name,
                'security_alerts': snapshot.security_alert_count,
            })
        if snapshot.stale_pr_count > 0:
            stale.append({
                'full_name': repo.full_name,
                'stale_prs': snapshot.stale_pr_count,
            })

    failing_ci.sort(key=lambda r: r['ci_success_rate'])
    security.sort(key=lambda r: r['security_alerts'], reverse=True)
    stale.sort(key=lambda r: r['stale_prs'], reverse=True)
    return Response({
        'failing_ci': failing_ci,
        'open_security_alerts': security,
        'stale_pull_requests': stale,
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def generate_fleet_digest_view(request: Request) -> Response:
    """Generate (synchronously) an org-wide fleet digest."""
    use_ai = request.data.get('use_ai', True)
    digest = FleetDigestService().generate_fleet_digest(use_ai=use_ai)
    return Response(RepoDigestSerializer(digest).data, status=status.HTTP_201_CREATED)
