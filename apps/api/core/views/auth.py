from __future__ import annotations

import json

from django.conf import settings
from django.http import JsonResponse

from ..models import AuditEvent, Organization


def admin_auth_audit(request):
    secret = settings.ADMIN_AUDIT_SECRET
    if not secret:
        return JsonResponse({"detail": "Admin audit secret not configured"}, status=400)
    header = request.headers.get("X-Admin-Audit-Token", "")
    if header != secret:
        return JsonResponse({"detail": "Unauthorized"}, status=403)
    payload = json.loads(request.body or "{}")
    outcome = str(payload.get("outcome", "")).strip()
    username = str(payload.get("username", "")).strip()
    org_id = settings.ADMIN_AUDIT_ORG_ID
    if not org_id:
        return JsonResponse({"detail": "Admin audit org not configured"}, status=400)
    organization = Organization.objects.filter(id=org_id).first()
    if not organization:
        return JsonResponse({"detail": "Admin audit org not found"}, status=404)
    AuditEvent.objects.create(
        organization=organization,
        actor=None,
        action=f"admin.login.{outcome or 'unknown'}",
        target_type="AdminAuth",
        target_id=username or "unknown",
        metadata={"ip": request.META.get("REMOTE_ADDR", "")},
    )
    return JsonResponse({"status": "ok"})
