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
    model = models.CharField(max_length=50, default='gpt-4o-mini')
    temperature = models.FloatField(default=0.2)
    max_tokens = models.IntegerField(default=2500)
    tokens_used = models.IntegerField(null=True, blank=True)
    cache_hit_count = models.IntegerField(default=0)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['prompt_hash']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"AI Response [{self.model}] - {self.prompt_hash[:8]}"

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
