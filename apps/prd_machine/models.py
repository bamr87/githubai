"""PRD MACHINE models - state, versions, and events for PRD automation."""
from django.db import models
from django.utils import timezone
from core.models import TimeStampedModel


class PRDState(TimeStampedModel):
    """Current state of a PRD document.

    Tracks the PRD.md file state, version, and automation configuration.

    Attributes:
        repo: GitHub repository (owner/repo format)
        file_path: Path to PRD.md in the repo
        content: Current PRD content (Markdown)
        content_hash: Hash of content for change detection
        version: Semantic version of the PRD
        is_locked: Whether PRD is locked from human edits (zero-touch mode)
        last_distilled_at: Last time PRD was distilled from repo signals
        last_synced_at: Last time PRD was synced with GitHub
        auto_evolve: Whether to auto-evolve PRD on repo changes
        slack_webhook: Optional Slack webhook for notifications
    """

    repo = models.CharField(max_length=255, db_index=True, help_text='GitHub repository (owner/repo)')
    file_path = models.CharField(max_length=500, default='PRD.md', help_text='Path to PRD file in repo')
    content = models.TextField(blank=True, help_text='Current PRD content (Markdown)')
    content_hash = models.CharField(max_length=64, blank=True, help_text='SHA256 hash of content')
    version = models.CharField(max_length=50, default='1.0.0', help_text='PRD version')

    # Automation settings
    is_locked = models.BooleanField(default=False, db_index=True, help_text='Zero-touch mode - no human edits')
    last_distilled_at = models.DateTimeField(null=True, blank=True, help_text='Last distillation time')
    last_synced_at = models.DateTimeField(null=True, blank=True, help_text='Last GitHub sync time')
    auto_evolve = models.BooleanField(default=True, help_text='Auto-evolve on repo changes')

    # Notifications
    slack_webhook = models.URLField(max_length=500, blank=True, help_text='Slack webhook for alerts')

    class Meta:
        verbose_name = 'PRD State'
        verbose_name_plural = 'PRD States'
        unique_together = ['repo', 'file_path']
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.repo}:{self.file_path} v{self.version}"

    def save(self, *args, **kwargs):
        """Auto-compute content hash on save."""
        import hashlib
        if self.content:
            self.content_hash = hashlib.sha256(self.content.encode()).hexdigest()
        super().save(*args, **kwargs)


class PRDVersion(TimeStampedModel):
    """Version history of PRD documents.

    Each edit/evolution creates a new version for audit trail.

    Attributes:
        prd_state: Parent PRD state
        version: Version number
        content: PRD content at this version
        content_hash: Hash for deduplication
        change_summary: AI-generated summary of changes
        trigger_type: What triggered this version
        trigger_ref: Reference to trigger (commit SHA, issue #, etc.)
        is_human_edit: Whether this was a human edit vs auto-generated
        reverted_to: If this version was a revert, which version
    """

    TRIGGER_TYPES = [
        ('initial', 'Initial Generation'),
        ('commit', 'Git Commit'),
        ('pr_merge', 'PR Merge'),
        ('issue_created', 'Issue Created'),
        ('issue_closed', 'Issue Closed'),
        ('manual_sync', 'Manual Sync'),
        ('scheduled', 'Scheduled Distillation'),
        ('human_edit', 'Human Edit'),
        ('revert', 'Revert'),
        ('export', 'Export to Issues'),
    ]

    prd_state = models.ForeignKey(PRDState, on_delete=models.CASCADE, related_name='versions')
    version = models.CharField(max_length=50, help_text='Version number')
    content = models.TextField(help_text='PRD content at this version')
    content_hash = models.CharField(max_length=64, help_text='SHA256 hash')
    change_summary = models.TextField(blank=True, help_text='AI-generated change summary')

    # Trigger tracking
    trigger_type = models.CharField(max_length=20, choices=TRIGGER_TYPES, db_index=True)
    trigger_ref = models.CharField(max_length=255, blank=True, help_text='Commit SHA, issue #, etc.')
    is_human_edit = models.BooleanField(default=False, db_index=True)
    reverted_to = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = 'PRD Version'
        verbose_name_plural = 'PRD Versions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['prd_state', '-created_at']),
            models.Index(fields=['trigger_type', '-created_at']),
        ]

    def __str__(self):
        return f"{self.prd_state.repo} v{self.version} ({self.trigger_type})"


class PRDEvent(TimeStampedModel):
    """Events that trigger PRD evolution.

    Log of all repo signals that may trigger PRD updates.

    Attributes:
        prd_state: Related PRD state
        event_type: Type of GitHub event
        event_data: JSON payload from webhook/API
        processed: Whether event has been processed
        processed_at: When event was processed
        result: Result of processing (success/error message)
    """

    EVENT_TYPES = [
        ('push', 'Push to Branch'),
        ('pull_request', 'Pull Request'),
        ('issues', 'Issue Event'),
        ('issue_comment', 'Issue Comment'),
        ('release', 'Release'),
        ('workflow_run', 'Workflow Run'),
        ('manual', 'Manual Trigger'),
    ]

    prd_state = models.ForeignKey(PRDState, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=30, choices=EVENT_TYPES, db_index=True)
    event_data = models.JSONField(default=dict, help_text='Event payload')

    # Processing status
    processed = models.BooleanField(default=False, db_index=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    result = models.TextField(blank=True, help_text='Processing result or error')

    class Meta:
        verbose_name = 'PRD Event'
        verbose_name_plural = 'PRD Events'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['processed', '-created_at']),
            models.Index(fields=['event_type', 'processed']),
        ]

    def __str__(self):
        status = "✓" if self.processed else "⏳"
        return f"{status} {self.event_type} for {self.prd_state.repo}"


class PRDConflict(TimeStampedModel):
    """Detected conflicts between PRD and repo state.

    When auto-analysis detects inconsistencies, they're logged here.

    Attributes:
        prd_state: Related PRD state
        conflict_type: Type of conflict detected
        description: Human-readable description
        severity: low/medium/high
        section_affected: PRD section (e.g., "MVP", "API", "ROAD")
        suggested_resolution: AI-suggested fix
        resolved: Whether conflict has been resolved
        resolved_by: How it was resolved
    """

    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    CONFLICT_TYPES = [
        ('outdated_api', 'API Documentation Outdated'),
        ('missing_feature', 'Feature in Code Not in PRD'),
        ('orphan_requirement', 'Requirement Not Implemented'),
        ('deadline_missed', 'Milestone Deadline Missed'),
        ('version_mismatch', 'Version Number Mismatch'),
        ('metric_drift', 'Metric Target Drift'),
        ('dependency_change', 'Dependency Changed'),
        ('other', 'Other'),
    ]

    prd_state = models.ForeignKey(PRDState, on_delete=models.CASCADE, related_name='conflicts')
    conflict_type = models.CharField(max_length=30, choices=CONFLICT_TYPES, db_index=True)
    description = models.TextField(help_text='Conflict description')
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='medium', db_index=True)
    section_affected = models.CharField(max_length=50, blank=True, help_text='PRD section affected')
    suggested_resolution = models.TextField(blank=True, help_text='AI-suggested resolution')

    # Resolution tracking
    resolved = models.BooleanField(default=False, db_index=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.CharField(max_length=255, blank=True, help_text='Auto/Manual + details')

    # Notification tracking
    slack_notified = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'PRD Conflict'
        verbose_name_plural = 'PRD Conflicts'
        ordering = ['-severity', '-created_at']
        indexes = [
            models.Index(fields=['resolved', 'severity']),
            models.Index(fields=['conflict_type', 'resolved']),
        ]

    def __str__(self):
        status = "✓" if self.resolved else "⚠"
        return f"{status} [{self.severity}] {self.conflict_type}: {self.description[:50]}"


class PRDExport(TimeStampedModel):
    """Track exports from PRD to GitHub issues, changelog, etc.

    Attributes:
        prd_state: Related PRD state
        prd_version: Version exported from
        export_type: Type of export (issues, changelog, version_bump)
        items_created: Count of items created
        details: JSON details of what was created
        github_refs: References to created GitHub items
    """

    EXPORT_TYPES = [
        ('issues', 'GitHub Issues'),
        ('changelog', 'Changelog Entry'),
        ('version_bump', 'Version Bump'),
        ('milestone', 'GitHub Milestone'),
        ('all', 'Full Export'),
    ]

    prd_state = models.ForeignKey(PRDState, on_delete=models.CASCADE, related_name='exports')
    prd_version = models.ForeignKey(PRDVersion, on_delete=models.SET_NULL, null=True, blank=True)
    export_type = models.CharField(max_length=20, choices=EXPORT_TYPES, db_index=True)
    items_created = models.IntegerField(default=0, help_text='Number of items created')
    details = models.JSONField(default=dict, help_text='Export details')
    github_refs = models.JSONField(default=list, help_text='GitHub issue/PR numbers created')

    class Meta:
        verbose_name = 'PRD Export'
        verbose_name_plural = 'PRD Exports'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.export_type} from {self.prd_state.repo} - {self.items_created} items"
