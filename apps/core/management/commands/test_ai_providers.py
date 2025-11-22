"""Management command to test and manage AI providers"""
from django.core.management.base import BaseCommand
from core.services.ai_service import AIService
from core.services.ai_providers import AIProviderError


class Command(BaseCommand):
    help = 'Test and manage AI providers'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test-provider',
            type=str,
            help='Test a specific AI provider (openai, xai)'
        )
        parser.add_argument(
            '--list-providers',
            action='store_true',
            help='List all available AI providers'
        )
        parser.add_argument(
            '--test-all',
            action='store_true',
            help='Test all configured providers'
        )
        parser.add_argument(
            '--prompt',
            type=str,
            default='Hello! Please respond with a short greeting.',
            help='Test prompt to send to AI'
        )

    def handle(self, *args, **options):
        if options['list_providers']:
            self.list_providers()
        elif options['test_all']:
            self.test_all_providers(options['prompt'])
        elif options['test_provider']:
            self.test_specific_provider(options['test_provider'], options['prompt'])
        else:
            self.stdout.write(
                self.style.ERROR('Please specify --list-providers, --test-all, or --test-provider')
            )

    def list_providers(self):
        """List all available AI providers"""
        self.stdout.write(self.style.SUCCESS('Available AI Providers:'))
        providers = AIService.get_available_providers()
        current = AIService.get_current_provider()

        for provider in providers:
            marker = ' (current)' if provider == current else ''
            self.stdout.write(f'  • {provider}{marker}')

        self.stdout.write(f'\\nCurrent provider: {current}')

    def test_specific_provider(self, provider_name, prompt):
        """Test a specific AI provider"""
        self.stdout.write(f'Testing provider: {provider_name}')

        try:
            ai_service = AIService()

            system_prompt = "You are a helpful assistant. Respond concisely."

            response = ai_service.call_ai_chat(
                system_prompt=system_prompt,
                user_prompt=prompt,
                provider_name=provider_name,
                use_cache=False  # Don't use cache for testing
            )

            self.stdout.write(self.style.SUCCESS(f'✅ {provider_name} test successful!'))
            self.stdout.write(f'Response: {response[:200]}{"..." if len(response) > 200 else ""}')

        except AIProviderError as e:
            self.stdout.write(self.style.ERROR(f'❌ {provider_name} test failed: {str(e)}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ {provider_name} unexpected error: {str(e)}'))

    def test_all_providers(self, prompt):
        """Test all available AI providers"""
        self.stdout.write('Testing all available AI providers...')
        providers = AIService.get_available_providers()

        for provider in providers:
            self.stdout.write(f'\\n{"-" * 50}')
            self.test_specific_provider(provider, prompt)
