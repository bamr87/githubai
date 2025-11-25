"""Core models - merged from all apps"""
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    """Abstract base model with automatic timestamp tracking.

    Provides created_at and updated_at fields that are automatically managed
    by Django. All models in the application should inherit from this base class
    to ensure consistent timestamp tracking.

    Attributes:
        created_at (DateTimeField): Automatically set when the record is created.
            Indexed for efficient querying by creation time.
        updated_at (DateTimeField): Automatically updated whenever the record is saved.
            Useful for tracking last modification time.

    Example:
        >>> class MyModel(TimeStampedModel):
        ...     name = models.CharField(max_length=100)
        >>> obj = MyModel.objects.create(name="Test")
        >>> print(obj.created_at)  # Auto-populated
        2025-11-24 10:30:00+00:00
    """
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# ============================================================================
# Core Models
# ============================================================================

class AIProvider(TimeStampedModel):
    """Configuration and credentials for AI service providers.

    Stores provider-specific settings including API keys, base URLs, and default
    parameters for AI model interactions. Supports multiple providers like OpenAI,
    XAI (Grok), and others through a unified interface.

    Attributes:
        name (str): Unique provider identifier (e.g., 'openai', 'xai').
        display_name (str): Human-readable provider name for UI display.
        api_key (str): Encrypted API key for authentication. Check has_api_key property
            before using.
        base_url (str): API endpoint base URL.
        is_active (bool): Whether this provider is currently enabled. Indexed for
            efficient filtering.
        default_temperature (float): Default temperature setting (0.0-2.0) for response
            randomness. Lower values = more deterministic.
        default_max_tokens (int): Default maximum tokens for responses.
        description (str): Optional description of the provider.
        documentation_url (str): Optional link to provider documentation.

    Relationships:
        models (reverse): AIModel instances available from this provider.

    Example:
        >>> provider = AIProvider.objects.create(
        ...     name='openai',
        ...     display_name='OpenAI',
        ...     base_url='https://api.openai.com/v1',
        ...     api_key='sk-...'
        ... )
        >>> provider.has_api_key
        True
    """

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
    def has_api_key(self) -> bool:
        """Check if API key is configured for this provider.

        Returns:
            bool: True if api_key field is non-empty, False otherwise.

        Example:
            >>> provider = AIProvider(api_key='')
            >>> provider.has_api_key
            False
            >>> provider.api_key = 'sk-test123'
            >>> provider.has_api_key
            True
        """
        return bool(self.api_key)


class AIModel(TimeStampedModel):
    """Specific AI models available from providers with capabilities and pricing.

    Represents individual AI models (e.g., gpt-4o, grok-beta) with their technical
    specifications, capabilities, and pricing information. Each model belongs to
    a single provider and can be marked as the default for that provider.

    Attributes:
        provider (ForeignKey): The AIProvider that offers this model.
        name (str): Model identifier used in API calls (e.g., 'gpt-4o-mini').
        display_name (str): User-friendly model name for UI display.
        capabilities (list): List of capabilities like 'chat', 'embedding', 'vision'.
        max_tokens (int): Maximum number of tokens this model can generate.
        context_window (int): Total context window size (input + output tokens).
        supports_system_prompt (bool): Whether model accepts system prompts.
        supports_streaming (bool): Whether model supports streaming responses.
        input_price_per_million (Decimal): Cost per 1M input tokens in USD.
        output_price_per_million (Decimal): Cost per 1M output tokens in USD.
        is_active (bool): Whether this model is currently available.
        is_default (bool): Whether this is the default model for its provider.
        description (str): Optional detailed description.
        release_date (date): Optional model release date.
        deprecation_date (date): Optional planned deprecation date.

    Relationships:
        provider (FK): Parent AIProvider instance.
        cached_responses (reverse): AIResponse instances using this model.
        prompt_templates (reverse): PromptTemplate instances configured for this model.
        executions (reverse): PromptExecution instances that used this model.

    Example:
        >>> model = AIModel.objects.create(
        ...     provider=openai_provider,
        ...     name='gpt-4o-mini',
        ...     display_name='GPT-4o Mini',
        ...     max_tokens=16384,
        ...     context_window=128000,
        ...     is_default=True
        ... )
        >>> print(model.full_name)
        'openai:gpt-4o-mini'
    """

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
    def full_name(self) -> str:
        """Return fully qualified model name in provider:model format.

        Useful for logging and debugging to identify both the provider and model.

        Returns:
            str: Model identifier in 'provider:model' format.

        Example:
            >>> model = AIModel(provider__name='openai', name='gpt-4o')
            >>> model.full_name
            'openai:gpt-4o'
        """
        return f"{self.provider.name}:{self.name}"


class APILog(TimeStampedModel):
    """Comprehensive logging for all external API interactions.

    Records detailed information about API calls to external services including
    AI providers (OpenAI, XAI) and GitHub. Useful for debugging, monitoring,
    cost tracking, and performance analysis.

    Attributes:
        api_type (str): Type of API ('ai' or 'github').
        endpoint (str): Full API endpoint URL or path.
        method (str): HTTP method (GET, POST, PUT, DELETE, etc.).
        request_data (dict): Request payload as JSON.
        response_data (dict): Response data as JSON.
        status_code (int): HTTP response status code.
        error_message (str): Error message if request failed.
        duration_ms (int): Request duration in milliseconds.
        user_id (str): Optional identifier of the user who made the request.

    Meta:
        ordering: Newest logs first (by created_at descending).
        indexes: Efficient querying by api_type, status_code, and timestamp.

    Example:
        >>> log = APILog.objects.create(
        ...     api_type='ai',
        ...     endpoint='/v1/chat/completions',
        ...     method='POST',
        ...     status_code=200,
        ...     duration_ms=1250
        ... )
        >>> print(log)
        'AI - POST /v1/chat/completions [200]'
    """

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
    """Cache for AI API responses to reduce costs and improve performance.

    Stores AI responses keyed by a hash of the prompt, model, temperature, and
    provider. When identical prompts are requested again, the cached response
    is returned instead of making a new API call.

    Attributes:
        prompt_hash (str): SHA-256 hash of (provider|model|temp|system|user prompts).
            Unique index for fast lookups.
        system_prompt (str): The system instructions used in the prompt.
        user_prompt (str): The user message/query sent to the AI.
        response_content (str): The AI's complete response text.
        ai_model (ForeignKey): Optional reference to the AIModel used.
        model (str): Legacy field - model name string.
        provider (str): Legacy field - provider name string.
        temperature (float): Temperature setting used for this response.
        max_tokens (int): Max tokens setting used for this response.
        tokens_used (int): Optional actual token count consumed.
        cache_hit_count (int): Number of times this cached response was reused.

    Relationships:
        ai_model (FK): AIModel instance if using database configuration.

    Example:
        >>> from hashlib import sha256
        >>> prompt_text = "openai|gpt-4o|0.2|You are helpful|Hello"
        >>> hash_val = sha256(prompt_text.encode()).hexdigest()
        >>> cached = AIResponse.objects.create(
        ...     prompt_hash=hash_val,
        ...     system_prompt="You are helpful",
        ...     user_prompt="Hello",
        ...     response_content="Hi there!",
        ...     provider='openai',
        ...     model='gpt-4o'
        ... )
        >>> cached.increment_cache_hit()
        >>> cached.cache_hit_count
        1
    """

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

    def increment_cache_hit(self) -> None:
        """Increment the cache hit counter atomically.

        Called whenever this cached response is reused instead of making a new
        API call. Uses update_fields for efficient database updates.

        Example:
            >>> response = AIResponse.objects.get(prompt_hash='abc123...')
            >>> response.cache_hit_count
            0
            >>> response.increment_cache_hit()
            >>> response.cache_hit_count
            1
        """
        self.cache_hit_count += 1
        self.save(update_fields=['cache_hit_count'])


# ============================================================================
# Issues Models
# ============================================================================

class IssueTemplate(TimeStampedModel):
    """Reusable templates for AI-generated GitHub issues.

    Templates define structure and AI instructions for generating specific types
    of GitHub issues. Each template includes a prompt for the AI, a Markdown body
    structure, and configuration for labels and file inclusions.

    Attributes:
        name (str): Unique template identifier (e.g., 'README_update.md').
        about (str): Description of the template's purpose and use case.
        title_prefix (str): Prefix added to generated issue titles.
        labels (list): List of label strings to apply to generated issues.
        prompt (str): AI instructions for content generation.
        template_body (str): Markdown structure/format for the issue body.
        include_files (list): List of file paths to include as context.
        is_active (bool): Whether this template is currently available.

    Relationships:
        issues (reverse): Issue instances created using this template.

    Example:
        >>> template = IssueTemplate.objects.create(
        ...     name='bug_report.md',
        ...     about='Template for bug reports',
        ...     title_prefix='[Bug]: ',
        ...     labels=['bug', 'needs-triage'],
        ...     prompt='Analyze the bug and create a detailed report',
        ...     template_body='## Bug Description\n\n...',
        ...     include_files=['README.md', 'CHANGELOG.md']
        ... )
    """
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
    """GitHub issues tracked in the database with AI generation metadata.

    Represents GitHub issues with full tracking of AI-generated content, parent-child
    relationships, and associated templates. Supports various issue types including
    features, bugs, README updates, and sub-issues.

    Attributes:
        github_issue_number (int): The issue number from GitHub (indexed).
        github_repo (str): Repository in 'owner/repo' format.
        title (str): Issue title (max 500 chars).
        body (str): Full issue body in Markdown.
        issue_type (str): Type of issue - one of ISSUE_TYPES choices.
        labels (list): List of GitHub labels applied to this issue.
        state (str): Issue state ('open', 'closed', etc.).
        parent_issue (ForeignKey): Optional parent issue for sub-issues.
        template (ForeignKey): Optional template used to generate this issue.
        ai_generated (bool): Whether this issue was generated by AI.
        ai_prompt_used (str): Optional prompt that was sent to the AI.
        ai_response (str): Optional raw AI response before formatting.
        html_url (str): Direct link to the GitHub issue.

    Relationships:
        parent_issue (FK): Parent Issue instance for hierarchical issues.
        template (FK): IssueTemplate used for generation.
        sub_issues (reverse): Child Issue instances.
        file_references (reverse): IssueFileReference instances.

    Meta:
        unique_together: Each (repo, issue_number) combination is unique.
        ordering: Newest issues first.

    Example:
        >>> issue = Issue.objects.create(
        ...     github_repo='owner/repo',
        ...     github_issue_number=42,
        ...     title='Fix login bug',
        ...     body='Users cannot log in when...',
        ...     issue_type='bug',
        ...     labels=['bug', 'priority-high'],
        ...     ai_generated=True
        ... )
        >>> print(issue.full_issue_identifier)
        'owner/repo#42'
    """

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
    def full_issue_identifier(self) -> str:
        """Return fully qualified GitHub issue identifier.

        Combines repository and issue number in standard GitHub format,
        useful for logging, URLs, and cross-references.

        Returns:
            str: Issue identifier in 'owner/repo#number' format.

        Example:
            >>> issue = Issue(github_repo='bamr87/githubai', github_issue_number=123)
            >>> issue.full_issue_identifier
            'bamr87/githubai#123'
        """
        return f"{self.github_repo}#{self.github_issue_number}"


class IssueFileReference(TimeStampedModel):
    """Files referenced or included as context when generating issues.

    Tracks which repository files were used as context when generating an issue,
    storing both the file path and optionally the file content at that point in time.
    Useful for understanding what information the AI had access to.

    Attributes:
        issue (ForeignKey): The Issue this file reference belongs to.
        file_path (str): Repository-relative path to the file.
        content (str): Optional snapshot of file content at generation time.
        content_hash (str): Optional SHA-256 hash of the content.

    Relationships:
        issue (FK): Parent Issue instance.

    Meta:
        unique_together: Each (issue, file_path) combination is unique.
        ordering: Alphabetical by file path.

    Example:
        >>> ref = IssueFileReference.objects.create(
        ...     issue=issue,
        ...     file_path='src/main.py',
        ...     content='def main():\n    pass',
        ...     content_hash='abc123...'
        ... )
        >>> print(ref)
        '#42: Fix login bug -> src/main.py'
    """
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
    """Parsed documentation extracted from source code files.

    Stores extracted docstrings and comments from Python source files, along with
    generated Markdown documentation. Used for auto-generating API documentation
    and tracking documentation changes over time.

    Attributes:
        file_path (str): Unique path to the source file (relative to project root).
        language (str): Programming language (default: 'python').
        docstrings (dict): Extracted docstrings keyed by function/class name.
        comments (list): List of extracted inline comments.
        markdown_content (str): Generated Markdown documentation.
        content_hash (str): SHA-256 hash for change detection (indexed).

    Meta:
        ordering: Alphabetical by file path.

    Example:
        >>> doc = DocumentationFile.objects.create(
        ...     file_path='src/services/ai_service.py',
        ...     language='python',
        ...     docstrings={'AIService': 'Service for AI interactions...'},
        ...     comments=['TODO: Add rate limiting'],
        ...     markdown_content='# AIService\n\nService for AI interactions...',
        ...     content_hash='def456...'
        ... )
        >>> print(doc)
        'src/services/ai_service.py'
    """

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
    """Semantic versioning history for the application.

    Tracks version numbers, bumps, and associated git commits/tags. Follows
    semantic versioning (semver) with major.minor.patch format. Each version
    can be associated with a git commit and tag.

    Attributes:
        version_number (str): Full version string (e.g., '1.2.3'), unique and indexed.
        major (int): Major version number (breaking changes).
        minor (int): Minor version number (new features, backward compatible).
        patch (int): Patch version number (bug fixes).
        bump_type (str): Type of version bump that created this version.
        commit_sha (str): Git commit SHA associated with this version.
        commit_message (str): Commit message from the version bump.
        git_tag (str): Git tag name (e.g., 'v1.2.3').
        is_published (bool): Whether this version has been released.
        published_at (datetime): When this version was published.

    Meta:
        ordering: Newest versions first (by created_at).
        indexes: Efficient sorting by semantic version components.

    Example:
        >>> version = Version.objects.create(
        ...     version_number='1.2.3',
        ...     major=1, minor=2, patch=3,
        ...     bump_type='minor',
        ...     git_tag='v1.2.3'
        ... )
        >>> print(version.semver)
        '1.2.3'
        >>> latest = Version.get_latest()
    """

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
    def get_latest(cls) -> 'Version':
        """Get the most recent version record.

        Returns:
            Version: The latest Version instance (ordered by created_at desc).

        Example:
            >>> latest = Version.get_latest()
            >>> print(f"Current version: {latest.version_number}")
            'Current version: 1.2.3'
        """
        return cls.objects.first()

    @property
    def semver(self) -> str:
        """Return semantic version string in major.minor.patch format.

        Returns:
            str: Semantic version string.

        Example:
            >>> v = Version(major=1, minor=2, patch=3)
            >>> v.semver
            '1.2.3'
        """
        return f"{self.major}.{self.minor}.{self.patch}"


# ============================================================================
# Prompt Management Models
# ============================================================================

class PromptTemplate(TimeStampedModel):
    """Versioned templates for AI prompts with Jinja2 variable support.

    Manages reusable AI prompt templates with system instructions and user prompt
    templates. Supports Jinja2 templating for dynamic variable substitution,
    versioning for A/B testing and improvements, and usage tracking for analytics.

    Attributes:
        name (str): Unique template identifier (indexed).
        category (str): Template category for organization (indexed).
        description (str): Detailed description of template purpose.
        system_prompt (str): Static system-level instructions for the AI.
        user_prompt_template (str): User prompt with Jinja2 variables
            (e.g., "{{ repo }}", "{{ issue_number }}").
        ai_model (ForeignKey): Optional specific AIModel to use.
        model (str): Legacy model name (for backward compatibility).
        provider (str): Legacy provider name or 'auto' for default.
        temperature (float): Response randomness (0.0-2.0).
        max_tokens (int): Maximum response length in tokens.
        version_number (int): Version number for this template.
        parent_version (ForeignKey): Previous version for tracking evolution.
        is_active (bool): Whether this template is currently usable (indexed).
        usage_count (int): Number of times this template has been executed.
        last_used_at (datetime): Most recent execution timestamp.

    Relationships:
        ai_model (FK): Preferred AIModel for this template.
        parent_version (FK): Previous version of this template.
        versions (reverse): Newer versions of this template.
        schemas (reverse): PromptSchema instances for output validation.
        datasets (reverse): PromptDataset instances for testing.
        executions (reverse): PromptExecution instances from usage.

    Meta:
        ordering: By category, name, and version (newest first).

    Example:
        >>> template = PromptTemplate.objects.create(
        ...     name='issue_analyzer',
        ...     category='auto_issue',
        ...     system_prompt='You are a code analyzer',
        ...     user_prompt_template='Analyze {{ repo }} issue #{{ issue_number }}',
        ...     version_number=1
        ... )
        >>> template.increment_usage()
        >>> template.usage_count
        1
    """

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

    def increment_usage(self) -> None:
        """Increment usage counter and update last used timestamp.

        Called automatically whenever this template is executed. Uses update_fields
        for efficient database updates without triggering full save.

        Example:
            >>> template = PromptTemplate.objects.get(name='issue_analyzer')
            >>> template.usage_count
            5
            >>> template.increment_usage()
            >>> template.usage_count
            6
            >>> template.last_used_at
            2025-11-24 15:30:00+00:00
        """
        self.usage_count += 1
        self.last_used_at = timezone.now()
        self.save(update_fields=['usage_count', 'last_used_at'])


class PromptSchema(TimeStampedModel):
    """Output validation schemas for prompt responses.

    Defines expected output formats and validation rules for AI responses generated
    from prompts. Supports JSON Schema validation, regex patterns, or custom
    validation logic to ensure AI outputs meet requirements.

    Attributes:
        prompt (ForeignKey): The PromptTemplate this schema validates.
        schema_type (str): Type of validation - 'json_schema', 'regex', or 'custom'.
        schema_definition (dict): The validation rules (JSON Schema object, regex
            pattern, or custom validation config).
        validation_enabled (bool): Whether to actively validate outputs.
        description (str): Optional description of validation purpose.

    Relationships:
        prompt (FK): Parent PromptTemplate instance.

    Example:
        >>> schema = PromptSchema.objects.create(
        ...     prompt=template,
        ...     schema_type='json_schema',
        ...     schema_definition={
        ...         'type': 'object',
        ...         'properties': {'title': {'type': 'string'}},
        ...         'required': ['title']
        ...     },
        ...     validation_enabled=True
        ... )
    """

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
    """Test datasets for evaluating and improving prompt performance.

    Collections of test cases for systematically evaluating prompt templates.
    Each dataset contains multiple entries with input variables and expected
    outputs, enabling A/B testing, regression testing, and quality assurance.

    Attributes:
        prompt (ForeignKey): The PromptTemplate this dataset tests.
        name (str): Dataset name (unique per prompt).
        description (str): Optional description of dataset purpose and coverage.
        is_active (bool): Whether this dataset is currently in use.

    Relationships:
        prompt (FK): Parent PromptTemplate instance.
        entries (reverse): PromptDatasetEntry instances in this dataset.

    Meta:
        unique_together: Each (prompt, name) combination is unique.

    Example:
        >>> dataset = PromptDataset.objects.create(
        ...     prompt=template,
        ...     name='edge_cases',
        ...     description='Edge cases and boundary conditions',
        ...     is_active=True
        ... )
        >>> dataset.entry_count
        15
    """

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
    def entry_count(self) -> int:
        """Return count of test entries in this dataset.

        Returns:
            int: Number of PromptDatasetEntry instances.

        Example:
            >>> dataset.entry_count
            15
        """
        return self.entries.count()


class PromptDatasetEntry(TimeStampedModel):
    """Individual test cases for prompt evaluation.

    Represents a single test case within a dataset, including input variables
    to render the prompt template and optional expected output patterns for
    validation. Useful for regression testing and quality benchmarking.

    Attributes:
        dataset (ForeignKey): The PromptDataset this entry belongs to.
        input_variables (dict): Variables to substitute in the prompt template
            (e.g., {"repo": "owner/repo", "issue_number": 123}).
        expected_output_pattern (str): Optional regex pattern or keywords to
            validate the AI's output against.
        tags (list): Optional tags for filtering (e.g., ['edge_case', 'regression']).
        notes (str): Optional notes about this test case.

    Relationships:
        dataset (FK): Parent PromptDataset instance.

    Meta:
        verbose_name_plural: 'Prompt Dataset Entries'

    Example:
        >>> entry = PromptDatasetEntry.objects.create(
        ...     dataset=dataset,
        ...     input_variables={'repo': 'owner/repo', 'issue': 42},
        ...     expected_output_pattern='.*bug.*',
        ...     tags=['regression', 'bug_report'],
        ...     notes='Test case for issue #42 bug report generation'
        ... )
    """

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
    """Detailed execution history and analytics for prompt templates.

    Records every execution of a prompt template including inputs, outputs,
    performance metrics, and success status. Essential for monitoring prompt
    quality, tracking costs, analyzing cache hit rates, and gathering user
    feedback for continuous improvement.

    Attributes:
        prompt (ForeignKey): The PromptTemplate that was executed.
        input_variables (dict): Variables used to render the template.
        rendered_system_prompt (str): Final system prompt sent to AI.
        rendered_user_prompt (str): Final user prompt sent to AI.
        output_content (str): The AI's complete response.
        ai_model (ForeignKey): AIModel used for this execution.
        provider_used (str): Provider name (e.g., 'openai', 'xai').
        model_used (str): Model identifier used.
        temperature_used (float): Temperature parameter used.
        tokens_used (int): Optional total tokens consumed.
        duration_ms (int): Optional execution time in milliseconds.
        cache_hit (bool): Whether response came from cache.
        success (bool): Whether execution completed successfully.
        error_message (str): Optional error details if failed.
        user_feedback_rating (int): Optional 1-5 star rating from user.
        validation_passed (bool): Optional whether output passed schema validation.

    Relationships:
        prompt (FK): Parent PromptTemplate instance.
        ai_model (FK): AIModel used for execution.

    Meta:
        ordering: Newest executions first.
        indexes: Efficient querying by prompt, success status, and cache hits.

    Example:
        >>> execution = PromptExecution.objects.create(
        ...     prompt=template,
        ...     input_variables={'repo': 'owner/repo'},
        ...     rendered_system_prompt='You are helpful',
        ...     rendered_user_prompt='Analyze owner/repo',
        ...     output_content='Analysis complete...',
        ...     provider_used='openai',
        ...     model_used='gpt-4o',
        ...     temperature_used=0.2,
        ...     tokens_used=150,
        ...     duration_ms=1200,
        ...     cache_hit=False,
        ...     success=True
        ... )
    """

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
