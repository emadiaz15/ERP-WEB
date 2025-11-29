from rest_framework import serializers
from apps.notifications.models.notification_model import Notification
from apps.products.api.serializers.base_serializer import BaseSerializer


class NotificationSerializer(BaseSerializer):
    class Meta:
        model = Notification
        fields = [
            "id",
            "notif_type",
            "title",
            "message",
            "payload",
            "is_read",
            "read_at",
            "created_at",
            "created_by",
        ]
        read_only_fields = [
            "id",
            "is_read",
            "read_at",
            "created_at",
            "created_by",
        ]
