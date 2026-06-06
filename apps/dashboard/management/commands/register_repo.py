"""Management command to register a repository in the cockpit."""
from django.core.management.base import BaseCommand, CommandError

from dashboard.services import RepositoryService


class Command(BaseCommand):
    help = 'Register a repository (owner/repo) in the DevOps cockpit watchlist.'

    def add_arguments(self, parser):
        parser.add_argument('--repo', required=True, help='Repository in owner/repo format')
        parser.add_argument(
            '--no-track', action='store_true',
            help='Register without adding to the active ingestion watchlist',
        )

    def handle(self, *args, **options):
        repo_name = options['repo']
        try:
            repo = RepositoryService().register_repository(
                repo_name, is_tracked=not options['no_track']
            )
        except ValueError as e:
            raise CommandError(str(e))

        self.stdout.write(self.style.SUCCESS(
            f"Registered {repo.full_name} (tracked={repo.is_tracked})"
        ))
