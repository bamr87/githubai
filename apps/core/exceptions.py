"""Custom exception handlers"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
import logging

logger = logging.getLogger('githubai')


def custom_exception_handler(exc, context):
    """Custom exception handler for REST framework"""
    response = exception_handler(exc, context)

    if response is not None:
        logger.error(f"API Error: {exc}", exc_info=True)
        response.data['status_code'] = response.status_code

    return response


# ============================================================================
# Prompt Management Exceptions
# ============================================================================

class PromptTemplateError(Exception):
    """Base exception for prompt template errors"""
    pass


class PromptTemplateNotFoundError(PromptTemplateError):
    """Raised when a prompt template cannot be found"""
    pass


class PromptRenderError(PromptTemplateError):
    """Raised when Jinja2 template rendering fails"""
    pass


class PromptValidationError(PromptTemplateError):
    """Raised when prompt output validation fails"""
    pass


class PromptSchemaError(PromptTemplateError):
    """Raised when there are issues with prompt schema"""
    pass

