"""Core views - merged from all apps"""
from typing import Any
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.request import Request
from django_filters.rest_framework import DjangoFilterBackend
from django.db import connection
from django.utils import timezone
from .models import Issue, IssueTemplate
from .serializers import (
    IssueSerializer,
    IssueTemplateSerializer,
    CreateSubIssueSerializer,
    CreateREADMEUpdateSerializer,
    CreateFeedbackIssueSerializer,
    CreateAutoIssueSerializer,
)
from .chat_serializers import ChatMessageSerializer, ChatResponseSerializer
from .services import IssueService
from .services import AutoIssueService
from .services.ai_service import AIService
import logging

logger = logging.getLogger('githubai')


class HealthCheckView(APIView):
    """Health check endpoint for monitoring"""
    permission_classes = []

    def get(self, request: Request) -> Response:
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
    def create_sub_issue(self, request: Request) -> Response:
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
    def create_readme_update(self, request: Request) -> Response:
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
    def create_from_feedback(self, request: Request) -> Response:
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
    def create_auto_issue(self, request: Request) -> Response:
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


class ChatView(APIView):
    """Chat endpoint using AIService for conversational interactions."""
    permission_classes = []

    def post(self, request: Request) -> Response:
        """Handle chat messages and return AI responses."""
        serializer = ChatMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_message = serializer.validated_data['message']

        try:
            # Use AIService to get response
            ai_service = AIService()

            system_message = ("You are a helpful AI assistant integrated with GitHubAI. "
                            "You can help users with questions about GitHub automation, "
                            "issue management, and general programming topics.")

            response_text = ai_service.call_ai_chat(
                system_prompt=system_message,
                user_prompt=user_message
            )

            response_data = {
                'response': response_text,
                'provider': ai_service.provider_name,
                'model': ai_service.model,
                'cached': False,  # AIService returns cached content directly, so we can't determine this
                'timestamp': timezone.now()
            }

            response_serializer = ChatResponseSerializer(data=response_data)
            response_serializer.is_valid(raise_exception=True)

            logger.info(f"Chat response generated - Provider: {ai_service.provider_name}, "
                       f"Model: {ai_service.model}")

            return Response(response_serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error in chat endpoint: {str(e)}")
            return Response(
                {'error': 'Failed to generate response. Please try again.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
