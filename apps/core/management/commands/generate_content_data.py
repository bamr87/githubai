"""
Management command to generate content data using AI.

Generates content data (Category 2) like:
- PromptTemplates
- IssueTemplates
- Sample Issues
- Sample executions

Can accept:
- Interactive prompts (--interactive)
- YAML prompt file (--prompt-file)
- Exports results as JSON fixture

This is separate from critical configuration (load_config_data.py).
"""
import json
import logging
import yaml
from pathlib import Path
from typing import Dict, List, Optional

from django.core.management.base import BaseCommand, CommandError
from django.core import serializers
from django.conf import settings

from core.models import (
    PromptTemplate,
    IssueTemplate,
    Issue,
    AIProvider,
    AIModel,
)
from core.services import AIService

logger = logging.getLogger('githubai')


class Command(BaseCommand):
    help = 'Generate content data using AI (prompts, templates, sample issues)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--interactive',
            action='store_true',
            help='Interactive mode - prompt for generation preferences',
        )
        parser.add_argument(
            '--prompt-file',
            type=str,
            help='Path to YAML file with generation instructions',
        )
        parser.add_argument(
            '--output',
            type=str,
            default='apps/core/fixtures/generated_content_data.json',
            help='Output path for generated fixture (default: apps/core/fixtures/generated_content_data.json)',
        )
        parser.add_argument(
            '--count',
            type=int,
            help='Number of items to generate per type',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview what would be generated without creating database records',
        )
        parser.add_argument(
            '--provider',
            type=str,
            help='AI provider to use for generation (default: auto)',
        )

    def handle(self, *args, **options):
        self.interactive = options['interactive']
        self.prompt_file = options.get('prompt_file')
        self.output_path = Path(options['output'])
        self.count = options.get('count')
        self.dry_run = options['dry_run']
        self.provider_name = options.get('provider')

        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.SUCCESS('AI-Powered Content Data Generation'))
        self.stdout.write('=' * 70 + '\n')

        if self.dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No database changes will be made\n'))

        # Check AI service availability
        if not self._check_ai_available():
            return

        # Load generation instructions
        if self.prompt_file:
            instructions = self._load_prompt_file()
        elif self.interactive:
            instructions = self._interactive_prompt()
        else:
            raise CommandError('Must specify either --interactive or --prompt-file')

        # Generate content
        generated_objects = []

        if instructions.get('generate_prompt_templates'):
            generated_objects.extend(
                self._generate_prompt_templates(instructions['prompt_templates'])
            )

        if instructions.get('generate_issue_templates'):
            generated_objects.extend(
                self._generate_issue_templates(instructions['issue_templates'])
            )

        if instructions.get('generate_sample_issues'):
            generated_objects.extend(
                self._generate_sample_issues(instructions['sample_issues'])
            )

        # Export to fixture
        if generated_objects and not self.dry_run:
            self._export_fixture(generated_objects)

        # Summary
        self._print_summary(generated_objects)

    def _check_ai_available(self) -> bool:
        """Check if AI service is configured and available."""
        self.stdout.write('Checking AI service availability...')

        try:
            providers = AIProvider.objects.filter(is_active=True)

            if self.provider_name:
                providers = providers.filter(name=self.provider_name)

            if not providers.exists():
                self.stdout.write(
                    self.style.ERROR(
                        '✗ No active AI providers configured. Run load_config_data first.'
                    )
                )
                return False

            provider = providers.first()
            if not provider.has_api_key:
                self.stdout.write(
                    self.style.ERROR(
                        f'✗ Provider {provider.display_name} missing API key'
                    )
                )
                return False

            self.stdout.write(
                self.style.SUCCESS(f'✓ Using provider: {provider.display_name}')
            )
            return True

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Error checking AI availability: {e}'))
            return False

    def _load_prompt_file(self) -> Dict:
        """Load generation instructions from YAML file."""
        prompt_path = Path(self.prompt_file)
        if not prompt_path.exists():
            raise CommandError(f'Prompt file not found: {self.prompt_file}')

        self.stdout.write(f'Loading instructions from: {self.prompt_file}\n')

        try:
            with open(prompt_path, 'r') as f:
                instructions = yaml.safe_load(f)
            return instructions
        except yaml.YAMLError as e:
            raise CommandError(f'Invalid YAML in prompt file: {e}')

    def _interactive_prompt(self) -> Dict:
        """Interactive prompts for generation preferences."""
        self.stdout.write(self.style.SUCCESS('Interactive Content Generation\n'))

        instructions = {
            'generate_prompt_templates': False,
            'generate_issue_templates': False,
            'generate_sample_issues': False,
            'prompt_templates': {},
            'issue_templates': {},
            'sample_issues': {},
        }

        # Ask what to generate
        self.stdout.write('What would you like to generate?\n')

        generate_prompts = input('  Generate PromptTemplates? [y/N]: ').lower() == 'y'
        instructions['generate_prompt_templates'] = generate_prompts

        if generate_prompts:
            count = input('  How many prompt templates? [3]: ').strip()
            count = int(count) if count else 3

            categories = input('  Categories (comma-separated) [chat,auto_issue,documentation]: ').strip()
            categories = categories.split(',') if categories else ['chat', 'auto_issue', 'documentation']

            instructions['prompt_templates'] = {
                'count': count,
                'categories': categories,
            }

        generate_issue_templates = input('  Generate IssueTemplates? [y/N]: ').lower() == 'y'
        instructions['generate_issue_templates'] = generate_issue_templates

        if generate_issue_templates:
            count = input('  How many issue templates? [2]: ').strip()
            count = int(count) if count else 2

            instructions['issue_templates'] = {
                'count': count,
            }

        generate_issues = input('  Generate sample Issues? [y/N]: ').lower() == 'y'
        instructions['generate_sample_issues'] = generate_issues

        if generate_issues:
            count = input('  How many sample issues? [5]: ').strip()
            count = int(count) if count else 5

            repo = input('  Repository [bamr87/githubai]: ').strip()
            repo = repo if repo else 'bamr87/githubai'

            instructions['sample_issues'] = {
                'count': count,
                'repo': repo,
            }

        return instructions

    def _generate_prompt_templates(self, config: Dict) -> List:
        """Generate PromptTemplate instances using AI."""
        self.stdout.write('\nGenerating PromptTemplates...')

        count = config.get('count', 3)
        categories = config.get('categories', ['chat', 'auto_issue', 'documentation'])

        generated = []
        ai_service = AIService()

        for i, category in enumerate(categories):
            if i >= count:
                break

            self.stdout.write(f'  Generating template for category: {category}')

            # Use AI to generate prompt template content
            system_prompt = (
                "You are an expert at creating AI prompt templates. "
                "Generate a well-structured prompt template with system and user prompts."
            )

            user_prompt = f"""Create a PromptTemplate for category: {category}

Return a JSON object with these fields:
- name: A descriptive name (e.g., "Customer Support Chat")
- description: What this prompt does
- system_prompt: System-level instructions for the AI
- user_prompt_template: User prompt with Jinja2 variables (use {{ variable_name }} syntax)

Make it professional and production-ready."""

            try:
                if not self.dry_run:
                    response = ai_service.call_ai_chat(
                        system_prompt=system_prompt,
                        user_prompt=user_prompt,
                        temperature=0.7,
                    )

                    # Parse JSON response
                    import json
                    template_data = json.loads(response)

                    # Create PromptTemplate
                    template = PromptTemplate.objects.create(
                        name=template_data['name'],
                        category=category,
                        description=template_data['description'],
                        system_prompt=template_data['system_prompt'],
                        user_prompt_template=template_data['user_prompt_template'],
                        model='gpt-4o-mini',
                        provider='auto',
                        temperature=0.2,
                        max_tokens=2500,
                        version_number=1,
                        is_active=True,
                    )

                    generated.append(template)
                    self.stdout.write(self.style.SUCCESS(f'    ✓ Created: {template.name}'))
                else:
                    self.stdout.write(f'    → Would generate {category} template')

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'    ✗ Error: {e}'))
                logger.error(f'Failed to generate prompt template: {e}')

        return generated

    def _generate_issue_templates(self, config: Dict) -> List:
        """Generate IssueTemplate instances using AI."""
        self.stdout.write('\nGenerating IssueTemplates...')

        count = config.get('count', 2)
        generated = []

        ai_service = AIService()

        for i in range(count):
            self.stdout.write(f'  Generating issue template {i+1}/{count}')

            system_prompt = "You are an expert at creating GitHub issue templates."
            user_prompt = f"""Create an IssueTemplate for common software project needs.

Return a JSON object with:
- name: Template filename (e.g., "bug_report.md")
- about: Description of what this template is for
- title_prefix: Prefix for issue titles (e.g., "[Bug]: ")
- labels: Array of label strings (e.g., ["bug", "needs-triage"])
- prompt: AI instructions for generating issue content
- template_body: Markdown structure for the issue body

Make it professional and useful."""

            try:
                if not self.dry_run:
                    response = ai_service.call_ai_chat(
                        system_prompt=system_prompt,
                        user_prompt=user_prompt,
                        temperature=0.7,
                    )

                    template_data = json.loads(response)

                    template = IssueTemplate.objects.create(
                        name=template_data['name'],
                        about=template_data['about'],
                        title_prefix=template_data.get('title_prefix', '[Generated]: '),
                        labels=template_data.get('labels', []),
                        prompt=template_data['prompt'],
                        template_body=template_data['template_body'],
                        include_files=[],
                        is_active=True,
                    )

                    generated.append(template)
                    self.stdout.write(self.style.SUCCESS(f'    ✓ Created: {template.name}'))
                else:
                    self.stdout.write(f'    → Would generate issue template {i+1}')

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'    ✗ Error: {e}'))

        return generated

    def _generate_sample_issues(self, config: Dict) -> List:
        """Generate sample Issue instances using AI."""
        self.stdout.write('\nGenerating sample Issues...')

        count = config.get('count', 5)
        repo = config.get('repo', 'bamr87/githubai')
        generated = []

        # For dry-run, just show what would be generated
        if self.dry_run:
            self.stdout.write(f'  → Would generate {count} sample issues for {repo}')
            return []

        self.stdout.write(f'  Generating {count} sample issues for {repo}')
        self.stdout.write(self.style.WARNING('  Note: These are database-only records, not created on GitHub'))

        for i in range(count):
            issue = Issue.objects.create(
                github_repo=repo,
                github_issue_number=1000 + i,  # Fake issue numbers
                title=f'Sample Issue {i+1}: Generated for testing',
                body=f'This is a sample issue generated for testing purposes.\n\n**Issue Number**: {i+1}\n**Repository**: {repo}',
                issue_type='other',
                labels=['sample', 'generated'],
                state='open',
                ai_generated=True,
            )

            generated.append(issue)

        self.stdout.write(self.style.SUCCESS(f'    ✓ Created {len(generated)} sample issues'))

        return generated

    def _export_fixture(self, objects: List):
        """Export generated objects to JSON fixture."""
        self.stdout.write(f'\nExporting to fixture: {self.output_path}')

        # Ensure directory exists
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

        # Serialize objects
        fixture_data = serializers.serialize('json', objects, indent=2)

        # Write to file
        with open(self.output_path, 'w') as f:
            f.write(fixture_data)

        self.stdout.write(self.style.SUCCESS(f'  ✓ Exported {len(objects)} objects'))
        self.stdout.write(f'  File: {self.output_path}')

    def _print_summary(self, objects: List):
        """Print generation summary."""
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write('Generation Summary')
        self.stdout.write('=' * 70)

        # Count by type
        from collections import Counter
        type_counts = Counter([type(obj).__name__ for obj in objects])

        self.stdout.write(f'\nTotal objects generated: {len(objects)}')
        for obj_type, count in type_counts.items():
            self.stdout.write(f'  {obj_type}: {count}')

        if not self.dry_run and objects:
            self.stdout.write(f'\nFixture exported to: {self.output_path}')
            self.stdout.write('\nTo load this fixture:')
            self.stdout.write(f'  python manage.py loaddata {self.output_path}')

        self.stdout.write('\n' + '=' * 70)
