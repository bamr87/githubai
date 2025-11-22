#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from pathlib import Path


def main():
    """Run administrative tasks."""
    # Get the project root directory (where manage.py is located)
    BASE_DIR = Path(__file__).resolve().parent

    # Add apps directory to Python path so Django can find the apps
    apps_dir = BASE_DIR / 'apps'
    if str(apps_dir) not in sys.path:
        sys.path.insert(0, str(apps_dir))

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
