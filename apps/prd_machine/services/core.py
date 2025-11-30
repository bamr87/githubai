"""PRD MACHINE Core Distiller Service.

Central service for PRD distillation, evolution, and synchronization.
Uses AIService for AI-powered PRD generation and conflict detection.
"""
import hashlib
import logging
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

from django.conf import settings
from django.utils import timezone

from core.services.ai_service import AIService
from core.services.github_service import GitHubService
from prd_machine.models import PRDState, PRDVersion, PRDEvent, PRDConflict, PRDExport

logger = logging.getLogger('githubai')


class PRDMachineService:
    """Core service for PRD MACHINE automation.

    Provides:
    - PRD distillation from repo signals
    - Auto-generation from scratch
    - Conflict detection
    - Export to issues/changelog
    - Zero-touch mode enforcement
    """

    def __init__(self, repo: Optional[str] = None) -> None:
        """Initialize PRD MACHINE service.

        Args:
            repo: GitHub repository (owner/repo). Defaults to settings.DEFAULT_REPO.
        """
        self.repo = repo or getattr(settings, 'DEFAULT_REPO', 'bamr87/githubai')
        self.ai_service = AIService()
        self.github_service = GitHubService()

    # =========================================================================
    # Core PRD Operations
    # =========================================================================

    def get_or_create_prd_state(self, file_path: str = 'PRD.md') -> PRDState:
        """Get or create PRD state for the repo.

        Args:
            file_path: Path to PRD file in repo.

        Returns:
            PRDState instance.
        """
        state, created = PRDState.objects.get_or_create(
            repo=self.repo,
            file_path=file_path,
            defaults={
                'version': '1.0.0',
                'auto_evolve': True,
            }
        )

        if created:
            logger.info(f"Created new PRD state for {self.repo}:{file_path}")

        return state

    def sync_from_github(self, file_path: str = 'PRD.md') -> PRDState:
        """Sync PRD state from GitHub repository.

        Fetches current PRD.md content from GitHub and updates local state.

        Args:
            file_path: Path to PRD file in repo.

        Returns:
            Updated PRDState.
        """
        state = self.get_or_create_prd_state(file_path)

        try:
            content = self.github_service.fetch_file_contents(self.repo, file_path)

            # Check if content changed
            new_hash = hashlib.sha256(content.encode()).hexdigest()

            if new_hash != state.content_hash:
                # Content changed - create version
                old_content = state.content
                state.content = content
                state.last_synced_at = timezone.now()
                state.save()

                # Create version record
                PRDVersion.objects.create(
                    prd_state=state,
                    version=state.version,
                    content=content,
                    content_hash=new_hash,
                    trigger_type='manual_sync',
                    trigger_ref=f"Synced from GitHub at {timezone.now().isoformat()}",
                    change_summary=self._generate_change_summary(old_content, content) if old_content else "Initial sync",
                )

                logger.info(f"Synced PRD from GitHub: {self.repo}:{file_path}")
            else:
                logger.info(f"PRD unchanged: {self.repo}:{file_path}")

        except Exception as e:
            logger.error(f"Failed to sync PRD from GitHub: {e}")
            raise

        return state

    def distill_prd(
        self,
        prd_state: PRDState,
        trigger_type: str = 'manual_sync',
        trigger_ref: str = '',
        context: Optional[Dict[str, Any]] = None,
    ) -> PRDState:
        """Distill/evolve PRD based on repo signals.

        Uses AI to analyze repo state and update PRD sections as needed.

        Args:
            prd_state: Current PRD state.
            trigger_type: What triggered the distillation.
            trigger_ref: Reference to trigger (commit SHA, issue #, etc.).
            context: Additional context for distillation.

        Returns:
            Updated PRDState with new version.
        """
        logger.info(f"Distilling PRD for {prd_state.repo} ({trigger_type})")

        # Gather repo context
        repo_context = self._gather_repo_context(context or {})

        # Generate AI prompt for distillation
        system_prompt = self._get_distill_system_prompt()
        user_prompt = self._get_distill_user_prompt(prd_state, repo_context, trigger_type)

        # Call AI service
        evolved_content = self.ai_service.call_ai_chat(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

        # Parse and validate evolved PRD
        validated_content = self._validate_prd_structure(evolved_content)

        # Update state
        old_content = prd_state.content
        prd_state.content = validated_content
        prd_state.last_distilled_at = timezone.now()
        prd_state.version = self._increment_version(prd_state.version)
        prd_state.save()

        # Create version record
        PRDVersion.objects.create(
            prd_state=prd_state,
            version=prd_state.version,
            content=validated_content,
            content_hash=prd_state.content_hash,
            trigger_type=trigger_type,
            trigger_ref=trigger_ref,
            change_summary=self._generate_change_summary(old_content, validated_content),
        )

        logger.info(f"PRD distilled to v{prd_state.version}")
        return prd_state

    def generate_prd_from_scratch(
        self,
        project_name: Optional[str] = None,
        file_path: str = 'PRD.md',
    ) -> PRDState:
        """Generate a complete PRD from repo analysis.

        Analyzes repo structure, README, issues, etc. to generate
        a comprehensive PRD following the template.

        Args:
            project_name: Project name for PRD title.
            file_path: Path to save PRD.

        Returns:
            New PRDState with generated content.
        """
        logger.info(f"Generating PRD from scratch for {self.repo}")

        # Gather comprehensive repo context
        repo_context = self._gather_comprehensive_repo_context()

        # Extract project name from repo if not provided
        if not project_name:
            project_name = self.repo.split('/')[-1].replace('-', ' ').title()

        # Generate PRD using AI
        system_prompt = self._get_generation_system_prompt()
        user_prompt = self._get_generation_user_prompt(project_name, repo_context)

        prd_content = self.ai_service.call_ai_chat(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

        # Validate structure
        validated_content = self._validate_prd_structure(prd_content)

        # Create or update state
        state = self.get_or_create_prd_state(file_path)
        state.content = validated_content
        state.version = '1.0.0'
        state.last_distilled_at = timezone.now()
        state.save()

        # Create initial version
        PRDVersion.objects.create(
            prd_state=state,
            version='1.0.0',
            content=validated_content,
            content_hash=state.content_hash,
            trigger_type='initial',
            trigger_ref=f"Generated from {self.repo}",
            change_summary="Initial PRD generation from repository analysis",
        )

        logger.info(f"Generated PRD v1.0.0 for {self.repo}")
        return state

    # =========================================================================
    # Conflict Detection
    # =========================================================================

    def detect_conflicts(self, prd_state: PRDState) -> List[PRDConflict]:
        """Detect conflicts between PRD and current repo state.

        Uses AI to compare PRD sections against actual code/docs.

        Args:
            prd_state: PRD state to check.

        Returns:
            List of detected PRDConflict instances.
        """
        logger.info(f"Detecting conflicts for {prd_state.repo}")

        if not prd_state.content:
            logger.warning("No PRD content to check for conflicts")
            return []

        # Gather current repo state
        repo_context = self._gather_repo_context({})

        # AI-powered conflict detection
        system_prompt = """You are a PRD compliance analyzer. Compare the PRD document against
the current repository state and identify any conflicts or inconsistencies.

For each conflict found, output in this exact format:
CONFLICT|<type>|<severity>|<section>|<description>|<suggestion>

Types: outdated_api, missing_feature, orphan_requirement, deadline_missed, version_mismatch, metric_drift, dependency_change, other
Severity: low, medium, high, critical
Section: WHY, MVP, UX, API, NFR, EDGE, OOS, ROAD, RISK, DONE

Only output conflicts, one per line. If no conflicts, output: NO_CONFLICTS"""

        user_prompt = f"""PRD Content:
{prd_state.content}

---

Repository Context:
{self._format_repo_context(repo_context)}

Analyze and identify all conflicts."""

        response = self.ai_service.call_ai_chat(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

        # Parse conflicts
        conflicts = []
        for line in response.strip().split('\n'):
            if line.startswith('CONFLICT|'):
                parts = line.split('|')
                if len(parts) >= 6:
                    conflict = PRDConflict.objects.create(
                        prd_state=prd_state,
                        conflict_type=parts[1],
                        severity=parts[2],
                        section_affected=parts[3],
                        description=parts[4],
                        suggested_resolution=parts[5] if len(parts) > 5 else '',
                    )
                    conflicts.append(conflict)

        logger.info(f"Detected {len(conflicts)} conflicts")
        return conflicts

    def send_slack_alert(self, conflict: PRDConflict) -> bool:
        """Send Slack alert for a conflict.

        Args:
            conflict: PRDConflict to notify about.

        Returns:
            True if notification sent successfully.
        """
        webhook_url = conflict.prd_state.slack_webhook
        if not webhook_url:
            logger.warning("No Slack webhook configured")
            return False

        try:
            import requests

            severity_emoji = {
                'low': '🔵',
                'medium': '🟡',
                'high': '🟠',
                'critical': '🔴',
            }

            payload = {
                "text": f"{severity_emoji.get(conflict.severity, '⚠️')} PRD Conflict Detected",
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": f"PRD Conflict: {conflict.conflict_type}",
                        }
                    },
                    {
                        "type": "section",
                        "fields": [
                            {"type": "mrkdwn", "text": f"*Repo:*\n{conflict.prd_state.repo}"},
                            {"type": "mrkdwn", "text": f"*Severity:*\n{conflict.severity.upper()}"},
                            {"type": "mrkdwn", "text": f"*Section:*\n{conflict.section_affected}"},
                        ]
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*Description:*\n{conflict.description}",
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*Suggested Resolution:*\n{conflict.suggested_resolution}",
                        }
                    },
                ]
            }

            response = requests.post(webhook_url, json=payload, timeout=10)

            if response.ok:
                conflict.slack_notified = True
                conflict.save()
                logger.info(f"Slack alert sent for conflict {conflict.id}")
                return True
            else:
                logger.error(f"Slack webhook failed: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")
            return False

    # =========================================================================
    # Export Operations
    # =========================================================================

    def export_to_issues(self, prd_state: PRDState) -> PRDExport:
        """Export PRD items to GitHub issues.

        Parses MVP user stories and creates GitHub issues for each.

        Args:
            prd_state: PRD state to export from.

        Returns:
            PRDExport record with created issue references.
        """
        logger.info(f"Exporting PRD to GitHub issues for {prd_state.repo}")

        # Parse MVP stories from PRD
        mvp_section = self._extract_section(prd_state.content, 'MVP')

        # Use AI to extract structured items
        system_prompt = """Extract user stories from the MVP section as structured items.
Output each item as: STORY|<title>|<description>|<priority>
Priority: P0, P1, P2, P3
Only output stories, one per line."""

        user_prompt = f"""MVP Section:
{mvp_section}

Extract all user stories as structured items."""

        response = self.ai_service.call_ai_chat(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

        # Create GitHub issues
        created_issues = []
        for line in response.strip().split('\n'):
            if line.startswith('STORY|'):
                parts = line.split('|')
                if len(parts) >= 3:
                    title = f"[PRD] {parts[1]}"
                    body = f"{parts[2]}\n\n---\n_Auto-generated from PRD v{prd_state.version}_"
                    labels = ['prd-generated', parts[3] if len(parts) > 3 else 'P1']

                    try:
                        issue = self.github_service.create_github_issue(
                            repo=self.repo,
                            title=title,
                            body=body,
                            labels=labels,
                        )
                        created_issues.append(issue['number'])
                        logger.info(f"Created issue #{issue['number']}: {title}")
                    except Exception as e:
                        logger.error(f"Failed to create issue: {e}")

        # Create export record
        export = PRDExport.objects.create(
            prd_state=prd_state,
            prd_version=prd_state.versions.first(),
            export_type='issues',
            items_created=len(created_issues),
            github_refs=created_issues,
            details={'stories_parsed': response.count('STORY|')},
        )

        logger.info(f"Exported {len(created_issues)} issues from PRD")
        return export

    def export_to_changelog(self, prd_state: PRDState, version: str) -> PRDExport:
        """Generate changelog entry from PRD changes.

        Args:
            prd_state: PRD state to generate changelog from.
            version: Version for changelog.

        Returns:
            PRDExport record.
        """
        logger.info(f"Generating changelog for {prd_state.repo} v{version}")

        # Get recent versions
        recent_versions = prd_state.versions.order_by('-created_at')[:2]

        if len(recent_versions) < 2:
            # First version - generate initial changelog
            changelog_content = f"## v{version}\n\n- Initial release\n"
        else:
            current = recent_versions[0]
            previous = recent_versions[1]

            # AI-generate changelog
            system_prompt = """Generate a concise changelog entry comparing two PRD versions.
Format as Markdown with categories: Added, Changed, Removed, Fixed.
Keep entries brief and actionable."""

            user_prompt = f"""Previous PRD (v{previous.version}):
{previous.content[:2000]}...

Current PRD (v{current.version}):
{current.content[:2000]}...

Generate changelog entry."""

            changelog_content = self.ai_service.call_ai_chat(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
            )

        # Create export record
        export = PRDExport.objects.create(
            prd_state=prd_state,
            prd_version=prd_state.versions.first(),
            export_type='changelog',
            items_created=1,
            details={'changelog': changelog_content, 'version': version},
        )

        return export

    def bump_version(self, prd_state: PRDState, bump_type: str = 'patch') -> str:
        """Bump PRD version.

        Args:
            prd_state: PRD state to bump.
            bump_type: Type of bump (major, minor, patch).

        Returns:
            New version string.
        """
        parts = prd_state.version.split('.')
        if len(parts) != 3:
            parts = ['1', '0', '0']

        major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])

        if bump_type == 'major':
            major += 1
            minor = 0
            patch = 0
        elif bump_type == 'minor':
            minor += 1
            patch = 0
        else:  # patch
            patch += 1

        new_version = f"{major}.{minor}.{patch}"
        prd_state.version = new_version
        prd_state.save()

        logger.info(f"Bumped PRD version to {new_version}")
        return new_version

    # =========================================================================
    # Zero-Touch Mode
    # =========================================================================

    def enforce_zero_touch(self, prd_state: PRDState, new_content: str) -> Tuple[bool, str]:
        """Enforce zero-touch mode - revert human edits.

        Args:
            prd_state: PRD state being checked.
            new_content: Proposed new content.

        Returns:
            Tuple of (allowed, message).
        """
        if not prd_state.is_locked:
            return True, "Edit allowed - zero-touch mode disabled"

        # Check if this is a machine edit (from our service)
        # In real implementation, would check auth/source

        # For now, compare against last machine-generated version
        last_machine_version = prd_state.versions.filter(
            is_human_edit=False
        ).order_by('-created_at').first()

        if last_machine_version:
            new_hash = hashlib.sha256(new_content.encode()).hexdigest()
            if new_hash != last_machine_version.content_hash:
                # Human trying to edit - revert
                message = "I got this, meatbag. Zero-touch mode active - reverting human edit."
                logger.warning(f"Blocked human edit on {prd_state.repo}")
                return False, message

        return True, "Edit allowed"

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _gather_repo_context(self, additional_context: Dict[str, Any]) -> Dict[str, Any]:
        """Gather context from repository for PRD distillation."""
        context = additional_context.copy()

        # Fetch key files
        key_files = ['README.md', 'pyproject.toml', 'package.json', 'VERSION']
        for file_path in key_files:
            try:
                content = self.github_service.fetch_file_contents(self.repo, file_path)
                context[file_path] = content[:2000]  # Limit size
            except Exception:
                pass

        return context

    def _gather_comprehensive_repo_context(self) -> Dict[str, Any]:
        """Gather comprehensive context for PRD generation."""
        context = self._gather_repo_context({})

        # Try to fetch additional context
        additional_files = [
            'docs/README.md',
            'CHANGELOG.md',
            'CONTRIBUTING.md',
            'apps/core/models.py',
            'apps/core/views.py',
        ]

        for file_path in additional_files:
            try:
                content = self.github_service.fetch_file_contents(self.repo, file_path)
                context[file_path] = content[:1500]
            except Exception:
                pass

        return context

    def _format_repo_context(self, context: Dict[str, Any]) -> str:
        """Format repo context for AI prompt."""
        formatted = []
        for file_path, content in context.items():
            formatted.append(f"=== {file_path} ===\n{content}\n")
        return "\n".join(formatted)

    def _get_distill_system_prompt(self) -> str:
        """Get system prompt for PRD distillation."""
        return """You are a PRD MACHINE - an AI system that maintains Product Requirements Documents.
Your job is to evolve the PRD based on repository signals while maintaining:
- KISS: Keep It Simple, Stupid (≤800 lines, short sentences)
- DRY: Don't Repeat Yourself (link to external docs, no duplicates)
- MVP: Focus on shippable core (defer nice-to-haves to OOS)

Maintain the 10-section structure:
0. WHY - North star and KFI
1. MVP - User stories (Must-have only)
2. UX - User flow diagram
3. API - Endpoint table
4. NFR - Non-functional requirements
5. EDGE - Dependencies and gotchas
6. OOS - Out of scope
7. ROAD - Roadmap milestones
8. RISK - Risk assessment
9. DONE - Definition of done

Output the complete updated PRD in Markdown format."""

    def _get_distill_user_prompt(
        self,
        prd_state: PRDState,
        repo_context: Dict[str, Any],
        trigger_type: str,
    ) -> str:
        """Get user prompt for PRD distillation."""
        return f"""Current PRD (v{prd_state.version}):
{prd_state.content}

---

Repository Context:
{self._format_repo_context(repo_context)}

---

Trigger: {trigger_type}

Evolve this PRD based on the repository context. Update any outdated sections,
add new information discovered, and ensure all sections remain current and accurate.
Output the complete evolved PRD."""

    def _get_generation_system_prompt(self) -> str:
        """Get system prompt for PRD generation from scratch."""
        return """You are a PRD MACHINE - an AI system that generates Product Requirements Documents.
Analyze the repository and generate a comprehensive PRD following this structure:

0. WHY - Define the north star and KFI (1 success metric)
1. MVP - 3-7 user stories as "As [user], I [action] so [benefit]"
2. UX - ASCII/text diagram of primary user flow
3. API - Table of endpoints | Method | Request | Response | Errors
4. NFR - Table of Category | Requirement | Metric
5. EDGE - Bullets for dependencies, gotchas, technical debt
6. OOS - Explicit list of what's NOT in scope
7. ROAD - Table of Milestone | Objective | Date
8. RISK - Table of Risk | Impact | Mitigation
9. DONE - Checklists for machine and human verification

Follow KISS (≤800 lines), DRY (no duplicates), MVP (core features only).
Output complete PRD in Markdown format."""

    def _get_generation_user_prompt(
        self,
        project_name: str,
        repo_context: Dict[str, Any],
    ) -> str:
        """Get user prompt for PRD generation."""
        return f"""Project: {project_name}
Repository: {self.repo}

Repository Contents:
{self._format_repo_context(repo_context)}

Generate a comprehensive PRD for this project based on the repository analysis.
Include all 10 sections with relevant content derived from the codebase."""

    def _validate_prd_structure(self, content: str) -> str:
        """Validate PRD has required sections."""
        required_sections = [
            'WHY', 'MVP', 'UX', 'API', 'NFR', 'EDGE', 'OOS', 'ROAD', 'RISK', 'DONE'
        ]

        for section in required_sections:
            if f"## " not in content or section not in content.upper():
                logger.warning(f"PRD missing section: {section}")

        return content

    def _extract_section(self, content: str, section_name: str) -> str:
        """Extract a specific section from PRD content."""
        pattern = rf"## \d*\.?\s*{section_name}.*?\n(.*?)(?=\n## |\Z)"
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        return match.group(1).strip() if match else ""

    def _generate_change_summary(self, old_content: str, new_content: str) -> str:
        """Generate AI summary of changes between versions."""
        if not old_content:
            return "Initial version"

        system_prompt = "Summarize the key changes between two PRD versions in 1-2 sentences."
        user_prompt = f"""Old PRD:
{old_content[:1500]}...

New PRD:
{new_content[:1500]}...

Summarize the changes."""

        return self.ai_service.call_ai_chat(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

    def _increment_version(self, version: str) -> str:
        """Auto-increment patch version."""
        parts = version.split('.')
        if len(parts) != 3:
            return '1.0.1'

        major, minor, patch = parts
        return f"{major}.{minor}.{int(patch) + 1}"

    # =========================================================================
    # Cross-Document Synchronization
    # =========================================================================

    def get_or_create_document_state(
        self,
        file_path: str,
        document_type: str = 'prd',
    ) -> PRDState:
        """Get or create document state for any document type.

        Args:
            file_path: Path to document file in repo.
            document_type: Type of document ('prd', 'readme', 'ip').

        Returns:
            PRDState instance.
        """
        state, created = PRDState.objects.get_or_create(
            repo=self.repo,
            file_path=file_path,
            defaults={
                'document_type': document_type,
                'version': '1.0.0',
                'auto_evolve': True,
            }
        )

        if created:
            logger.info(f"Created new {document_type} state for {self.repo}:{file_path}")

        return state

    def sync_readme_from_prd(self, prd_state: PRDState) -> PRDState:
        """Sync README.md content from PRD.md.

        Updates README sections based on PRD content:
        - Features section from PRD MVP user stories
        - API endpoints from PRD API section
        - Project version from PRD ROAD section

        Args:
            prd_state: Source PRD state to sync from.

        Returns:
            Updated README PRDState.
        """
        logger.info(f"Syncing README from PRD for {self.repo}")

        # Get or create README state
        readme_state = self.get_or_create_document_state('README.md', 'readme')
        readme_state.parent_document = prd_state

        # Fetch current README from GitHub
        try:
            current_readme = self.github_service.fetch_file_contents(self.repo, 'README.md')
        except Exception:
            logger.warning("README.md not found, cannot sync")
            return readme_state

        # Extract PRD sections for sync
        prd_mvp = self._extract_section(prd_state.content, 'MVP')
        prd_api = self._extract_section(prd_state.content, 'API')
        prd_road = self._extract_section(prd_state.content, 'ROAD')

        # Use AI to update README sections
        system_prompt = """You are a documentation synchronization assistant.
Update the README.md to align with the PRD content while preserving README structure and style.

Rules:
1. Keep the existing README format and tone
2. Update the Features section to reflect MVP user stories
3. Update API Endpoints section if it differs from PRD API
4. Keep installation, quick start, and other sections unchanged
5. Output the complete updated README.md

Do NOT change:
- Project name/title
- Installation instructions
- Quick start guide
- Docker/development sections"""

        user_prompt = f"""Current README.md:
{current_readme}

---

PRD MVP Section (source of truth for features):
{prd_mvp}

PRD API Section (source of truth for endpoints):
{prd_api}

PRD ROAD Section (current version info):
{prd_road}

Update the README to align with the PRD. Output the complete updated README.md."""

        updated_readme = self.ai_service.call_ai_chat(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

        # Update README state
        readme_state.content = updated_readme
        readme_state.last_aligned_at = timezone.now()
        readme_state.save()

        # Create version record
        PRDVersion.objects.create(
            prd_state=readme_state,
            version=readme_state.version,
            content=updated_readme,
            content_hash=readme_state.content_hash,
            trigger_type='manual_sync',
            trigger_ref=f"Synced from PRD v{prd_state.version}",
            change_summary=f"Aligned with PRD v{prd_state.version}",
        )

        logger.info(f"README synced from PRD v{prd_state.version}")
        return readme_state

    def sync_ip_from_prd(self, prd_state: PRDState) -> PRDState:
        """Sync IP.md (Implementation Plan) from PRD.md.

        Updates IP deliverables and status based on PRD ROAD section.

        Args:
            prd_state: Source PRD state to sync from.

        Returns:
            Updated IP PRDState.
        """
        logger.info(f"Syncing IP from PRD for {self.repo}")

        # Get or create IP state
        ip_state = self.get_or_create_document_state('IP.md', 'ip')
        ip_state.parent_document = prd_state

        # Fetch current IP from GitHub
        try:
            current_ip = self.github_service.fetch_file_contents(self.repo, 'IP.md')
        except Exception:
            logger.warning("IP.md not found, cannot sync")
            return ip_state

        # Extract PRD ROAD section for sync
        prd_road = self._extract_section(prd_state.content, 'ROAD')
        prd_done = self._extract_section(prd_state.content, 'DONE')

        # Use AI to update IP
        system_prompt = """You are an Implementation Plan synchronization assistant.
Update the IP.md to align deliverable status with PRD ROAD milestones.

Rules:
1. Keep the IP table structure (# | Deliverable | Owner | Deadline | Dep | Risk | Status)
2. Update Status column to match PRD ROAD completion status
3. Add new deliverables from PRD ROAD if missing from IP
4. Mark completed items with ✅ DONE
5. Keep IP automation rules and NFR sections unchanged
6. Output the complete updated IP.md"""

        user_prompt = f"""Current IP.md:
{current_ip}

---

PRD ROAD Section (milestones and dates):
{prd_road}

PRD DONE Section (completion criteria):
{prd_done}

Update the IP to align deliverable status with PRD. Output the complete updated IP.md."""

        updated_ip = self.ai_service.call_ai_chat(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

        # Update IP state
        ip_state.content = updated_ip
        ip_state.last_aligned_at = timezone.now()
        ip_state.save()

        # Create version record
        PRDVersion.objects.create(
            prd_state=ip_state,
            version=ip_state.version,
            content=updated_ip,
            content_hash=ip_state.content_hash,
            trigger_type='manual_sync',
            trigger_ref=f"Synced from PRD v{prd_state.version}",
            change_summary=f"Aligned deliverables with PRD v{prd_state.version}",
        )

        logger.info(f"IP synced from PRD v{prd_state.version}")
        return ip_state

    def align_all_documents(self) -> Dict[str, PRDState]:
        """Align all documents (PRD, README, IP) for consistency.

        Syncs README and IP from PRD as source of truth.

        Returns:
            Dict with 'prd', 'readme', 'ip' PRDState instances.
        """
        logger.info(f"Aligning all documents for {self.repo}")

        # Sync PRD from GitHub first
        prd_state = self.sync_from_github('PRD.md')

        # Sync README and IP from PRD
        readme_state = self.sync_readme_from_prd(prd_state)
        ip_state = self.sync_ip_from_prd(prd_state)

        logger.info("All documents aligned successfully")
        return {
            'prd': prd_state,
            'readme': readme_state,
            'ip': ip_state,
        }

    def detect_document_drift(self) -> List[PRDConflict]:
        """Detect inconsistencies between PRD, README, and IP.

        Compares key sections across documents to find drift.

        Returns:
            List of PRDConflict instances for detected drift.
        """
        logger.info(f"Detecting document drift for {self.repo}")

        conflicts = []

        # Get all document states
        prd_state = self.get_or_create_prd_state('PRD.md')
        readme_state = self.get_or_create_document_state('README.md', 'readme')
        ip_state = self.get_or_create_document_state('IP.md', 'ip')

        # Fetch current content from GitHub
        try:
            prd_content = self.github_service.fetch_file_contents(self.repo, 'PRD.md')
            readme_content = self.github_service.fetch_file_contents(self.repo, 'README.md')
            ip_content = self.github_service.fetch_file_contents(self.repo, 'IP.md')
        except Exception as e:
            logger.error(f"Failed to fetch documents for drift detection: {e}")
            return conflicts

        # AI-powered drift detection
        system_prompt = """You are a document consistency analyzer.
Compare the PRD, README, and IP documents to find inconsistencies.

For each inconsistency found, output in this format:
DRIFT|<source_doc>|<target_doc>|<severity>|<section>|<description>

Source/Target: PRD, README, IP
Severity: low, medium, high
Section: Features, API, Version, Structure, Other

Only output drift issues, one per line. If documents are consistent, output: NO_DRIFT"""

        user_prompt = f"""PRD.md:
{prd_content[:3000]}

---

README.md:
{readme_content[:3000]}

---

IP.md:
{ip_content[:3000]}

Analyze for inconsistencies between documents."""

        response = self.ai_service.call_ai_chat(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

        # Parse drift issues
        for line in response.strip().split('\n'):
            if line.startswith('DRIFT|'):
                parts = line.split('|')
                if len(parts) >= 6:
                    conflict = PRDConflict.objects.create(
                        prd_state=prd_state,
                        conflict_type='version_mismatch' if 'version' in parts[4].lower() else 'other',
                        severity=parts[3],
                        section_affected=f"{parts[1]}↔{parts[2]}: {parts[4]}",
                        description=parts[5],
                        suggested_resolution=f"Sync {parts[2]} from {parts[1]}",
                    )
                    conflicts.append(conflict)

        logger.info(f"Detected {len(conflicts)} document drift issues")
        return conflicts