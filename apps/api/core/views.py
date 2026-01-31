from __future__ import annotations

from django.http import JsonResponse

from .models import AuditEvent
from .rbac import has_permission


def health(_request):
    return JsonResponse({"status": "ok"})


def me(request):
    user = request.user
    membership = request.membership  # type: ignore[attr-defined]
    return JsonResponse(
        {
            "id": user.id,
            "email": user.email,
            "organization_id": membership.organization_id,
            "role": membership.role,
        }
    )


def current_org(request):
    organization = request.organization  # type: ignore[attr-defined]
    return JsonResponse(
        {"id": organization.id, "name": organization.name, "slug": organization.slug}
    )


def audit_events(request):
    membership = request.membership  # type: ignore[attr-defined]
    permission = has_permission(membership.role, "audit:view")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)

    events = AuditEvent.objects.filter(organization=membership.organization)[:50]
    payload = [
        {
            "id": event.id,
            "action": event.action,
            "target_type": event.target_type,
            "target_id": event.target_id,
            "created_at": event.created_at.isoformat(),
        }
        for event in events
    ]
    return JsonResponse({"results": payload})
