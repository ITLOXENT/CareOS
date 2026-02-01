from __future__ import annotations

from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db.models.signals import post_save
from django.dispatch import receiver

from .audit import record_audit_event
from .models import (
    AuditEvent,
    EvidenceEvent,
    EvidenceItem,
    OrgInvite,
    OrganizationSubscription,
    Episode,
    EpisodeEvent,
    Membership,
    Organization,
    Site,
    Team,
    WorkItem,
)


def _target_identity(instance) -> tuple[str, str]:
    return (instance.__class__.__name__, str(instance.pk))


@receiver(post_save, sender=Organization)
@receiver(post_save, sender=Site)
@receiver(post_save, sender=Team)
@receiver(post_save, sender=Membership)
@receiver(post_save, sender=Episode)
@receiver(post_save, sender=EpisodeEvent)
@receiver(post_save, sender=EvidenceItem)
@receiver(post_save, sender=EvidenceEvent)
@receiver(post_save, sender=OrgInvite)
@receiver(post_save, sender=OrganizationSubscription)
@receiver(post_save, sender=WorkItem)
def audit_on_write(sender, instance, created, **kwargs):  # type: ignore[no-untyped-def]
    if isinstance(instance, AuditEvent):
        return
    action = "created" if created else "updated"
    target_type, target_id = _target_identity(instance)
    organization = instance.organization if hasattr(instance, "organization") else instance
    record_audit_event(
        organization=organization,
        actor_id=None,
        action=f"{sender.__name__}.{action}",
        target_type=target_type,
        target_id=target_id,
    )


@receiver(user_logged_in)
def audit_on_login(sender, request, user, **kwargs):  # type: ignore[no-untyped-def]
    membership = (
        Membership.objects.filter(user=user, is_active=True)
        .select_related("organization")
        .first()
    )
    if not membership:
        return
    record_audit_event(
        organization=membership.organization,
        actor_id=user.id,
        action="auth.login",
        target_type="User",
        target_id=str(user.id),
        metadata={"ip": request.META.get("REMOTE_ADDR", "") if request else ""},
    )


@receiver(user_logged_out)
def audit_on_logout(sender, request, user, **kwargs):  # type: ignore[no-untyped-def]
    if not user:
        return
    membership = (
        Membership.objects.filter(user=user, is_active=True)
        .select_related("organization")
        .first()
    )
    if not membership:
        return
    record_audit_event(
        organization=membership.organization,
        actor_id=user.id,
        action="auth.logout",
        target_type="User",
        target_id=str(user.id),
        metadata={"ip": request.META.get("REMOTE_ADDR", "") if request else ""},
    )
