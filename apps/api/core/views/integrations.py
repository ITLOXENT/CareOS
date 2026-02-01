from __future__ import annotations

import json
import secrets
import hashlib

from django.http import JsonResponse
from django.utils import timezone

from ..models import AuditEvent, Integration, IntegrationApiKey
from ..rbac import has_permission


def integrations_list(request):
    membership = request.membership  # type: ignore[attr-defined]
    permission = has_permission(membership.role, "integration:read")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    integrations = Integration.objects.filter(
        organization=membership.organization
    ).order_by("provider")
    payload = [
        {
            "id": integration.id,
            "provider": integration.provider,
            "status": integration.status,
            "last_tested_at": integration.last_tested_at.isoformat()
            if integration.last_tested_at
            else None,
            "last_error": integration.last_error,
            "config": {
                "sender": (integration.config_json or {}).get("sender", "")
                if integration.provider == "email"
                else ""
            },
        }
        for integration in integrations
    ]
    return JsonResponse({"results": payload})


def integrations_connect(request, provider: str):
    membership = request.membership  # type: ignore[attr-defined]
    permission = has_permission(membership.role, "integration:write")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    payload = json.loads(request.body or "{}")
    if provider != "email":
        return JsonResponse({"detail": "Provider not supported"}, status=400)
    api_key = str(payload.get("api_key", "")).strip()
    sender = str(payload.get("sender", "")).strip()
    if not api_key or not sender:
        return JsonResponse({"detail": "api_key and sender required"}, status=400)
    integration, _ = Integration.objects.get_or_create(
        organization=membership.organization, provider=provider
    )
    integration.status = "connected"
    integration.config_json = {"api_key": api_key, "sender": sender}
    integration.last_error = ""
    integration.save(update_fields=["status", "config_json", "last_error", "updated_at"])
    AuditEvent.objects.create(
        organization=membership.organization,
        actor=request.user,
        action="integration.connected",
        target_type="Integration",
        target_id=str(integration.id),
        metadata={"provider": provider},
    )
    return JsonResponse(
        {"id": integration.id, "provider": provider, "status": integration.status}
    )


def integrations_test(request, provider: str):
    membership = request.membership  # type: ignore[attr-defined]
    permission = has_permission(membership.role, "integration:write")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    integration = Integration.objects.filter(
        organization=membership.organization, provider=provider
    ).first()
    if not integration:
        return JsonResponse({"detail": "Not connected"}, status=404)
    if provider != "email":
        return JsonResponse({"detail": "Provider not supported"}, status=400)
    now = timezone.now()
    integration.last_tested_at = now
    integration.last_error = ""
    integration.save(update_fields=["last_tested_at", "last_error", "updated_at"])
    return JsonResponse(
        {"provider": provider, "status": "ok", "tested_at": now.isoformat()}
    )


def integrations_disconnect(request, provider: str):
    membership = request.membership  # type: ignore[attr-defined]
    permission = has_permission(membership.role, "integration:write")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    integration = Integration.objects.filter(
        organization=membership.organization, provider=provider
    ).first()
    if not integration:
        return JsonResponse({"detail": "Not found."}, status=404)
    integration.status = "disconnected"
    integration.config_json = {}
    integration.save(update_fields=["status", "config_json", "updated_at"])
    AuditEvent.objects.create(
        organization=membership.organization,
        actor=request.user,
        action="integration.disconnected",
        target_type="Integration",
        target_id=str(integration.id),
        metadata={"provider": provider},
    )
    return JsonResponse({"provider": provider, "status": integration.status})


def integration_api_keys(request):
    membership = request.membership  # type: ignore[attr-defined]
    permission = has_permission(membership.role, "org:manage")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    if request.method == "POST":
        payload = json.loads(request.body or "{}")
        name = str(payload.get("name", "")).strip()
        if not name:
            return JsonResponse({"detail": "name is required"}, status=400)
        token = secrets.token_urlsafe(32)
        prefix = token[:8]
        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
        api_key = IntegrationApiKey.objects.create(
            organization=membership.organization,
            name=name,
            key_prefix=prefix,
            key_hash=token_hash,
            created_by=request.user,
        )
        AuditEvent.objects.create(
            organization=membership.organization,
            actor=request.user,
            action="integration_api_key.created",
            target_type="IntegrationApiKey",
            target_id=str(api_key.id),
            metadata={"name": name, "prefix": prefix},
        )
        return JsonResponse(
            {
                "id": api_key.id,
                "name": api_key.name,
                "prefix": api_key.key_prefix,
                "created_at": api_key.created_at.isoformat(),
                "revoked_at": api_key.revoked_at.isoformat()
                if api_key.revoked_at
                else None,
                "token": token,
            },
            status=201,
        )
    keys = IntegrationApiKey.objects.filter(
        organization=membership.organization
    ).order_by("-created_at")
    payload = [
        {
            "id": key.id,
            "name": key.name,
            "prefix": key.key_prefix,
            "created_at": key.created_at.isoformat(),
            "revoked_at": key.revoked_at.isoformat() if key.revoked_at else None,
            "created_by": key.created_by_id,
        }
        for key in keys
    ]
    return JsonResponse({"results": payload})


def integration_api_key_revoke(request, key_id: int):
    membership = request.membership  # type: ignore[attr-defined]
    permission = has_permission(membership.role, "org:manage")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    api_key = IntegrationApiKey.objects.filter(
        organization=membership.organization, id=key_id
    ).first()
    if not api_key:
        return JsonResponse({"detail": "Not found."}, status=404)
    if not api_key.revoked_at:
        api_key.revoked_at = timezone.now()
        api_key.save(update_fields=["revoked_at"])
        AuditEvent.objects.create(
            organization=membership.organization,
            actor=request.user,
            action="integration_api_key.revoked",
            target_type="IntegrationApiKey",
            target_id=str(api_key.id),
        )
    return JsonResponse(
        {
            "id": api_key.id,
            "revoked_at": api_key.revoked_at.isoformat() if api_key.revoked_at else None,
        }
    )
