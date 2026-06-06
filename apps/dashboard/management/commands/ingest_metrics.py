"""Management command to ingest metrics snapshots for tracked repositories."""
from django.core.management.base import BaseCommand

from dashboard.models import Repository
from dashboard.services import MetricsCollectorService, RepositoryService


class Command(BaseCommand):
    help = 'Collect a metrics snapshot for one repository or all tracked repos.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--repo', help='Single repository (owner/repo). Omit to ingest all tracked repos.'
        )

    def handle(self, *args, **options):
        collector = MetricsCollectorService()

        if options['repo']:
            repos = Repository.objects.filter(full_name=options['repo'])
            if not repos.exists():
                self.stderr.write(self.style.ERROR(
                    f"Repository '{options['repo']}' is not registered. "
                    "Run register_repo first."
                ))
                return
        else:
            repos = RepositoryService.tracked_repositories()

        count = 0
        for repo in repos:
            snapshot = collector.collect_snapshot(repo)
            count += 1
            self.stdout.write(self.style.SUCCESS(
                f"{repo.full_name}: snapshot #{snapshot.id} "
                f"(health={snapshot.health_score})"
            ))

        self.stdout.write(self.style.SUCCESS(f"Collected {count} snapshot(s)."))
