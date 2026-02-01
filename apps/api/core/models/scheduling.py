from __future__ import annotations

from django.conf import settings
from django.db import models

from ..state import APPOINTMENT_STATUSES, TASK_PRIORITIES, TASK_STATUSES
from .base import TimestampedModel


class Appointment(TimestampedModel):
    organization = models.ForeignKey("Organization", on_delete=models.CASCADE)
    patient = models.ForeignKey(
        "Patient", on_delete=models.SET_NULL, null=True, blank=True
    )
    episode = models.ForeignKey(
        "Episode", on_delete=models.SET_NULL, null=True, blank=True
    )
    scheduled_at = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=30)
    location = models.CharField(max_length=255, blank=True)
    status = models.CharField(
        max_length=32, choices=APPOINTMENT_STATUSES, default="scheduled"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    notes = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["organization", "scheduled_at"]),
            models.Index(fields=["organization", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.organization_id}:{self.scheduled_at}:{self.status}"


class Task(TimestampedModel):
    organization = models.ForeignKey("Organization", on_delete=models.CASCADE)
    episode = models.ForeignKey(
        "Episode", on_delete=models.SET_NULL, null=True, blank=True
    )
    work_item = models.ForeignKey(
        "WorkItem", on_delete=models.SET_NULL, null=True, blank=True
    )
    title = models.CharField(max_length=255)
    status = models.CharField(max_length=32, choices=TASK_STATUSES, default="open")
    priority = models.CharField(
        max_length=16, choices=TASK_PRIORITIES, default="medium"
    )
    due_at = models.DateTimeField(null=True, blank=True)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_tasks",
    )
    completed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["organization", "status", "due_at"]),
            models.Index(fields=["organization", "priority"]),
        ]

    def __str__(self) -> str:
        return f"{self.organization_id}:{self.title}:{self.status}"
