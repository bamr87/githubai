"""Core views - merged from all apps"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from django.db import connection
from .models import Issue, IssueTemplate
from .serializers import (
    IssueSerializer,
    IssueTemplateSerializer,
    CreateSubIssueSerializer,
    CreateREADMEUpdateSerializer,
    CreateFeedbackIssueSerializer,
    CreateAutoIssueSerializer,
)
from .services import IssueService
from .services import AutoIssueService


class HealthCheckView(APIView):
    """Health check endpoint for monitoring"""
    permission_classes = []

    def get(self, request):
        """Return health status"""
        health_status = {
            'status': 'healthy',
            'database': 'unknown',
        }

        # Check database connection
        try:
            connection.ensure_connection()
            health_status['database'] = 'connected'
        except Exception as e:
            health_status['status'] = 'unhealthy'
            health_status['database'] = f'error: {str(e)}'
            return Response(health_status, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        return Response(health_status, status=status.HTTP_200_OK)


class IssueTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for issue templates"""
    queryset = IssueTemplate.objects.filter(is_active=True)
    serializer_class = IssueTemplateSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name', 'is_active']


class IssueViewSet(viewsets.ModelViewSet):
    """ViewSet for issues"""
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['issue_type', 'state', 'github_repo', 'ai_generated']
    search_fields = ['title', 'body', 'github_issue_number']

    @action(detail=False, methods=['post'], url_path='create-sub-issue')
    def create_sub_issue(self, request):
        """Create a sub-issue from a parent issue"""
        serializer = CreateSubIssueSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            service = IssueService()
            issue = service.create_sub_issue_from_template(
                repo=serializer.validated_data['repo'],
                parent_issue_number=serializer.validated_data['parent_issue_number'],
                file_refs=serializer.validated_data.get('file_refs', [])
            )
            return Response(
                IssueSerializer(issue).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['post'], url_path='create-readme-update')
    def create_readme_update(self, request):
        """Create a README update issue"""
        serializer = CreateREADMEUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            service = IssueService()
            issue = service.create_readme_update_issue(
                repo=serializer.validated_data['repo'],
                issue_number=serializer.validated_data['issue_number'],
                additional_files=serializer.validated_data.get('additional_files', [])
            )
            return Response(
                IssueSerializer(issue).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=["post"], url_path="create-from-feedback")
    def create_from_feedback(self, request):
        """Create an issue directly from user feedback using AI refinement."""
        serializer = CreateFeedbackIssueSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        try:
            service = IssueService()
            issue = service.create_issue_from_feedback(
                feedback_type=data["feedback_type"],
                summary=data["summary"],
                description=data["description"],
                repo=data.get("repo"),
                context_files=data.get("context_files") or [],
            )
            return Response(IssueSerializer(issue).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], url_path="create-auto-issue")
    def create_auto_issue(self, request):
        """Automatically analyze repository and create maintenance issue."""
        serializer = CreateAutoIssueSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        try:
            service = AutoIssueService()
            issue = service.analyze_repo_and_create_issue(
                repo=data.get("repo", "bamr87/githubai"),
                chore_type=data["chore_type"],
                context_files=data.get("context_files"),
                auto_submit=data.get("auto_submit", True),
            )

            if not data.get("auto_submit", True):
                return Response(
                    {"analysis": issue, "message": "Dry run - no issue created"},
                    status=status.HTTP_200_OK
                )

            return Response(IssueSerializer(issue).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
