"""
Test environment settings for GitHubAI.

This module extends the base settings with test-specific configurations:
- Isolated test database
- Mock AI provider support
- Synchronous Celery tasks for easier debugging
- Query logging for analysis
- Auto-loads .env.test file

Usage:
    export DJANGO_SETTINGS_MODULE=githubai.settings_test
    # or set in docker-compose.test.yml
"""

import logging
from pathlib import Path

# Import all base settings
from .settings import *  # noqa: F403, F401

# Auto-load .env.test file (takes precedence over .env)
env_test_file = BASE_DIR / ".env.test"  # noqa: F405
if env_test_file.exists():
    environ.Env.read_env(str(env_test_file))  # noqa: F405
    logger = logging.getLogger("githubai")
    logger.info(f"Loaded test environment from {env_test_file}")
else:
    logger = logging.getLogger("githubai")
    logger.warning(
        f"Test environment file not found: {env_test_file}. "
        "Copy .env.test.example to .env.test and customize."
    )

# ==============================================================================
# TEST DATABASE CONFIGURATION
# ==============================================================================

# Override database for test environment
DATABASES = {  # noqa: F405
    "default": env.db(  # noqa: F405
        "DATABASE_URL",
        default="postgresql://githubai_test:test123@db:5432/githubai_test",
    )
}

# Enable connection pooling
DATABASES["default"]["CONN_MAX_AGE"] = 600  # noqa: F405
DATABASES["default"]["CONN_HEALTH_CHECKS"] = True  # noqa: F405

# ==============================================================================
# DEBUG AND LOGGING
# ==============================================================================

# Force DEBUG on in test environment
DEBUG = True  # noqa: F405

# Enable query logging for analysis
if env("ENABLE_QUERY_LOGGING", default=True):  # noqa: F405
    LOGGING["loggers"]["django.db.backends"] = {  # noqa: F405
        "level": "DEBUG",
        "handlers": ["console", "file"],
        "propagate": False,
    }

# ==============================================================================
# CELERY CONFIGURATION (TEST)
# ==============================================================================

# Run Celery tasks synchronously in test environment for easier debugging
CELERY_TASK_ALWAYS_EAGER = env("CELERY_TASK_ALWAYS_EAGER", default=True)  # noqa: F405
CELERY_TASK_EAGER_PROPAGATES = env("CELERY_TASK_EAGER_PROPAGATES", default=True)  # noqa: F405

# Use different Redis DB for test environment
CELERY_BROKER_URL = env(  # noqa: F405
    "CELERY_BROKER_URL", default="redis://redis:6379/1"
)
CELERY_RESULT_BACKEND = env(  # noqa: F405
    "CELERY_RESULT_BACKEND", default="redis://redis:6379/1"
)

# ==============================================================================
# MOCK AI PROVIDER REGISTRATION
# ==============================================================================

# Register MockAIProvider for test environment
# This allows deterministic testing without real API calls
TEST_ENV = env("TEST_ENV", default=False)  # noqa: F405

if TEST_ENV:
    # Import and register MockAIProvider
    try:
        from core.services.mock_provider import MockAIProvider
        from core.services.ai_providers import AIProviderFactory

        AIProviderFactory.register_provider("mock", MockAIProvider)
        logger.info("MockAIProvider registered for test environment")
    except ImportError as e:
        logger.warning(f"MockAIProvider not available: {e} - real providers will be used")

# ==============================================================================
# TEST DATA CONFIGURATION
# ==============================================================================

# Control test data generation volumes
TEST_DATA_CONFIG = {
    "providers": env("TEST_DATA_PROVIDERS", default=2),  # noqa: F405
    "models": env("TEST_DATA_MODELS", default=4),  # noqa: F405
    "templates": env("TEST_DATA_TEMPLATES", default=10),  # noqa: F405
    "issues": env("TEST_DATA_ISSUES", default=20),  # noqa: F405
}

# Path to mock AI responses fixture (dated format)
MOCK_AI_RESPONSES_FIXTURE = env(  # noqa: F405
    "MOCK_AI_RESPONSES_FIXTURE",
    default="apps/core/fixtures/test_ai_responses_2025-11-25.json",
)

# ==============================================================================
# SECURITY (TEST)
# ==============================================================================

# Relaxed security for test environment
SECRET_KEY = env(  # noqa: F405
    "SECRET_KEY", default="test-secret-key-do-not-use-in-production"
)
ALLOWED_HOSTS = ["*"]  # Allow all hosts in test environment  # noqa: F405

# ==============================================================================
# STATIC/MEDIA (TEST)
# ==============================================================================

# Separate static/media for test environment
STATIC_ROOT = BASE_DIR / "staticfiles_test"  # noqa: F405
MEDIA_ROOT = BASE_DIR / "media_test"  # noqa: F405

# ==============================================================================
# EMAIL (TEST)
# ==============================================================================

# Use console backend for email in test environment
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"  # noqa: F405

# ==============================================================================
# CACHE (TEST)
# ==============================================================================

# Use Redis DB 1 for cache in test environment
CACHES = {  # noqa: F405
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

# Log test environment activation
logger.info("=" * 80)
logger.info("TEST ENVIRONMENT ACTIVATED")
logger.info(f"Database: {DATABASES['default']['NAME']}")  # noqa: F405
logger.info(f"Mock AI: {TEST_ENV}")
logger.info(f"Celery Eager: {CELERY_TASK_ALWAYS_EAGER}")
logger.info("=" * 80)
