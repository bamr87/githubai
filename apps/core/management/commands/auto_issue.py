"""Management command to automatically create issues from repo analysis"""
from django.core.management.base import BaseCommand
from core.services import AutoIssueService


class Command(BaseCommand):
    help = 'Automatically analyze repository and create GitHub issues for maintenance tasks'

    def add_arguments(self, parser):
        parser.add_argument(
            '--repo',
            type=str,
            default='bamr87/githubai',
            help='GitHub repository in format owner/repo (default: bamr87/githubai)'
        )
        parser.add_argument(
            '--chore-type',
            type=str,
            default='general_review',
            choices=[
                'code_quality',
                'todo_scan',
                'documentation',
                'dependencies',
                'test_coverage',
                'general_review',
            ],
            help='Type of automated analysis to perform'
        )
        parser.add_argument(
            '--files',
            nargs='*',
            default=None,
            help='Optional list of specific files to analyze'
        )
        parser.add_argument(
            '--list-chores',
            action='store_true',
            help='List available chore types and exit'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Analyze without creating GitHub issue'
        )

    def handle(self, *args, **options):
        service = AutoIssueService()

        # List available chore types
        if options['list_chores']:
            self.stdout.write(self.style.SUCCESS('Available chore types:'))
            for chore_type, description in service.list_chore_types().items():
                self.stdout.write(f"  • {chore_type}: {description}")
            return

        try:
            self.stdout.write(
                f"🔍 Running auto-issue analysis: {options['chore_type']}..."
            )

            issue = service.analyze_repo_and_create_issue(
                repo=options['repo'],
                chore_type=options['chore_type'],
                context_files=options['files'],
                auto_submit=not options['dry_run'],
            )

            if options['dry_run']:
                self.stdout.write(self.style.WARNING(
                    f"🏃 Dry run complete - issue not created"
                ))
                self.stdout.write(f"\nGenerated content:\n{issue}")
            else:
                self.stdout.write(self.style.SUCCESS(
                    f"✅ Created auto-issue #{issue.github_issue_number}: {issue.title}"
                ))
                self.stdout.write(f"🔗 URL: {issue.html_url}")
                self.stdout.write(f"🏷️  Labels: {', '.join(issue.labels)}")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error: {str(e)}'))
            raise
