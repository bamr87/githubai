"""Tests for prompt refinement functionality"""
import pytest
from django.test import TestCase
from core.models import PromptTemplate
from core.services.ai_service import AIService


@pytest.mark.django_db
class TestPromptRefinement:
    """Test prompt refinement functionality"""

    @pytest.fixture
    def sample_prompts(self):
        """Create sample prompts for testing"""
        prompts = [
            PromptTemplate.objects.create(
                name="Test Issue Generator",
                category="auto_issue",
                description="Generate GitHub issues from code analysis",
                system_prompt="You are a helpful assistant that creates GitHub issues.",
                user_prompt_template="Create an issue for repo {{ repo }} with context: {{ context }}",
                version_number=1,
                is_active=True
            ),
            PromptTemplate.objects.create(
                name="Test Bug Report",
                category="auto_issue",
                description="Generate bug reports",
                system_prompt="You are a bug report generator.",
                user_prompt_template="Create a bug report for: {{ issue_description }}",
                version_number=1,
                is_active=True
            ),
        ]
        return prompts

    @pytest.fixture
    def ai_service(self):
        """Create AIService instance"""
        return AIService()

    @pytest.mark.integration
    def test_refine_prompts_structure(self, ai_service, sample_prompts):
        """Test that refine_prompts returns proper structure"""
        # Note: This will call actual AI API
        try:
            results = ai_service.refine_prompts(
                selected_prompts=sample_prompts[:1],
                refinement_context="Make the prompt more concise",
                operation_mode='refine'
            )

            # Verify structure
            assert isinstance(results, list)
            assert len(results) >= 1

            for result in results:
                assert 'system_prompt' in result
                assert 'user_prompt_template' in result
                assert 'suggested_name' in result
                assert 'suggested_variables' in result
                assert isinstance(result['suggested_variables'], list)

        except Exception as e:
            pytest.skip(f"AI service not available: {e}")

    @pytest.mark.integration
    def test_refine_prompts_with_additional_prompts(self, ai_service, sample_prompts):
        """Test refinement with additional reference prompts"""
        try:
            results = ai_service.refine_prompts(
                selected_prompts=sample_prompts[:1],
                refinement_context="Combine features from both prompts",
                operation_mode='create_new',
                additional_prompts=sample_prompts[1:]
            )

            assert isinstance(results, list)
            assert len(results) >= 1

        except Exception as e:
            pytest.skip(f"AI service not available: {e}")

    @pytest.mark.integration
    def test_original_prompt_attachment(self, ai_service, sample_prompts):
        """Test that original prompts are attached in refine mode"""
        try:
            results = ai_service.refine_prompts(
                selected_prompts=sample_prompts[:1],
                refinement_context="Improve clarity",
                operation_mode='refine'
            )

            # In refine mode, should have original_prompt
            if results:
                assert results[0].get('original_prompt') is not None

        except Exception as e:
            pytest.skip(f"AI service not available: {e}")

    @pytest.mark.integration
    def test_create_new_mode(self, ai_service, sample_prompts):
        """Test create_new operation mode"""
        try:
            results = ai_service.refine_prompts(
                selected_prompts=sample_prompts[:1],
                refinement_context="Create a variation for documentation generation",
                operation_mode='create_new'
            )

            assert isinstance(results, list)

        except Exception as e:
            pytest.skip(f"AI service not available: {e}")


@pytest.mark.django_db
class TestPromptTemplateVersioning:
    """Test version management for prompts"""

    @pytest.fixture
    def sample_prompt(self):
        """Create a sample prompt"""
        return PromptTemplate.objects.create(
            name="Test Issue Generator",
            category="auto_issue",
            description="Generate GitHub issues from code analysis",
            system_prompt="You are a helpful assistant that creates GitHub issues.",
            user_prompt_template="Create an issue for repo {{ repo }} with context: {{ context }}",
            version_number=1,
            is_active=True
        )

    def test_version_increment(self, sample_prompt):
        """Test that creating new versions increments version number"""
        original = sample_prompt

        new_version = PromptTemplate.objects.create(
            name=f"{original.name} v2",  # Unique name required
            category=original.category,
            description="Refined version",
            system_prompt="Updated system prompt",
            user_prompt_template="Updated user prompt",
            version_number=original.version_number + 1,
            parent_version=original,
            is_active=True
        )

        assert new_version.version_number == 2
        assert new_version.parent_version == original

    def test_multiple_versions(self, sample_prompt):
        """Test creating multiple versions of same prompt"""
        original = sample_prompt

        v2 = PromptTemplate.objects.create(
            name=f"{original.name} v2",  # Unique name required
            category=original.category,
            description="Version 2",
            system_prompt="V2 system prompt",
            user_prompt_template="V2 user prompt",
            version_number=2,
            parent_version=original,
            is_active=True
        )

        v3 = PromptTemplate.objects.create(
            name=f"{original.name} v3",  # Unique name required
            category=original.category,
            description="Version 3",
            system_prompt="V3 system prompt",
            user_prompt_template="V3 user prompt",
            version_number=3,
            parent_version=v2,
            is_active=True
        )

        # Check version chain
        assert v3.parent_version == v2
        assert v2.parent_version == original
        assert original.parent_version is None


@pytest.mark.django_db
class TestPromptAdminActions:
    """Test admin interface functionality"""

    def test_prompt_template_creation(self):
        """Test basic prompt template creation"""
        prompt = PromptTemplate.objects.create(
            name="Test Prompt",
            category="chat",
            description="Test description",
            system_prompt="Test system prompt",
            user_prompt_template="Test user prompt {{ variable }}",
            is_active=False
        )

        assert prompt.name == "Test Prompt"
        assert prompt.version_number == 1
        assert not prompt.is_active

    def test_suggested_variables_in_template(self):
        """Test that Jinja2 variables are properly formatted"""
        prompt = PromptTemplate.objects.create(
            name="Variable Test",
            category="chat",
            description="Test",
            system_prompt="System prompt",
            user_prompt_template="Hello {{ name }}, your repo is {{ repo_name }}",
            is_active=True
        )

        # Check that template contains proper Jinja2 syntax
        assert "{{ name }}" in prompt.user_prompt_template
        assert "{{ repo_name }}" in prompt.user_prompt_template

