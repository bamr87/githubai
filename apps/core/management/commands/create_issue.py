"""Management command to create issues"""
from django.core.management.base import BaseCommand
from core.services import IssueService


class Command(BaseCommand):
    help = 'Create GitHub issues with AI-generated content'

    def add_arguments(self, parser):
        parser.add_argument(
            '--repo',
            type=str,
            required=True,
            help='GitHub repository in format owner/repo'
        )
        parser.add_argument(
            '--parent',
            type=int,
            dest='parent_issue_number',
            help='Parent issue number for sub-issue creation'
        )
        parser.add_argument(
            '--issue-number',
            type=int,
            help='Issue number for README update'
        )
        parser.add_argument(
            '--file-refs',
            nargs='*',
            default=[],
            help='Optional file references'
        )
        parser.add_argument(
            '--readme-update',
            action='store_true',
            help='Create README update issue'
        )

    def handle(self, *args, **options):
        service = IssueService()

        try:
            if options['readme_update'] and options['issue_number']:
                # Create README update issue
                self.stdout.write('Creating README update issue...')
                issue = service.create_readme_update_issue(
                    repo=options['repo'],
                    issue_number=options['issue_number']
                )
                self.stdout.write(self.style.SUCCESS(
                    f'✅ Created README update issue: {issue.html_url}'
                ))

            elif options['parent_issue_number']:
                # Create sub-issue
                self.stdout.write('Creating sub-issue...')
                issue = service.create_sub_issue_from_template(
                    repo=options['repo'],
                    parent_issue_number=options['parent_issue_number'],
                    file_refs=options['file_refs']
                )
                self.stdout.write(self.style.SUCCESS(
                    f'✅ Created sub-issue: {issue.html_url}'
                ))

            else:
                self.stdout.write(self.style.ERROR(
                    'Error: Either --parent or --readme-update with --issue-number must be specified'
                ))
                return

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error: {str(e)}'))
            raise
