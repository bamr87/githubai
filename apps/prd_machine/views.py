"""PRD MACHINE views - REST API endpoints for PRD automation."""
import hmac
import hashlib
import json
import logging

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response

from prd_machine.models import PRDState, PRDVersion, PRDEvent, PRDConflict, PRDExport
from prd_machine.serializers import (
    PRDStateSerializer, PRDVersionSerializer, PRDEventSerializer,
    PRDConflictSerializer, PRDExportSerializer
)
from prd_machine.services.core import PRDMachineService
from prd_machine import tasks

logger = logging.getLogger('githubai')


# ============================================================================
# ViewSets for CRUD operations
# ============================================================================

class PRDStateViewSet(viewsets.ModelViewSet):
    """ViewSet for PRD State management."""
    queryset = PRDState.objects.all()
    serializer_class = PRDStateSerializer
    filterset_fields = ['repo', 'is_locked', 'auto_evolve']
    search_fields = ['repo', 'file_path']
    ordering_fields = ['created_at', 'updated_at', 'last_distilled_at']
    ordering = ['-updated_at']

    @action(detail=True, methods=['post'])
    def sync(self, request, pk=None):
        """Sync PRD from GitHub."""
        prd_state = self.get_object()
        service = PRDMachineService(repo=prd_state.repo)

        try:
            updated_state = service.sync_from_github(prd_state.file_path)
            return Response({
                'status': 'synced',
                'version': updated_state.version,
                'content_hash': updated_state.content_hash,
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def distill(self, request, pk=None):
        """Distill/evolve PRD using AI."""
        prd_state = self.get_object()
        service = PRDMachineService(repo=prd_state.repo)

        try:
            updated_state = service.distill_prd(
                prd_state=prd_state,
                trigger_type='manual_sync',
                trigger_ref='API: distill endpoint'
            )
            return Response({
                'status': 'distilled',
                'version': updated_state.version,
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def detect_conflicts(self, request, pk=None):
        """Detect conflicts between PRD and repo state."""
        prd_state = self.get_object()
        service = PRDMachineService(repo=prd_state.repo)

        try:
            conflicts = service.detect_conflicts(prd_state)
            return Response({
                'conflicts_found': len(conflicts),
                'conflicts': PRDConflictSerializer(conflicts, many=True).data,
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def export_issues(self, request, pk=None):
        """Export PRD to GitHub issues."""
        prd_state = self.get_object()
        service = PRDMachineService(repo=prd_state.repo)

        try:
            export = service.export_to_issues(prd_state)
            return Response({
                'status': 'exported',
                'items_created': export.items_created,
                'github_refs': export.github_refs,
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def toggle_lock(self, request, pk=None):
        """Toggle zero-touch mode."""
        prd_state = self.get_object()
        prd_state.is_locked = not prd_state.is_locked
        prd_state.save()

        return Response({
            'status': 'toggled',
            'is_locked': prd_state.is_locked,
            'message': "I got this, meatbag." if prd_state.is_locked else "Human edits allowed.",
        })


class PRDVersionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for PRD Version history (read-only)."""
    queryset = PRDVersion.objects.all()
    serializer_class = PRDVersionSerializer
    filterset_fields = ['prd_state', 'trigger_type', 'is_human_edit']
    ordering = ['-created_at']


class PRDEventViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for PRD Events (read-only)."""
    queryset = PRDEvent.objects.all()
    serializer_class = PRDEventSerializer
    filterset_fields = ['prd_state', 'event_type', 'processed']
    ordering = ['-created_at']


class PRDConflictViewSet(viewsets.ModelViewSet):
    """ViewSet for PRD Conflicts."""
    queryset = PRDConflict.objects.all()
    serializer_class = PRDConflictSerializer
    filterset_fields = ['prd_state', 'conflict_type', 'severity', 'resolved']
    ordering = ['-severity', '-created_at']

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Mark conflict as resolved."""
        from django.utils import timezone

        conflict = self.get_object()
        conflict.resolved = True
        conflict.resolved_at = timezone.now()
        conflict.resolved_by = f"API: {request.user.username if request.user.is_authenticated else 'anonymous'}"
        conflict.save()

        return Response({
            'status': 'resolved',
            'conflict_id': conflict.id,
        })


# ============================================================================
# Function-based views for webhooks and manual triggers
# ============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def github_webhook(request):
    """Handle GitHub webhook events.

    Processes push, pull_request, and issues events to trigger PRD updates.
    """
    # Verify webhook signature if secret is configured
    webhook_secret = getattr(settings, 'GITHUB_WEBHOOK_SECRET', None)
    if webhook_secret:
        signature = request.headers.get('X-Hub-Signature-256')
        if not signature:
            return JsonResponse({'error': 'Missing signature'}, status=403)

        expected = 'sha256=' + hmac.new(
            webhook_secret.encode(),
            request.body,
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(signature, expected):
            return JsonResponse({'error': 'Invalid signature'}, status=403)

    # Parse event
    event_type = request.headers.get('X-GitHub-Event')
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    # Extract repo
    repo = payload.get('repository', {}).get('full_name')
    if not repo:
        return JsonResponse({'error': 'Missing repository'}, status=400)

    # Dispatch to appropriate task
    if event_type == 'push':
        commit = payload.get('head_commit', {})
        tasks.process_github_push_event.delay(
            repo=repo,
            commit_sha=commit.get('id', ''),
            commit_message=commit.get('message', ''),
        )
        return JsonResponse({'status': 'queued', 'event': 'push'})

    elif event_type == 'pull_request':
        pr = payload.get('pull_request', {})
        tasks.process_github_pr_event.delay(
            repo=repo,
            pr_number=pr.get('number'),
            action=payload.get('action'),
            title=pr.get('title', ''),
            body=pr.get('body', ''),
        )
        return JsonResponse({'status': 'queued', 'event': 'pull_request'})

    elif event_type == 'issues':
        issue = payload.get('issue', {})
        tasks.process_github_issue_event.delay(
            repo=repo,
            issue_number=issue.get('number'),
            action=payload.get('action'),
            title=issue.get('title', ''),
            labels=[l.get('name') for l in issue.get('labels', [])],
        )
        return JsonResponse({'status': 'queued', 'event': 'issues'})

    else:
        return JsonResponse({'status': 'ignored', 'event': event_type})


@api_view(['POST'])
def sync_prd(request, repo):
    """Sync PRD from GitHub for a specific repo.

    Args:
        repo: Repository name (URL-encoded, e.g., "owner%2Frepo")
    """
    repo = repo.replace('%2F', '/')
    file_path = request.data.get('file_path', 'PRD.md')

    # Queue async task
    tasks.sync_prd_from_github_task.delay(repo=repo, file_path=file_path)

    return Response({
        'status': 'queued',
        'repo': repo,
        'file_path': file_path,
    })


@api_view(['POST'])
def distill_prd(request, repo):
    """Trigger PRD distillation for a specific repo.

    Args:
        repo: Repository name (URL-encoded)
    """
    repo = repo.replace('%2F', '/')

    service = PRDMachineService(repo=repo)
    prd_state = service.get_or_create_prd_state()

    try:
        updated_state = service.distill_prd(
            prd_state=prd_state,
            trigger_type='manual_sync',
            trigger_ref='API: distill endpoint'
        )

        return Response({
            'status': 'distilled',
            'repo': repo,
            'version': updated_state.version,
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def generate_prd(request, repo):
    """Generate new PRD from scratch for a specific repo.

    Args:
        repo: Repository name (URL-encoded)
    """
    repo = repo.replace('%2F', '/')
    project_name = request.data.get('project_name')

    # Queue async task
    tasks.generate_prd_task.delay(repo=repo, project_name=project_name)

    return Response({
        'status': 'queued',
        'repo': repo,
    })


@api_view(['POST'])
def detect_conflicts(request, repo):
    """Detect conflicts for a specific repo's PRD.

    Args:
        repo: Repository name (URL-encoded)
    """
    repo = repo.replace('%2F', '/')

    service = PRDMachineService(repo=repo)
    prd_state = service.get_or_create_prd_state()

    try:
        conflicts = service.detect_conflicts(prd_state)

        return Response({
            'repo': repo,
            'conflicts_found': len(conflicts),
            'conflicts': PRDConflictSerializer(conflicts, many=True).data,
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def export_to_issues(request, repo):
    """Export PRD to GitHub issues for a specific repo.

    Args:
        repo: Repository name (URL-encoded)
    """
    repo = repo.replace('%2F', '/')

    # Queue async task
    tasks.export_prd_to_issues_task.delay(repo=repo)

    return Response({
        'status': 'queued',
        'repo': repo,
    })
