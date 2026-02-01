from __future__ import annotations

from django.conf import settings
from django.db import models

from .base import TimestampedModel


class ExportJob(TimestampedModel):
    organization = models.ForeignKey("Organization", on_delete=models.CASCADE)
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    kind = models.CharField(max_length=64)
    params_json = models.JSONField(default=dict)
    status = models.CharField(max_length=16, default="queued")
    finished_at = models.DateTimeField(null=True, blank=True)
    artifact_path = models.CharField(max_length=512, blank=True)

    def __str__(self) -> str:
        return f"{self.organization_id}:{self.kind}:{self.status}"
