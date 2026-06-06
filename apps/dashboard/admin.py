"""Django admin registration for the dashboard (cockpit) models."""
from django.contrib import admin

from dashboard.models import (
    Organization,
    Repository,
    RepoConnection,
    RepoMetricSnapshot,
    RepoDigest,
)


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['login', 'name', 'org_type', 'is_active', 'created_at']
    list_filter = ['org_type', 'is_active']
    search_fields = ['login', 'name']


@admin.register(Repository)
class RepositoryAdmin(admin.ModelAdmin):
    list_display = [
        'full_name', 'language', 'is_tracked', 'is_archived',
        'stars', 'last_ingested_at',
    ]
    list_filter = ['is_tracked', 'is_archived', 'is_private', 'language']
    search_fields = ['full_name', 'owner', 'name']
    actions = ['mark_tracked', 'mark_untracked']

    @admin.action(description='Add selected repositories to watchlist')
    def mark_tracked(self, request, queryset):
        queryset.update(is_tracked=True)

    @admin.action(description='Remove selected repositories from watchlist')
    def mark_untracked(self, request, queryset):
        queryset.update(is_tracked=False)


@admin.register(RepoConnection)
class RepoConnectionAdmin(admin.ModelAdmin):
    list_display = ['organization', 'connection_type', 'token_env_var', 'is_active']
    list_filter = ['connection_type', 'is_active']


@admin.register(RepoMetricSnapshot)
class RepoMetricSnapshotAdmin(admin.ModelAdmin):
    list_display = [
        'repository', 'captured_at', 'open_pr_count', 'stale_pr_count',
        'ci_success_rate', 'security_alert_count',
    ]
    list_filter = ['captured_at', 'repository']
    search_fields = ['repository__full_name']
    date_hierarchy = 'captured_at'


@admin.register(RepoDigest)
class RepoDigestAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'scope', 'severity', 'generated_by_model', 'created_at']
    list_filter = ['scope', 'severity']
    search_fields = ['title', 'summary', 'repository__full_name']
