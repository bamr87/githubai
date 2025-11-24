"""Management command to test prompt template functionality"""
from django.core.management.base import BaseCommand
from jinja2 import Template
from core.models import PromptTemplate


class Command(BaseCommand):
    help = 'Test prompt template functionality'

    def handle(self, *args, **options):
        """Run prompt template tests"""

        # Test 1: List all templates
        self.stdout.write("=" * 60)
        self.stdout.write("TEST 1: List All Prompt Templates")
        self.stdout.write("=" * 60)
        templates = PromptTemplate.objects.all()
        for template in templates:
            self.stdout.write(
                f"- {template.name} (Category: {template.category}, Version: {template.version_number})"
            )

        # Test 2: Get a specific template
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("TEST 2: Get Chat Assistant Template")
        self.stdout.write("=" * 60)
        chat_template = PromptTemplate.objects.get(name='Chat Assistant', is_active=True)
        self.stdout.write(f"Name: {chat_template.name}")
        self.stdout.write(f"Category: {chat_template.category}")
        self.stdout.write(f"System Prompt: {chat_template.system_prompt[:100]}...")
        self.stdout.write(f"User Prompt Template: {chat_template.user_prompt_template}")
        self.stdout.write(f"Model: {chat_template.model}")
        self.stdout.write(f"Provider: {chat_template.provider}")

        # Test 3: Test Jinja2 rendering
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("TEST 3: Test Jinja2 Template Rendering")
        self.stdout.write("=" * 60)

        # Test with Auto Issue template
        auto_issue_template = PromptTemplate.objects.get(name='Auto Issue Generator', is_active=True)
        context = {
            'repo': 'bamr87/githubai',
            'chore_type': 'code_quality',
            'analysis_data': 'Sample analysis data here...'
        }

        user_template = Template(auto_issue_template.user_prompt_template)
        rendered = user_template.render(**context)
        self.stdout.write(f"Template: {auto_issue_template.name}")
        self.stdout.write(f"Context: {context}")
        self.stdout.write(f"Rendered:\n{rendered}")

        # Test 4: Check template with Feedback Issue
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("TEST 4: Test Feedback Issue Template with Files")
        self.stdout.write("=" * 60)
        feedback_template = PromptTemplate.objects.get(name='Feedback Issue Creator', is_active=True)
        context = {
            'feedback_type': 'bug',
            'summary': 'Chat interface not loading',
            'description': 'The chat interface fails to load on mobile devices',
            'context_files': ['frontend/src/App.jsx', 'frontend/src/index.css']
        }

        user_template = Template(feedback_template.user_prompt_template)
        rendered = user_template.render(**context)
        self.stdout.write(f"Template: {feedback_template.name}")
        self.stdout.write(f"Rendered:\n{rendered}")

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("All tests completed successfully!"))
        self.stdout.write("=" * 60)
