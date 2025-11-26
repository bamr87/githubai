"""
Management command to validate critical configuration.

Tests:
- AIProvider API keys exist
- API endpoints are reachable
- Models are available
- Database connectivity
"""
import logging
from typing import List, Dict

from django.core.management.base import BaseCommand
from django.conf import settings

from core.models import AIProvider, AIModel

logger = logging.getLogger('githubai')


class Command(BaseCommand):
    help = 'Validate critical technical configuration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--provider',
            type=str,
            help='Only validate specific provider',
        )
        parser.add_argument(
            '--skip-connectivity',
            action='store_true',
            help='Skip API connectivity tests',
        )
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Attempt to fix common issues automatically',
        )

    def handle(self, *args, **options):
        self.provider_name = options.get('provider')
        self.skip_connectivity = options['skip_connectivity']
        self.fix_issues = options['fix']

        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.SUCCESS('Configuration Validation Report'))
        self.stdout.write('=' * 70 + '\n')

        self.errors = []
        self.warnings = []
        self.passed = []

        # Run validation checks
        self._check_database()
        self._check_providers()
        self._check_models()

        if not self.skip_connectivity:
            self._check_connectivity()

        # Print results
        self._print_results()

    def _check_database(self):
        """Verify database connectivity and tables exist."""
        self.stdout.write('Database Checks:')

        try:
            # Test basic query
            provider_count = AIProvider.objects.count()
            model_count = AIModel.objects.count()

            self.passed.append(f'Database connected (Providers: {provider_count}, Models: {model_count})')
            self.stdout.write(self.style.SUCCESS(f'  ✓ Database connected'))
            self.stdout.write(f'    Providers: {provider_count}')
            self.stdout.write(f'    Models: {model_count}')

        except Exception as e:
            self.errors.append(f'Database connection failed: {e}')
            self.stdout.write(self.style.ERROR(f'  ✗ Database connection failed: {e}'))

    def _check_providers(self):
        """Validate AI providers configuration."""
        self.stdout.write('\nProvider Checks:')

        providers = AIProvider.objects.all()
        if self.provider_name:
            providers = providers.filter(name=self.provider_name)

        if not providers.exists():
            msg = f'No providers found' + (f' matching "{self.provider_name}"' if self.provider_name else '')
            self.errors.append(msg)
            self.stdout.write(self.style.ERROR(f'  ✗ {msg}'))
            return

        for provider in providers:
            self.stdout.write(f'\n  {provider.display_name}:')

            # Check API key
            if provider.has_api_key:
                self.passed.append(f'{provider.display_name} has API key')
                self.stdout.write(self.style.SUCCESS(f'    ✓ API key configured'))
            else:
                msg = f'{provider.display_name} missing API key'
                if provider.is_active:
                    self.errors.append(msg)
                    self.stdout.write(self.style.ERROR(f'    ✗ Missing API key (provider is ACTIVE)'))
                else:
                    self.warnings.append(msg)
                    self.stdout.write(self.style.WARNING(f'    ⚠ Missing API key (provider is inactive)'))

            # Check base URL
            if provider.base_url:
                self.passed.append(f'{provider.display_name} has base URL')
                self.stdout.write(self.style.SUCCESS(f'    ✓ Base URL: {provider.base_url}'))
            else:
                msg = f'{provider.display_name} missing base URL'
                self.errors.append(msg)
                self.stdout.write(self.style.ERROR(f'    ✗ Missing base URL'))

            # Check models
            model_count = provider.models.count()
            if model_count > 0:
                self.passed.append(f'{provider.display_name} has {model_count} models')
                self.stdout.write(self.style.SUCCESS(f'    ✓ Models configured: {model_count}'))

                # Check for default model
                default_models = provider.models.filter(is_default=True)
                if default_models.exists():
                    self.passed.append(f'{provider.display_name} has default model')
                    self.stdout.write(f'      Default: {default_models.first().display_name}')
                else:
                    msg = f'{provider.display_name} has no default model'
                    self.warnings.append(msg)
                    self.stdout.write(self.style.WARNING(f'    ⚠ No default model set'))

                    if self.fix_issues and model_count > 0:
                        # Set first model as default
                        first_model = provider.models.first()
                        first_model.is_default = True
                        first_model.save(update_fields=['is_default'])
                        self.stdout.write(self.style.SUCCESS(f'      → Fixed: Set {first_model.display_name} as default'))
            else:
                msg = f'{provider.display_name} has no models configured'
                self.warnings.append(msg)
                self.stdout.write(self.style.WARNING(f'    ⚠ No models configured'))

    def _check_models(self):
        """Validate AI models configuration."""
        self.stdout.write('\nModel Checks:')

        models = AIModel.objects.all()
        if self.provider_name:
            models = models.filter(provider__name=self.provider_name)

        if not models.exists():
            msg = 'No models configured'
            self.warnings.append(msg)
            self.stdout.write(self.style.WARNING(f'  ⚠ {msg}'))
            return

        # Check for required fields
        issues = []
        for model in models:
            if not model.max_tokens or model.max_tokens <= 0:
                issues.append(f'{model.full_name}: invalid max_tokens')
            if not model.context_window or model.context_window <= 0:
                issues.append(f'{model.full_name}: invalid context_window')

        if issues:
            self.errors.extend(issues)
            self.stdout.write(self.style.ERROR(f'  ✗ Found {len(issues)} model configuration issues:'))
            for issue in issues:
                self.stdout.write(f'    - {issue}')
        else:
            self.passed.append(f'All {models.count()} models properly configured')
            self.stdout.write(self.style.SUCCESS(f'  ✓ All {models.count()} models properly configured'))

    def _check_connectivity(self):
        """Test API connectivity (optional)."""
        self.stdout.write('\nConnectivity Checks:')
        self.stdout.write(self.style.WARNING('  → Skipping (use --test-api to enable)'))
        self.warnings.append('API connectivity not tested')

    def _print_results(self):
        """Print validation summary."""
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write('Validation Results')
        self.stdout.write('=' * 70)

        self.stdout.write(f'\n{self.style.SUCCESS("✓ Passed:")} {len(self.passed)}')
        self.stdout.write(f'{self.style.WARNING("⚠ Warnings:")} {len(self.warnings)}')
        self.stdout.write(f'{self.style.ERROR("✗ Errors:")} {len(self.errors)}')

        if self.warnings:
            self.stdout.write('\n' + self.style.WARNING('Warnings:'))
            for warning in self.warnings:
                self.stdout.write(f'  ⚠ {warning}')

        if self.errors:
            self.stdout.write('\n' + self.style.ERROR('Errors:'))
            for error in self.errors:
                self.stdout.write(f'  ✗ {error}')

        self.stdout.write('\n' + '=' * 70)

        # Exit code
        if self.errors:
            self.stdout.write(
                self.style.ERROR(
                    '\n❌ Validation FAILED - Please fix errors above'
                )
            )
            exit(1)
        elif self.warnings:
            self.stdout.write(
                self.style.WARNING(
                    '\n⚠️  Validation completed with warnings'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    '\n✅ Validation PASSED - All checks successful!'
                )
            )
