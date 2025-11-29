"""PRD MACHINE serializers for REST API."""
from rest_framework import serializers
from prd_machine.models import PRDState, PRDVersion, PRDEvent, PRDConflict, PRDExport


class PRDVersionSerializer(serializers.ModelSerializer):
    """Serializer for PRD Version."""

    class Meta:
        model = PRDVersion
        fields = [
            'id', 'prd_state', 'version', 'content_hash', 'change_summary',
            'trigger_type', 'trigger_ref', 'is_human_edit', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'content_hash']


class PRDVersionDetailSerializer(PRDVersionSerializer):
    """Detailed serializer including content."""

    class Meta(PRDVersionSerializer.Meta):
        fields = PRDVersionSerializer.Meta.fields + ['content']


class PRDEventSerializer(serializers.ModelSerializer):
    """Serializer for PRD Event."""

    class Meta:
        model = PRDEvent
        fields = [
            'id', 'prd_state', 'event_type', 'event_data',
            'processed', 'processed_at', 'result', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class PRDConflictSerializer(serializers.ModelSerializer):
    """Serializer for PRD Conflict."""

    class Meta:
        model = PRDConflict
        fields = [
            'id', 'prd_state', 'conflict_type', 'description', 'severity',
            'section_affected', 'suggested_resolution', 'resolved',
            'resolved_at', 'resolved_by', 'slack_notified', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class PRDExportSerializer(serializers.ModelSerializer):
    """Serializer for PRD Export."""

    class Meta:
        model = PRDExport
        fields = [
            'id', 'prd_state', 'prd_version', 'export_type',
            'items_created', 'details', 'github_refs', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class PRDStateSerializer(serializers.ModelSerializer):
    """Serializer for PRD State."""

    versions_count = serializers.SerializerMethodField()
    conflicts_count = serializers.SerializerMethodField()
    latest_version = PRDVersionSerializer(source='versions.first', read_only=True)

    class Meta:
        model = PRDState
        fields = [
            'id', 'repo', 'file_path', 'version', 'content_hash',
            'is_locked', 'auto_evolve', 'last_distilled_at', 'last_synced_at',
            'slack_webhook', 'created_at', 'updated_at',
            'versions_count', 'conflicts_count', 'latest_version'
        ]
        read_only_fields = ['id', 'content_hash', 'created_at', 'updated_at']

    def get_versions_count(self, obj):
        return obj.versions.count()

    def get_conflicts_count(self, obj):
        return obj.conflicts.filter(resolved=False).count()


class PRDStateDetailSerializer(PRDStateSerializer):
    """Detailed serializer including content."""

    recent_versions = PRDVersionSerializer(many=True, read_only=True)
    open_conflicts = PRDConflictSerializer(many=True, read_only=True)

    class Meta(PRDStateSerializer.Meta):
        fields = PRDStateSerializer.Meta.fields + [
            'content', 'recent_versions', 'open_conflicts'
        ]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['recent_versions'] = PRDVersionSerializer(
            instance.versions.order_by('-created_at')[:5],
            many=True
        ).data
        ret['open_conflicts'] = PRDConflictSerializer(
            instance.conflicts.filter(resolved=False),
            many=True
        ).data
        return ret
