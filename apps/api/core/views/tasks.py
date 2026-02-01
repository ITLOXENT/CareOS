from __future__ import annotations

import json

from django.contrib.auth import get_user_model
from django.db import models
from django.http import JsonResponse
from django.utils import timezone

from ..models import AuditEvent, Episode, EpisodeEvent, Task, WorkItem
from ..rbac import Role, has_permission
from ..state import TASK_TRANSITIONS
from .utils import parse_datetime


def tasks_list(request):
    membership = request.membership  # type: ignore[attr-defined]
    if request.method == "POST":
        permission = has_permission(membership.role, "work:write")
        if not permission.allowed:
            return JsonResponse({"detail": "Not authorized."}, status=403)
        payload = json.loads(request.body or "{}")
        title = str(payload.get("title", "")).strip()
        if not title:
            return JsonResponse({"detail": "title is required"}, status=400)
        episode = None
        if payload.get("episode_id"):
            episode = Episode.objects.filter(
                organization=membership.organization, id=payload.get("episode_id")
            ).first()
            if not episode:
                return JsonResponse({"detail": "episode not found"}, status=404)
        work_item = None
        if payload.get("work_item_id"):
            work_item = WorkItem.objects.filter(
                organization=membership.organization, id=payload.get("work_item_id")
            ).first()
            if not work_item:
                return JsonResponse({"detail": "work_item not found"}, status=404)
        due_at = parse_datetime(payload.get("due_at")) if payload.get("due_at") else None
        task = Task.objects.create(
            organization=membership.organization,
            episode=episode,
            work_item=work_item,
            title=title,
            status=str(payload.get("status", "open")).strip() or "open",
            priority=str(payload.get("priority", "medium")).strip() or "medium",
            due_at=due_at,
            created_by=request.user,
        )
        if task.work_item_id is None:
            linked_item = WorkItem.objects.create(
                organization=membership.organization,
                episode=task.episode,
                kind="task",
                status="open",
                due_at=task.due_at,
                created_by=request.user,
            )
            task.work_item = linked_item
            task.save(update_fields=["work_item"])
        AuditEvent.objects.create(
            organization=membership.organization,
            actor=request.user,
            action="task.created",
            target_type="Task",
            target_id=str(task.id),
            metadata={"episode_id": task.episode_id, "work_item_id": task.work_item_id},
        )
        if task.episode_id:
            EpisodeEvent.objects.create(
                organization=membership.organization,
                episode=task.episode,
                created_by=request.user,
                event_type="task.created",
                from_state="",
                to_state=task.status,
                payload_json={"task_id": task.id},
            )
        return JsonResponse(_task_payload(task), status=201)

    permission = has_permission(membership.role, "work:read")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    tasks = Task.objects.filter(organization=membership.organization).order_by(
        "-created_at"
    )
    status_filter = request.GET.get("status")
    if status_filter:
        tasks = tasks.filter(status=status_filter)
    priority_filter = request.GET.get("priority")
    if priority_filter:
        tasks = tasks.filter(priority=priority_filter)
    episode_filter = request.GET.get("episode_id")
    if episode_filter:
        tasks = tasks.filter(episode_id=episode_filter)
    work_item_filter = request.GET.get("work_item_id")
    if work_item_filter:
        tasks = tasks.filter(work_item_id=work_item_filter)
    due_before = request.GET.get("due_before")
    if due_before:
        due_before_dt = parse_datetime(due_before)
        if not due_before_dt:
            return JsonResponse({"detail": "due_before must be ISO datetime"}, status=400)
        tasks = tasks.filter(due_at__lte=due_before_dt)
    try:
        page = max(int(request.GET.get("page", "1")), 1)
    except ValueError:
        page = 1
    try:
        page_size = min(max(int(request.GET.get("page_size", "50")), 1), 200)
    except ValueError:
        page_size = 50
    total = tasks.count()
    start = (page - 1) * page_size
    tasks = tasks[start : start + page_size]
    payload = [_task_payload(item) for item in tasks]
    return JsonResponse(
        {"results": payload, "count": total, "page": page, "page_size": page_size}
    )


def task_assign(request, task_id: int):
    membership = request.membership  # type: ignore[attr-defined]
    permission = has_permission(membership.role, "work:write")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    task = Task.objects.filter(organization=membership.organization, id=task_id).first()
    if not task:
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
    task.assigned_to = assignee
    if task.status == "open":
        task.status = "assigned"
    task.save(update_fields=["assigned_to", "status", "updated_at"])
    if task.work_item_id:
        task.work_item.assigned_to = assignee
        if task.work_item.status == "open":
            task.work_item.status = "assigned"
        task.work_item.save(update_fields=["assigned_to", "status"])
    AuditEvent.objects.create(
        organization=membership.organization,
        actor=request.user,
        action="task.assigned",
        target_type="Task",
        target_id=str(task.id),
        metadata={"assigned_to": task.assigned_to_id},
    )
    return JsonResponse(
        {"id": task.id, "status": task.status, "assigned_to": task.assigned_to_id}
    )


def task_complete(request, task_id: int):
    membership = request.membership  # type: ignore[attr-defined]
    permission = has_permission(membership.role, "work:write")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    task = Task.objects.filter(organization=membership.organization, id=task_id).first()
    if not task:
        return JsonResponse({"detail": "Not found."}, status=404)
    if membership.role != Role.ADMIN and task.assigned_to_id != request.user.id:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    task.status = "completed"
    task.completed_at = timezone.now()
    task.save(update_fields=["status", "completed_at", "updated_at"])
    if task.work_item_id and task.work_item.status != "completed":
        task.work_item.status = "completed"
        task.work_item.completed_at = timezone.now()
        task.work_item.save(update_fields=["status", "completed_at"])
    AuditEvent.objects.create(
        organization=membership.organization,
        actor=request.user,
        action="task.completed",
        target_type="Task",
        target_id=str(task.id),
    )
    if task.episode_id:
        EpisodeEvent.objects.create(
            organization=membership.organization,
            episode=task.episode,
            created_by=request.user,
            event_type="task.completed",
            from_state="",
            to_state=task.status,
            payload_json={"task_id": task.id},
        )
    return JsonResponse({"id": task.id, "status": task.status})


def task_transition(request, task_id: int):
    membership = request.membership  # type: ignore[attr-defined]
    permission = has_permission(membership.role, "work:write")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    task = Task.objects.filter(organization=membership.organization, id=task_id).first()
    if not task:
        return JsonResponse({"detail": "Not found."}, status=404)
    payload = json.loads(request.body or "{}")
    to_state = str(payload.get("to_state") or payload.get("to_status") or "").strip()
    if not to_state:
        return JsonResponse({"detail": "to_state is required"}, status=400)
    allowed = TASK_TRANSITIONS.get(task.status, set())
    if to_state not in allowed:
        return JsonResponse({"detail": "Invalid transition."}, status=400)
    from_state = task.status
    task.status = to_state
    if to_state == "completed":
        task.completed_at = timezone.now()
    task.save(update_fields=["status", "completed_at", "updated_at"])
    AuditEvent.objects.create(
        organization=membership.organization,
        actor=request.user,
        action="task.transition",
        target_type="Task",
        target_id=str(task.id),
        metadata={"from_state": from_state, "to_state": to_state},
    )
    if task.episode_id:
        EpisodeEvent.objects.create(
            organization=membership.organization,
            episode=task.episode,
            created_by=request.user,
            event_type="task.transition",
            from_state=from_state,
            to_state=to_state,
            payload_json={"task_id": task.id},
        )
    return JsonResponse({"id": task.id, "status": task.status})


def _task_payload(task: Task) -> dict:
    return {
        "id": task.id,
        "episode_id": task.episode_id,
        "work_item_id": task.work_item_id,
        "title": task.title,
        "status": task.status,
        "priority": task.priority,
        "due_at": task.due_at.isoformat() if task.due_at else None,
        "assigned_to": task.assigned_to_id,
        "created_by": task.created_by_id,
        "created_at": task.created_at.isoformat(),
        "completed_at": task.completed_at.isoformat() if task.completed_at else None,
    }
