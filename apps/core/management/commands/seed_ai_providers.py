"""
Management command to seed AI providers and models.
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from core.models import AIProvider, AIModel
from datetime import date


class Command(BaseCommand):
    help = 'Seed AI providers and their available models'

    def add_arguments(self, parser):
        parser.add_argument(
            '--update-keys',
            action='store_true',
            help='Update API keys from environment variables',
        )

    def handle(self, *args, **options):
        update_keys = options['update_keys']

        self.stdout.write('\n' + '=' * 70)
        self.stdout.write('Seeding AI Providers and Models')
        self.stdout.write('=' * 70 + '\n')

        # Seed OpenAI
        self.seed_openai(update_keys)

        # Seed XAI (Grok)
        self.seed_xai(update_keys)

        # Seed Anthropic (Claude) - optional
        self.seed_anthropic(update_keys)

        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.SUCCESS('✓ Seeding complete!'))
        self.stdout.write('=' * 70 + '\n')

        # Summary
        providers = AIProvider.objects.all()
        models = AIModel.objects.all()

        self.stdout.write(f'\nTotal Providers: {providers.count()}')
        for provider in providers:
            key_status = '✓' if provider.has_api_key else '✗'
            model_count = provider.models.filter(is_active=True).count()
            self.stdout.write(f'  {key_status} {provider.display_name}: {model_count} active models')

        self.stdout.write(f'\nTotal Models: {models.count()}')
        self.stdout.write('')

    def seed_openai(self, update_keys):
        self.stdout.write('\nOpenAI Provider:')
        self.stdout.write('-' * 70)

        # Get API key from settings
        api_key = getattr(settings, 'OPENAI_API_KEY', '')

        # Create or update provider
        provider, created = AIProvider.objects.get_or_create(
            name='openai',
            defaults={
                'display_name': 'OpenAI',
                'api_key': api_key,
                'base_url': 'https://api.openai.com/v1',
                'default_temperature': 0.2,
                'default_max_tokens': 2500,
                'description': 'OpenAI GPT models including GPT-4 and GPT-3.5',
                'documentation_url': 'https://platform.openai.com/docs/api-reference',
                'is_active': True,
            }
        )

        if not created and update_keys and api_key:
            provider.api_key = api_key
            provider.save()
            self.stdout.write(self.style.SUCCESS(f'  ✓ Updated API key for {provider.display_name}'))
        elif created:
            self.stdout.write(self.style.SUCCESS(f'  ✓ Created provider: {provider.display_name}'))
        else:
            self.stdout.write(f'  → Provider exists: {provider.display_name}')

        # Seed models
        models_data = [
            {
                'name': 'gpt-4o',
                'display_name': 'GPT-4o',
                'capabilities': ['chat', 'vision', 'code'],
                'max_tokens': 4096,
                'context_window': 128000,
                'input_price': 2.50,
                'output_price': 10.00,
                'is_default': False,
            },
            {
                'name': 'gpt-4o-mini',
                'display_name': 'GPT-4o Mini',
                'capabilities': ['chat', 'vision', 'code'],
                'max_tokens': 16384,
                'context_window': 128000,
                'input_price': 0.15,
                'output_price': 0.60,
                'is_default': True,
            },
            {
                'name': 'gpt-4-turbo',
                'display_name': 'GPT-4 Turbo',
                'capabilities': ['chat', 'vision', 'code'],
                'max_tokens': 4096,
                'context_window': 128000,
                'input_price': 10.00,
                'output_price': 30.00,
                'is_default': False,
            },
            {
                'name': 'gpt-3.5-turbo',
                'display_name': 'GPT-3.5 Turbo',
                'capabilities': ['chat', 'code'],
                'max_tokens': 4096,
                'context_window': 16385,
                'input_price': 0.50,
                'output_price': 1.50,
                'is_default': False,
            },
        ]

        for model_data in models_data:
            model, created = AIModel.objects.get_or_create(
                provider=provider,
                name=model_data['name'],
                defaults={
                    'display_name': model_data['display_name'],
                    'capabilities': model_data['capabilities'],
                    'max_tokens': model_data['max_tokens'],
                    'context_window': model_data['context_window'],
                    'input_price_per_million': model_data['input_price'],
                    'output_price_per_million': model_data['output_price'],
                    'is_default': model_data['is_default'],
                    'is_active': True,
                    'supports_system_prompt': True,
                    'supports_streaming': True,
                }
            )

            if created:
                self.stdout.write(f'    ✓ Added model: {model.display_name}')
            else:
                self.stdout.write(f'    → Model exists: {model.display_name}')

    def seed_xai(self, update_keys):
        self.stdout.write('\nXAI (Grok) Provider:')
        self.stdout.write('-' * 70)

        # Get API key from settings
        api_key = getattr(settings, 'XAI_API_KEY', '')

        # Create or update provider
        provider, created = AIProvider.objects.get_or_create(
            name='xai',
            defaults={
                'display_name': 'XAI (Grok)',
                'api_key': api_key,
                'base_url': 'https://api.x.ai/v1',
                'default_temperature': 0.2,
                'default_max_tokens': 2500,
                'description': 'XAI Grok models by xAI',
                'documentation_url': 'https://docs.x.ai/',
                'is_active': True,
            }
        )

        if not created and update_keys and api_key:
            provider.api_key = api_key
            provider.save()
            self.stdout.write(self.style.SUCCESS(f'  ✓ Updated API key for {provider.display_name}'))
        elif created:
            self.stdout.write(self.style.SUCCESS(f'  ✓ Created provider: {provider.display_name}'))
        else:
            self.stdout.write(f'  → Provider exists: {provider.display_name}')

        # Seed models
        models_data = [
            {
                'name': 'grok-beta',
                'display_name': 'Grok Beta',
                'capabilities': ['chat', 'code'],
                'max_tokens': 4096,
                'context_window': 131072,
                'input_price': 5.00,
                'output_price': 15.00,
                'is_default': True,
            },
            {
                'name': 'grok-vision-beta',
                'display_name': 'Grok Vision Beta',
                'capabilities': ['chat', 'vision', 'code'],
                'max_tokens': 4096,
                'context_window': 8192,
                'input_price': 5.00,
                'output_price': 15.00,
                'is_default': False,
            },
        ]

        for model_data in models_data:
            model, created = AIModel.objects.get_or_create(
                provider=provider,
                name=model_data['name'],
                defaults={
                    'display_name': model_data['display_name'],
                    'capabilities': model_data['capabilities'],
                    'max_tokens': model_data['max_tokens'],
                    'context_window': model_data['context_window'],
                    'input_price_per_million': model_data['input_price'],
                    'output_price_per_million': model_data['output_price'],
                    'is_default': model_data['is_default'],
                    'is_active': True,
                    'supports_system_prompt': True,
                    'supports_streaming': True,
                }
            )

            if created:
                self.stdout.write(f'    ✓ Added model: {model.display_name}')
            else:
                self.stdout.write(f'    → Model exists: {model.display_name}')

    def seed_anthropic(self, update_keys):
        self.stdout.write('\nAnthropic (Claude) Provider:')
        self.stdout.write('-' * 70)

        # Get API key from settings (optional)
        api_key = getattr(settings, 'ANTHROPIC_API_KEY', '')

        # Create or update provider
        provider, created = AIProvider.objects.get_or_create(
            name='anthropic',
            defaults={
                'display_name': 'Anthropic (Claude)',
                'api_key': api_key,
                'base_url': 'https://api.anthropic.com/v1',
                'default_temperature': 0.2,
                'default_max_tokens': 2500,
                'description': 'Anthropic Claude models',
                'documentation_url': 'https://docs.anthropic.com/',
                'is_active': bool(api_key),  # Only active if key is provided
            }
        )

        if not created and update_keys and api_key:
            provider.api_key = api_key
            provider.is_active = True
            provider.save()
            self.stdout.write(self.style.SUCCESS(f'  ✓ Updated API key for {provider.display_name}'))
        elif created:
            status = 'Created' if api_key else 'Created (inactive - no API key)'
            self.stdout.write(self.style.SUCCESS(f'  ✓ {status}: {provider.display_name}'))
        else:
            self.stdout.write(f'  → Provider exists: {provider.display_name}')

        # Seed models
        models_data = [
            {
                'name': 'claude-3-5-sonnet-20241022',
                'display_name': 'Claude 3.5 Sonnet',
                'capabilities': ['chat', 'vision', 'code'],
                'max_tokens': 8192,
                'context_window': 200000,
                'input_price': 3.00,
                'output_price': 15.00,
                'is_default': True,
            },
            {
                'name': 'claude-3-opus-20240229',
                'display_name': 'Claude 3 Opus',
                'capabilities': ['chat', 'vision', 'code'],
                'max_tokens': 4096,
                'context_window': 200000,
                'input_price': 15.00,
                'output_price': 75.00,
                'is_default': False,
            },
            {
                'name': 'claude-3-haiku-20240307',
                'display_name': 'Claude 3 Haiku',
                'capabilities': ['chat', 'vision', 'code'],
                'max_tokens': 4096,
                'context_window': 200000,
                'input_price': 0.25,
                'output_price': 1.25,
                'is_default': False,
            },
        ]

        for model_data in models_data:
            model, created = AIModel.objects.get_or_create(
                provider=provider,
                name=model_data['name'],
                defaults={
                    'display_name': model_data['display_name'],
                    'capabilities': model_data['capabilities'],
                    'max_tokens': model_data['max_tokens'],
                    'context_window': model_data['context_window'],
                    'input_price_per_million': model_data['input_price'],
                    'output_price_per_million': model_data['output_price'],
                    'is_default': model_data['is_default'],
                    'is_active': True,
                    'supports_system_prompt': True,
                    'supports_streaming': True,
                }
            )

            if created:
                self.stdout.write(f'    ✓ Added model: {model.display_name}')
            else:
                self.stdout.write(f'    → Model exists: {model.display_name}')
