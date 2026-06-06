"""Dashboard serializers for the cockpit REST API."""
from rest_framework import serializers

from dashboard.models import (
    Organization,
    Repository,
    RepoConnection,
    RepoMetricSnapshot,
    RepoDigest,
)


class OrganizationSerializer(serializers.ModelSerializer):
    repository_count = serializers.IntegerField(source='repositories.count', read_only=True)

    class Meta:
        model = Organization
        fields = [
            'id', 'login', 'name', 'org_type', 'avatar_url', 'html_url',
            'is_active', 'repository_count', 'created_at', 'updated_at',
        ]


class RepoConnectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepoConnection
        fields = [
            'id', 'organization', 'connection_type', 'token_env_var',
            'installation_id', 'is_active', 'created_at', 'updated_at',
        ]


class RepoMetricSnapshotSerializer(serializers.ModelSerializer):
    health_score = serializers.IntegerField(read_only=True)

    class Meta:
        model = RepoMetricSnapshot
        fields = [
            'id', 'repository', 'captured_at', 'open_pr_count', 'stale_pr_count',
            'open_issue_count', 'ci_total_runs', 'ci_success_count',
            'ci_failure_count', 'ci_success_rate', 'security_alert_count',
            'last_release_tag', 'last_release_at', 'stars', 'forks',
            'health_score', 'data', 'created_at',
        ]


class RepoDigestSerializer(serializers.ModelSerializer):
    repository_full_name = serializers.CharField(
        source='repository.full_name', read_only=True, default=None
    )

    class Meta:
        model = RepoDigest
        fields = [
            'id', 'repository', 'repository_full_name', 'scope', 'title',
            'summary', 'severity', 'generated_by_model', 'data', 'created_at',
        ]


class RepositorySerializer(serializers.ModelSerializer):
    organization_login = serializers.CharField(source='organization.login', read_only=True)
    latest_snapshot = serializers.SerializerMethodField()

    class Meta:
        model = Repository
        fields = [
            'id', 'organization', 'organization_login', 'full_name', 'owner',
            'name', 'description', 'default_branch', 'is_private', 'is_archived',
            'is_fork', 'language', 'topics', 'html_url', 'is_tracked',
            'last_ingested_at', 'stars', 'forks', 'open_issues_count',
            'latest_snapshot', 'created_at', 'updated_at',
        ]
        read_only_fields = ['organization', 'owner', 'last_ingested_at']

    def get_latest_snapshot(self, obj):
        snapshot = obj.snapshots.order_by('-captured_at').first()
        if snapshot is None:
            return None
        return RepoMetricSnapshotSerializer(snapshot).data


class RegisterRepositorySerializer(serializers.Serializer):
    """Input serializer for registering a repository by ``owner/repo``."""
    full_name = serializers.CharField(max_length=512)
    is_tracked = serializers.BooleanField(default=True)

    def validate_full_name(self, value: str) -> str:
        if '/' not in value:
            raise serializers.ValidationError("Expected 'owner/repo' format.")
        return value


class DiscoverRepositoriesSerializer(serializers.Serializer):
    """Input serializer for discovering repositories for an owner."""
    owner = serializers.CharField(max_length=255)
    owner_type = serializers.ChoiceField(choices=['org', 'user'], default='org')
