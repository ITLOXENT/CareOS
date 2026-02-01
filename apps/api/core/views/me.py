from __future__ import annotations

import json

from django.http import JsonResponse

from ..models import AuditEvent
from ..rbac import has_permission


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
    if request.method in {"PATCH", "POST"}:
        membership = request.membership  # type: ignore[attr-defined]
        permission = has_permission(membership.role, "org:manage")
        if not permission.allowed:
            return JsonResponse({"detail": "Not authorized."}, status=403)
        payload = json.loads(request.body or "{}")
        previous_name = organization.name
        if "name" in payload:
            organization.name = str(payload.get("name", "")).strip() or organization.name
        organization.save(update_fields=["name"])
        if organization.name != previous_name:
            AuditEvent.objects.create(
                organization=membership.organization,
                actor=request.user,
                action="org.updated",
                target_type="Organization",
                target_id=str(organization.id),
                metadata={"name": organization.name},
            )
    return JsonResponse(
        {"id": organization.id, "name": organization.name, "slug": organization.slug}
    )
