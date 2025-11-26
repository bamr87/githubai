"""
Interactive setup wizard for GitHubAI production deployment.

Guides users through:
1. Provider selection and API key configuration
2. Model preferences
3. Content generation topics
4. Validation and testing
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Interactive setup wizard for GitHubAI production deployment'

    def handle(self, *args, **options):
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.SUCCESS('GitHubAI Setup Wizard'))
        self.stdout.write('=' * 70 + '\n')

        self.stdout.write('This wizard will guide you through setting up GitHubAI.\n')
        self.stdout.write('Steps:')
        self.stdout.write('  1. Configure AI providers and API keys')
        self.stdout.write('  2. Seed AI models')
        self.stdout.write('  3. Generate initial content (optional)')
        self.stdout.write('  4. Validate configuration')
        self.stdout.write('')

        if not self._confirm('Ready to begin?'):
            self.stdout.write('Setup cancelled.')
            return

        # Step 1: Load configuration
        self.stdout.write('\n' + '-' * 70)
        self.stdout.write(self.style.SUCCESS('Step 1: Configure AI Providers'))
        self.stdout.write('-' * 70 + '\n')

        self.stdout.write('This will configure your AI providers and API keys.\n')

        try:
            call_command('load_config_data', interactive=True)
        except KeyboardInterrupt:
            self.stdout.write('\n\nSetup interrupted.')
            return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\nError during configuration: {e}'))
            if not self._confirm('Continue anyway?'):
                return

        # Step 2: Seed models
        self.stdout.write('\n' + '-' * 70)
        self.stdout.write(self.style.SUCCESS('Step 2: Seed AI Models'))
        self.stdout.write('-' * 70 + '\n')

        if self._confirm('Seed standard AI models (GPT-4o, Grok, etc.)?'):
            try:
                call_command('seed_ai_providers', update_keys=True)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error seeding models: {e}'))

        # Step 3: Generate content (optional)
        self.stdout.write('\n' + '-' * 70)
        self.stdout.write(self.style.SUCCESS('Step 3: Generate Initial Content'))
        self.stdout.write('-' * 70 + '\n')

        self.stdout.write('You can generate prompt templates and sample data using AI.\n')

        if self._confirm('Generate initial content?'):
            try:
                call_command('generate_content_data', interactive=True)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error generating content: {e}'))
        else:
            self.stdout.write('Skipping content generation.')
            if self._confirm('Load default prompt templates instead?'):
                try:
                    call_command('seed_prompt_templates')
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error seeding prompts: {e}'))

        # Step 4: Validate
        self.stdout.write('\n' + '-' * 70)
        self.stdout.write(self.style.SUCCESS('Step 4: Validate Configuration'))
        self.stdout.write('-' * 70 + '\n')

        try:
            call_command('validate_config')
        except SystemExit:
            # validate_config may call exit(1) on errors
            self.stdout.write(self.style.WARNING('\nValidation found issues. Please review above.'))

        # Complete
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.SUCCESS('Setup Complete!'))
        self.stdout.write('=' * 70 + '\n')

        self.stdout.write('Next steps:')
        self.stdout.write('  1. Review configuration in Django admin: /admin/core/')
        self.stdout.write('  2. Test AI chat: POST /api/chat/')
        self.stdout.write('  3. Create your first issue: python manage.py create_issue')
        self.stdout.write('\nFor help: python manage.py --help')
        self.stdout.write('')

    def _confirm(self, question: str) -> bool:
        """Ask user for yes/no confirmation."""
        response = input(f'{question} [y/N]: ').lower().strip()
        return response == 'y' or response == 'yes'
