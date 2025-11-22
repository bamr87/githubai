"""Management command to bump version"""
from django.core.management.base import BaseCommand
from core.services import VersioningService


class Command(BaseCommand):
    help = 'Bump semantic version based on commit messages'

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            choices=['major', 'minor', 'patch'],
            help='Force specific bump type (overrides commit message)'
        )
        parser.add_argument(
            '--skip-tag',
            action='store_true',
            help='Skip creating git tag'
        )

    def handle(self, *args, **options):
        service = VersioningService()

        try:
            self.stdout.write('Processing version bump...')
            version = service.process_version_bump()

            self.stdout.write(self.style.SUCCESS(
                f'✅ Version bumped to {version.version_number}'
            ))
            self.stdout.write(f'Bump type: {version.bump_type}')
            self.stdout.write(f'Commit: {version.commit_sha[:7]}')

            if not options['skip_tag']:
                self.stdout.write('Creating git tag...')
                service.create_git_tag(version)
                self.stdout.write(self.style.SUCCESS(
                    f'✅ Created git tag: {version.git_tag}'
                ))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error: {str(e)}'))
            raise
