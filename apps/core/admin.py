"""Core admin configuration - merged from all apps"""
from django.contrib import admin
from .models import (
    APILog, AIResponse, Issue, IssueTemplate, IssueFileReference,
    ChangelogEntry, DocumentationFile, Version
)


# ============================================================================
# Core Admin
# ============================================================================

@admin.register(APILog)
class APILogAdmin(admin.ModelAdmin):
    list_display = ['api_type', 'method', 'endpoint', 'status_code', 'duration_ms', 'created_at']
    list_filter = ['api_type', 'method', 'status_code', 'created_at']
    search_fields = ['endpoint', 'user_id', 'error_message']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


# ============================================================================
# AI Services Admin
# ============================================================================

@admin.register(AIResponse)
class AIResponseAdmin(admin.ModelAdmin):
    list_display = ['prompt_hash_short', 'model', 'temperature', 'tokens_used', 'cache_hit_count', 'created_at']
    list_filter = ['model', 'temperature', 'created_at']
    search_fields = ['prompt_hash', 'system_prompt', 'user_prompt']
    readonly_fields = ['created_at', 'updated_at', 'prompt_hash', 'tokens_used', 'cache_hit_count']
    date_hierarchy = 'created_at'

    def prompt_hash_short(self, obj):
        return obj.prompt_hash[:16]
    prompt_hash_short.short_description = 'Prompt Hash'

    def has_add_permission(self, request):
        return False


# ============================================================================
# Issues Admin
# ============================================================================

class IssueFileReferenceInline(admin.TabularInline):
    model = IssueFileReference
    extra = 0
    fields = ['file_path', 'content_hash', 'created_at']
    readonly_fields = ['content_hash', 'created_at']


@admin.register(IssueTemplate)
class IssueTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'title_prefix', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'about', 'prompt']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ['github_issue_number', 'title', 'issue_type', 'state', 'ai_generated', 'created_at']
    list_filter = ['issue_type', 'state', 'ai_generated', 'github_repo', 'created_at']
    search_fields = ['title', 'body', 'github_issue_number']
    readonly_fields = ['created_at', 'updated_at', 'html_url']
    inlines = [IssueFileReferenceInline]
    date_hierarchy = 'created_at'

    fieldsets = (
        ('GitHub Info', {
            'fields': ('github_repo', 'github_issue_number', 'html_url', 'state')
        }),
        ('Content', {
            'fields': ('title', 'body', 'issue_type', 'labels')
        }),
        ('Relationships', {
            'fields': ('parent_issue', 'template')
        }),
        ('AI Generation', {
            'fields': ('ai_generated', 'ai_prompt_used', 'ai_response'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(IssueFileReference)
class IssueFileReferenceAdmin(admin.ModelAdmin):
    list_display = ['issue', 'file_path', 'content_hash', 'created_at']
    list_filter = ['created_at']
    search_fields = ['file_path', 'issue__title']
    readonly_fields = ['created_at', 'updated_at', 'content_hash']


# ============================================================================
# Documentation Admin
# ============================================================================

@admin.register(ChangelogEntry)
class ChangelogEntryAdmin(admin.ModelAdmin):
    list_display = ['entry_type', 'commit_sha_short', 'pr_number', 'file_path', 'created_at']
    list_filter = ['entry_type', 'file_path', 'created_at']
    search_fields = ['commit_sha', 'commit_message', 'ai_generated_content']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'

    def commit_sha_short(self, obj):
        return obj.commit_sha[:7] if obj.commit_sha else '-'
    commit_sha_short.short_description = 'Commit'


@admin.register(DocumentationFile)
class DocumentationFileAdmin(admin.ModelAdmin):
    list_display = ['file_path', 'language', 'content_hash_short', 'updated_at']
    list_filter = ['language', 'updated_at']
    search_fields = ['file_path', 'markdown_content']
    readonly_fields = ['created_at', 'updated_at', 'content_hash']

    def content_hash_short(self, obj):
        return obj.content_hash[:16]
    content_hash_short.short_description = 'Content Hash'


# ============================================================================
# Versioning Admin
# ============================================================================

@admin.register(Version)
class VersionAdmin(admin.ModelAdmin):
    list_display = ['version_number', 'bump_type', 'is_published', 'git_tag', 'created_at']
    list_filter = ['bump_type', 'is_published', 'created_at']
    search_fields = ['version_number', 'commit_message', 'git_tag']
    readonly_fields = ['created_at', 'updated_at', 'commit_sha', 'published_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Version Info', {
            'fields': ('version_number', 'major', 'minor', 'patch', 'bump_type')
        }),
        ('Git Info', {
            'fields': ('commit_sha', 'commit_message', 'git_tag')
        }),
        ('Publishing', {
            'fields': ('is_published', 'published_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
