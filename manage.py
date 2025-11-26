#!/usr/bin/env python
"""Django's command-line utility for administrative tasks.

This script is the entry point for all Django management commands.
It automatically configures the Python path and Django settings module.

For more information on django-admin and manage.py commands, see:
https://docs.djangoproject.com/en/5.2/ref/django-admin/

Usage:
    python manage.py <command> [options]

Common commands:
    runserver           Start the development server
    migrate             Apply database migrations
    makemigrations      Create new migrations based on model changes
    createsuperuser     Create a superuser account
    shell               Start the Python interactive interpreter
    test                Run tests
    check               Check for common project issues

For a full list of commands:
    python manage.py help

For help with a specific command:
    python manage.py help <command>
"""
import os
import sys
from pathlib import Path


def main():
    """Run administrative tasks.

    This function:
    1. Sets up the Python path to include the apps directory
    2. Configures the Django settings module
    3. Executes the requested management command

    Raises:
        ImportError: If Django is not installed or cannot be imported
    """
    # Get the project root directory (where manage.py is located)
    BASE_DIR = Path(__file__).resolve().parent

    # Add apps directory to Python path so Django can find the apps
    # This allows importing as 'from core.models import ...' instead of 'from apps.core.models'
    apps_dir = BASE_DIR / 'apps'
    if str(apps_dir) not in sys.path:
        sys.path.insert(0, str(apps_dir))

    # Set the Django settings module
    # Can be overridden with DJANGO_SETTINGS_MODULE environment variable
    # or --settings command line option
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'githubai.settings')

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
