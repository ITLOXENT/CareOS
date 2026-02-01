from __future__ import annotations

from django.conf import settings
from django.db import models

from careos_api.observability import request_id_ctx

from .base import TimestampedModel


class AuditEvent(TimestampedModel):
    organization = models.ForeignKey("Organization", on_delete=models.CASCADE)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    action = models.CharField(max_length=200)
    target_type = models.CharField(max_length=120)
    target_id = models.CharField(max_length=120)
    metadata = models.JSONField(default=dict, blank=True)
    request_id = models.CharField(max_length=64, blank=True, default="")

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["organization", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.action}:{self.target_type}:{self.target_id}"

    def save(self, *args, **kwargs) -> None:  # type: ignore[override]
        if not self.request_id:
            self.request_id = request_id_ctx.get("-")
        super().save(*args, **kwargs)
