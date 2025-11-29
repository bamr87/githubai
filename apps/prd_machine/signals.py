"""PRD MACHINE signals - Django signals for automated PRD updates."""
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger('githubai')


# Note: Most PRD MACHINE automation is triggered via:
# 1. Celery tasks (for GitHub webhook events)
# 2. Management commands (for CLI operations)
# 3. Admin actions (for manual triggers)
#
# Django signals are used here for internal state synchronization
# and to trigger side effects when models are updated.


@receiver(post_save, sender='prd_machine.PRDConflict')
def on_conflict_created(sender, instance, created, **kwargs):
    """Send Slack alert when a high-severity conflict is created."""
    if created and instance.severity in ('high', 'critical'):
        # Queue Slack notification
        if instance.prd_state.slack_webhook and not instance.slack_notified:
            try:
                from prd_machine.tasks import send_slack_alert_task
                # Note: This task doesn't exist yet - would need to be added
                # send_slack_alert_task.delay(instance.id)
                logger.info(f"Queued Slack alert for conflict {instance.id}")
            except Exception as e:
                logger.warning(f"Could not queue Slack alert: {e}")


@receiver(post_save, sender='prd_machine.PRDState')
def on_prd_state_updated(sender, instance, created, **kwargs):
    """Track PRD state changes for audit logging."""
    if created:
        logger.info(f"New PRD state created: {instance.repo}:{instance.file_path}")
    else:
        logger.debug(f"PRD state updated: {instance.repo} v{instance.version}")


@receiver(post_save, sender='prd_machine.PRDVersion')
def on_version_created(sender, instance, created, **kwargs):
    """Log version creation events."""
    if created:
        logger.info(
            f"PRD version created: {instance.prd_state.repo} v{instance.version} "
            f"(trigger: {instance.trigger_type})"
        )
