from __future__ import annotations

from django.conf import settings
from django.db import models

from .base import TimestampedModel


class FormTemplate(TimestampedModel):
    name = models.CharField(max_length=255)
    version = models.PositiveIntegerField(default=1)
    schema = models.JSONField(default=dict)
    active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("name", "version")

    def __str__(self) -> str:
        return f"{self.name}@v{self.version}"


class FormResponse(TimestampedModel):
    organization = models.ForeignKey("Organization", on_delete=models.CASCADE)
    episode = models.ForeignKey("Episode", on_delete=models.CASCADE)
    template = models.ForeignKey(FormTemplate, on_delete=models.PROTECT)
    data = models.JSONField(default=dict)
    validated = models.BooleanField(default=False)
    validation_errors = models.JSONField(default=list)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self) -> str:
        return f"{self.episode_id}:{self.template_id}"


class Signature(TimestampedModel):
    response = models.ForeignKey(FormResponse, on_delete=models.CASCADE)
    signer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    template_version = models.PositiveIntegerField()
    signed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.response_id}:{self.signer_id}"
