"""PRD MACHINE Admin configuration - custom admin panel for PRD management."""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django import forms
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.shortcuts import render

from prd_machine.models import PRDState, PRDVersion, PRDEvent, PRDConflict, PRDExport


class PRDVersionInline(admin.TabularInline):
    """Inline display of PRD versions."""
    model = PRDVersion
    extra = 0
    readonly_fields = ['version', 'trigger_type', 'trigger_ref', 'change_summary', 'created_at', 'is_human_edit']
    fields = ['version', 'trigger_type', 'trigger_ref', 'change_summary', 'is_human_edit', 'created_at']
    ordering = ['-created_at']
    max_num = 10
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


class PRDConflictInline(admin.TabularInline):
    """Inline display of unresolved conflicts."""
    model = PRDConflict
    extra = 0
    readonly_fields = ['conflict_type', 'severity', 'section_affected', 'description', 'created_at']
    fields = ['conflict_type', 'severity', 'section_affected', 'resolved', 'created_at']
    ordering = ['-severity', '-created_at']
    max_num = 10

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(resolved=False)


class PRDExportInline(admin.TabularInline):
    """Inline display of recent exports."""
    model = PRDExport
    extra = 0
    readonly_fields = ['export_type', 'items_created', 'github_refs', 'created_at']
    fields = ['export_type', 'items_created', 'github_refs', 'created_at']
    ordering = ['-created_at']
    max_num = 5
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(PRDState)
class PRDStateAdmin(admin.ModelAdmin):
    """Admin for PRD State with custom actions."""

    list_display = [
        'repo', 'file_path', 'version', 'status_badge', 'lock_badge',
        'auto_evolve', 'last_distilled_at', 'conflict_count'
    ]
    list_filter = ['is_locked', 'auto_evolve', 'created_at']
    search_fields = ['repo', 'file_path']
    readonly_fields = [
        'content_hash', 'last_distilled_at', 'last_synced_at',
        'created_at', 'updated_at', 'content_preview'
    ]
    inlines = [PRDVersionInline, PRDConflictInline, PRDExportInline]

    fieldsets = (
        ('Repository', {
            'fields': ('repo', 'file_path', 'version')
        }),
        ('Content', {
            'fields': ('content_preview', 'content_hash'),
            'classes': ('collapse',)
        }),
        ('Automation Settings', {
            'fields': ('auto_evolve', 'is_locked', 'slack_webhook')
        }),
        ('Timestamps', {
            'fields': ('last_distilled_at', 'last_synced_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = [
        'action_sync_from_github',
        'action_distill_prd',
        'action_detect_conflicts',
        'action_export_to_issues',
        'action_toggle_lock',
        'action_generate_prd',
    ]

    def status_badge(self, obj):
        """Display freshness status badge."""
        from django.utils import timezone
        from datetime import timedelta

        if not obj.last_distilled_at:
            return format_html('<span style="color: gray;">⚪ Never Distilled</span>')

        age = timezone.now() - obj.last_distilled_at

        if age < timedelta(hours=24):
            return format_html('<span style="color: green;">🟢 Fresh</span>')
        elif age < timedelta(days=7):
            return format_html('<span style="color: orange;">🟡 Aging</span>')
        else:
            return format_html('<span style="color: red;">🔴 Stale</span>')
    status_badge.short_description = 'Freshness'

    def lock_badge(self, obj):
        """Display lock status badge."""
        if obj.is_locked:
            return format_html('<span style="color: red;">🔒 Zero-Touch</span>')
        return format_html('<span style="color: green;">🔓 Editable</span>')
    lock_badge.short_description = 'Lock'

    def conflict_count(self, obj):
        """Display unresolved conflict count."""
        count = obj.conflicts.filter(resolved=False).count()
        if count == 0:
            return format_html('<span style="color: green;">✓ None</span>')
        elif count < 3:
            return format_html(f'<span style="color: orange;">⚠ {count}</span>')
        else:
            return format_html(f'<span style="color: red;">⛔ {count}</span>')
    conflict_count.short_description = 'Conflicts'

    def content_preview(self, obj):
        """Display truncated content preview."""
        if obj.content:
            preview = obj.content[:1000].replace('\n', '<br>')
            return format_html(f'<pre style="max-height: 300px; overflow: auto;">{preview}...</pre>')
        return "No content"
    content_preview.short_description = 'Content Preview'

    # =========================================================================
    # Custom Actions
    # =========================================================================

    @admin.action(description="🔄 Sync PRD from GitHub")
    def action_sync_from_github(self, request, queryset):
        """Sync selected PRDs from GitHub."""
        from prd_machine.services.core import PRDMachineService

        synced = 0
        for prd_state in queryset:
            try:
                service = PRDMachineService(repo=prd_state.repo)
                service.sync_from_github(prd_state.file_path)
                synced += 1
            except Exception as e:
                messages.error(request, f"Failed to sync {prd_state.repo}: {e}")

        if synced:
            messages.success(request, f"Successfully synced {synced} PRD(s) from GitHub")

    @admin.action(description="🧠 Distill PRD with AI")
    def action_distill_prd(self, request, queryset):
        """Distill/evolve selected PRDs using AI."""
        from prd_machine.services.core import PRDMachineService

        distilled = 0
        for prd_state in queryset:
            try:
                service = PRDMachineService(repo=prd_state.repo)
                service.distill_prd(
                    prd_state=prd_state,
                    trigger_type='manual_sync',
                    trigger_ref='Admin action: Distill PRD'
                )
                distilled += 1
            except Exception as e:
                messages.error(request, f"Failed to distill {prd_state.repo}: {e}")

        if distilled:
            messages.success(request, f"Successfully distilled {distilled} PRD(s)")

    @admin.action(description="🔍 Detect Conflicts")
    def action_detect_conflicts(self, request, queryset):
        """Detect conflicts for selected PRDs."""
        from prd_machine.services.core import PRDMachineService

        total_conflicts = 0
        for prd_state in queryset:
            try:
                service = PRDMachineService(repo=prd_state.repo)
                conflicts = service.detect_conflicts(prd_state)
                total_conflicts += len(conflicts)
            except Exception as e:
                messages.error(request, f"Failed to detect conflicts for {prd_state.repo}: {e}")

        if total_conflicts:
            messages.warning(request, f"Detected {total_conflicts} conflict(s) across selected PRDs")
        else:
            messages.success(request, "No conflicts detected!")

    @admin.action(description="📤 Export to GitHub Issues")
    def action_export_to_issues(self, request, queryset):
        """Export selected PRDs to GitHub issues."""
        from prd_machine.services.core import PRDMachineService

        total_issues = 0
        for prd_state in queryset:
            try:
                service = PRDMachineService(repo=prd_state.repo)
                export = service.export_to_issues(prd_state)
                total_issues += export.items_created
            except Exception as e:
                messages.error(request, f"Failed to export {prd_state.repo}: {e}")

        if total_issues:
            messages.success(request, f"Created {total_issues} GitHub issue(s)")

    @admin.action(description="🔒 Toggle Zero-Touch Mode")
    def action_toggle_lock(self, request, queryset):
        """Toggle zero-touch mode for selected PRDs."""
        for prd_state in queryset:
            prd_state.is_locked = not prd_state.is_locked
            prd_state.save()

            status = "ENABLED" if prd_state.is_locked else "DISABLED"
            messages.info(request, f"Zero-touch mode {status} for {prd_state.repo}")

    @admin.action(description="🔧 Generate New PRD")
    def action_generate_prd(self, request, queryset):
        """Generate new PRD from scratch for selected repos."""
        from prd_machine.services.core import PRDMachineService

        generated = 0
        for prd_state in queryset:
            try:
                service = PRDMachineService(repo=prd_state.repo)
                service.generate_prd_from_scratch(file_path=prd_state.file_path)
                generated += 1
            except Exception as e:
                messages.error(request, f"Failed to generate PRD for {prd_state.repo}: {e}")

        if generated:
            messages.success(request, f"Generated {generated} new PRD(s)")


@admin.register(PRDVersion)
class PRDVersionAdmin(admin.ModelAdmin):
    """Admin for PRD Version history."""

    list_display = [
        'prd_state', 'version', 'trigger_type', 'is_human_edit',
        'change_summary_short', 'created_at'
    ]
    list_filter = ['trigger_type', 'is_human_edit', 'created_at']
    search_fields = ['prd_state__repo', 'version', 'change_summary', 'trigger_ref']
    readonly_fields = ['prd_state', 'version', 'content', 'content_hash', 'trigger_type', 'trigger_ref', 'created_at']

    fieldsets = (
        ('Version Info', {
            'fields': ('prd_state', 'version', 'trigger_type', 'trigger_ref', 'is_human_edit')
        }),
        ('Content', {
            'fields': ('content', 'content_hash'),
            'classes': ('collapse',)
        }),
        ('Summary', {
            'fields': ('change_summary',)
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def change_summary_short(self, obj):
        if obj.change_summary:
            return obj.change_summary[:100] + "..." if len(obj.change_summary) > 100 else obj.change_summary
        return "-"
    change_summary_short.short_description = 'Summary'


@admin.register(PRDEvent)
class PRDEventAdmin(admin.ModelAdmin):
    """Admin for PRD Events."""

    list_display = [
        'prd_state', 'event_type', 'processed_badge', 'result_short', 'created_at'
    ]
    list_filter = ['event_type', 'processed', 'created_at']
    search_fields = ['prd_state__repo', 'result']
    readonly_fields = ['prd_state', 'event_type', 'event_data', 'processed', 'processed_at', 'created_at']

    def processed_badge(self, obj):
        if obj.processed:
            return format_html('<span style="color: green;">✓ Processed</span>')
        return format_html('<span style="color: orange;">⏳ Pending</span>')
    processed_badge.short_description = 'Status'

    def result_short(self, obj):
        if obj.result:
            return obj.result[:50] + "..." if len(obj.result) > 50 else obj.result
        return "-"
    result_short.short_description = 'Result'


@admin.register(PRDConflict)
class PRDConflictAdmin(admin.ModelAdmin):
    """Admin for PRD Conflicts."""

    list_display = [
        'prd_state', 'conflict_type', 'severity_badge', 'section_affected',
        'resolved_badge', 'slack_notified', 'created_at'
    ]
    list_filter = ['conflict_type', 'severity', 'resolved', 'slack_notified', 'created_at']
    search_fields = ['prd_state__repo', 'description', 'suggested_resolution']

    fieldsets = (
        ('Conflict Details', {
            'fields': ('prd_state', 'conflict_type', 'severity', 'section_affected')
        }),
        ('Description', {
            'fields': ('description', 'suggested_resolution')
        }),
        ('Resolution', {
            'fields': ('resolved', 'resolved_at', 'resolved_by')
        }),
        ('Notifications', {
            'fields': ('slack_notified',),
            'classes': ('collapse',)
        }),
    )

    actions = ['action_resolve_conflicts', 'action_send_slack_alert']

    def severity_badge(self, obj):
        colors = {
            'low': 'blue',
            'medium': 'orange',
            'high': 'red',
            'critical': 'darkred',
        }
        color = colors.get(obj.severity, 'gray')
        return format_html(f'<span style="color: {color}; font-weight: bold;">{obj.severity.upper()}</span>')
    severity_badge.short_description = 'Severity'

    def resolved_badge(self, obj):
        if obj.resolved:
            return format_html('<span style="color: green;">✓ Resolved</span>')
        return format_html('<span style="color: red;">✗ Open</span>')
    resolved_badge.short_description = 'Status'

    @admin.action(description="✓ Mark as Resolved")
    def action_resolve_conflicts(self, request, queryset):
        """Mark selected conflicts as resolved."""
        from django.utils import timezone

        count = queryset.update(
            resolved=True,
            resolved_at=timezone.now(),
            resolved_by=f"Admin: {request.user.username}"
        )
        messages.success(request, f"Marked {count} conflict(s) as resolved")

    @admin.action(description="📢 Send Slack Alert")
    def action_send_slack_alert(self, request, queryset):
        """Send Slack alerts for selected conflicts."""
        from prd_machine.services.core import PRDMachineService

        sent = 0
        for conflict in queryset:
            service = PRDMachineService(repo=conflict.prd_state.repo)
            if service.send_slack_alert(conflict):
                sent += 1

        if sent:
            messages.success(request, f"Sent {sent} Slack alert(s)")
        else:
            messages.warning(request, "No alerts sent (check Slack webhook configuration)")


@admin.register(PRDExport)
class PRDExportAdmin(admin.ModelAdmin):
    """Admin for PRD Exports."""

    list_display = [
        'prd_state', 'export_type', 'items_created', 'github_refs_display', 'created_at'
    ]
    list_filter = ['export_type', 'created_at']
    search_fields = ['prd_state__repo']
    readonly_fields = ['prd_state', 'prd_version', 'export_type', 'items_created', 'details', 'github_refs', 'created_at']

    def github_refs_display(self, obj):
        if obj.github_refs:
            refs = ', '.join(f"#{r}" for r in obj.github_refs[:5])
            if len(obj.github_refs) > 5:
                refs += f" (+{len(obj.github_refs) - 5} more)"
            return refs
        return "-"
    github_refs_display.short_description = 'GitHub Refs'
