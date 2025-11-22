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
