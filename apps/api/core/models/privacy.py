from __future__ import annotations

from django.conf import settings
from django.db import models

from .base import TimestampedModel


class ConsentRecord(TimestampedModel):
    organization = models.ForeignKey("Organization", on_delete=models.CASCADE)
    patient = models.ForeignKey(
        "Patient", on_delete=models.SET_NULL, null=True, blank=True
    )
    subject_type = models.CharField(max_length=32)
    subject_id = models.CharField(max_length=64)
    consent_type = models.CharField(max_length=120)
    scope = models.CharField(max_length=120, blank=True)
    lawful_basis = models.CharField(max_length=120, blank=True)
    granted_by = models.CharField(max_length=120, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    policy_version = models.CharField(max_length=64)
    channel = models.CharField(max_length=64, blank=True)
    granted = models.BooleanField(default=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    recorded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.organization_id}:{self.subject_type}:{self.consent_type}"


class DsarExport(TimestampedModel):
    organization = models.ForeignKey("Organization", on_delete=models.CASCADE)
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    subject_type = models.CharField(max_length=32)
    subject_id = models.CharField(max_length=64)
    status = models.CharField(max_length=32, default="pending")
    params_json = models.JSONField(default=dict, blank=True)
    artifact_path = models.CharField(max_length=512, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.organization_id}:{self.subject_type}:{self.subject_id}:{self.status}"
