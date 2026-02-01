from __future__ import annotations

from django.http import JsonResponse

from ..models import AuditEvent
from ..rbac import has_permission
from .utils import parse_datetime


def audit_events(request):
    membership = request.membership  # type: ignore[attr-defined]
    permission = has_permission(membership.role, "audit:view")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)

    events = AuditEvent.objects.filter(organization=membership.organization)
    actor_filter = request.GET.get("actor")
    if actor_filter:
        events = events.filter(actor_id=actor_filter)
    action_filter = request.GET.get("action")
    if action_filter:
        events = events.filter(action=action_filter)
    target_type = request.GET.get("target_type") or request.GET.get("resource")
    if target_type:
        events = events.filter(target_type=target_type)
    target_id = request.GET.get("target_id")
    if target_id:
        events = events.filter(target_id=target_id)
    start = request.GET.get("start") or request.GET.get("from")
    if start:
        start_dt = parse_datetime(start)
        if not start_dt:
            return JsonResponse({"detail": "start must be ISO datetime"}, status=400)
        events = events.filter(created_at__gte=start_dt)
    end = request.GET.get("end") or request.GET.get("to")
    if end:
        end_dt = parse_datetime(end)
        if not end_dt:
            return JsonResponse({"detail": "end must be ISO datetime"}, status=400)
        events = events.filter(created_at__lte=end_dt)
    try:
        page = max(int(request.GET.get("page", "1")), 1)
    except ValueError:
        page = 1
    limit = request.GET.get("limit")
    if limit:
        page_size_value = limit
    else:
        page_size_value = request.GET.get("page_size", "50")
    try:
        page_size = min(max(int(page_size_value), 1), 200)
    except ValueError:
        page_size = 50
    total = events.count()
    start_index = (page - 1) * page_size
    events = events.order_by("-created_at", "-id")[start_index : start_index + page_size]
    payload = [
        {
            "id": event.id,
            "action": event.action,
            "target_type": event.target_type,
            "target_id": event.target_id,
            "actor_id": event.actor_id,
            "metadata": event.metadata,
            "request_id": event.request_id,
            "created_at": event.created_at.isoformat(),
        }
        for event in events
    ]
    return JsonResponse(
        {"results": payload, "count": total, "page": page, "page_size": page_size}
    )
