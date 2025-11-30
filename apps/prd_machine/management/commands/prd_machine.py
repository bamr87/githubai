"""Management command to sync PRD from GitHub or distill from repo signals."""
from django.core.management.base import BaseCommand
from prd_machine.services.core import PRDMachineService


class Command(BaseCommand):
    help = 'Sync PRD from GitHub or distill from repository signals'

    def add_arguments(self, parser):
        parser.add_argument(
            '--repo',
            type=str,
            default='bamr87/githubai',
            help='GitHub repository in format owner/repo (default: bamr87/githubai)'
        )
        parser.add_argument(
            '--file-path',
            type=str,
            default='PRD.md',
            help='Path to PRD file in repository (default: PRD.md)'
        )
        parser.add_argument(
            '--distill',
            action='store_true',
            help='Distill/evolve PRD using AI after sync'
        )
        parser.add_argument(
            '--generate',
            action='store_true',
            help='Generate new PRD from scratch (ignores existing)'
        )
        parser.add_argument(
            '--project-name',
            type=str,
            default=None,
            help='Project name for generated PRD (default: derived from repo)'
        )
        parser.add_argument(
            '--detect-conflicts',
            action='store_true',
            help='Detect conflicts between PRD and repo state'
        )
        parser.add_argument(
            '--export-issues',
            action='store_true',
            help='Export PRD MVP stories to GitHub issues'
        )
        parser.add_argument(
            '--export-changelog',
            type=str,
            default=None,
            metavar='VERSION',
            help='Generate changelog for specified version'
        )
        parser.add_argument(
            '--bump-version',
            type=str,
            choices=['major', 'minor', 'patch'],
            default=None,
            help='Bump PRD version'
        )
        parser.add_argument(
            '--lock',
            action='store_true',
            help='Enable zero-touch mode (lock from human edits)'
        )
        parser.add_argument(
            '--unlock',
            action='store_true',
            help='Disable zero-touch mode (allow human edits)'
        )
        parser.add_argument(
            '--status',
            action='store_true',
            help='Show current PRD status and exit'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes'
        )
        # Cross-document sync flags
        parser.add_argument(
            '--sync-readme',
            action='store_true',
            help='Sync README.md from PRD.md (PRD is source of truth)'
        )
        parser.add_argument(
            '--sync-ip',
            action='store_true',
            help='Sync IP.md from PRD.md (PRD is source of truth)'
        )
        parser.add_argument(
            '--align-all',
            action='store_true',
            help='Align all documents (PRD, README, IP) for consistency'
        )
        parser.add_argument(
            '--detect-drift',
            action='store_true',
            help='Detect inconsistencies between PRD, README, and IP'
        )

    def handle(self, *args, **options):
        service = PRDMachineService(repo=options['repo'])

        # Status check
        if options['status']:
            self._show_status(service, options['file_path'])
            return

        # Lock/unlock operations
        if options['lock'] or options['unlock']:
            self._toggle_lock(service, options['file_path'], options['lock'])
            return

        # Generate new PRD from scratch
        if options['generate']:
            self._generate_prd(service, options)
            return

        # Cross-document sync operations
        if options['align_all']:
            self._align_all_documents(service, options)
            return

        if options['sync_readme']:
            self._sync_readme(service, options)
            return

        if options['sync_ip']:
            self._sync_ip(service, options)
            return

        if options['detect_drift']:
            self._detect_drift(service, options)
            return

        # Sync from GitHub
        if not options['detect_conflicts'] and not options['export_issues'] and not options['export_changelog'] and not options['bump_version']:
            self._sync_prd(service, options)

        # Distill/evolve
        if options['distill']:
            self._distill_prd(service, options)

        # Detect conflicts
        if options['detect_conflicts']:
            self._detect_conflicts(service, options['file_path'])

        # Export operations
        if options['export_issues']:
            self._export_issues(service, options)

        if options['export_changelog']:
            self._export_changelog(service, options)

        # Version bump
        if options['bump_version']:
            self._bump_version(service, options)

    def _show_status(self, service: PRDMachineService, file_path: str):
        """Show current PRD status."""
        from prd_machine.models import PRDState

        try:
            state = PRDState.objects.get(repo=service.repo, file_path=file_path)
        except PRDState.DoesNotExist:
            self.stdout.write(self.style.WARNING(
                f"No PRD state found for {service.repo}:{file_path}"
            ))
            self.stdout.write("Run `prd_machine sync` to initialize.")
            return

        self.stdout.write(self.style.SUCCESS(f"\n📄 PRD Status: {service.repo}"))
        self.stdout.write(f"   File: {state.file_path}")
        self.stdout.write(f"   Version: {state.version}")
        self.stdout.write(f"   Content Hash: {state.content_hash[:12]}...")
        self.stdout.write(f"   Auto-evolve: {'✓ Enabled' if state.auto_evolve else '✗ Disabled'}")
        self.stdout.write(f"   Zero-touch: {'🔒 Locked' if state.is_locked else '🔓 Unlocked'}")
        self.stdout.write(f"   Last Synced: {state.last_synced_at or 'Never'}")
        self.stdout.write(f"   Last Distilled: {state.last_distilled_at or 'Never'}")

        # Version history
        versions = state.versions.order_by('-created_at')[:5]
        if versions:
            self.stdout.write(f"\n📜 Recent Versions:")
            for v in versions:
                self.stdout.write(f"   • v{v.version} ({v.trigger_type}) - {v.created_at.strftime('%Y-%m-%d %H:%M')}")

        # Conflicts
        conflicts = state.conflicts.filter(resolved=False)
        if conflicts.exists():
            self.stdout.write(self.style.WARNING(f"\n⚠️  Unresolved Conflicts: {conflicts.count()}"))
            for c in conflicts[:3]:
                self.stdout.write(f"   • [{c.severity}] {c.conflict_type}: {c.description[:50]}...")

        # Exports
        exports = state.exports.order_by('-created_at')[:3]
        if exports:
            self.stdout.write(f"\n📤 Recent Exports:")
            for e in exports:
                self.stdout.write(f"   • {e.export_type}: {e.items_created} items - {e.created_at.strftime('%Y-%m-%d')}")

    def _toggle_lock(self, service: PRDMachineService, file_path: str, lock: bool):
        """Toggle zero-touch mode."""
        prd_state = service.get_or_create_prd_state(file_path)
        prd_state.is_locked = lock
        prd_state.save()

        if lock:
            self.stdout.write(self.style.SUCCESS(
                f"🔒 Zero-touch mode ENABLED for {service.repo}"
            ))
            self.stdout.write("   Human edits will be blocked. The machine is in control.")
        else:
            self.stdout.write(self.style.WARNING(
                f"🔓 Zero-touch mode DISABLED for {service.repo}"
            ))
            self.stdout.write("   Human edits are now allowed.")

    def _generate_prd(self, service: PRDMachineService, options: dict):
        """Generate new PRD from scratch."""
        if options['dry_run']:
            self.stdout.write(self.style.WARNING(
                f"🏃 DRY RUN: Would generate new PRD for {service.repo}"
            ))
            return

        self.stdout.write(f"🔧 Generating new PRD for {service.repo}...")

        try:
            prd_state = service.generate_prd_from_scratch(
                project_name=options['project_name'],
                file_path=options['file_path']
            )

            self.stdout.write(self.style.SUCCESS(
                f"✅ Generated PRD v{prd_state.version}"
            ))
            self.stdout.write(f"   Content length: {len(prd_state.content)} characters")
            self.stdout.write(f"\n📄 Preview (first 500 chars):\n")
            self.stdout.write(prd_state.content[:500] + "...")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Generation failed: {e}"))
            raise

    def _sync_prd(self, service: PRDMachineService, options: dict):
        """Sync PRD from GitHub."""
        if options['dry_run']:
            self.stdout.write(self.style.WARNING(
                f"🏃 DRY RUN: Would sync PRD from {service.repo}:{options['file_path']}"
            ))
            return

        self.stdout.write(f"🔄 Syncing PRD from GitHub: {service.repo}...")

        try:
            prd_state = service.sync_from_github(options['file_path'])

            self.stdout.write(self.style.SUCCESS(
                f"✅ Synced PRD v{prd_state.version}"
            ))
            self.stdout.write(f"   Content hash: {prd_state.content_hash[:12]}...")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Sync failed: {e}"))
            raise

    def _distill_prd(self, service: PRDMachineService, options: dict):
        """Distill/evolve PRD using AI."""
        if options['dry_run']:
            self.stdout.write(self.style.WARNING(
                f"🏃 DRY RUN: Would distill PRD for {service.repo}"
            ))
            return

        prd_state = service.get_or_create_prd_state(options['file_path'])

        self.stdout.write(f"🧠 Distilling PRD with AI...")

        try:
            prd_state = service.distill_prd(
                prd_state=prd_state,
                trigger_type='manual_sync',
                trigger_ref='CLI: prd_machine sync --distill'
            )

            self.stdout.write(self.style.SUCCESS(
                f"✅ Distilled PRD to v{prd_state.version}"
            ))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Distillation failed: {e}"))
            raise

    def _detect_conflicts(self, service: PRDMachineService, file_path: str):
        """Detect conflicts between PRD and repo."""
        prd_state = service.get_or_create_prd_state(file_path)

        self.stdout.write(f"🔍 Detecting conflicts for {service.repo}...")

        try:
            conflicts = service.detect_conflicts(prd_state)

            if not conflicts:
                self.stdout.write(self.style.SUCCESS("✅ No conflicts detected!"))
                return

            self.stdout.write(self.style.WARNING(
                f"⚠️  Found {len(conflicts)} conflicts:"
            ))

            for c in conflicts:
                severity_colors = {
                    'low': self.style.NOTICE,
                    'medium': self.style.WARNING,
                    'high': self.style.ERROR,
                    'critical': self.style.ERROR,
                }
                color = severity_colors.get(c.severity, self.style.WARNING)

                self.stdout.write(color(
                    f"\n   [{c.severity.upper()}] {c.conflict_type}"
                ))
                self.stdout.write(f"   Section: {c.section_affected}")
                self.stdout.write(f"   Description: {c.description}")
                self.stdout.write(f"   Suggestion: {c.suggested_resolution}")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Conflict detection failed: {e}"))
            raise

    def _export_issues(self, service: PRDMachineService, options: dict):
        """Export PRD to GitHub issues."""
        if options['dry_run']:
            self.stdout.write(self.style.WARNING(
                f"🏃 DRY RUN: Would export PRD to issues for {service.repo}"
            ))
            return

        prd_state = service.get_or_create_prd_state(options['file_path'])

        self.stdout.write(f"📤 Exporting PRD to GitHub issues...")

        try:
            export = service.export_to_issues(prd_state)

            self.stdout.write(self.style.SUCCESS(
                f"✅ Created {export.items_created} GitHub issues"
            ))

            if export.github_refs:
                self.stdout.write(f"   Issue numbers: {', '.join(map(str, export.github_refs))}")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Export failed: {e}"))
            raise

    def _export_changelog(self, service: PRDMachineService, options: dict):
        """Generate changelog from PRD."""
        prd_state = service.get_or_create_prd_state(options['file_path'])
        version = options['export_changelog']

        self.stdout.write(f"📝 Generating changelog for v{version}...")

        try:
            export = service.export_to_changelog(prd_state, version)

            self.stdout.write(self.style.SUCCESS(f"✅ Generated changelog:"))
            self.stdout.write(export.details.get('changelog', ''))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Changelog generation failed: {e}"))
            raise

    def _bump_version(self, service: PRDMachineService, options: dict):
        """Bump PRD version."""
        if options['dry_run']:
            self.stdout.write(self.style.WARNING(
                f"🏃 DRY RUN: Would bump version ({options['bump_version']})"
            ))
            return

        prd_state = service.get_or_create_prd_state(options['file_path'])
        old_version = prd_state.version

        new_version = service.bump_version(prd_state, options['bump_version'])

        self.stdout.write(self.style.SUCCESS(
            f"✅ Bumped version: {old_version} → {new_version}"
        ))

    # =========================================================================
    # Cross-Document Sync Methods
    # =========================================================================

    def _align_all_documents(self, service: PRDMachineService, options: dict):
        """Align all documents (PRD, README, IP)."""
        if options['dry_run']:
            self.stdout.write(self.style.WARNING(
                f"🏃 DRY RUN: Would align all documents for {service.repo}"
            ))
            self.stdout.write("   Would sync README.md from PRD.md")
            self.stdout.write("   Would sync IP.md from PRD.md")
            return

        self.stdout.write(f"🔄 Aligning all documents for {service.repo}...")

        try:
            result = service.align_all_documents()

            self.stdout.write(self.style.SUCCESS(f"\n✅ All documents aligned!"))
            self.stdout.write(f"   📄 PRD: v{result['prd'].version} (hash: {result['prd'].content_hash[:8]}...)")
            self.stdout.write(f"   📖 README: synced at {result['readme'].last_aligned_at}")
            self.stdout.write(f"   📋 IP: synced at {result['ip'].last_aligned_at}")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Document alignment failed: {e}"))
            raise

    def _sync_readme(self, service: PRDMachineService, options: dict):
        """Sync README.md from PRD.md."""
        if options['dry_run']:
            self.stdout.write(self.style.WARNING(
                f"🏃 DRY RUN: Would sync README.md from PRD.md for {service.repo}"
            ))
            return

        prd_state = service.get_or_create_prd_state(options['file_path'])

        self.stdout.write(f"📖 Syncing README.md from PRD v{prd_state.version}...")

        try:
            readme_state = service.sync_readme_from_prd(prd_state)

            self.stdout.write(self.style.SUCCESS(
                f"✅ README synced from PRD v{prd_state.version}"
            ))
            self.stdout.write(f"   Content hash: {readme_state.content_hash[:12]}...")
            self.stdout.write(f"   Aligned at: {readme_state.last_aligned_at}")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ README sync failed: {e}"))
            raise

    def _sync_ip(self, service: PRDMachineService, options: dict):
        """Sync IP.md from PRD.md."""
        if options['dry_run']:
            self.stdout.write(self.style.WARNING(
                f"🏃 DRY RUN: Would sync IP.md from PRD.md for {service.repo}"
            ))
            return

        prd_state = service.get_or_create_prd_state(options['file_path'])

        self.stdout.write(f"📋 Syncing IP.md from PRD v{prd_state.version}...")

        try:
            ip_state = service.sync_ip_from_prd(prd_state)

            self.stdout.write(self.style.SUCCESS(
                f"✅ IP synced from PRD v{prd_state.version}"
            ))
            self.stdout.write(f"   Content hash: {ip_state.content_hash[:12]}...")
            self.stdout.write(f"   Aligned at: {ip_state.last_aligned_at}")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ IP sync failed: {e}"))
            raise

    def _detect_drift(self, service: PRDMachineService, options: dict):
        """Detect document drift between PRD, README, and IP."""
        self.stdout.write(f"🔍 Detecting document drift for {service.repo}...")

        try:
            conflicts = service.detect_document_drift()

            if not conflicts:
                self.stdout.write(self.style.SUCCESS(
                    "✅ No document drift detected - all documents are consistent!"
                ))
                return

            self.stdout.write(self.style.WARNING(
                f"\n⚠️  Found {len(conflicts)} document drift issues:"
            ))

            for conflict in conflicts:
                severity_emoji = {
                    'low': '🔵',
                    'medium': '🟡',
                    'high': '🟠',
                    'critical': '🔴',
                }.get(conflict.severity, '⚠️')

                self.stdout.write(f"\n{severity_emoji} [{conflict.severity.upper()}] {conflict.section_affected}")
                self.stdout.write(f"   {conflict.description}")
                self.stdout.write(f"   💡 {conflict.suggested_resolution}")

            self.stdout.write(f"\n📝 Run `--align-all` to fix drift automatically")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Drift detection failed: {e}"))
            raise
