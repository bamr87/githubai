"""Dashboard Celery tasks - scheduled ingestion and AI digests.

These wire the cockpit's data backbone into Celery Beat. Schedules are not
hard-coded here; configure them via django-celery-beat (DatabaseScheduler) or
add entries to ``CELERY_BEAT_SCHEDULE`` so operators control cadence and which
repositories are polled.
"""
from __future__ import annotations

import logging

from celery import shared_task

logger = logging.getLogger('githubai')


@shared_task(bind=True, max_retries=3)
def ingest_repository_metrics(self, full_name: str):
    """Collect and persist a metrics snapshot for a single repository."""
    from dashboard.models import Repository
    from dashboard.services import MetricsCollectorService

    try:
        repo = Repository.objects.get(full_name=full_name)
    except Repository.DoesNotExist:
        logger.error(f"ingest_repository_metrics: repo not found: {full_name}")
        return {'status': 'not_found', 'repo': full_name}

    try:
        snapshot = MetricsCollectorService().collect_snapshot(repo)
        return {'status': 'ok', 'repo': full_name, 'snapshot_id': snapshot.id}
    except Exception as exc:  # noqa: BLE001
        logger.error(f"ingest_repository_metrics failed for {full_name}: {exc}")
        raise self.retry(exc=exc, countdown=60)


@shared_task
def ingest_all_tracked_repositories():
    """Fan out ingestion across every repository on the active watchlist."""
    from dashboard.services import RepositoryService

    repos = list(RepositoryService.tracked_repositories().values_list('full_name', flat=True))
    for full_name in repos:
        ingest_repository_metrics.delay(full_name)
    logger.info(f"Queued ingestion for {len(repos)} tracked repositories")
    return {'queued': len(repos)}


@shared_task
def generate_repo_digest(full_name: str, use_ai: bool = True):
    """Generate an AI "what needs attention" digest for one repository."""
    from dashboard.models import Repository
    from dashboard.services import FleetDigestService

    try:
        repo = Repository.objects.get(full_name=full_name)
    except Repository.DoesNotExist:
        logger.error(f"generate_repo_digest: repo not found: {full_name}")
        return {'status': 'not_found', 'repo': full_name}

    digest = FleetDigestService().generate_repo_digest(repo, use_ai=use_ai)
    return {'status': 'ok', 'repo': full_name, 'digest_id': digest.id}


@shared_task
def generate_fleet_digest(use_ai: bool = True):
    """Generate the org-wide fleet digest across all tracked repositories."""
    from dashboard.services import FleetDigestService

    digest = FleetDigestService().generate_fleet_digest(use_ai=use_ai)
    return {'status': 'ok', 'digest_id': digest.id, 'severity': digest.severity}
