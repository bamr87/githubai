"""Core admin configuration - merged from all apps"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django import forms
from .models import (
    APILog, AIResponse, Issue, IssueTemplate, IssueFileReference,
    ChangelogEntry, DocumentationFile, Version,
    PromptTemplate, PromptSchema, PromptDataset, PromptDatasetEntry, PromptExecution,
    AIProvider, AIModel
)


# ============================================================================
# Core Admin
# ============================================================================

# Custom form to handle API key field
class AIProviderForm(forms.ModelForm):
    """Custom form for AIProvider to handle API key as password field"""

    api_key = forms.CharField(
        required=False,
        widget=forms.PasswordInput(render_value=True),
        help_text='API key will be stored securely. Leave blank to keep existing key.'
    )

    class Meta:
        model = AIProvider
        fields = '__all__'


@admin.register(AIProvider)
class AIProviderAdmin(admin.ModelAdmin):
    form = AIProviderForm
    list_display = ['display_name', 'name', 'has_key_badge', 'is_active', 'model_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'display_name', 'description']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'display_name', 'description', 'is_active')
        }),
        ('API Configuration', {
            'fields': ('api_key', 'base_url', 'documentation_url')
        }),
        ('Default Settings', {
            'fields': ('default_temperature', 'default_max_tokens'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def has_key_badge(self, obj):
        if obj.has_api_key:
            return format_html('<span style="color: green;">✓ Configured</span>')
        return format_html('<span style="color: red;">✗ Missing</span>')
    has_key_badge.short_description = 'API Key'

    def model_count(self, obj):
        count = obj.models.filter(is_active=True).count()
        return format_html(f'<a href="?provider__id__exact={obj.id}">{count} models</a>')
    model_count.short_description = 'Active Models'


@admin.register(AIModel)
class AIModelAdmin(admin.ModelAdmin):
    list_display = [
        'display_name', 'provider', 'name', 'is_default', 'is_active',
        'max_tokens', 'pricing_display', 'created_at'
    ]
    list_filter = ['provider', 'is_active', 'is_default', 'capabilities', 'created_at']
    search_fields = ['name', 'display_name', 'description']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('provider', 'name', 'display_name', 'description', 'is_active', 'is_default')
        }),
        ('Capabilities', {
            'fields': ('capabilities', 'supports_system_prompt', 'supports_streaming')
        }),
        ('Limits', {
            'fields': ('max_tokens', 'context_window')
        }),
        ('Pricing', {
            'fields': ('input_price_per_million', 'output_price_per_million'),
            'classes': ('collapse',)
        }),
        ('Lifecycle', {
            'fields': ('release_date', 'deprecation_date'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def pricing_display(self, obj):
        if obj.input_price_per_million and obj.output_price_per_million:
            return format_html(
                'In: ${} / Out: ${}',
                obj.input_price_per_million,
                obj.output_price_per_million
            )
        return '-'
    pricing_display.short_description = 'Pricing (per 1M tokens)'

    actions = ['set_as_default', 'activate_models', 'deactivate_models']

    @admin.action(description='Set as default for provider')
    def set_as_default(self, request, queryset):
        for model in queryset:
            # Unset other defaults for this provider
            AIModel.objects.filter(provider=model.provider, is_default=True).update(is_default=False)
            model.is_default = True
            model.save()
        self.message_user(request, f'Set {queryset.count()} model(s) as default.')

    @admin.action(description='Activate selected models')
    def activate_models(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f'Activated {queryset.count()} model(s).')

    @admin.action(description='Deactivate selected models')
    def deactivate_models(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f'Deactivated {queryset.count()} model(s).')


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


# ============================================================================
# Prompt Management Admin
# ============================================================================

class PromptSchemaInline(admin.TabularInline):
    model = PromptSchema
    extra = 0
    fields = ['schema_type', 'validation_enabled', 'description']
    readonly_fields = []


class PromptDatasetInline(admin.StackedInline):
    model = PromptDataset
    extra = 0
    fields = ['name', 'description', 'is_active']
    show_change_link = True


@admin.register(PromptTemplate)
class PromptTemplateAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'category', 'version_number', 'model', 'provider',
        'usage_count', 'is_active', 'last_used_at', 'created_at'
    ]
    list_filter = ['category', 'provider', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'system_prompt', 'user_prompt_template']
    readonly_fields = [
        'created_at', 'updated_at', 'usage_count', 'last_used_at',
        'version_link'
    ]
    inlines = [PromptSchemaInline, PromptDatasetInline]
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Identification', {
            'fields': ('name', 'category', 'description', 'is_active')
        }),
        ('Prompt Content', {
            'fields': ('system_prompt', 'user_prompt_template'),
            'description': 'Use Jinja2 syntax for variables: {{ variable_name }}'
        }),
        ('Model Configuration', {
            'fields': ('provider', 'model', 'temperature', 'max_tokens')
        }),
        ('Versioning', {
            'fields': ('version_number', 'parent_version', 'version_link'),
            'classes': ('collapse',)
        }),
        ('Usage Analytics', {
            'fields': ('usage_count', 'last_used_at'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['duplicate_prompt', 'create_new_version', 'deactivate_prompts', 'activate_prompts']

    def version_link(self, obj):
        """Show link to parent version"""
        if obj.parent_version:
            url = reverse('admin:core_prompttemplate_change', args=[obj.parent_version.id])
            return format_html('<a href="{}">{}</a>', url, obj.parent_version)
        return '-'
    version_link.short_description = 'Parent Version'

    def duplicate_prompt(self, request, queryset):
        """Duplicate selected prompts with incremented version"""
        count = 0
        for prompt in queryset:
            # Find highest version number for this prompt name
            base_name = prompt.name.rsplit(' v', 1)[0] if ' v' in prompt.name else prompt.name
            existing = PromptTemplate.objects.filter(name__startswith=base_name).order_by('-version_number')
            next_version = existing.first().version_number + 1 if existing else 1

            # Create duplicate
            new_prompt = PromptTemplate.objects.create(
                name=f"{base_name} v{next_version}",
                category=prompt.category,
                description=f"Duplicate of {prompt.name}",
                system_prompt=prompt.system_prompt,
                user_prompt_template=prompt.user_prompt_template,
                model=prompt.model,
                provider=prompt.provider,
                temperature=prompt.temperature,
                max_tokens=prompt.max_tokens,
                version_number=next_version,
                parent_version=prompt,
                is_active=False  # Start inactive for review
            )
            count += 1

        self.message_user(request, f"Successfully duplicated {count} prompt(s)")
    duplicate_prompt.short_description = "Duplicate selected prompts"

    def create_new_version(self, request, queryset):
        """Create new version of selected prompts"""
        count = 0
        for prompt in queryset:
            new_prompt = PromptTemplate.objects.create(
                name=prompt.name,
                category=prompt.category,
                description=prompt.description,
                system_prompt=prompt.system_prompt,
                user_prompt_template=prompt.user_prompt_template,
                model=prompt.model,
                provider=prompt.provider,
                temperature=prompt.temperature,
                max_tokens=prompt.max_tokens,
                version_number=prompt.version_number + 1,
                parent_version=prompt,
                is_active=False
            )
            # Deactivate old version
            prompt.is_active = False
            prompt.save(update_fields=['is_active'])
            count += 1

        self.message_user(request, f"Successfully created new version for {count} prompt(s)")
    create_new_version.short_description = "Create new version"

    def deactivate_prompts(self, request, queryset):
        """Deactivate selected prompts"""
        count = queryset.update(is_active=False)
        self.message_user(request, f"Successfully deactivated {count} prompt(s)")
    deactivate_prompts.short_description = "Deactivate selected prompts"

    def activate_prompts(self, request, queryset):
        """Activate selected prompts"""
        count = queryset.update(is_active=True)
        self.message_user(request, f"Successfully activated {count} prompt(s)")
    activate_prompts.short_description = "Activate selected prompts"




@admin.register(PromptSchema)
class PromptSchemaAdmin(admin.ModelAdmin):
    list_display = ['prompt', 'schema_type', 'validation_enabled', 'created_at']
    list_filter = ['schema_type', 'validation_enabled', 'created_at']
    search_fields = ['prompt__name', 'description']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Basic Info', {
            'fields': ('prompt', 'schema_type', 'validation_enabled')
        }),
        ('Schema Definition', {
            'fields': ('schema_definition', 'description')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class PromptDatasetEntryInline(admin.TabularInline):
    model = PromptDatasetEntry
    extra = 1
    fields = ['input_variables', 'expected_output_pattern', 'tags']


@admin.register(PromptDataset)
class PromptDatasetAdmin(admin.ModelAdmin):
    list_display = ['name', 'prompt', 'entry_count_display', 'is_active', 'created_at']
    list_filter = ['is_active', 'prompt__category', 'created_at']
    search_fields = ['name', 'description', 'prompt__name']
    readonly_fields = ['created_at', 'updated_at', 'entry_count_display']
    inlines = [PromptDatasetEntryInline]

    fieldsets = (
        ('Basic Info', {
            'fields': ('prompt', 'name', 'description', 'is_active')
        }),
        ('Statistics', {
            'fields': ('entry_count_display',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def entry_count_display(self, obj):
        """Display entry count"""
        return obj.entry_count
    entry_count_display.short_description = 'Number of Entries'

    actions = ['run_dataset_test']

    def run_dataset_test(self, request, queryset):
        """Run prompt tests against dataset entries"""
        # This would trigger the actual test execution
        # For now, just a placeholder
        self.message_user(
            request,
            f"Dataset testing feature coming soon. Selected {queryset.count()} dataset(s)."
        )
    run_dataset_test.short_description = "Run tests with this dataset"


@admin.register(PromptDatasetEntry)
class PromptDatasetEntryAdmin(admin.ModelAdmin):
    list_display = ['dataset', 'input_vars_preview', 'tags_display', 'created_at']
    list_filter = ['dataset__prompt__category', 'created_at']
    search_fields = ['dataset__name', 'notes', 'expected_output_pattern']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Dataset', {
            'fields': ('dataset',)
        }),
        ('Test Case', {
            'fields': ('input_variables', 'expected_output_pattern', 'tags', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def input_vars_preview(self, obj):
        """Show preview of input variables"""
        if obj.input_variables:
            preview = str(obj.input_variables)
            return preview[:50] + '...' if len(preview) > 50 else preview
        return '-'
    input_vars_preview.short_description = 'Input Variables'

    def tags_display(self, obj):
        """Display tags as comma-separated list"""
        return ', '.join(obj.tags) if obj.tags else '-'
    tags_display.short_description = 'Tags'


@admin.register(PromptExecution)
class PromptExecutionAdmin(admin.ModelAdmin):
    list_display = [
        'status_icon', 'prompt', 'provider_used', 'model_used',
        'tokens_used', 'duration_ms', 'cache_hit', 'success', 'created_at'
    ]
    list_filter = ['success', 'cache_hit', 'provider_used', 'prompt__category', 'created_at']
    search_fields = ['prompt__name', 'output_content', 'error_message']
    readonly_fields = [
        'created_at', 'updated_at', 'prompt', 'input_variables',
        'rendered_system_prompt', 'rendered_user_prompt', 'output_content',
        'provider_used', 'model_used', 'temperature_used', 'tokens_used',
        'duration_ms', 'cache_hit', 'success', 'error_message'
    ]
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Execution Info', {
            'fields': ('prompt', 'success', 'cache_hit', 'created_at')
        }),
        ('Input', {
            'fields': ('input_variables', 'rendered_system_prompt', 'rendered_user_prompt')
        }),
        ('Output', {
            'fields': ('output_content', 'error_message')
        }),
        ('Configuration Used', {
            'fields': ('provider_used', 'model_used', 'temperature_used')
        }),
        ('Performance Metrics', {
            'fields': ('tokens_used', 'duration_ms')
        }),
        ('Analytics', {
            'fields': ('user_feedback_rating', 'validation_passed'),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        """Prevent manual creation of execution records"""
        return False

    def status_icon(self, obj):
        """Show status icon"""
        if obj.success:
            return format_html('<span style="color: green;">✓</span>')
        return format_html('<span style="color: red;">✗</span>')
    status_icon.short_description = 'Status'

