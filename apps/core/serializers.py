"""Core serializers - merged from issues app"""
from rest_framework import serializers
from .models import Issue, IssueTemplate, IssueFileReference, AIProvider, AIModel


class AIProviderSerializer(serializers.ModelSerializer):
    """Serializer for AIProvider model (read-only, excludes api_key)."""

    has_api_key = serializers.ReadOnlyField()
    models_count = serializers.SerializerMethodField()

    class Meta:
        model = AIProvider
        fields = [
            'id',
            'name',
            'display_name',
            'base_url',
            'is_active',
            'default_temperature',
            'default_max_tokens',
            'description',
            'documentation_url',
            'has_api_key',
            'models_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields  # All fields read-only for security

    def get_models_count(self, obj):
        """Return count of active models for this provider."""
        return obj.models.filter(is_active=True).count()


class AIModelSerializer(serializers.ModelSerializer):
    """Serializer for AIModel model."""

    provider_name = serializers.CharField(source='provider.name', read_only=True)
    provider_display_name = serializers.CharField(source='provider.display_name', read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = AIModel
        fields = [
            'id',
            'provider',
            'provider_name',
            'provider_display_name',
            'name',
            'display_name',
            'full_name',
            'capabilities',
            'max_tokens',
            'context_window',
            'supports_system_prompt',
            'supports_streaming',
            'input_price_per_million',
            'output_price_per_million',
            'is_active',
            'is_default',
            'description',
            'release_date',
            'deprecation_date',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_full_name(self, obj):
        """Return provider:model format name."""
        return f"{obj.provider.name}:{obj.name}"


class IssueTemplateSerializer(serializers.ModelSerializer):
    """Serializer for IssueTemplate model."""

    class Meta:
        model = IssueTemplate
        fields = [
            'id',
            'name',
            'about',
            'title_prefix',
            'labels',
            'prompt',
            'template_body',
            'include_files',
            'is_active',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class IssueFileReferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = IssueFileReference
        fields = ['id', 'file_path', 'content', 'content_hash', 'created_at']


class IssueSerializer(serializers.ModelSerializer):
    """Serializer for Issue model with nested relationships."""

    file_references = IssueFileReferenceSerializer(many=True, read_only=True)
    sub_issues_count = serializers.SerializerMethodField()

    class Meta:
        model = Issue
        fields = [
            'id',
            'github_repo',
            'github_issue_number',
            'title',
            'body',
            'html_url',
            'state',
            'issue_type',
            'labels',
            'parent_issue',
            'ai_generated',
            'template',
            'file_references',
            'sub_issues_count',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'ai_generated', 'sub_issues_count']

    def get_sub_issues_count(self, obj):
        """Return count of sub-issues."""
        return obj.sub_issues.count()


class CreateSubIssueSerializer(serializers.Serializer):
    """Serializer for creating sub-issues"""
    parent_issue_number = serializers.IntegerField(required=True)
    repo = serializers.CharField(max_length=200, default='bamr87/githubai')
    file_refs = serializers.ListField(child=serializers.CharField(), required=False)


class CreateREADMEUpdateSerializer(serializers.Serializer):
    """Serializer for creating README update issues"""
    issue_number = serializers.IntegerField(required=True)
    repo = serializers.CharField(max_length=200, default='bamr87/githubai')
    additional_files = serializers.ListField(child=serializers.CharField(), required=False)


class CreateFeedbackIssueSerializer(serializers.Serializer):
    """Serializer for creating issues from user feedback"""

    FEEDBACK_TYPES = ("bug", "feature")

    feedback_type = serializers.ChoiceField(choices=FEEDBACK_TYPES)
    summary = serializers.CharField(max_length=200)
    description = serializers.CharField()
    repo = serializers.CharField(max_length=200, required=False, default='bamr87/githubai')
    context_files = serializers.ListField(
        child=serializers.CharField(), required=False, allow_empty=True
    )


class CreateAutoIssueSerializer(serializers.Serializer):
    """Serializer for creating auto-generated issues from repo analysis"""

    CHORE_TYPES = (
        'code_quality',
        'todo_scan',
        'documentation',
        'dependencies',
        'test_coverage',
        'general_review',
    )

    chore_type = serializers.ChoiceField(choices=CHORE_TYPES, default='general_review')
    repo = serializers.CharField(max_length=200, required=False, default='bamr87/githubai')
    context_files = serializers.ListField(
        child=serializers.CharField(), required=False, allow_empty=True
    )
    auto_submit = serializers.BooleanField(default=True)

