"""Core models - merged from all apps"""
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    """Abstract base model with created and updated timestamps"""
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# ============================================================================
# Core Models
# ============================================================================

class AIProvider(TimeStampedModel):
    """AI service providers and their configuration"""

    name = models.CharField(max_length=50, unique=True, db_index=True, help_text='Provider name (e.g., openai, xai)')
    display_name = models.CharField(max_length=100, help_text='Human-readable name (e.g., OpenAI, XAI)')
    api_key = models.CharField(max_length=500, blank=True, help_text='API key (encrypted in production)')
    base_url = models.URLField(max_length=500, help_text='API base URL')
    is_active = models.BooleanField(default=True, db_index=True)

    # Optional settings
    default_temperature = models.FloatField(default=0.2, help_text='Default temperature for this provider')
    default_max_tokens = models.IntegerField(default=2500, help_text='Default max tokens for this provider')

    # Metadata
    description = models.TextField(blank=True)
    documentation_url = models.URLField(max_length=500, blank=True)

    class Meta:
        ordering = ['display_name']

    def __str__(self):
        return self.display_name

    @property
    def has_api_key(self):
        """Check if API key is configured"""
        return bool(self.api_key)


class AIModel(TimeStampedModel):
    """Available AI models per provider"""

    CAPABILITY_CHOICES = [
        ('chat', 'Chat Completion'),
        ('embedding', 'Text Embedding'),
        ('image', 'Image Generation'),
        ('vision', 'Vision/Image Understanding'),
        ('code', 'Code Generation'),
    ]

    provider = models.ForeignKey(AIProvider, on_delete=models.CASCADE, related_name='models')
    name = models.CharField(max_length=100, db_index=True, help_text='Model identifier (e.g., gpt-4o, grok-beta)')
    display_name = models.CharField(max_length=150, help_text='Human-readable name')

    # Capabilities
    capabilities = models.JSONField(default=list, help_text='List of capabilities (chat, embedding, etc.)')

    # Limits and configuration
    max_tokens = models.IntegerField(help_text='Maximum tokens this model supports')
    context_window = models.IntegerField(help_text='Context window size')
    supports_system_prompt = models.BooleanField(default=True)
    supports_streaming = models.BooleanField(default=True)

    # Pricing (per 1M tokens)
    input_price_per_million = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Input token price per 1M tokens (USD)'
    )
    output_price_per_million = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Output token price per 1M tokens (USD)'
    )

    # Status
    is_active = models.BooleanField(default=True, db_index=True)
    is_default = models.BooleanField(default=False, help_text='Default model for this provider')

    # Metadata
    description = models.TextField(blank=True)
    release_date = models.DateField(null=True, blank=True)
    deprecation_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['provider', '-is_default', 'display_name']
        unique_together = [['provider', 'name']]
        indexes = [
            models.Index(fields=['provider', 'is_active']),
            models.Index(fields=['is_default', 'is_active']),
        ]

    def __str__(self):
        return f"{self.provider.display_name} - {self.display_name}"

    @property
    def full_name(self):
        """Return provider:model format"""
        return f"{self.provider.name}:{self.name}"


class APILog(TimeStampedModel):
    """Log all external API calls"""

    API_TYPES = [
        ('ai', 'AI'),
        ('github', 'GitHub'),
    ]

    api_type = models.CharField(max_length=20, choices=API_TYPES, db_index=True)
    endpoint = models.CharField(max_length=500)
    method = models.CharField(max_length=10, default='GET')
    request_data = models.JSONField(null=True, blank=True)
    response_data = models.JSONField(null=True, blank=True)
    status_code = models.IntegerField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    duration_ms = models.IntegerField(null=True, blank=True, help_text='Request duration in milliseconds')
    user_id = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['api_type', '-created_at']),
            models.Index(fields=['status_code', '-created_at']),
        ]

    def __str__(self):
        return f"{self.api_type.upper()} - {self.method} {self.endpoint} [{self.status_code}]"


# ============================================================================
# AI Services Models
# ============================================================================

class AIResponse(TimeStampedModel):
    """Cache AI responses to avoid duplicate API calls"""

    prompt_hash = models.CharField(max_length=64, unique=True, db_index=True)
    system_prompt = models.TextField()
    user_prompt = models.TextField()
    response_content = models.TextField()

    # New: Reference to AIModel (optional for backward compatibility)
    ai_model = models.ForeignKey(
        'AIModel',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cached_responses',
        help_text='AI model used for this response'
    )

    # Legacy fields (kept for backward compatibility)
    model = models.CharField(max_length=50, default='gpt-4o-mini')
    provider = models.CharField(max_length=20, default='openai', help_text='AI provider used (openai, xai, etc.)')
    temperature = models.FloatField(default=0.2)
    max_tokens = models.IntegerField(default=2500)
    tokens_used = models.IntegerField(null=True, blank=True)
    cache_hit_count = models.IntegerField(default=0)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['prompt_hash']),
            models.Index(fields=['provider', '-created_at']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"AI Response [{self.provider}:{self.model}] - {self.prompt_hash[:8]}"

    def increment_cache_hit(self):
        """Increment the cache hit counter"""
        self.cache_hit_count += 1
        self.save(update_fields=['cache_hit_count'])


# ============================================================================
# Issues Models
# ============================================================================

class IssueTemplate(TimeStampedModel):
    """Templates for generating issues"""
    name = models.CharField(max_length=200, unique=True)
    about = models.TextField(help_text='Description of what this template is for')
    title_prefix = models.CharField(max_length=100, default='[Generated]: ')
    labels = models.JSONField(default=list, help_text='List of labels to apply')
    prompt = models.TextField(help_text='AI instructions for generating content')
    template_body = models.TextField(help_text='Markdown template structure')
    include_files = models.JSONField(default=list, help_text='Files to include as context')
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Issue(TimeStampedModel):
    """GitHub issues tracked in database"""

    ISSUE_TYPES = [
        ('feature', 'Feature Request'),
        ('bug', 'Bug Report'),
        ('readme', 'README Update'),
        ('sub_issue', 'Sub-Issue'),
        ('other', 'Other'),
    ]

    github_issue_number = models.IntegerField(db_index=True)
    github_repo = models.CharField(max_length=200, default='bamr87/githubai')
    title = models.CharField(max_length=500)
    body = models.TextField()
    issue_type = models.CharField(max_length=20, choices=ISSUE_TYPES, default='other')
    labels = models.JSONField(default=list)
    state = models.CharField(max_length=20, default='open')

    # Relationships
    parent_issue = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sub_issues'
    )
    template = models.ForeignKey(
        IssueTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='issues'
    )

    # AI Generation tracking
    ai_generated = models.BooleanField(default=False)
    ai_prompt_used = models.TextField(null=True, blank=True)
    ai_response = models.TextField(null=True, blank=True)

    # GitHub URLs
    html_url = models.URLField(max_length=500, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = [['github_repo', 'github_issue_number']]
        indexes = [
            models.Index(fields=['github_repo', 'github_issue_number']),
            models.Index(fields=['issue_type', '-created_at']),
            models.Index(fields=['state', '-created_at']),
        ]

    def __str__(self):
        return f"#{self.github_issue_number}: {self.title}"

    @property
    def full_issue_identifier(self):
        """Return full GitHub issue identifier"""
        return f"{self.github_repo}#{self.github_issue_number}"


class IssueFileReference(TimeStampedModel):
    """Track files referenced in issues"""
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='file_references')
    file_path = models.CharField(max_length=500)
    content = models.TextField(null=True, blank=True)
    content_hash = models.CharField(max_length=64, null=True, blank=True)

    class Meta:
        ordering = ['file_path']
        unique_together = [['issue', 'file_path']]

    def __str__(self):
        return f"{self.issue} -> {self.file_path}"


# ============================================================================
# Documentation Models
# ============================================================================

class ChangelogEntry(TimeStampedModel):
    """Track changelog entries"""

    ENTRY_TYPES = [
        ('commit', 'Commit'),
        ('pr', 'Pull Request'),
        ('manual', 'Manual'),
    ]

    entry_type = models.CharField(max_length=20, choices=ENTRY_TYPES, default='commit')
    commit_sha = models.CharField(max_length=40, null=True, blank=True, db_index=True)
    pr_number = models.IntegerField(null=True, blank=True, db_index=True)
    commit_message = models.TextField(null=True, blank=True)
    diff_summary = models.TextField(null=True, blank=True)
    ai_generated_content = models.TextField()
    file_path = models.CharField(max_length=500, default='CHANGELOG_AI.md')

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['entry_type', '-created_at']),
            models.Index(fields=['commit_sha']),
        ]
        verbose_name_plural = 'Changelog Entries'

    def __str__(self):
        if self.commit_sha:
            return f"Changelog: {self.commit_sha[:7]}"
        elif self.pr_number:
            return f"Changelog: PR #{self.pr_number}"
        return f"Changelog: {self.id}"


class DocumentationFile(TimeStampedModel):
    """Track parsed documentation from code files"""

    file_path = models.CharField(max_length=500, unique=True)
    language = models.CharField(max_length=50, default='python')
    docstrings = models.JSONField(default=dict, help_text='Extracted docstrings')
    comments = models.JSONField(default=list, help_text='Extracted comments')
    markdown_content = models.TextField(help_text='Generated markdown documentation')
    content_hash = models.CharField(max_length=64, db_index=True)

    class Meta:
        ordering = ['file_path']

    def __str__(self):
        return self.file_path


# ============================================================================
# Versioning Models
# ============================================================================

class Version(TimeStampedModel):
    """Track version history"""

    BUMP_TYPES = [
        ('major', 'Major'),
        ('minor', 'Minor'),
        ('patch', 'Patch'),
    ]

    version_number = models.CharField(max_length=20, unique=True, db_index=True)
    major = models.IntegerField()
    minor = models.IntegerField()
    patch = models.IntegerField()
    bump_type = models.CharField(max_length=10, choices=BUMP_TYPES)
    commit_sha = models.CharField(max_length=40, null=True, blank=True)
    commit_message = models.TextField(null=True, blank=True)
    git_tag = models.CharField(max_length=50, null=True, blank=True)
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-major', '-minor', '-patch']),
        ]

    def __str__(self):
        return f"v{self.version_number}"

    @classmethod
    def get_latest(cls):
        """Get the latest version"""
        return cls.objects.first()

    @property
    def semver(self):
        """Return semantic version string"""
        return f"{self.major}.{self.minor}.{self.patch}"


# ============================================================================
# Prompt Management Models
# ============================================================================

class PromptTemplate(TimeStampedModel):
    """Manage AI prompt templates with versioning and configuration"""

    CATEGORY_CHOICES = [
        ('chat', 'Chat'),
        ('auto_issue', 'Auto Issue'),
        ('sub_issue', 'Sub-Issue'),
        ('readme_update', 'README Update'),
        ('documentation', 'Documentation'),
        ('changelog', 'Changelog'),
        ('feedback_issue', 'Feedback Issue'),
        ('other', 'Other'),
    ]

    PROVIDER_CHOICES = [
        ('openai', 'OpenAI'),
        ('xai', 'XAI (Grok)'),
        ('auto', 'Auto (Use Default)'),
    ]

    # Identification
    name = models.CharField(max_length=200, unique=True, db_index=True)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, db_index=True)
    description = models.TextField(help_text='Description of what this prompt does')

    # Prompt Content
    system_prompt = models.TextField(help_text='System instructions for AI')
    user_prompt_template = models.TextField(
        help_text='User prompt template with Jinja2 variables (e.g., {{ repo }}, {{ issue_number }})'
    )

    # Model Configuration
    ai_model = models.ForeignKey(
        'AIModel',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='prompt_templates',
        help_text='AI model to use for this prompt'
    )

    # Legacy fields (kept for backward compatibility)
    model = models.CharField(max_length=50, default='gpt-4o-mini')
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES, default='auto')
    temperature = models.FloatField(default=0.2)
    max_tokens = models.IntegerField(default=2500)

    # Versioning
    version_number = models.IntegerField(default=1, help_text='Version number for this prompt')
    parent_version = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='versions',
        help_text='Previous version of this prompt'
    )

    # Status
    is_active = models.BooleanField(default=True, db_index=True)

    # Usage tracking
    usage_count = models.IntegerField(default=0, help_text='Number of times this prompt has been used')
    last_used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['category', 'name', '-version_number']
        indexes = [
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['name', '-version_number']),
        ]

    def __str__(self):
        return f"{self.name} (v{self.version_number})"

    def increment_usage(self):
        """Increment usage counter and update last used timestamp"""
        self.usage_count += 1
        self.last_used_at = timezone.now()
        self.save(update_fields=['usage_count', 'last_used_at'])


class PromptSchema(TimeStampedModel):
    """Define expected output schemas for prompt validation"""

    SCHEMA_TYPE_CHOICES = [
        ('json_schema', 'JSON Schema'),
        ('regex', 'Regular Expression'),
        ('custom', 'Custom Validation'),
    ]

    prompt = models.ForeignKey(
        PromptTemplate,
        on_delete=models.CASCADE,
        related_name='schemas'
    )
    schema_type = models.CharField(max_length=20, choices=SCHEMA_TYPE_CHOICES, default='json_schema')
    schema_definition = models.JSONField(
        help_text='JSON Schema definition or validation rules'
    )
    validation_enabled = models.BooleanField(default=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['prompt', '-created_at']

    def __str__(self):
        return f"Schema for {self.prompt.name} ({self.schema_type})"


class PromptDataset(TimeStampedModel):
    """Test datasets for evaluating prompt performance"""

    prompt = models.ForeignKey(
        PromptTemplate,
        on_delete=models.CASCADE,
        related_name='datasets'
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['prompt', 'name']
        unique_together = [['prompt', 'name']]

    def __str__(self):
        return f"{self.prompt.name} - {self.name}"

    @property
    def entry_count(self):
        """Return count of test entries"""
        return self.entries.count()


class PromptDatasetEntry(TimeStampedModel):
    """Individual test cases within a dataset"""

    dataset = models.ForeignKey(
        PromptDataset,
        on_delete=models.CASCADE,
        related_name='entries'
    )
    input_variables = models.JSONField(
        help_text='Variables to render in the prompt template (e.g., {"repo": "owner/repo", "issue_number": 123})'
    )
    expected_output_pattern = models.TextField(
        blank=True,
        help_text='Expected output pattern or keywords to validate against'
    )
    tags = models.JSONField(
        default=list,
        help_text='Tags for filtering test cases (e.g., ["edge_case", "regression"])'
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['dataset', 'created_at']
        verbose_name_plural = 'Prompt Dataset Entries'

    def __str__(self):
        return f"{self.dataset.name} - Entry {self.id}"


class PromptExecution(TimeStampedModel):
    """Track prompt execution history and performance"""

    prompt = models.ForeignKey(
        PromptTemplate,
        on_delete=models.CASCADE,
        related_name='executions'
    )

    # Input/Output
    input_variables = models.JSONField(
        null=True,
        blank=True,
        help_text='Variables used to render the prompt'
    )
    rendered_system_prompt = models.TextField()
    rendered_user_prompt = models.TextField()
    output_content = models.TextField()

    # Execution Details
    ai_model = models.ForeignKey(
        'AIModel',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='executions',
        help_text='AI model used for this execution'
    )
    provider_used = models.CharField(max_length=20)
    model_used = models.CharField(max_length=50)
    temperature_used = models.FloatField()
    tokens_used = models.IntegerField(null=True, blank=True)
    duration_ms = models.IntegerField(null=True, blank=True)
    cache_hit = models.BooleanField(default=False)

    # Status
    success = models.BooleanField(default=True)
    error_message = models.TextField(null=True, blank=True)

    # Analytics
    user_feedback_rating = models.IntegerField(
        null=True,
        blank=True,
        help_text='User rating 1-5 stars'
    )
    validation_passed = models.BooleanField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['prompt', '-created_at']),
            models.Index(fields=['success', '-created_at']),
            models.Index(fields=['cache_hit', '-created_at']),
        ]

    def __str__(self):
        status = "✓" if self.success else "✗"
        return f"{status} {self.prompt.name} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
