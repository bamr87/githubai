"""
Example: Using Prompt Templates in GitHubAI

This demonstrates how to use the new prompt template system
instead of hardcoded prompts.
"""

from core.models import PromptTemplate
from core.services.ai_service import AIService


def example_1_chat_with_template():
    """Example 1: Use Chat Assistant template"""
    print("=" * 60)
    print("Example 1: Chat with Template")
    print("=" * 60)

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

    print(f"User: What is GitHubAI?")
    print(f"AI: {response[:200]}...")
    print()


def example_2_auto_issue():
    """Example 2: Generate auto issue with template"""
    print("=" * 60)
    print("Example 2: Auto Issue Generation")
    print("=" * 60)

    # Get template by category
    template = PromptTemplate.objects.get(
        category='auto_issue',
        is_active=True
    )

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

    # Generate issue (dry run - don't actually call AI to save tokens)
    print(f"Template: {template.name}")
    print(f"Context: {context}")
    print("\nThis would generate a GitHub issue with AI-generated content")
    print()


def example_3_backward_compatibility():
    """Example 3: Old way still works"""
    print("=" * 60)
    print("Example 3: Backward Compatibility")
    print("=" * 60)

    ai_service = AIService()

    # Old direct prompt method still works
    response = ai_service.call_ai_chat(
        system_prompt="You are a helpful assistant.",
        user_prompt="Say 'Hello, World!' in Python."
    )

    print(f"User: Say 'Hello, World!' in Python")
    print(f"AI: {response[:100]}...")
    print()


def example_4_query_templates():
    """Example 4: Query and filter templates"""
    print("=" * 60)
    print("Example 4: Query Templates")
    print("=" * 60)

    # Get all active templates
    active = PromptTemplate.objects.filter(is_active=True)
    print(f"Active templates: {active.count()}")

    # Get templates by category
    chat_templates = PromptTemplate.objects.filter(
        category='chat',
        is_active=True
    )
    print(f"Chat templates: {chat_templates.count()}")

    # Get most used template
    most_used = PromptTemplate.objects.filter(
        is_active=True
    ).order_by('-usage_count').first()

    if most_used:
        print(f"Most used: {most_used.name} ({most_used.usage_count} uses)")

    print()


if __name__ == '__main__':
    """
    Run with Django shell:
    docker-compose -f infra/docker/docker-compose.yml exec web python manage.py shell
    >>> exec(open('demo_prompt_templates.py').read())
    """

    print("\n" + "=" * 60)
    print("PROMPT TEMPLATE SYSTEM EXAMPLES")
    print("=" * 60 + "\n")

    example_4_query_templates()
    example_1_chat_with_template()
    example_2_auto_issue()
    example_3_backward_compatibility()

    print("=" * 60)
    print("Examples complete!")
    print("=" * 60)
