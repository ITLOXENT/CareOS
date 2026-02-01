from __future__ import annotations

from django.conf import settings
from django.db import models
from django.db.models import Q

from .base import TimestampedModel


class Notification(TimestampedModel):
    organization = models.ForeignKey("Organization", on_delete=models.CASCADE)
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications"
    )
    kind = models.CharField(max_length=64, default="general")
    title = models.CharField(max_length=255)
    body = models.TextField(blank=True)
    url = models.CharField(max_length=512, blank=True)
    unread = models.BooleanField(default=True)
    read_at = models.DateTimeField(null=True, blank=True)
    dedupe_key = models.CharField(max_length=120, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "recipient", "dedupe_key"],
                name="unique_notification_dedupe",
                condition=Q(dedupe_key__isnull=False),
            )
        ]
        indexes = [
            models.Index(fields=["recipient", "read_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.organization_id}:{self.recipient_id}:{self.title}"
