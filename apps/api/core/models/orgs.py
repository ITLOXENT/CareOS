from __future__ import annotations

from django.conf import settings
from django.db import models

from ..rbac import Role
from .base import TimestampedModel


class Organization(TimestampedModel):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=120, unique=True)

    def __str__(self) -> str:
        return self.name


class OrganizationSubscription(TimestampedModel):
    organization = models.OneToOneField(
        Organization, on_delete=models.CASCADE, related_name="subscription"
    )
    stripe_customer_id = models.CharField(max_length=120, blank=True)
    stripe_subscription_id = models.CharField(max_length=120, blank=True)
    plan_code = models.CharField(max_length=64, blank=True)
    status = models.CharField(max_length=32, default="inactive")
    current_period_end = models.DateTimeField(null=True, blank=True)
    seat_limit = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.organization_id}:{self.plan_code}:{self.status}"


class Integration(TimestampedModel):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    provider = models.CharField(max_length=64)
    status = models.CharField(max_length=32, default="disconnected")
    config_json = models.JSONField(default=dict)
    last_tested_at = models.DateTimeField(null=True, blank=True)
    last_error = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("organization", "provider")

    def __str__(self) -> str:
        return f"{self.organization_id}:{self.provider}:{self.status}"


class IntegrationApiKey(TimestampedModel):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=120)
    key_prefix = models.CharField(max_length=12)
    key_hash = models.CharField(max_length=128)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    revoked_at = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.organization_id}:{self.name}:{self.key_prefix}"


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
    is_active = models.BooleanField(default=True)
    deactivated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("user", "organization")

    def __str__(self) -> str:
        return f"{self.user_id}:{self.organization_id}:{self.role}"


class OrgInvite(TimestampedModel):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    email = models.EmailField()
    role = models.CharField(max_length=20, choices=Role.choices())
    token_hash = models.CharField(max_length=64)
    expires_at = models.DateTimeField()
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    accepted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.organization_id}:{self.email}:{self.role}"
