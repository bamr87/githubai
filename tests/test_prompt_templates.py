"""
Tests for Prompt Template System

Converted from demo_prompt_templates.py to pytest test suite.
Tests prompt template usage, AI service integration, and backward compatibility.
"""

import pytest
from core.models import PromptTemplate
from core.services.ai_service import AIService


@pytest.mark.django_db
class TestPromptTemplateUsage:
    """Test prompt template system functionality"""

    @pytest.mark.integration
    def test_chat_with_template(self):
        """Test using Chat Assistant template with AI service"""
        # Get the template
        template = PromptTemplate.objects.get(
            name='Chat Assistant',
            is_active=True
        )

        # Create AI service
        ai_service = AIService()

        # Call AI with template and context
        response = ai_service.call_ai_chat(
            prompt_template_id=template.id,
            context={'message': 'What is GitHubAI?'}
        )

        assert response is not None
        assert len(response) > 0
        assert isinstance(response, str)

    def test_query_templates(self):
        """Test querying and filtering prompt templates"""
        # Get all active templates
        active = PromptTemplate.objects.filter(is_active=True)
        assert active.count() > 0

        # Get templates by category
        chat_templates = PromptTemplate.objects.filter(
            category='chat',
            is_active=True
        )
        # Should have at least one chat template
        assert chat_templates.exists()

    def test_template_usage_count(self):
        """Test that templates track usage count"""
        # Get most used template
        most_used = PromptTemplate.objects.filter(
            is_active=True
        ).order_by('-usage_count').first()

        if most_used:
            assert most_used.usage_count >= 0
            assert most_used.name is not None

    @pytest.mark.integration
    def test_auto_issue_template(self):
        """Test auto issue generation with template"""
        # Get template by category
        template = PromptTemplate.objects.filter(
            category='auto_issue',
            is_active=True
        ).first()

        if not template:
            pytest.skip("No auto_issue template found")

        ai_service = AIService()

        # Prepare context
        context = {
            'repo': 'bamr87/githubai',
            'chore_type': 'documentation',
            'analysis_data': '''
            Found 10 files missing docstrings:
            - apps/core/models.py (3 classes)
            - apps/core/services/ai_service.py (5 methods)
            - apps/core/admin.py (2 admin classes)

            Recommendation: Add comprehensive docstrings following Google style guide.
            '''
        }

        # Test template rendering (don't call AI to save tokens)
        from jinja2 import Template
        rendered_template = Template(template.user_prompt_template)
        rendered = rendered_template.render(**context)

        assert 'bamr87/githubai' in rendered
        assert 'documentation' in rendered
        assert len(rendered) > 0

    @pytest.mark.integration
    def test_backward_compatibility(self):
        """Test that old direct prompt method still works"""
        ai_service = AIService()

        # Old direct prompt method should still work
        response = ai_service.call_ai_chat(
            system_prompt="You are a helpful assistant.",
            user_prompt="Say 'Hello, World!' in Python."
        )

        assert response is not None
        assert len(response) > 0
        assert isinstance(response, str)

    def test_template_categories(self):
        """Test that templates have valid categories"""
        templates = PromptTemplate.objects.filter(is_active=True)

        valid_categories = ['chat', 'auto_issue', 'documentation', 'code_analysis', 'other']

        for template in templates:
            assert template.category in valid_categories, \
                f"Template {template.name} has invalid category: {template.category}"

    def test_template_has_required_fields(self):
        """Test that active templates have required fields populated"""
        templates = PromptTemplate.objects.filter(is_active=True)

        for template in templates:
            assert template.name is not None and len(template.name) > 0
            # Either system or user prompt should be present
            has_system = template.system_prompt_template and len(template.system_prompt_template) > 0
            has_user = template.user_prompt_template and len(template.user_prompt_template) > 0
            assert has_system or has_user, \
                f"Template {template.name} missing both system and user prompts"

    @pytest.mark.integration
    def test_template_caching(self):
        """Test that AI responses are cached when using templates"""
        ai_service = AIService()

        # Get a simple template
        template = PromptTemplate.objects.filter(
            category='chat',
            is_active=True
        ).first()

        if not template:
            pytest.skip("No chat template found")

        context = {'message': 'Test caching'}

        # First call - should hit API
        response1 = ai_service.call_ai_chat(
            prompt_template_id=template.id,
            context=context,
            use_cache=True
        )

        # Second call - should use cache
        response2 = ai_service.call_ai_chat(
            prompt_template_id=template.id,
            context=context,
            use_cache=True
        )

        # Responses should be identical due to caching
        assert response1 == response2

    def test_inactive_templates_not_used(self):
        """Test that inactive templates are not used by default queries"""
        # Create an inactive template for testing
        inactive_template = PromptTemplate.objects.create(
            name='Test Inactive Template',
            category='other',
            system_prompt_template='Test system prompt',
            user_prompt_template='Test user prompt',
            is_active=False
        )

        # Query should not return inactive templates
        active_templates = PromptTemplate.objects.filter(
            is_active=True,
            name='Test Inactive Template'
        )

        assert active_templates.count() == 0

        # Cleanup
        inactive_template.delete()
