from __future__ import annotations

import json

from django.conf import settings
from django.http import JsonResponse

from ..interop import SimulatorAdapter, enqueue_message, process_outbox
from ..models import InteropMessage
from ..rbac import has_permission


def interop_messages(request):
    membership = request.membership  # type: ignore[attr-defined]
    permission = has_permission(membership.role, "org:manage")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    if request.method == "POST":
        payload = json.loads(request.body or "{}")
        external_system = str(payload.get("external_system", "")).strip()
        if not external_system:
            return JsonResponse({"detail": "external_system required"}, status=400)
        simulator_mode = bool(payload.get("simulator", False))
        if simulator_mode and not settings.INTEROP_SIMULATOR_ENABLED:
            return JsonResponse({"detail": "Simulator not enabled"}, status=400)
        message = InteropMessage.objects.create(
            organization=membership.organization,
            episode_id=payload.get("episode_id"),
            external_system=external_system,
            payload=payload.get("payload", {}),
            status="draft",
            simulator_mode=simulator_mode,
            created_by=request.user,
        )
        enqueue_message(message)
        return JsonResponse({"id": message.id, "status": message.status}, status=201)
    messages = (
        InteropMessage.objects.filter(organization=membership.organization)
        .order_by("-created_at")[:100]
    )
    payload = [
        {
            "id": message.id,
            "external_system": message.external_system,
            "status": message.status,
            "attempts": message.attempts,
            "external_id": message.external_id,
            "simulator_mode": message.simulator_mode,
            "created_at": message.created_at.isoformat(),
            "status_events": [
                {
                    "status": event.status,
                    "detail": event.detail,
                    "created_at": event.created_at.isoformat(),
                }
                for event in message.status_events.order_by("created_at")
            ],
        }
        for message in messages
    ]
    return JsonResponse({"results": payload})


def interop_process(request):
    membership = request.membership  # type: ignore[attr-defined]
    permission = has_permission(membership.role, "org:manage")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    queued = InteropMessage.objects.filter(
        organization=membership.organization, status="queued"
    )
    if not settings.INTEROP_SIMULATOR_ENABLED:
        return JsonResponse({"detail": "Simulator not enabled"}, status=400)
    adapter = SimulatorAdapter(system_name="SIM")
    processed = process_outbox(list(queued), adapter)
    return JsonResponse({"processed": processed})
