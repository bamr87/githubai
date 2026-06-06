"""Management command to generate AI digests for repos or the fleet."""
from django.core.management.base import BaseCommand

from dashboard.models import Repository
from dashboard.services import FleetDigestService


class Command(BaseCommand):
    help = 'Generate an AI "what needs attention" digest (per-repo or fleet).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--repo', help='Repository (owner/repo) for a single-repo digest.'
        )
        parser.add_argument(
            '--fleet', action='store_true', help='Generate a fleet-wide digest.'
        )
        parser.add_argument(
            '--no-ai', action='store_true',
            help='Use the deterministic rule-based summary instead of calling the AI.',
        )

    def handle(self, *args, **options):
        service = FleetDigestService()
        use_ai = not options['no_ai']

        if options['repo']:
            try:
                repo = Repository.objects.get(full_name=options['repo'])
            except Repository.DoesNotExist:
                self.stderr.write(self.style.ERROR(
                    f"Repository '{options['repo']}' is not registered."
                ))
                return
            digest = service.generate_repo_digest(repo, use_ai=use_ai)
            self.stdout.write(self.style.SUCCESS(f"[{digest.severity}] {digest.title}"))
            self.stdout.write(digest.summary)
            return

        if options['fleet']:
            digest = service.generate_fleet_digest(use_ai=use_ai)
            self.stdout.write(self.style.SUCCESS(f"[{digest.severity}] {digest.title}"))
            self.stdout.write(digest.summary)
            return

        self.stdout.write(self.style.WARNING('Specify --repo <owner/repo> or --fleet.'))
