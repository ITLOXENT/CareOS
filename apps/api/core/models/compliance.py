from __future__ import annotations

from django.conf import settings
from django.db import models

from .base import TimestampedModel


class EvidenceBundle(TimestampedModel):
    organization = models.ForeignKey("Organization", on_delete=models.CASCADE)
    episode = models.ForeignKey("Episode", on_delete=models.CASCADE)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    manifest = models.JSONField(default=dict)
    artifact_path = models.CharField(max_length=512, blank=True)

    def __str__(self) -> str:
        return f"{self.episode_id}:{self.id}"


class ReportJob(TimestampedModel):
    organization = models.ForeignKey("Organization", on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    report_type = models.CharField(max_length=120)
    status = models.CharField(max_length=32, default="active")
    interval_days = models.PositiveIntegerField(default=30)
    next_run_at = models.DateTimeField(null=True, blank=True)
    last_run_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    params_json = models.JSONField(default=dict, blank=True)
    artifact_path = models.CharField(max_length=512, blank=True)

    def __str__(self) -> str:
        return f"{self.organization_id}:{self.name}:{self.report_type}"


class SubmissionRecord(TimestampedModel):
    organization = models.ForeignKey("Organization", on_delete=models.CASCADE)
    episode = models.ForeignKey("Episode", on_delete=models.SET_NULL, null=True, blank=True)
    due_date = models.DateField()
    submitted_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=32, default="pending")
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self) -> str:
        return f"{self.organization_id}:{self.status}:{self.due_date.isoformat()}"
