from __future__ import annotations

from django.conf import settings
from django.db import models

from ..state import AI_ARTIFACT_STATUSES
from .base import TimestampedModel


class AIArtifact(TimestampedModel):
    organization = models.ForeignKey("Organization", on_delete=models.CASCADE)
    episode = models.ForeignKey("Episode", on_delete=models.CASCADE)
    artifact_type = models.CharField(max_length=120)
    version = models.PositiveIntegerField(default=1)
    confidence = models.FloatField(default=0.0)
    policy_version = models.CharField(max_length=64)
    status = models.CharField(
        max_length=16, choices=AI_ARTIFACT_STATUSES, default="pending"
    )
    content = models.JSONField(default=dict)
    prompt_redacted = models.JSONField(default=dict)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_ai_artifacts",
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    rejected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="rejected_ai_artifacts",
    )
    rejected_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)

    def __str__(self) -> str:
        return f"{self.episode_id}:{self.artifact_type}:{self.status}"


class AIReviewRequest(TimestampedModel):
    organization = models.ForeignKey("Organization", on_delete=models.CASCADE)
    input_type = models.CharField(max_length=120)
    payload = models.JSONField(default=dict)
    status = models.CharField(max_length=32, default="pending")
    output = models.JSONField(default=dict, blank=True)
    model_provider = models.CharField(max_length=64, blank=True)
    model_version = models.CharField(max_length=64, blank=True)
    model_name = models.CharField(max_length=64, blank=True)
    error = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self) -> str:
        return f"{self.organization_id}:{self.input_type}:{self.status}"


class AIReviewItem(TimestampedModel):
    organization = models.ForeignKey("Organization", on_delete=models.CASCADE)
    episode = models.ForeignKey("Episode", on_delete=models.SET_NULL, null=True, blank=True)
    kind = models.CharField(max_length=120)
    payload_json = models.JSONField(default=dict)
    status = models.CharField(max_length=32, default="pending")
    decided_at = models.DateTimeField(null=True, blank=True)
    decided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    decision_note = models.TextField(blank=True)

    def __str__(self) -> str:
        return f"{self.organization_id}:{self.kind}:{self.status}"
