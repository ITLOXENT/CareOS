from __future__ import annotations

from django.db import models

from .base import TimestampedModel


class PortalInvite(TimestampedModel):
    organization = models.ForeignKey("Organization", on_delete=models.CASCADE)
    patient = models.ForeignKey("Patient", on_delete=models.CASCADE)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=32, blank=True)
    role = models.CharField(max_length=20)
    token_hash = models.CharField(max_length=64)
    expires_at = models.DateTimeField()
    accepted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.organization_id}:{self.patient_id}:{self.role}"


class PortalSession(TimestampedModel):
    organization = models.ForeignKey("Organization", on_delete=models.CASCADE)
    patient = models.ForeignKey("Patient", on_delete=models.CASCADE)
    role = models.CharField(max_length=20)
    token = models.CharField(max_length=64, unique=True)
    expires_at = models.DateTimeField()

    def __str__(self) -> str:
        return f"{self.organization_id}:{self.patient_id}:{self.role}"


class PortalNotification(TimestampedModel):
    organization = models.ForeignKey("Organization", on_delete=models.CASCADE)
    patient = models.ForeignKey("Patient", on_delete=models.CASCADE)
    kind = models.CharField(max_length=64, default="general")
    title = models.CharField(max_length=255)
    body = models.TextField(blank=True)
    url = models.CharField(max_length=512, blank=True)
    unread = models.BooleanField(default=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["patient", "read_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.organization_id}:{self.patient_id}:{self.title}"
