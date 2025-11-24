"""Management command to seed initial prompt templates from hardcoded prompts"""
from django.core.management.base import BaseCommand
from core.models import PromptTemplate


class Command(BaseCommand):
    help = 'Seed initial prompt templates from existing hardcoded prompts'

    def handle(self, *args, **options):
        """Create initial prompt templates"""

        templates_created = 0
        templates_updated = 0

        # Define all initial prompt templates
        initial_templates = [
            {
                'name': 'Chat Assistant',
                'category': 'chat',
                'description': 'General purpose AI assistant for GitHubAI chat interface',
                'system_prompt': (
                    'You are a helpful AI assistant integrated with GitHubAI. '
                    'You can help users with questions about GitHub automation, '
                    'issue management, and general programming topics.'
                ),
                'user_prompt_template': '{{ message }}',
                'model': 'gpt-4o-mini',
                'provider': 'auto',
                'temperature': 0.2,
                'max_tokens': 2500,
            },
            {
                'name': 'Auto Issue Generator',
                'category': 'auto_issue',
                'description': 'Generate GitHub issues from repository analysis',
                'system_prompt': (
                    'You are a software engineering assistant that creates detailed GitHub issues '
                    'for repository maintenance and improvements. Based on the analysis data provided, '
                    'generate a clear, actionable GitHub issue in Markdown format. Include:\n'
                    '- A summary of findings\n'
                    '- Specific recommendations with file references\n'
                    '- Prioritized action items\n'
                    '- Expected benefits of addressing these items\n\n'
                    'Format the issue professionally with proper Markdown sections.'
                ),
                'user_prompt_template': (
                    'Repository: {{ repo }}\n'
                    'Analysis Type: {{ chore_type }}\n\n'
                    '{{ analysis_data }}'
                ),
                'model': 'gpt-4o-mini',
                'provider': 'auto',
                'temperature': 0.2,
                'max_tokens': 3000,
            },
            {
                'name': 'Feedback Issue Creator',
                'category': 'feedback_issue',
                'description': 'Convert user feedback into well-structured GitHub issues',
                'system_prompt': (
                    'You are an assistant that converts raw user feedback about a GitHub '
                    'project into a well-structured GitHub issue. '
                    'Return GitHub-flavored Markdown with clear sections such as Summary, '
                    'Details, Steps to Reproduce (for bugs), Expected vs Actual, or '
                    'Motivation and Acceptance Criteria (for features). Do not include '
                    'front-matter or YAML, only the Markdown body.'
                ),
                'user_prompt_template': (
                    'Feedback Type: {{ feedback_type }}\n'
                    'Summary: {{ summary }}\n'
                    'Description: {{ description }}\n\n'
                    '{% if context_files %}'
                    'Relevant Files:\n'
                    '{% for file in context_files %}'
                    '- {{ file }}\n'
                    '{% endfor %}'
                    '{% endif %}'
                ),
                'model': 'gpt-4o-mini',
                'provider': 'auto',
                'temperature': 0.3,
                'max_tokens': 2500,
            },
            {
                'name': 'Documentation Generator',
                'category': 'documentation',
                'description': 'Generate documentation from code files',
                'system_prompt': 'You are an expert software documenter.',
                'user_prompt_template': (
                    'Generate clear, comprehensive documentation for the following code:\n\n'
                    '{{ code_content }}\n\n'
                    'File: {{ file_path }}\n'
                    'Language: {{ language }}'
                ),
                'model': 'gpt-4o-mini',
                'provider': 'auto',
                'temperature': 0.2,
                'max_tokens': 3000,
            },
            {
                'name': 'README Update Generator',
                'category': 'readme_update',
                'description': 'Generate README updates based on parent issue context',
                'system_prompt': (
                    'You are a technical writer assistant that helps update README files. '
                    'Based on the parent issue context and existing README content, '
                    'generate a comprehensive update that improves documentation clarity, '
                    'accuracy, and completeness.'
                ),
                'user_prompt_template': (
                    'Parent Issue:\n{{ parent_issue }}\n\n'
                    '{% if readme_content %}'
                    'Current README:\n{{ readme_content }}\n\n'
                    '{% endif %}'
                    '{% if additional_files %}'
                    'Additional Context Files:\n'
                    '{% for file in additional_files %}'
                    '- {{ file }}\n'
                    '{% endfor %}'
                    '{% endif %}'
                ),
                'model': 'gpt-4o-mini',
                'provider': 'auto',
                'temperature': 0.3,
                'max_tokens': 4000,
            },
            {
                'name': 'Sub-Issue Generator',
                'category': 'sub_issue',
                'description': 'Generate sub-issues from parent issue using templates',
                'system_prompt': (
                    'You are a project management assistant that breaks down large issues '
                    'into actionable sub-tasks. Generate a well-structured sub-issue '
                    'that addresses a specific aspect of the parent issue.'
                ),
                'user_prompt_template': (
                    'Parent Issue:\n{{ parent_issue }}\n\n'
                    'Template Instructions:\n{{ template_instructions }}\n\n'
                    '{% if file_refs %}'
                    'Referenced Files:\n'
                    '{% for file in file_refs %}'
                    '- {{ file }}\n'
                    '{% endfor %}'
                    '{% endif %}'
                ),
                'model': 'gpt-4o-mini',
                'provider': 'auto',
                'temperature': 0.2,
                'max_tokens': 2500,
            },
        ]

        # Create or update templates
        for template_data in initial_templates:
            name = template_data['name']

            # Check if template already exists
            existing = PromptTemplate.objects.filter(name=name).first()

            if existing:
                # Update existing template
                for key, value in template_data.items():
                    if key != 'name':
                        setattr(existing, key, value)
                existing.save()
                templates_updated += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Updated template: {name}')
                )
            else:
                # Create new template
                PromptTemplate.objects.create(**template_data)
                templates_created += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created template: {name}')
                )

        # Summary
        self.stdout.write(
            self.style.SUCCESS(
                f'\nSeeding complete: {templates_created} created, {templates_updated} updated'
            )
        )
