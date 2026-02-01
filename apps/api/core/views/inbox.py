from __future__ import annotations

import json

from django.contrib.auth import get_user_model
from django.db import models
from django.http import JsonResponse
from django.utils import timezone

from ..models import AuditEvent, Membership, WorkItem
from ..notifications import create_notification
from ..rbac import Role, has_permission
from .utils import parse_datetime


def work_items_list(request):
    membership = request.membership  # type: ignore[attr-defined]
    permission = has_permission(membership.role, "work:read")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    items = WorkItem.objects.filter(organization=membership.organization).order_by(
        "-created_at"
    )
    status_filter = request.GET.get("status")
    if status_filter:
        items = items.filter(status=status_filter)
    assigned_to_filter = request.GET.get("assigned_to") or request.GET.get("assignee")
    if assigned_to_filter:
        items = items.filter(assigned_to_id=assigned_to_filter)
    kind_filter = request.GET.get("kind")
    if kind_filter:
        items = items.filter(kind=kind_filter)
    due_before = request.GET.get("due_before")
    if due_before:
        due_before_dt = parse_datetime(due_before)
        if not due_before_dt:
            return JsonResponse({"detail": "due_before must be ISO datetime"}, status=400)
        items = items.filter(due_at__lte=due_before_dt)
    episode_filter = request.GET.get("episode_id")
    if episode_filter:
        items = items.filter(episode_id=episode_filter)
    appointment_filter = request.GET.get("appointment_id")
    if appointment_filter:
        items = items.filter(appointment_id=appointment_filter)
    appointment_linked = request.GET.get("appointment")
    if appointment_linked == "linked":
        items = items.filter(appointment_id__isnull=False)
    if appointment_linked == "unlinked":
        items = items.filter(appointment_id__isnull=True)
    sla_filter = request.GET.get("sla")
    now = timezone.now()
    if sla_filter == "breached":
        items = items.filter(
            models.Q(sla_breach_at__isnull=False, sla_breach_at__lte=now)
            | models.Q(
                due_at__isnull=False,
                due_at__lte=now,
                status__in=["open", "assigned"],
            )
        )
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
    total = items.count()
    start_index = (page - 1) * page_size
    items = items[start_index : start_index + page_size]
    payload = [
        {
            "id": item.id,
            "kind": item.kind,
            "status": item.status,
            "episode_id": item.episode_id,
            "appointment_id": item.appointment_id,
            "assigned_to": item.assigned_to_id,
            "due_at": item.due_at.isoformat() if item.due_at else None,
            "sla_breach_at": item.sla_breach_at.isoformat()
            if item.sla_breach_at
            else None,
            "created_by": item.created_by_id,
            "created_at": item.created_at.isoformat(),
            "completed_at": item.completed_at.isoformat()
            if item.completed_at
            else None,
            "sla_breached": bool(
                (item.sla_breach_at and item.sla_breach_at <= now)
                or (item.due_at and item.due_at <= now and item.status != "completed")
            ),
        }
        for item in items
    ]
    return JsonResponse(
        {"results": payload, "count": total, "page": page, "page_size": page_size}
    )


def work_item_assign(request, item_id: int):
    membership = request.membership  # type: ignore[attr-defined]
    permission = has_permission(membership.role, "work:write")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    item = WorkItem.objects.filter(
        organization=membership.organization, id=item_id
    ).first()
    if not item:
        return JsonResponse({"detail": "Not found."}, status=404)
    payload = json.loads(request.body or "{}")
    assignee_id = payload.get("assigned_to_id", payload.get("assignee_id"))
    user_model = get_user_model()
    if assignee_id is None:
        assignee = request.user
    else:
        assignee = user_model.objects.filter(id=assignee_id).first()
        if not assignee:
            return JsonResponse({"detail": "assigned_to not found"}, status=404)
    if not Membership.objects.filter(
        user=assignee, organization=membership.organization, is_active=True
    ).exists():
        return JsonResponse({"detail": "assigned_to not found"}, status=404)
    item.assigned_to = assignee
    item.status = "assigned"
    item.save(update_fields=["assigned_to", "status"])
    AuditEvent.objects.create(
        organization=membership.organization,
        actor=request.user,
        action="work_item.assigned",
        target_type="WorkItem",
        target_id=str(item.id),
        metadata={"assigned_to": item.assigned_to_id},
    )
    create_notification(
        organization=membership.organization,
        recipient=item.assigned_to,
        kind="work_item.assigned",
        title="Work item assigned",
        body=f"{item.kind} work item {item.id} assigned to you.",
        url=f"/episodes/{item.episode_id}" if item.episode_id else "/inbox",
        actor=request.user,
        metadata={"work_item_id": item.id},
    )
    return JsonResponse(
        {"id": item.id, "status": item.status, "assigned_to": item.assigned_to_id}
    )


def work_item_complete(request, item_id: int):
    membership = request.membership  # type: ignore[attr-defined]
    permission = has_permission(membership.role, "work:write")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    item = WorkItem.objects.filter(
        organization=membership.organization, id=item_id
    ).first()
    if not item:
        return JsonResponse({"detail": "Not found."}, status=404)
    if membership.role != Role.ADMIN and item.assigned_to_id != request.user.id:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    item.status = "completed"
    item.completed_at = timezone.now()
    item.save(update_fields=["status", "completed_at"])
    AuditEvent.objects.create(
        organization=membership.organization,
        actor=request.user,
        action="work_item.completed",
        target_type="WorkItem",
        target_id=str(item.id),
    )
    return JsonResponse({"id": item.id, "status": item.status})
