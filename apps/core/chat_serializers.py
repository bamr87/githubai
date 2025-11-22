"""
Serializers for chat API.
"""
from rest_framework import serializers


class ChatMessageSerializer(serializers.Serializer):
    """Serializer for incoming chat messages."""
    message = serializers.CharField(required=True, allow_blank=False)


class ChatResponseSerializer(serializers.Serializer):
    """Serializer for chat responses."""
    response = serializers.CharField()
    provider = serializers.CharField()
    model = serializers.CharField()
    cached = serializers.BooleanField()
    timestamp = serializers.DateTimeField()
