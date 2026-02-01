from __future__ import annotations

import json
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.http import JsonResponse
from django.utils import timezone

from ..models import AuditEvent, ConsentRecord, Episode, EpisodeEvent, Patient, WorkItem
from ..notifications import create_notification
from ..rbac import Role, has_permission
from ..state import EPISODE_TRANSITIONS


def _requires_episode_consent(patient: Patient | None) -> bool:
    return bool(patient and patient.restricted)


def _has_active_consent(org_id: int, patient: Patient | None, scope: str) -> bool:
    if not patient:
        return True
    now = timezone.now()
    return ConsentRecord.objects.filter(
        organization_id=org_id,
        patient=patient,
        scope=scope,
        granted=True,
        revoked_at__isnull=True,
    ).filter(models.Q(expires_at__isnull=True) | models.Q(expires_at__gte=now)).exists()


def episodes_list(request):
    membership = request.membership  # type: ignore[attr-defined]
    if request.method == "POST":
        permission = has_permission(membership.role, "episode:write")
        if not permission.allowed or membership.role != Role.ADMIN:
            return JsonResponse({"detail": "Not authorized."}, status=403)
        payload = json.loads(request.body or "{}")
        title = str(payload.get("title", "")).strip()
        if not title:
            return JsonResponse({"detail": "title is required"}, status=400)
        description = str(payload.get("description", ""))
        patient = None
        if payload.get("patient_id"):
            patient = Patient.objects.filter(
                organization=membership.organization, id=payload.get("patient_id")
            ).first()
            if not patient:
                return JsonResponse({"detail": "patient not found"}, status=404)
        assigned_to = None
        if payload.get("assigned_to_id"):
            user_model = get_user_model()
            assigned_to = user_model.objects.filter(
                id=payload.get("assigned_to_id")
            ).first()
            if not assigned_to:
                return JsonResponse({"detail": "assigned_to not found"}, status=404)
        episode = Episode.objects.create(
            organization=membership.organization,
            title=title,
            description=description,
            patient=patient,
            created_by=request.user,
            assigned_to=assigned_to,
        )
        EpisodeEvent.objects.create(
            organization=membership.organization,
            episode=episode,
            created_by=request.user,
            event_type="episode.created",
            from_state="",
            to_state=episode.status,
            payload_json={
                "title": episode.title,
                "description": episode.description,
                "patient_id": episode.patient_id,
                "assigned_to_id": episode.assigned_to_id,
            },
        )
        AuditEvent.objects.create(
            organization=membership.organization,
            actor=request.user,
            action="episode.created",
            target_type="Episode",
            target_id=str(episode.id),
        )
        if settings.AUTO_CREATE_EPISODE_WORK_ITEM:
            due_at = timezone.now() + timedelta(minutes=settings.SLA_DEFAULT_MINUTES)
            WorkItem.objects.create(
                organization=membership.organization,
                episode=episode,
                kind="episode_triage",
                status="open",
                assigned_to=episode.assigned_to,
                due_at=due_at,
                created_by=request.user,
            )
        return JsonResponse(
            {
                "id": episode.id,
                "title": episode.title,
                "description": episode.description,
                "status": episode.status,
                "assigned_to": episode.assigned_to_id,
                "created_by": episode.created_by_id,
                "patient_id": episode.patient_id,
                "created_at": episode.created_at.isoformat(),
                "updated_at": episode.updated_at.isoformat(),
            },
            status=201,
        )

    permission = has_permission(membership.role, "episode:read")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    episodes = Episode.objects.filter(organization=membership.organization).order_by(
        "-created_at"
    )
    status_filter = request.GET.get("status")
    if status_filter:
        episodes = episodes.filter(status=status_filter)
    assigned_to_filter = request.GET.get("assigned_to")
    if assigned_to_filter:
        episodes = episodes.filter(assigned_to_id=assigned_to_filter)
    created_by_filter = request.GET.get("created_by")
    if created_by_filter:
        episodes = episodes.filter(created_by_id=created_by_filter)
    search_filter = request.GET.get("search")
    if search_filter:
        episodes = episodes.filter(title__icontains=search_filter)
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
    total = episodes.count()
    start_index = (page - 1) * page_size
    episodes = episodes[start_index : start_index + page_size]
    payload = [
        {
            "id": episode.id,
            "title": episode.title,
            "description": episode.description,
            "status": episode.status,
            "created_at": episode.created_at.isoformat(),
            "updated_at": episode.updated_at.isoformat(),
            "assigned_to": episode.assigned_to_id,
            "created_by": episode.created_by_id,
            "patient_id": episode.patient_id,
        }
        for episode in episodes
    ]
    return JsonResponse(
        {"results": payload, "count": total, "page": page, "page_size": page_size}
    )


def episode_detail(request, episode_id: int):
    membership = request.membership  # type: ignore[attr-defined]
    permission = has_permission(membership.role, "episode:read")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    episode = Episode.objects.filter(
        organization=membership.organization, id=episode_id
    ).first()
    if not episode:
        return JsonResponse({"detail": "Not found."}, status=404)
    if _requires_episode_consent(episode.patient) and not _has_active_consent(
        membership.organization_id, episode.patient, "episodes.read"
    ):
        return JsonResponse({"detail": "Consent required."}, status=403)
    AuditEvent.objects.create(
        organization=membership.organization,
        actor=request.user,
        action="episode.read",
        target_type="Episode",
        target_id=str(episode.id),
    )
    payload = {
        "id": episode.id,
        "title": episode.title,
        "description": episode.description,
        "status": episode.status,
        "created_at": episode.created_at.isoformat(),
        "updated_at": episode.updated_at.isoformat(),
        "assigned_to": episode.assigned_to_id,
        "created_by": episode.created_by_id,
        "patient_id": episode.patient_id,
    }
    return JsonResponse(payload)


def episode_timeline(request, episode_id: int):
    membership = request.membership  # type: ignore[attr-defined]
    permission = has_permission(membership.role, "episode:read")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    episode = Episode.objects.filter(
        organization=membership.organization, id=episode_id
    ).first()
    if not episode:
        return JsonResponse({"detail": "Not found."}, status=404)
    if _requires_episode_consent(episode.patient) and not _has_active_consent(
        membership.organization_id, episode.patient, "episodes.read"
    ):
        return JsonResponse({"detail": "Consent required."}, status=403)
    events = EpisodeEvent.objects.filter(
        organization=membership.organization, episode=episode
    ).order_by("created_at", "id")
    try:
        page = max(int(request.GET.get("page", "1")), 1)
    except ValueError:
        page = 1
    try:
        page_size = min(max(int(request.GET.get("page_size", "50")), 1), 200)
    except ValueError:
        page_size = 50
    total = events.count()
    start_index = (page - 1) * page_size
    events = events[start_index : start_index + page_size]
    payload = [
        {
            "id": event.id,
            "event_type": event.event_type,
            "from_state": event.from_state,
            "to_state": event.to_state,
            "from_status": event.from_state,
            "to_status": event.to_state,
            "note": event.note,
            "payload_json": event.payload_json,
            "created_by": event.created_by_id,
            "created_at": event.created_at.isoformat(),
        }
        for event in events
    ]
    return JsonResponse(
        {"results": payload, "count": total, "page": page, "page_size": page_size}
    )


def episode_transition(request, episode_id: int):
    membership = request.membership  # type: ignore[attr-defined]
    permission = has_permission(membership.role, "episode:write")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    episode = Episode.objects.filter(
        organization=membership.organization, id=episode_id
    ).first()
    if not episode:
        return JsonResponse({"detail": "Not found."}, status=404)
    payload = json.loads(request.body or "{}")
    to_state = str(payload.get("to_state") or payload.get("to_status") or "").strip()
    if not to_state:
        return JsonResponse({"detail": "to_state is required."}, status=400)
    if membership.role == Role.STAFF:
        if to_state == "cancelled":
            return JsonResponse({"detail": "Not authorized."}, status=403)
        if episode.status != "triage" and episode.assigned_to_id != request.user.id:
            return JsonResponse({"detail": "Not authorized."}, status=403)
    if membership.role != Role.ADMIN and to_state == "cancelled":
        return JsonResponse({"detail": "Not authorized."}, status=403)
    if to_state != "cancelled":
        allowed = EPISODE_TRANSITIONS.get(episode.status, set())
        if to_state not in allowed:
            return JsonResponse({"detail": "Invalid transition."}, status=400)
    from_state = episode.status
    episode.status = to_state
    episode.save(update_fields=["status", "updated_at"])
    note = str(payload.get("note", ""))
    payload_json = payload.get("payload_json") or {
        "from_state": from_state,
        "to_state": to_state,
        "from_status": from_state,
        "to_status": to_state,
        "note": note,
    }
    EpisodeEvent.objects.create(
        organization=membership.organization,
        episode=episode,
        created_by=request.user,
        event_type="episode.transition",
        from_state=from_state,
        to_state=to_state,
        note=note,
        payload_json=payload_json,
    )
    if to_state in {"resolved", "closed", "cancelled"}:
        open_items = WorkItem.objects.filter(
            organization=membership.organization,
            episode=episode,
            status__in=["open", "assigned"],
        )
        now = timezone.now()
        for item in open_items:
            item.status = "completed"
            item.completed_at = now
            item.save(update_fields=["status", "completed_at"])
            AuditEvent.objects.create(
                organization=membership.organization,
                actor=request.user,
                action="work_item.auto_completed",
                target_type="WorkItem",
                target_id=str(item.id),
                metadata={"episode_id": episode.id},
            )
    AuditEvent.objects.create(
        organization=membership.organization,
        actor=request.user,
        action="episode.transition",
        target_type="Episode",
        target_id=str(episode.id),
        metadata={
            "from_state": from_state,
            "to_state": to_state,
            "from_status": from_state,
            "to_status": to_state,
        },
    )
    recipients = []
    if episode.assigned_to_id:
        recipients.append(episode.assigned_to)
    if episode.created_by_id and episode.created_by_id != episode.assigned_to_id:
        recipients.append(episode.created_by)
    for recipient in recipients:
        if recipient is None:
            continue
        create_notification(
            organization=membership.organization,
            recipient=recipient,
            kind="episode.transition",
            title="Episode updated",
            body=f"Episode {episode.id} moved to {to_state}.",
            url=f"/episodes/{episode.id}",
            actor=request.user,
            metadata={"episode_id": episode.id, "to_state": to_state},
        )
    return JsonResponse({"id": episode.id, "status": episode.status})
