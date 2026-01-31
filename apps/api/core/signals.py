from __future__ import annotations

from django.db.models.signals import post_save
from django.dispatch import receiver

from .audit import record_audit_event
from .models import AuditEvent, Membership, Organization, Site, Team


def _target_identity(instance) -> tuple[str, str]:
    return (instance.__class__.__name__, str(instance.pk))


@receiver(post_save, sender=Organization)
@receiver(post_save, sender=Site)
@receiver(post_save, sender=Team)
@receiver(post_save, sender=Membership)
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
