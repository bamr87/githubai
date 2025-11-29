"""PRD MACHINE - AI-powered Product Requirements Document automation.

This app provides:
- Auto-generation of PRD.md from repo signals
- Real-time PRD distillation from GitHub events
- Conflict detection and Slack alerts
- Export to auto-issues, changelog, and version bump
- Zero-touch mode for fully automated PRD management

Configuration:
    Add 'prd_machine.apps.PrdMachineConfig' to INSTALLED_APPS
"""

default_app_config = 'prd_machine.apps.PrdMachineConfig'
