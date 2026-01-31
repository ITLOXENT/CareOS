from __future__ import annotations

from .models import AuditEvent, Organization


def record_audit_event(
    *,
    organization: Organization,
    actor_id: int | None,
    action: str,
    target_type: str,
    target_id: str,
    metadata: dict | None = None,
) -> AuditEvent:
    return AuditEvent.objects.create(
        organization=organization,
        actor_id=actor_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        metadata=metadata or {},
    )
