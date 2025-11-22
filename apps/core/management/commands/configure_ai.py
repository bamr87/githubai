"""Management command to configure AI providers"""
import os
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Configure AI provider settings'

    def add_arguments(self, parser):
        parser.add_argument(
            '--show-config',
            action='store_true',
            help='Show current AI provider configuration'
        )
        parser.add_argument(
            '--set-provider',
            type=str,
            choices=['openai', 'xai'],
            help='Set the default AI provider'
        )
        parser.add_argument(
            '--check-keys',
            action='store_true',
            help='Check which API keys are configured'
        )

    def handle(self, *args, **options):
        if options['show_config']:
            self.show_config()
        elif options['set_provider']:
            self.set_provider(options['set_provider'])
        elif options['check_keys']:
            self.check_keys()
        else:
            self.stdout.write(
                self.style.ERROR('Please specify --show-config, --set-provider, or --check-keys')
            )

    def show_config(self):
        """Show current AI configuration"""
        self.stdout.write(self.style.SUCCESS('Current AI Provider Configuration:'))
        self.stdout.write(f'Active Provider: {settings.AI_PROVIDER}')

        self.stdout.write('\\nOpenAI Configuration:')
        self.stdout.write(f'  Model: {settings.OPENAI_MODEL}')
        self.stdout.write(f'  Temperature: {settings.OPENAI_TEMPERATURE}')
        self.stdout.write(f'  Max Tokens: {settings.OPENAI_MAX_TOKENS}')
        self.stdout.write(f'  Base URL: {settings.OPENAI_BASE_URL}')
        self.stdout.write(f'  API Key: {"✅ Set" if settings.OPENAI_API_KEY else "❌ Not set"}')

        self.stdout.write('\\nXAI Configuration:')
        self.stdout.write(f'  Model: {settings.XAI_MODEL}')
        self.stdout.write(f'  Temperature: {settings.XAI_TEMPERATURE}')
        self.stdout.write(f'  Max Tokens: {settings.XAI_MAX_TOKENS}')
        self.stdout.write(f'  Base URL: {settings.XAI_BASE_URL}')
        self.stdout.write(f'  API Key: {"✅ Set" if settings.XAI_API_KEY else "❌ Not set"}')

    def set_provider(self, provider_name):
        """Set the default AI provider in .env file"""
        env_file_path = os.path.join(settings.BASE_DIR, '.env')

        if not os.path.exists(env_file_path):
            self.stdout.write(self.style.ERROR('.env file not found'))
            return

        # Read current .env content
        with open(env_file_path, 'r') as f:
            lines = f.readlines()

        # Update or add AI_PROVIDER line
        provider_line_updated = False
        new_lines = []

        for line in lines:
            if line.startswith('AI_PROVIDER='):
                new_lines.append(f'AI_PROVIDER={provider_name}\\n')
                provider_line_updated = True
            else:
                new_lines.append(line)

        # Add AI_PROVIDER if it wasn't found
        if not provider_line_updated:
            new_lines.append(f'AI_PROVIDER={provider_name}\\n')

        # Write back to .env file
        with open(env_file_path, 'w') as f:
            f.writelines(new_lines)

        self.stdout.write(
            self.style.SUCCESS(f'✅ Default AI provider set to: {provider_name}')
        )
        self.stdout.write(
            self.style.WARNING('Note: Restart the application for changes to take effect.')
        )

    def check_keys(self):
        """Check which API keys are configured"""
        self.stdout.write(self.style.SUCCESS('API Key Configuration Status:'))

        keys_status = {
            'OpenAI': settings.OPENAI_API_KEY,
            'XAI': settings.XAI_API_KEY,
            'GitHub': settings.GITHUB_TOKEN,
        }

        for service, key in keys_status.items():
            status = "✅ Configured" if key else "❌ Not configured"
            if key:
                # Show partial key for security
                partial_key = f"{key[:8]}...{key[-4:]}" if len(key) > 12 else "***"
                self.stdout.write(f'  {service}: {status} ({partial_key})')
            else:
                self.stdout.write(f'  {service}: {status}')

        # Recommendations
        self.stdout.write('\\nRecommendations:')
        if not settings.OPENAI_API_KEY and not settings.XAI_API_KEY:
            self.stdout.write('  ⚠️  No AI provider API keys configured!')
            self.stdout.write('     Set OPENAI_API_KEY or XAI_API_KEY in your .env file')

        if not settings.GITHUB_TOKEN:
            self.stdout.write('  ⚠️  GitHub token not configured!')
            self.stdout.write('     Set GITHUB_TOKEN in your .env file for GitHub API access')