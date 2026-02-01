from __future__ import annotations

from django.conf import settings
from django.db import models

from ..state import INTEROP_STATUSES
from .base import TimestampedModel


class InteropMessage(TimestampedModel):
    organization = models.ForeignKey("Organization", on_delete=models.CASCADE)
    episode = models.ForeignKey("Episode", on_delete=models.SET_NULL, null=True, blank=True)
    external_system = models.CharField(max_length=64)
    payload = models.JSONField(default=dict)
    status = models.CharField(max_length=16, choices=INTEROP_STATUSES, default="draft")
    status_reason = models.TextField(blank=True)
    attempts = models.PositiveIntegerField(default=0)
    last_error = models.TextField(blank=True)
    simulator_mode = models.BooleanField(default=False)
    external_id = models.CharField(max_length=128, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self) -> str:
        return f"{self.external_system}:{self.id}:{self.status}"


class InteropStatusEvent(TimestampedModel):
    message = models.ForeignKey(
        InteropMessage, on_delete=models.CASCADE, related_name="status_events"
    )
    status = models.CharField(max_length=16, choices=INTEROP_STATUSES)
    detail = models.TextField(blank=True)

    def __str__(self) -> str:
        return f"{self.message_id}:{self.status}"
