from __future__ import annotations

from django.conf import settings
from django.db import models

from .rbac import Role


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class Organization(TimestampedModel):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=120, unique=True)

    def __str__(self) -> str:
        return self.name


class Site(TimestampedModel):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=120)

    class Meta:
        unique_together = ("organization", "slug")

    def __str__(self) -> str:
        return f"{self.organization.slug}:{self.slug}"


class Team(TimestampedModel):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=120)

    class Meta:
        unique_together = ("organization", "slug")

    def __str__(self) -> str:
        return f"{self.organization.slug}:{self.slug}"


class Membership(TimestampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=Role.choices())

    class Meta:
        unique_together = ("user", "organization")

    def __str__(self) -> str:
        return f"{self.user_id}:{self.organization_id}:{self.role}"


class AuditEvent(TimestampedModel):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    action = models.CharField(max_length=200)
    target_type = models.CharField(max_length=120)
    target_id = models.CharField(max_length=120)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"{self.action}:{self.target_type}:{self.target_id}"
