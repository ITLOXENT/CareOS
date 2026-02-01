from __future__ import annotations

from django.conf import settings
from django.db import models

from ..state import WORK_ITEM_STATUSES
from .base import TimestampedModel


class WorkItem(TimestampedModel):
    organization = models.ForeignKey("Organization", on_delete=models.CASCADE)
    episode = models.ForeignKey(
        "Episode", on_delete=models.CASCADE, related_name="work_items", null=True, blank=True
    )
    appointment = models.ForeignKey(
        "Appointment",
        on_delete=models.SET_NULL,
        related_name="work_items",
        null=True,
        blank=True,
    )
    kind = models.CharField(max_length=120)
    status = models.CharField(max_length=32, choices=WORK_ITEM_STATUSES, default="open")
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    due_at = models.DateTimeField(null=True, blank=True)
    sla_breach_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_work_items",
    )
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["organization", "status", "due_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.episode_id}:{self.kind}:{self.status}"
