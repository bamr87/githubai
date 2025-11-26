"""Core app for shared functionality"""
import logging

from django.apps import AppConfig
from django.conf import settings

logger = logging.getLogger("githubai")


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = 'Core'

    def ready(self):
        """Called when Django apps are fully loaded."""
        # Register MockAIProvider for test environment
        # This must be done here, after Django apps are ready
        if getattr(settings, "TEST_ENV", False):
            try:
                from core.services.mock_provider import MockAIProvider
                from core.services.ai_providers import AIProviderFactory

                AIProviderFactory.register_provider("mock", MockAIProvider)
                logger.info("MockAIProvider registered for test environment")
            except ImportError as e:
                logger.warning(
                    f"MockAIProvider not available: {e} - real providers will be used"
                )
