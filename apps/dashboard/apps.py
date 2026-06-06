"""Dashboard app configuration.

The dashboard app turns GitHubAI from a single-repo, action-oriented tool into a
multi-repo, observation-oriented "DevOps cockpit": it registers repositories,
ingests signals from them on a schedule, stores time-series metrics, and lets
the AI layer distill what needs attention across the whole fleet.
"""
from django.apps import AppConfig


class DashboardConfig(AppConfig):
    """Configuration for the multi-repo DevOps cockpit dashboard app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dashboard'
    verbose_name = 'DevOps Cockpit Dashboard'
