from __future__ import annotations

from django.conf import settings
from django.db import models

from .base import TimestampedModel


class EvidencePack(TimestampedModel):
    organization = models.ForeignKey("Organization", on_delete=models.CASCADE)
    episode = models.ForeignKey("Episode", on_delete=models.CASCADE)
    manifest = models.JSONField(default=dict)
    pdf_bytes = models.BinaryField()

    def __str__(self) -> str:
        return f"{self.episode_id}:{self.id}"


class EvidenceItem(TimestampedModel):
    organization = models.ForeignKey("Organization", on_delete=models.CASCADE)
    episode = models.ForeignKey("Episode", on_delete=models.SET_NULL, null=True, blank=True)
    patient = models.ForeignKey("Patient", on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=255)
    kind = models.CharField(max_length=64)
    file_name = models.CharField(max_length=255)
    content_type = models.CharField(max_length=120, blank=True)
    size_bytes = models.PositiveIntegerField(default=0)
    storage_path = models.CharField(max_length=512)
    storage_key = models.CharField(max_length=255, blank=True)
    sha256 = models.CharField(max_length=64)
    tags = models.JSONField(default=list, blank=True)
    retention_class = models.CharField(max_length=64, blank=True, default="")
    retention_until = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_evidence_items",
    )

    def __str__(self) -> str:
        return f"{self.organization_id}:{self.title}:{self.kind}"


class EvidenceEvent(TimestampedModel):
    organization = models.ForeignKey("Organization", on_delete=models.CASCADE)
    evidence = models.ForeignKey(
        EvidenceItem, on_delete=models.CASCADE, related_name="events"
    )
    event_type = models.CharField(max_length=120)
    payload_json = models.JSONField(default=dict, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        ordering = ("created_at",)

    def __str__(self) -> str:
        return f"{self.evidence_id}:{self.event_type}"


class EpisodeEvidence(TimestampedModel):
    organization = models.ForeignKey("Organization", on_delete=models.CASCADE)
    episode = models.ForeignKey("Episode", on_delete=models.CASCADE)
    evidence = models.ForeignKey(EvidenceItem, on_delete=models.CASCADE)
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        unique_together = ("episode", "evidence")

    def __str__(self) -> str:
        return f"{self.episode_id}:{self.evidence_id}"
