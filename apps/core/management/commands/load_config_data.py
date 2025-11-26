"""
Management command to load critical technical configuration data.

Loads API keys, provider settings, and model configurations from:
- Environment variables (.env file)
- Secrets files (infra/secrets/)
- Interactive prompts (--interactive flag)
- JSON configuration files (--config-file)

This handles CRITICAL configuration only (Category 1 data).
For content data generation, use generate_content_data.py instead.
"""
import json
import os
import sys
from pathlib import Path
from typing import Dict, Optional

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from core.models import AIProvider, AIModel


class Command(BaseCommand):
    help = 'Load critical technical configuration (API keys, providers, models)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--interactive',
            action='store_true',
            help='Interactive mode - prompt for all configuration values',
        )
        parser.add_argument(
            '--non-interactive',
            action='store_true',
            help='Non-interactive mode - only use env vars/files, fail if missing',
        )
        parser.add_argument(
            '--config-file',
            type=str,
            help='Path to JSON configuration file',
        )
        parser.add_argument(
            '--secrets-dir',
            type=str,
            default='infra/secrets',
            help='Directory containing secrets files (default: infra/secrets)',
        )
        parser.add_argument(
            '--update-keys-only',
            action='store_true',
            help='Only update API keys for existing providers',
        )
        parser.add_argument(
            '--test',
            action='store_true',
            help='Load test configuration (minimal, no real API keys)',
        )
        parser.add_argument(
            '--validate',
            action='store_true',
            help='Run validation after loading configuration',
        )

    def handle(self, *args, **options):
        self.interactive = options['interactive']
        self.non_interactive = options['non_interactive']
        self.config_file = options['config_file']
        self.secrets_dir = Path(options['secrets_dir'])
        self.update_keys_only = options['update_keys_only']
        self.test_mode = options['test']
        self.validate = options['validate']

        if self.interactive and self.non_interactive:
            raise CommandError('Cannot use both --interactive and --non-interactive')

        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.SUCCESS('Loading Critical Configuration Data'))
        self.stdout.write('=' * 70 + '\n')

        # Load configuration
        if self.test_mode:
            self._load_test_config()
        elif self.config_file:
            self._load_from_file()
        else:
            self._load_from_sources()

        # Summary
        self._print_summary()

        # Validate if requested
        if self.validate:
            self.stdout.write('\nRunning validation...')
            from django.core.management import call_command
            call_command('validate_config')

    def _load_test_config(self):
        """Load minimal test configuration without real API keys."""
        self.stdout.write(self.style.WARNING('Loading TEST configuration (no real API keys)'))

        providers_config = [
            {
                'name': 'openai',
                'display_name': 'OpenAI (Test)',
                'api_key': 'test-openai-key',
                'base_url': 'https://api.openai.com/v1',
                'default_temperature': 0.2,
                'default_max_tokens': 2500,
                'is_active': True,
            },
            {
                'name': 'xai',
                'display_name': 'XAI (Test)',
                'api_key': 'test-xai-key',
                'base_url': 'https://api.x.ai/v1',
                'default_temperature': 0.2,
                'default_max_tokens': 2500,
                'is_active': False,
            },
        ]

        for config in providers_config:
            self._create_or_update_provider(config)

    def _load_from_file(self):
        """Load configuration from JSON file."""
        config_path = Path(self.config_file)
        if not config_path.exists():
            raise CommandError(f'Configuration file not found: {self.config_file}')

        self.stdout.write(f'Loading configuration from: {self.config_file}')

        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            raise CommandError(f'Invalid JSON in configuration file: {e}')

        if 'providers' not in config:
            raise CommandError('Configuration file must contain "providers" key')

        for provider_config in config['providers']:
            self._create_or_update_provider(provider_config)

            # Create models if specified
            if 'models' in provider_config:
                provider = AIProvider.objects.get(name=provider_config['name'])
                for model_config in provider_config['models']:
                    self._create_or_update_model(provider, model_config)

    def _load_from_sources(self):
        """Load configuration from environment variables and secrets files."""
        # Try environment variables first
        self._load_openai()
        self._load_xai()
        self._load_anthropic()

    def _load_openai(self):
        """Load OpenAI configuration."""
        api_key = self._get_config_value(
            'OPENAI_API_KEY',
            'Enter OpenAI API Key',
            secret=True
        )

        if not api_key and not self.interactive:
            self.stdout.write(self.style.WARNING('  → Skipping OpenAI (no API key)'))
            return

        if not api_key:
            return

        provider_config = {
            'name': 'openai',
            'display_name': 'OpenAI',
            'api_key': api_key,
            'base_url': self._get_config_value(
                'OPENAI_BASE_URL',
                'OpenAI Base URL',
                default='https://api.openai.com/v1'
            ),
            'default_temperature': float(self._get_config_value(
                'OPENAI_TEMPERATURE',
                'Default Temperature',
                default='0.2'
            )),
            'default_max_tokens': int(self._get_config_value(
                'OPENAI_MAX_TOKENS',
                'Default Max Tokens',
                default='2500'
            )),
            'is_active': True,
        }

        self._create_or_update_provider(provider_config)

    def _load_xai(self):
        """Load XAI configuration."""
        api_key = self._get_config_value(
            'XAI_API_KEY',
            'Enter XAI (Grok) API Key',
            secret=True
        )

        if not api_key and not self.interactive:
            self.stdout.write(self.style.WARNING('  → Skipping XAI (no API key)'))
            return

        if not api_key:
            return

        provider_config = {
            'name': 'xai',
            'display_name': 'XAI (Grok)',
            'api_key': api_key,
            'base_url': self._get_config_value(
                'XAI_BASE_URL',
                'XAI Base URL',
                default='https://api.x.ai/v1'
            ),
            'default_temperature': float(self._get_config_value(
                'XAI_TEMPERATURE',
                'Default Temperature',
                default='0.2'
            )),
            'default_max_tokens': int(self._get_config_value(
                'XAI_MAX_TOKENS',
                'Default Max Tokens',
                default='2500'
            )),
            'is_active': True,
        }

        self._create_or_update_provider(provider_config)

    def _load_anthropic(self):
        """Load Anthropic configuration."""
        api_key = self._get_config_value(
            'ANTHROPIC_API_KEY',
            'Enter Anthropic API Key',
            secret=True
        )

        if not api_key and not self.interactive:
            self.stdout.write(self.style.WARNING('  → Skipping Anthropic (no API key)'))
            return

        if not api_key:
            return

        provider_config = {
            'name': 'anthropic',
            'display_name': 'Anthropic',
            'api_key': api_key,
            'base_url': self._get_config_value(
                'ANTHROPIC_BASE_URL',
                'Anthropic Base URL',
                default='https://api.anthropic.com/v1'
            ),
            'default_temperature': float(self._get_config_value(
                'ANTHROPIC_TEMPERATURE',
                'Default Temperature',
                default='0.2'
            )),
            'default_max_tokens': int(self._get_config_value(
                'ANTHROPIC_MAX_TOKENS',
                'Default Max Tokens',
                default='2500'
            )),
            'is_active': True,
        }

        self._create_or_update_provider(provider_config)

    def _get_config_value(
        self,
        env_var: str,
        prompt: str,
        default: Optional[str] = None,
        secret: bool = False
    ) -> Optional[str]:
        """Get configuration value from environment or prompt user."""
        # Try environment variable first
        value = os.getenv(env_var)

        # Try secrets file
        if not value and self.secrets_dir.exists():
            secret_file = self.secrets_dir / f'{env_var.lower()}.txt'
            if secret_file.exists():
                value = secret_file.read_text().strip()

        # If interactive and no value found, prompt user
        if not value and self.interactive:
            if secret:
                import getpass
                value = getpass.getpass(f'{prompt}: ')
            else:
                value = input(f'{prompt} [{default or ""}]: ').strip()
                if not value and default:
                    value = default

        # If still no value and we have a default, use it
        if not value and default:
            value = default

        return value if value else None

    def _create_or_update_provider(self, config: Dict):
        """Create or update an AI provider."""
        name = config['name']

        if self.update_keys_only:
            try:
                provider = AIProvider.objects.get(name=name)
                if 'api_key' in config:
                    provider.api_key = config['api_key']
                    provider.save(update_fields=['api_key', 'updated_at'])
                    self.stdout.write(
                        self.style.SUCCESS(f'  ✓ Updated API key for {provider.display_name}')
                    )
                return
            except AIProvider.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'  → Provider {name} not found, skipping')
                )
                return

        provider, created = AIProvider.objects.update_or_create(
            name=name,
            defaults={
                'display_name': config.get('display_name', name.upper()),
                'api_key': config.get('api_key', ''),
                'base_url': config.get('base_url', ''),
                'default_temperature': config.get('default_temperature', 0.2),
                'default_max_tokens': config.get('default_max_tokens', 2500),
                'is_active': config.get('is_active', True),
                'description': config.get('description', ''),
                'documentation_url': config.get('documentation_url', ''),
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f'  ✓ Created provider: {provider.display_name}'))
        else:
            self.stdout.write(f'  → Updated provider: {provider.display_name}')

    def _create_or_update_model(self, provider: AIProvider, config: Dict):
        """Create or update an AI model."""
        name = config['name']

        model, created = AIModel.objects.update_or_create(
            provider=provider,
            name=name,
            defaults={
                'display_name': config.get('display_name', name),
                'capabilities': config.get('capabilities', ['chat']),
                'max_tokens': config.get('max_tokens', 4096),
                'context_window': config.get('context_window', 8192),
                'supports_system_prompt': config.get('supports_system_prompt', True),
                'supports_streaming': config.get('supports_streaming', True),
                'input_price_per_million': config.get('input_price_per_million'),
                'output_price_per_million': config.get('output_price_per_million'),
                'is_active': config.get('is_active', True),
                'is_default': config.get('is_default', False),
                'description': config.get('description', ''),
            }
        )

        if created:
            self.stdout.write(f'    ✓ Added model: {model.display_name}')
        else:
            self.stdout.write(f'    → Updated model: {model.display_name}')

    def _print_summary(self):
        """Print summary of loaded configuration."""
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write('Configuration Summary')
        self.stdout.write('=' * 70)

        providers = AIProvider.objects.all()
        self.stdout.write(f'\nTotal Providers: {providers.count()}')

        for provider in providers:
            status = '✓' if provider.has_api_key else '✗'
            active = '[ACTIVE]' if provider.is_active else '[INACTIVE]'
            self.stdout.write(f'  {status} {provider.display_name} {active}')

            models = provider.models.all()
            if models.exists():
                self.stdout.write(f'     Models: {models.count()}')
                for model in models:
                    default = ' [DEFAULT]' if model.is_default else ''
                    active_m = '[ACTIVE]' if model.is_active else '[INACTIVE]'
                    self.stdout.write(f'       - {model.display_name} {active_m}{default}')

        self.stdout.write('\n' + '=' * 70)

        # Warnings
        providers_without_keys = providers.filter(api_key='')
        if providers_without_keys.exists():
            self.stdout.write(
                self.style.WARNING(
                    f'\n⚠ Warning: {providers_without_keys.count()} provider(s) missing API keys'
                )
            )
            for provider in providers_without_keys:
                self.stdout.write(f'  - {provider.display_name}')
