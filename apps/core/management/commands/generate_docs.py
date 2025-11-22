"""Management command to generate documentation"""
from django.core.management.base import BaseCommand
from core.services import DocGenerationService, ChangelogService


class Command(BaseCommand):
    help = 'Generate documentation from code files or commits'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            help='Python file to parse and generate docs'
        )
        parser.add_argument(
            '--commit',
            action='store_true',
            help='Generate changelog from latest commit'
        )
        parser.add_argument(
            '--pr',
            type=int,
            help='Generate changelog from pull request number'
        )
        parser.add_argument(
            '--repo',
            type=str,
            help='Repository name (for PR mode)'
        )

    def handle(self, *args, **options):
        try:
            if options['file']:
                # Parse Python file
                self.stdout.write(f"Parsing file: {options['file']}")
                service = DocGenerationService()
                doc_file = service.process_file(options['file'])
                self.stdout.write(self.style.SUCCESS(
                    f"✅ Generated documentation for {doc_file.file_path}"
                ))
                self.stdout.write(f"\n{doc_file.markdown_content}")

            elif options['commit']:
                # Generate from commit
                self.stdout.write("Generating changelog from commit...")
                service = ChangelogService()
                entry = service.generate_from_commit()
                self.stdout.write(self.style.SUCCESS(
                    f"✅ Generated changelog entry for commit {entry.commit_sha[:7]}"
                ))
                self.stdout.write(f"\n{entry.ai_generated_content}")

            elif options['pr']:
                # Generate from PR
                self.stdout.write(f"Generating changelog from PR #{options['pr']}...")
                service = ChangelogService()
                entry = service.generate_from_pr(
                    options['pr'],
                    options.get('repo')
                )
                self.stdout.write(self.style.SUCCESS(
                    f"✅ Generated changelog entry for PR #{entry.pr_number}"
                ))
                self.stdout.write(f"\n{entry.ai_generated_content}")

            else:
                self.stdout.write(self.style.ERROR(
                    'Error: Specify --file, --commit, or --pr'
                ))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error: {str(e)}'))
            raise
