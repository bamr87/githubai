"""PRD MACHINE Celery tasks - GitHub event listeners and scheduled tasks."""
from celery import shared_task
from django.conf import settings
from django.utils import timezone
import logging

logger = logging.getLogger('githubai')


# ============================================================================
# GitHub Event Listener Tasks
# ============================================================================

@shared_task(bind=True, max_retries=3)
def process_github_push_event(self, repo: str, commit_sha: str, commit_message: str):
    """Process GitHub push event and trigger PRD distillation if needed.

    Args:
        repo: Repository in owner/repo format.
        commit_sha: SHA of the pushed commit.
        commit_message: Commit message for context.
    """
    try:
        from prd_machine.services.core import PRDMachineService
        from prd_machine.models import PRDState, PRDEvent

        logger.info(f"Processing push event for {repo}: {commit_sha[:7]}")

        service = PRDMachineService(repo=repo)
        prd_state = service.get_or_create_prd_state()

        # Log event
        event = PRDEvent.objects.create(
            prd_state=prd_state,
            event_type='push',
            event_data={
                'commit_sha': commit_sha,
                'commit_message': commit_message,
            }
        )

        # Check if auto-evolve is enabled
        if not prd_state.auto_evolve:
            event.processed = True
            event.processed_at = timezone.now()
            event.result = "Auto-evolve disabled - skipped"
            event.save()
            return {'status': 'skipped', 'reason': 'auto_evolve_disabled'}

        # Check if PRD-related files changed (heuristic based on commit message)
        prd_keywords = ['prd', 'requirement', 'feature', 'api', 'endpoint', 'milestone']
        should_distill = any(kw in commit_message.lower() for kw in prd_keywords)

        if should_distill or 'PRD.md' in commit_message:
            # Trigger distillation
            service.distill_prd(
                prd_state=prd_state,
                trigger_type='commit',
                trigger_ref=commit_sha,
                context={'commit_message': commit_message}
            )

            event.processed = True
            event.processed_at = timezone.now()
            event.result = f"Distilled PRD to v{prd_state.version}"
            event.save()

            return {
                'status': 'distilled',
                'version': prd_state.version,
                'commit_sha': commit_sha
            }
        else:
            event.processed = True
            event.processed_at = timezone.now()
            event.result = "No PRD-relevant changes detected"
            event.save()
            return {'status': 'skipped', 'reason': 'no_relevant_changes'}

    except Exception as exc:
        logger.error(f"Error processing push event: {exc}")
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def process_github_pr_event(self, repo: str, pr_number: int, action: str, title: str, body: str = ''):
    """Process GitHub pull request event.

    Args:
        repo: Repository in owner/repo format.
        pr_number: PR number.
        action: PR action (opened, closed, merged).
        title: PR title.
        body: PR body/description.
    """
    try:
        from prd_machine.services.core import PRDMachineService
        from prd_machine.models import PRDState, PRDEvent

        logger.info(f"Processing PR event for {repo}: PR #{pr_number} ({action})")

        service = PRDMachineService(repo=repo)
        prd_state = service.get_or_create_prd_state()

        # Log event
        event = PRDEvent.objects.create(
            prd_state=prd_state,
            event_type='pull_request',
            event_data={
                'pr_number': pr_number,
                'action': action,
                'title': title,
                'body': body[:500],  # Truncate
            }
        )

        # Only process merged PRs for distillation
        if action == 'closed' and prd_state.auto_evolve:
            service.distill_prd(
                prd_state=prd_state,
                trigger_type='pr_merge',
                trigger_ref=f"PR #{pr_number}",
                context={'pr_title': title, 'pr_body': body}
            )

            event.processed = True
            event.processed_at = timezone.now()
            event.result = f"Distilled PRD to v{prd_state.version}"
            event.save()

            return {
                'status': 'distilled',
                'version': prd_state.version,
                'pr_number': pr_number
            }
        else:
            event.processed = True
            event.processed_at = timezone.now()
            event.result = f"PR action '{action}' - no distillation needed"
            event.save()
            return {'status': 'logged', 'action': action}

    except Exception as exc:
        logger.error(f"Error processing PR event: {exc}")
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def process_github_issue_event(self, repo: str, issue_number: int, action: str, title: str, labels: list = None):
    """Process GitHub issue event.

    Args:
        repo: Repository in owner/repo format.
        issue_number: Issue number.
        action: Issue action (opened, closed, labeled).
        title: Issue title.
        labels: Issue labels.
    """
    try:
        from prd_machine.services.core import PRDMachineService
        from prd_machine.models import PRDState, PRDEvent

        logger.info(f"Processing issue event for {repo}: Issue #{issue_number} ({action})")

        service = PRDMachineService(repo=repo)
        prd_state = service.get_or_create_prd_state()

        # Log event
        event = PRDEvent.objects.create(
            prd_state=prd_state,
            event_type='issues',
            event_data={
                'issue_number': issue_number,
                'action': action,
                'title': title,
                'labels': labels or [],
            }
        )

        # Check for PRD-relevant labels
        prd_labels = {'prd', 'requirement', 'feature-request', 'enhancement', 'milestone'}
        has_prd_label = bool(set(labels or []) & prd_labels)

        if has_prd_label and action in ('opened', 'closed') and prd_state.auto_evolve:
            trigger_type = 'issue_created' if action == 'opened' else 'issue_closed'

            service.distill_prd(
                prd_state=prd_state,
                trigger_type=trigger_type,
                trigger_ref=f"Issue #{issue_number}",
                context={'issue_title': title, 'labels': labels}
            )

            event.processed = True
            event.processed_at = timezone.now()
            event.result = f"Distilled PRD to v{prd_state.version}"
            event.save()

            return {
                'status': 'distilled',
                'version': prd_state.version,
                'issue_number': issue_number
            }
        else:
            event.processed = True
            event.processed_at = timezone.now()
            event.result = "No PRD-relevant labels"
            event.save()
            return {'status': 'logged', 'action': action}

    except Exception as exc:
        logger.error(f"Error processing issue event: {exc}")
        raise self.retry(exc=exc, countdown=60)


# ============================================================================
# Scheduled Tasks
# ============================================================================

@shared_task(bind=True)
def scheduled_prd_distillation(self, repo: str = None):
    """Scheduled task to distill PRD periodically.

    Runs on a schedule (e.g., daily) to keep PRD fresh.

    Args:
        repo: Optional specific repo. If None, processes all active PRDs.
    """
    from prd_machine.services.core import PRDMachineService
    from prd_machine.models import PRDState

    if repo:
        repos = [repo]
    else:
        # Get all repos with auto_evolve enabled
        repos = PRDState.objects.filter(
            auto_evolve=True
        ).values_list('repo', flat=True).distinct()

    results = []
    for r in repos:
        try:
            service = PRDMachineService(repo=r)
            prd_state = service.get_or_create_prd_state()

            service.distill_prd(
                prd_state=prd_state,
                trigger_type='scheduled',
                trigger_ref=f"Scheduled distillation at {timezone.now().isoformat()}"
            )

            results.append({
                'repo': r,
                'status': 'success',
                'version': prd_state.version
            })

        except Exception as e:
            logger.error(f"Scheduled distillation failed for {r}: {e}")
            results.append({
                'repo': r,
                'status': 'error',
                'error': str(e)
            })

    return results


@shared_task(bind=True)
def scheduled_conflict_detection(self, repo: str = None):
    """Scheduled task to detect PRD conflicts.

    Runs periodically to catch PRD drift from reality.

    Args:
        repo: Optional specific repo. If None, processes all active PRDs.
    """
    from prd_machine.services.core import PRDMachineService
    from prd_machine.models import PRDState

    if repo:
        repos = [repo]
    else:
        repos = PRDState.objects.filter(
            auto_evolve=True
        ).values_list('repo', flat=True).distinct()

    results = []
    for r in repos:
        try:
            service = PRDMachineService(repo=r)
            prd_state = service.get_or_create_prd_state()

            conflicts = service.detect_conflicts(prd_state)

            # Send Slack alerts for high/critical conflicts
            for conflict in conflicts:
                if conflict.severity in ('high', 'critical'):
                    service.send_slack_alert(conflict)

            results.append({
                'repo': r,
                'conflicts_found': len(conflicts),
                'high_severity': sum(1 for c in conflicts if c.severity in ('high', 'critical'))
            })

        except Exception as e:
            logger.error(f"Conflict detection failed for {r}: {e}")
            results.append({
                'repo': r,
                'status': 'error',
                'error': str(e)
            })

    return results


# ============================================================================
# Export Tasks
# ============================================================================

@shared_task(bind=True, max_retries=3)
def export_prd_to_issues_task(self, repo: str):
    """Async task to export PRD to GitHub issues.

    Args:
        repo: Repository in owner/repo format.
    """
    try:
        from prd_machine.services.core import PRDMachineService

        service = PRDMachineService(repo=repo)
        prd_state = service.get_or_create_prd_state()

        export = service.export_to_issues(prd_state)

        return {
            'status': 'success',
            'items_created': export.items_created,
            'github_refs': export.github_refs
        }

    except Exception as exc:
        logger.error(f"Export to issues failed: {exc}")
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def export_prd_changelog_task(self, repo: str, version: str):
    """Async task to generate changelog from PRD.

    Args:
        repo: Repository in owner/repo format.
        version: Version for changelog.
    """
    try:
        from prd_machine.services.core import PRDMachineService

        service = PRDMachineService(repo=repo)
        prd_state = service.get_or_create_prd_state()

        export = service.export_to_changelog(prd_state, version)

        return {
            'status': 'success',
            'changelog': export.details.get('changelog', ''),
            'version': version
        }

    except Exception as exc:
        logger.error(f"Changelog generation failed: {exc}")
        raise self.retry(exc=exc, countdown=60)


# ============================================================================
# Sync Tasks
# ============================================================================

@shared_task(bind=True, max_retries=3)
def sync_prd_from_github_task(self, repo: str, file_path: str = 'PRD.md'):
    """Async task to sync PRD from GitHub.

    Args:
        repo: Repository in owner/repo format.
        file_path: Path to PRD file.
    """
    try:
        from prd_machine.services.core import PRDMachineService

        service = PRDMachineService(repo=repo)
        prd_state = service.sync_from_github(file_path)

        return {
            'status': 'success',
            'repo': repo,
            'version': prd_state.version,
            'content_hash': prd_state.content_hash
        }

    except Exception as exc:
        logger.error(f"PRD sync failed: {exc}")
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True)
def generate_prd_task(self, repo: str, project_name: str = None):
    """Async task to generate PRD from scratch.

    Args:
        repo: Repository in owner/repo format.
        project_name: Optional project name.
    """
    try:
        from prd_machine.services.core import PRDMachineService

        service = PRDMachineService(repo=repo)
        prd_state = service.generate_prd_from_scratch(project_name=project_name)

        return {
            'status': 'success',
            'repo': repo,
            'version': prd_state.version,
            'content_length': len(prd_state.content)
        }

    except Exception as exc:
        logger.error(f"PRD generation failed: {exc}")
        raise
