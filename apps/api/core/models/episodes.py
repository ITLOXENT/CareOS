from __future__ import annotations

from django.conf import settings
from django.db import models

from ..state import EPISODE_STATES, PICKUP_STATUSES
from .base import TimestampedModel


class Episode(TimestampedModel):
    organization = models.ForeignKey("Organization", on_delete=models.CASCADE)
    patient = models.ForeignKey(
        "Patient", on_delete=models.SET_NULL, null=True, blank=True
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=32, choices=EPISODE_STATES, default="new")
    pickup_status = models.CharField(
        max_length=32, choices=PICKUP_STATUSES, default="not_ready"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_episodes",
    )
    retention_class = models.CharField(max_length=64, blank=True, default="")
    retention_until = models.DateField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["organization", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.organization_id}:{self.title}"


class EpisodeEvent(TimestampedModel):
    organization = models.ForeignKey("Organization", on_delete=models.CASCADE)
    episode = models.ForeignKey("Episode", on_delete=models.CASCADE, related_name="events")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    event_type = models.CharField(max_length=120)
    from_state = models.CharField(max_length=32, blank=True)
    to_state = models.CharField(max_length=32, blank=True)
    note = models.TextField(blank=True)
    payload_json = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ("created_at",)

    def __str__(self) -> str:
        return f"{self.episode_id}:{self.event_type}:{self.to_state}"
