"""Dashboard models - the multi-repo registry and time-series metrics store.

This module introduces the first-class entities the cockpit hangs off of:

* :class:`Organization` - a GitHub org or user account that owns repositories.
* :class:`Repository` - a registered repo that can be tracked ("watchlisted").
* :class:`RepoConnection` - how a repo is accessed (token env var / GitHub App),
  storing *references* to credentials, never the secrets themselves.
* :class:`RepoMetricSnapshot` - a point-in-time roll-up of repo signals, so the
  dashboard can chart trends over time.
* :class:`RepoDigest` - an AI-distilled "what needs attention" summary, either
  for a single repo or for the whole fleet.
"""
from __future__ import annotations

from django.db import models

from core.models import TimeStampedModel


class Organization(TimeStampedModel):
    """A GitHub organization or user account that owns repositories.

    Attributes:
        login: GitHub login/slug (e.g. ``bamr87``). Unique.
        name: Human-readable display name.
        org_type: Whether the owner is an ``org`` or a ``user``.
        avatar_url: URL to the owner's avatar image.
        html_url: Link to the owner's GitHub profile.
        is_active: Whether this org is shown in the cockpit.
    """

    ORG_TYPES = [
        ('org', 'Organization'),
        ('user', 'User'),
    ]

    login = models.CharField(max_length=255, unique=True, db_index=True,
                             help_text='GitHub login (e.g. owner slug)')
    name = models.CharField(max_length=255, blank=True, help_text='Display name')
    org_type = models.CharField(max_length=10, choices=ORG_TYPES, default='org', db_index=True)
    avatar_url = models.URLField(max_length=500, blank=True)
    html_url = models.URLField(max_length=500, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ['login']

    def __str__(self) -> str:
        return self.login


class Repository(TimeStampedModel):
    """A GitHub repository registered in the cockpit.

    The ``full_name`` (``owner/repo``) is the canonical identifier used by every
    downstream metric, snapshot, and digest. ``is_tracked`` controls whether the
    repo is part of the active watchlist that scheduled ingestion runs against.
    """

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name='repositories'
    )
    full_name = models.CharField(max_length=512, unique=True, db_index=True,
                                 help_text='owner/repo')
    owner = models.CharField(max_length=255, db_index=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    default_branch = models.CharField(max_length=255, default='main')
    is_private = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False, db_index=True)
    is_fork = models.BooleanField(default=False)
    language = models.CharField(max_length=100, blank=True, db_index=True)
    topics = models.JSONField(default=list, blank=True)
    html_url = models.URLField(max_length=500, blank=True)

    # Watchlist / ingestion control
    is_tracked = models.BooleanField(
        default=True, db_index=True,
        help_text='Whether this repo is on the active ingestion watchlist'
    )
    last_ingested_at = models.DateTimeField(null=True, blank=True)
    metadata_etag = models.CharField(
        max_length=255, blank=True,
        help_text='ETag from the last repo metadata fetch (conditional requests)'
    )

    # Lightweight metadata cache (refreshed on metadata sync)
    stars = models.IntegerField(default=0)
    forks = models.IntegerField(default=0)
    open_issues_count = models.IntegerField(default=0)

    class Meta:
        ordering = ['full_name']
        verbose_name_plural = 'repositories'
        indexes = [
            models.Index(fields=['is_tracked', 'is_archived']),
        ]

    def __str__(self) -> str:
        return self.full_name


class RepoConnection(TimeStampedModel):
    """How a repository (or org) is accessed by the cockpit.

    Secrets are **never** stored here. For token auth we store only the *name*
    of the environment variable that holds the token; for GitHub App auth we
    store the (non-secret) installation id. This keeps credentials in the
    environment / secret manager per the project's security NFR.
    """

    CONNECTION_TYPES = [
        ('token', 'Personal Access Token (env var)'),
        ('github_app', 'GitHub App Installation'),
    ]

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name='connections'
    )
    connection_type = models.CharField(max_length=20, choices=CONNECTION_TYPES, default='token')
    token_env_var = models.CharField(
        max_length=255, blank=True,
        help_text='Name of the env var holding the token (NOT the token itself)'
    )
    installation_id = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ['organization', 'connection_type']

    def __str__(self) -> str:
        return f"{self.organization.login} [{self.connection_type}]"


class RepoMetricSnapshot(TimeStampedModel):
    """A point-in-time roll-up of a repository's DevOps signals.

    The most important fleet-level metrics are stored as indexed scalar columns
    (so cross-cutting queries like "all repos with failing CI" stay efficient),
    while the full raw payload lives in :attr:`data` for richer drill-downs.
    """

    repository = models.ForeignKey(
        Repository, on_delete=models.CASCADE, related_name='snapshots'
    )
    captured_at = models.DateTimeField(db_index=True)

    # Pull requests
    open_pr_count = models.IntegerField(default=0)
    stale_pr_count = models.IntegerField(default=0,
                                         help_text='Open PRs not updated within the staleness window')

    # Issues
    open_issue_count = models.IntegerField(default=0)

    # CI / GitHub Actions
    ci_total_runs = models.IntegerField(default=0)
    ci_success_count = models.IntegerField(default=0)
    ci_failure_count = models.IntegerField(default=0)
    ci_success_rate = models.FloatField(
        null=True, blank=True,
        help_text='Success ratio (0.0-1.0) over the sampled workflow runs'
    )

    # Security
    security_alert_count = models.IntegerField(default=0)

    # Releases
    last_release_tag = models.CharField(max_length=255, blank=True)
    last_release_at = models.DateTimeField(null=True, blank=True)

    # Popularity
    stars = models.IntegerField(default=0)
    forks = models.IntegerField(default=0)

    # Full raw payload for drill-down / future metrics
    data = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-captured_at']
        get_latest_by = 'captured_at'
        indexes = [
            models.Index(fields=['repository', '-captured_at']),
            models.Index(fields=['ci_success_rate']),
            models.Index(fields=['security_alert_count']),
        ]

    def __str__(self) -> str:
        return f"{self.repository.full_name} @ {self.captured_at:%Y-%m-%d %H:%M}"

    @property
    def health_score(self) -> int:
        """A coarse 0-100 health score combining CI, security and PR staleness.

        Used for the fleet overview's health badge. Heuristic and intentionally
        simple; the AI digest provides the nuanced interpretation.
        """
        score = 100
        if self.ci_success_rate is not None:
            score -= int((1.0 - self.ci_success_rate) * 40)
        score -= min(self.security_alert_count * 10, 30)
        score -= min(self.stale_pr_count * 3, 30)
        return max(0, min(100, score))


class RepoDigest(TimeStampedModel):
    """An AI-distilled summary of what needs attention.

    A digest may be scoped to a single repository (``repository`` set) or to the
    whole fleet (``repository`` null, ``scope='fleet'``). The ``severity`` field
    lets the dashboard sort the most urgent digests to the top.
    """

    SCOPES = [
        ('repo', 'Repository'),
        ('fleet', 'Fleet'),
    ]
    SEVERITIES = [
        ('info', 'Info'),
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    repository = models.ForeignKey(
        Repository, on_delete=models.CASCADE, related_name='digests',
        null=True, blank=True
    )
    scope = models.CharField(max_length=10, choices=SCOPES, default='repo', db_index=True)
    title = models.CharField(max_length=500)
    summary = models.TextField(help_text='AI-generated "what needs attention" summary')
    severity = models.CharField(max_length=10, choices=SEVERITIES, default='info', db_index=True)
    generated_by_model = models.CharField(max_length=100, blank=True)
    data = models.JSONField(default=dict, blank=True,
                            help_text='Structured context the digest was built from')

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['scope', '-created_at']),
            models.Index(fields=['severity', '-created_at']),
        ]

    def __str__(self) -> str:
        target = self.repository.full_name if self.repository else 'FLEET'
        return f"[{self.severity}] {target}: {self.title}"
