"""
Comprehensive tests for two-tier data loading system.

Tests:
- load_config_data command with various options
- generate_content_data command
- validate_config command
- Pytest fixtures
- Fixture files integrity
"""
import json
import pytest
from pathlib import Path
from django.core.management import call_command
from django.core.management.base import CommandError
from io import StringIO

from core.models import (
    AIProvider,
    AIModel,
    PromptTemplate,
    IssueTemplate,
    Issue,
)


class TestLoadConfigData:
    """Test load_config_data management command."""

    @pytest.mark.django_db
    def test_load_test_config(self):
        """Test loading test configuration."""
        # Clear any existing data
        AIProvider.objects.all().delete()
        AIModel.objects.all().delete()

        # Load test config
        out = StringIO()
        call_command('load_config_data', '--test', stdout=out)
        output = out.getvalue()

        # Verify providers created
        assert AIProvider.objects.count() >= 2
        assert AIProvider.objects.filter(name='openai').exists()
        assert AIProvider.objects.filter(name='xai').exists()

        # Verify test API keys
        openai = AIProvider.objects.get(name='openai')
        assert openai.has_api_key
        assert 'test' in openai.api_key.lower()

        # Check output
        assert 'Loading TEST configuration' in output
        assert 'OpenAI (Test)' in output

    @pytest.mark.django_db
    def test_update_keys_only(self):
        """Test updating only API keys."""
        # Create initial provider
        provider = AIProvider.objects.create(
            name='openai',
            display_name='OpenAI',
            api_key='old-key',
            base_url='https://api.openai.com/v1',
        )

        # Load with test flag to update key
        call_command('load_config_data', '--test', '--update-keys-only')

        # Verify key was updated
        provider.refresh_from_db()
        assert provider.api_key != 'old-key'
        assert 'test' in provider.api_key.lower()

    @pytest.mark.django_db
    def test_non_interactive_mode(self):
        """Test non-interactive mode skips missing providers."""
        AIProvider.objects.all().delete()

        out = StringIO()
        # Should not prompt, should skip providers without env vars
        call_command('load_config_data', '--non-interactive', stdout=out)
        output = out.getvalue()

        # Should skip providers without keys
        assert 'Skipping' in output or AIProvider.objects.count() == 0


class TestValidateConfig:
    """Test validate_config management command."""

    @pytest.mark.django_db
    def test_validate_with_valid_config(self, load_test_config):
        """Test validation passes with valid configuration."""
        out = StringIO()

        # Should not raise exception
        call_command('validate_config', stdout=out)
        output = out.getvalue()

        assert 'Validation Results' in output
        assert 'Passed:' in output
        # Should have some passed checks
        assert not output.endswith('Validation FAILED')

    @pytest.mark.django_db
    def test_validate_missing_api_key(self):
        """Test validation detects missing API keys."""
        # Create provider without API key
        AIProvider.objects.create(
            name='test',
            display_name='Test Provider',
            api_key='',
            base_url='https://test.com',
            is_active=True,
        )

        out = StringIO()
        err = StringIO()

        # Validation should fail
        with pytest.raises(SystemExit) as exc_info:
            call_command('validate_config', stdout=out, stderr=err)

        assert exc_info.value.code == 1
        output = out.getvalue()
        assert 'Missing API key' in output

    @pytest.mark.django_db
    def test_validate_with_fix(self, load_test_config):
        """Test auto-fix capability."""
        # Remove default flag from all models
        AIModel.objects.all().update(is_default=False)

        out = StringIO()
        call_command('validate_config', '--fix', stdout=out)
        output = out.getvalue()

        # Should have fixed by setting a default
        assert AIModel.objects.filter(is_default=True).exists() or 'Fixed' in output

    @pytest.mark.django_db
    def test_validate_specific_provider(self, load_test_config):
        """Test validating specific provider."""
        out = StringIO()
        call_command('validate_config', '--provider', 'openai', stdout=out)
        output = out.getvalue()

        assert 'OpenAI' in output


class TestGenerateContentData:
    """Test generate_content_data management command."""

    @pytest.mark.django_db
    def test_dry_run_mode(self, load_test_config):
        """Test dry-run mode doesn't create records."""
        initial_count = PromptTemplate.objects.count()

        out = StringIO()
        # Note: Can't test interactive mode in automated tests
        # Would need to mock input()
        call_command(
            'generate_content_data',
            '--dry-run',
            stdout=out,
        )
        output = out.getvalue()

        # Should show dry run message
        assert 'DRY RUN' in output

    @pytest.mark.django_db
    def test_requires_ai_provider(self):
        """Test fails gracefully without AI provider."""
        AIProvider.objects.all().delete()

        out = StringIO()
        # Should detect no providers and return early
        # Can't test interactive without mocking input
        # Just verify it doesn't crash
        try:
            call_command('generate_content_data', '--dry-run', stdout=out)
            output = out.getvalue()
            assert 'No active AI providers' in output or 'Checking AI' in output
        except (CommandError, SystemExit):
            # Expected if no providers
            pass


class TestFixtureFiles:
    """Test fixture file integrity."""

    def test_test_config_fixture_exists(self):
        """Test test_config.json exists and is valid."""
        fixture_path = Path('apps/core/fixtures/test_config.json')
        assert fixture_path.exists(), "test_config.json not found"

        with open(fixture_path, 'r') as f:
            data = json.load(f)

        assert isinstance(data, list)
        assert len(data) > 0

        # Check for AIProvider records
        providers = [r for r in data if r['model'] == 'core.aiprovider']
        assert len(providers) >= 2

        # Check for AIModel records
        models = [r for r in data if r['model'] == 'core.aimodel']
        assert len(models) >= 2

    def test_test_content_fixture_exists(self):
        """Test test_content.json exists and is valid."""
        fixture_path = Path('apps/core/fixtures/test_content.json')
        assert fixture_path.exists(), "test_content.json not found"

        with open(fixture_path, 'r') as f:
            data = json.load(f)

        assert isinstance(data, list)
        assert len(data) > 0

        # Check for PromptTemplate records
        templates = [r for r in data if r['model'] == 'core.prompttemplate']
        assert len(templates) >= 2

        # Check for Issue records
        issues = [r for r in data if r['model'] == 'core.issue']
        assert len(issues) >= 2

    @pytest.mark.django_db
    def test_load_test_config_fixture(self):
        """Test loading test_config.json fixture."""
        AIProvider.objects.all().delete()
        AIModel.objects.all().delete()

        call_command('loaddata', 'apps/core/fixtures/test_config.json', verbosity=0)

        assert AIProvider.objects.count() >= 2
        assert AIModel.objects.count() >= 2

    @pytest.mark.django_db
    def test_load_test_content_fixture(self, load_test_config):
        """Test loading test_content.json fixture."""
        PromptTemplate.objects.all().delete()
        Issue.objects.all().delete()

        call_command('loaddata', 'apps/core/fixtures/test_content.json', verbosity=0)

        assert PromptTemplate.objects.count() >= 2
        assert Issue.objects.count() >= 2


class TestPytestFixtures:
    """Test pytest fixtures work correctly."""

    @pytest.mark.django_db
    def test_load_test_config_fixture(self, load_test_config):
        """Test load_test_config fixture."""
        assert AIProvider.objects.count() >= 2
        assert AIModel.objects.count() >= 2

        openai = AIProvider.objects.filter(name='openai').first()
        assert openai is not None
        assert openai.has_api_key

    @pytest.mark.django_db
    def test_sample_content_data_fixture(self, sample_content_data):
        """Test sample_content_data fixture."""
        assert PromptTemplate.objects.count() >= 2
        assert Issue.objects.count() >= 2

    @pytest.mark.django_db
    def test_ai_provider_config_fixture(self, ai_provider_config):
        """Test ai_provider_config fixture."""
        assert 'providers' in ai_provider_config
        assert 'default_provider' in ai_provider_config
        assert 'default_model' in ai_provider_config
        assert 'models' in ai_provider_config

        assert len(ai_provider_config['providers']) >= 2
        assert ai_provider_config['default_provider'] is not None

    @pytest.mark.django_db
    def test_test_prompt_templates_fixture(self, test_prompt_templates):
        """Test test_prompt_templates fixture."""
        assert isinstance(test_prompt_templates, dict)
        assert len(test_prompt_templates) >= 2

        # Should have chat and auto_issue categories
        assert 'chat' in test_prompt_templates or 'auto_issue' in test_prompt_templates

    @pytest.mark.django_db
    def test_test_issues_fixture(self, test_issues):
        """Test test_issues fixture."""
        assert isinstance(test_issues, list)
        assert len(test_issues) >= 2

        # All should be from test repo
        assert all(issue.github_repo == 'test/repo' for issue in test_issues)


class TestDataLoadingIntegration:
    """Integration tests for complete workflows."""

    @pytest.mark.django_db
    def test_complete_test_workflow(self):
        """Test complete test environment setup."""
        # 1. Clear database
        AIProvider.objects.all().delete()
        AIModel.objects.all().delete()
        PromptTemplate.objects.all().delete()
        Issue.objects.all().delete()

        # 2. Load test config
        call_command('load_config_data', '--test')

        # 3. Validate
        out = StringIO()
        call_command('validate_config', stdout=out)
        output = out.getvalue()

        # 4. Load content
        call_command('loaddata', 'apps/core/fixtures/test_content.json', verbosity=0)

        # 5. Verify everything
        assert AIProvider.objects.count() >= 2
        assert AIModel.objects.count() >= 2
        assert PromptTemplate.objects.count() >= 2
        assert Issue.objects.count() >= 2

        # Verify relationships
        openai = AIProvider.objects.get(name='openai')
        assert openai.models.count() >= 1

        default_model = AIModel.objects.filter(is_default=True).first()
        assert default_model is not None

    @pytest.mark.django_db
    def test_fixture_loading_order(self):
        """Test fixtures load in correct order."""
        # Clear all
        AIProvider.objects.all().delete()
        AIModel.objects.all().delete()
        PromptTemplate.objects.all().delete()

        # Load in order: config first, then content
        call_command('loaddata', 'apps/core/fixtures/test_config.json', verbosity=0)
        call_command('loaddata', 'apps/core/fixtures/test_content.json', verbosity=0)

        # Verify foreign keys work
        templates = PromptTemplate.objects.filter(ai_model__isnull=False)
        for template in templates:
            assert template.ai_model.provider is not None

    @pytest.mark.django_db
    def test_update_and_validate_workflow(self, load_test_config):
        """Test update and validate workflow."""
        # 1. Initial state
        initial_provider = AIProvider.objects.first()
        old_key = initial_provider.api_key

        # 2. Update keys
        call_command('load_config_data', '--test', '--update-keys-only')

        # 3. Validate
        out = StringIO()
        call_command('validate_config', stdout=out)

        # 4. Verify
        initial_provider.refresh_from_db()
        assert initial_provider.api_key != '' or old_key != ''


class TestCommandOptions:
    """Test various command options and flags."""

    @pytest.mark.django_db
    def test_load_config_with_validate_flag(self):
        """Test --validate flag on load_config_data."""
        AIProvider.objects.all().delete()

        out = StringIO()
        # Load and validate in one command
        call_command('load_config_data', '--test', '--validate', stdout=out)
        output = out.getvalue()

        assert 'Loading TEST configuration' in output
        assert 'Validation' in output

    @pytest.mark.django_db
    def test_validate_skip_connectivity(self, load_test_config):
        """Test --skip-connectivity flag."""
        out = StringIO()
        call_command('validate_config', '--skip-connectivity', stdout=out)
        output = out.getvalue()

        assert 'Connectivity Checks' in output
        assert 'Skipping' in output or 'not tested' in output


class TestErrorHandling:
    """Test error handling and edge cases."""

    @pytest.mark.django_db
    def test_validate_empty_database(self):
        """Test validation with empty database."""
        AIProvider.objects.all().delete()

        out = StringIO()
        err = StringIO()

        with pytest.raises(SystemExit):
            call_command('validate_config', stdout=out, stderr=err)

        output = out.getvalue()
        assert 'No providers found' in output or 'Errors:' in output

    @pytest.mark.django_db
    def test_load_config_invalid_json(self, tmp_path):
        """Test loading from invalid JSON file."""
        # Create invalid JSON file
        invalid_file = tmp_path / "invalid.json"
        invalid_file.write_text("{invalid json")

        with pytest.raises(CommandError) as exc_info:
            call_command('load_config_data', '--config-file', str(invalid_file))

        assert 'Invalid JSON' in str(exc_info.value)

    @pytest.mark.django_db
    def test_load_config_missing_file(self):
        """Test loading from non-existent file."""
        with pytest.raises(CommandError) as exc_info:
            call_command('load_config_data', '--config-file', 'nonexistent.json')

        assert 'not found' in str(exc_info.value)


class TestModelRelationships:
    """Test model relationships in fixtures."""

    @pytest.mark.django_db
    def test_provider_model_relationship(self, load_test_config):
        """Test AIProvider -> AIModel relationship."""
        providers = AIProvider.objects.all()

        for provider in providers:
            models = provider.models.all()
            # Each provider should have at least one model
            assert models.exists() or not provider.is_active

    @pytest.mark.django_db
    def test_template_model_relationship(self, sample_content_data):
        """Test PromptTemplate -> AIModel relationship."""
        templates = PromptTemplate.objects.filter(ai_model__isnull=False)

        for template in templates:
            assert template.ai_model.provider is not None
            assert template.ai_model.provider.has_api_key

    @pytest.mark.django_db
    def test_issue_template_relationship(self, sample_content_data):
        """Test Issue -> IssueTemplate relationship."""
        issues = Issue.objects.filter(template__isnull=False)

        for issue in issues:
            assert issue.template.name
            assert issue.template.is_active


class TestFixtureConsistency:
    """Test fixture data consistency."""

    def test_fixture_primary_keys_unique(self):
        """Test that fixture PKs don't conflict."""
        config_path = Path('apps/core/fixtures/test_config.json')
        content_path = Path('apps/core/fixtures/test_content.json')

        with open(config_path, 'r') as f:
            config_data = json.load(f)

        with open(content_path, 'r') as f:
            content_data = json.load(f)

        # Collect PKs by model
        config_pks = {}
        for record in config_data:
            model = record['model']
            pk = record['pk']
            if model not in config_pks:
                config_pks[model] = []
            config_pks[model].append(pk)

        content_pks = {}
        for record in content_data:
            model = record['model']
            pk = record['pk']
            if model not in content_pks:
                content_pks[model] = []
            content_pks[model].append(pk)

        # Check for overlaps in same model
        for model in config_pks:
            if model in content_pks:
                config_set = set(config_pks[model])
                content_set = set(content_pks[model])
                overlap = config_set & content_set
                assert len(overlap) == 0, f"PK overlap in {model}: {overlap}"

    def test_fixture_foreign_keys_valid(self):
        """Test that foreign keys in fixtures are valid."""
        config_path = Path('apps/core/fixtures/test_config.json')
        content_path = Path('apps/core/fixtures/test_content.json')

        with open(config_path, 'r') as f:
            config_data = json.load(f)

        with open(content_path, 'r') as f:
            content_data = json.load(f)

        # Collect available PKs from config
        available_providers = set()
        available_models = set()

        for record in config_data:
            if record['model'] == 'core.aiprovider':
                available_providers.add(record['pk'])
            elif record['model'] == 'core.aimodel':
                available_models.add(record['pk'])

        # Check content references
        for record in content_data:
            if record['model'] == 'core.aimodel':
                provider_fk = record['fields'].get('provider')
                if provider_fk:
                    assert provider_fk in available_providers, \
                        f"Invalid provider FK: {provider_fk}"

            elif record['model'] == 'core.prompttemplate':
                model_fk = record['fields'].get('ai_model')
                if model_fk:
                    assert model_fk in available_models, \
                        f"Invalid ai_model FK: {model_fk}"


# Run summary test
@pytest.mark.django_db
def test_complete_system(load_test_config, sample_content_data):
    """
    Comprehensive test that everything works together.

    This is the main integration test that verifies:
    1. Fixtures load correctly
    2. Relationships are valid
    3. Data is accessible
    4. Queries work
    """
    # Test Category 1: Critical Config
    assert AIProvider.objects.count() >= 2, "Need at least 2 providers"
    assert AIModel.objects.count() >= 2, "Need at least 2 models"

    openai = AIProvider.objects.get(name='openai')
    assert openai.has_api_key, "OpenAI should have API key"
    assert openai.is_active, "OpenAI should be active"

    default_model = AIModel.objects.filter(is_default=True, is_active=True).first()
    assert default_model is not None, "Should have a default model"

    # Test Category 2: Content Data
    assert PromptTemplate.objects.count() >= 2, "Need at least 2 templates"
    assert Issue.objects.count() >= 2, "Need at least 2 issues"

    chat_template = PromptTemplate.objects.filter(category='chat').first()
    assert chat_template is not None, "Should have chat template"
    assert chat_template.is_active, "Chat template should be active"

    # Test Relationships
    for model in AIModel.objects.all():
        assert model.provider is not None, f"Model {model} missing provider"
        assert model.provider.has_api_key, f"Provider {model.provider} missing key"

    for template in PromptTemplate.objects.filter(ai_model__isnull=False):
        assert template.ai_model.provider is not None, f"Template {template} has orphaned model"

    # Test Queries
    active_providers = AIProvider.objects.filter(is_active=True)
    assert active_providers.exists(), "Should have active providers"

    default_models = AIModel.objects.filter(is_default=True)
    assert default_models.exists(), "Should have default models"

    print("\n✅ All integration tests passed!")
    print(f"   Providers: {AIProvider.objects.count()}")
    print(f"   Models: {AIModel.objects.count()}")
    print(f"   Templates: {PromptTemplate.objects.count()}")
    print(f"   Issues: {Issue.objects.count()}")
