"""FleetDigestService - AI distillation of "what needs attention".

This is the Phase 3 entry point. It reads the latest metrics snapshots and asks
the existing multi-provider :class:`AIService` to produce a ranked, human-
readable summary - per repository and across the whole fleet. The AI call is
optional: if the AI layer is unavailable, a deterministic rule-based summary is
produced so the cockpit still works.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from django.utils import timezone

from dashboard.models import Repository, RepoMetricSnapshot, RepoDigest

logger = logging.getLogger('githubai')

DIGEST_SYSTEM_PROMPT = (
    "You are a DevOps cockpit assistant. Given metrics about software "
    "repositories, produce a concise, prioritized summary of what needs "
    "attention. Lead with the most urgent items (failing CI, open security "
    "alerts, stale pull requests). Be specific and actionable. Do not invent "
    "data that is not present in the metrics."
)


class FleetDigestService:
    """Generate AI-distilled digests for repositories and the fleet."""

    def __init__(self, ai_service: Optional[Any] = None) -> None:
        # Imported lazily so the dashboard can be used without AI configured.
        self._ai_service = ai_service

    @property
    def ai_service(self):
        if self._ai_service is None:
            from core.services.ai_service import AIService
            self._ai_service = AIService()
        return self._ai_service

    # ------------------------------------------------------------------
    # Per-repository digest
    # ------------------------------------------------------------------
    def generate_repo_digest(self, repo: Repository, use_ai: bool = True) -> RepoDigest:
        """Build a digest for a single repository from its latest snapshot."""
        snapshot = repo.snapshots.order_by('-captured_at').first()
        context = self._repo_context(repo, snapshot)
        severity = self._severity_for_repo(snapshot)

        summary = self._summarize(
            user_prompt=self._repo_prompt(context), use_ai=use_ai
        ) or self._fallback_repo_summary(context)

        return RepoDigest.objects.create(
            repository=repo,
            scope='repo',
            title=f"Attention digest for {repo.full_name}",
            summary=summary,
            severity=severity,
            generated_by_model=self._model_name(use_ai),
            data=context,
        )

    # ------------------------------------------------------------------
    # Fleet-level digest
    # ------------------------------------------------------------------
    def generate_fleet_digest(self, use_ai: bool = True) -> RepoDigest:
        """Build an org-wide "Monday morning report" across all tracked repos."""
        repos = Repository.objects.filter(is_tracked=True, is_archived=False)
        repo_contexts: List[Dict[str, Any]] = []
        worst_severity = 'info'
        severity_rank = {'info': 0, 'low': 1, 'medium': 2, 'high': 3, 'critical': 4}

        for repo in repos:
            snapshot = repo.snapshots.order_by('-captured_at').first()
            ctx = self._repo_context(repo, snapshot)
            repo_contexts.append(ctx)
            sev = self._severity_for_repo(snapshot)
            if severity_rank[sev] > severity_rank[worst_severity]:
                worst_severity = sev

        context = {'repositories': repo_contexts, 'repo_count': len(repo_contexts)}
        summary = self._summarize(
            user_prompt=self._fleet_prompt(repo_contexts), use_ai=use_ai
        ) or self._fallback_fleet_summary(repo_contexts)

        return RepoDigest.objects.create(
            repository=None,
            scope='fleet',
            title=f"Fleet digest ({len(repo_contexts)} repositories)",
            summary=summary,
            severity=worst_severity,
            generated_by_model=self._model_name(use_ai),
            data=context,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _summarize(self, user_prompt: str, use_ai: bool) -> Optional[str]:
        if not use_ai:
            return None
        try:
            return self.ai_service.call_ai_chat(
                system_prompt=DIGEST_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                use_cache=True,
            )
        except Exception as e:  # noqa: BLE001 - fall back to rule-based summary
            logger.warning(f"AI digest unavailable, using fallback: {e}")
            return None

    @staticmethod
    def _model_name(use_ai: bool) -> str:
        return 'ai' if use_ai else 'rule-based'

    @staticmethod
    def _repo_context(repo: Repository, snapshot: Optional[RepoMetricSnapshot]) -> Dict[str, Any]:
        if snapshot is None:
            return {
                'repo': repo.full_name,
                'has_metrics': False,
                'health_score': None,
            }
        return {
            'repo': repo.full_name,
            'has_metrics': True,
            'health_score': snapshot.health_score,
            'open_prs': snapshot.open_pr_count,
            'stale_prs': snapshot.stale_pr_count,
            'open_issues': snapshot.open_issue_count,
            'ci_success_rate': snapshot.ci_success_rate,
            'ci_failures': snapshot.ci_failure_count,
            'security_alerts': snapshot.security_alert_count,
            'last_release': snapshot.last_release_tag,
            'captured_at': snapshot.captured_at.isoformat(),
        }

    @staticmethod
    def _severity_for_repo(snapshot: Optional[RepoMetricSnapshot]) -> str:
        if snapshot is None:
            return 'info'
        if snapshot.security_alert_count >= 1 and (
            snapshot.ci_success_rate is not None and snapshot.ci_success_rate < 0.5
        ):
            return 'critical'
        if snapshot.security_alert_count >= 3:
            return 'high'
        if snapshot.ci_success_rate is not None and snapshot.ci_success_rate < 0.5:
            return 'high'
        if snapshot.security_alert_count >= 1 or snapshot.stale_pr_count >= 3:
            return 'medium'
        if snapshot.stale_pr_count >= 1:
            return 'low'
        return 'info'

    @staticmethod
    def _repo_prompt(context: Dict[str, Any]) -> str:
        import json
        return (
            "Summarize what needs attention for this repository based on the "
            "following metrics:\n" + json.dumps(context, indent=2)
        )

    @staticmethod
    def _fleet_prompt(contexts: List[Dict[str, Any]]) -> str:
        import json
        return (
            "Produce a prioritized fleet-wide briefing. Highlight the top "
            "repositories that need attention and why, based on these metrics:\n"
            + json.dumps(contexts, indent=2)
        )

    @staticmethod
    def _fallback_repo_summary(context: Dict[str, Any]) -> str:
        if not context.get('has_metrics'):
            return f"No metrics collected yet for {context['repo']}. Run ingestion to populate signals."
        parts = [f"Health score: {context['health_score']}/100."]
        if context.get('ci_failures'):
            parts.append(f"{context['ci_failures']} recent CI failures.")
        if context.get('security_alerts'):
            parts.append(f"{context['security_alerts']} open security alerts.")
        if context.get('stale_prs'):
            parts.append(f"{context['stale_prs']} stale pull requests (>2 weeks).")
        if len(parts) == 1:
            parts.append("No urgent issues detected.")
        return ' '.join(parts)

    @classmethod
    def _fallback_fleet_summary(cls, contexts: List[Dict[str, Any]]) -> str:
        if not contexts:
            return "No tracked repositories. Register repositories to start monitoring."

        def attention_rank(ctx: Dict[str, Any]) -> int:
            if not ctx.get('has_metrics'):
                return -1
            return (
                ctx.get('security_alerts', 0) * 10
                + ctx.get('ci_failures', 0) * 5
                + ctx.get('stale_prs', 0)
            )

        ranked = sorted(contexts, key=attention_rank, reverse=True)
        lines = [f"Fleet overview across {len(contexts)} repositories:"]
        for ctx in ranked[:5]:
            lines.append(f"- {ctx['repo']}: " + cls._fallback_repo_summary(ctx))
        return '\n'.join(lines)
