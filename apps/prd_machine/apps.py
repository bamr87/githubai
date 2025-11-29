"""PRD MACHINE app configuration"""
import logging

from django.apps import AppConfig

logger = logging.getLogger("githubai")


class PrdMachineConfig(AppConfig):
    """Configuration for PRD MACHINE app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'prd_machine'
    verbose_name = 'PRD MACHINE'

    def ready(self):
        """Called when Django apps are fully loaded."""
        # Import signals to register them
        try:
            from prd_machine import signals  # noqa: F401
            logger.info("PRD MACHINE signals registered")
        except ImportError as e:
            logger.warning(f"PRD MACHINE signals not loaded: {e}")
