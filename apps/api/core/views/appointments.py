from __future__ import annotations

import json

from django.conf import settings
from django.db import models
from django.http import JsonResponse
from django.utils import timezone

from ..models import Appointment, AuditEvent, Episode, EpisodeEvent, Patient, WorkItem
from ..rbac import has_permission
from ..state import APPOINTMENT_TRANSITIONS
from .utils import parse_datetime


def appointments_list(request):
    membership = request.membership  # type: ignore[attr-defined]
    if request.method == "POST":
        permission = has_permission(membership.role, "episode:write")
        if not permission.allowed:
            return JsonResponse({"detail": "Not authorized."}, status=403)
        payload = json.loads(request.body or "{}")
        scheduled_at = parse_datetime(payload.get("scheduled_at"))
        if not scheduled_at:
            return JsonResponse({"detail": "scheduled_at is required"}, status=400)
        patient = None
        if payload.get("patient_id"):
            patient = Patient.objects.filter(
                organization=membership.organization, id=payload.get("patient_id")
            ).first()
            if not patient:
                return JsonResponse({"detail": "patient not found"}, status=404)
        episode = None
        if payload.get("episode_id"):
            episode = Episode.objects.filter(
                organization=membership.organization, id=payload.get("episode_id")
            ).first()
            if not episode:
                return JsonResponse({"detail": "episode not found"}, status=404)
        appointment = Appointment.objects.create(
            organization=membership.organization,
            patient=patient,
            episode=episode,
            scheduled_at=scheduled_at,
            duration_minutes=int(payload.get("duration_minutes") or 30),
            location=str(payload.get("location", "")).strip(),
            status=str(payload.get("status", "scheduled")).strip() or "scheduled",
            created_by=request.user,
            notes=str(payload.get("notes", "")).strip(),
        )
        AuditEvent.objects.create(
            organization=membership.organization,
            actor=request.user,
            action="appointment.created",
            target_type="Appointment",
            target_id=str(appointment.id),
            metadata={"episode_id": appointment.episode_id, "patient_id": appointment.patient_id},
        )
        if appointment.episode_id:
            EpisodeEvent.objects.create(
                organization=membership.organization,
                episode=appointment.episode,
                created_by=request.user,
                event_type="appointment.created",
                from_state="",
                to_state=appointment.status,
                payload_json={
                    "appointment_id": appointment.id,
                    "scheduled_at": appointment.scheduled_at.isoformat(),
                },
            )
        if settings.AUTO_CREATE_APPOINTMENT_WORK_ITEM:
            WorkItem.objects.create(
                organization=membership.organization,
                episode=appointment.episode,
                appointment=appointment,
                kind="appointment",
                status="open",
                due_at=appointment.scheduled_at,
                created_by=request.user,
            )
        return JsonResponse(_appointment_payload(appointment), status=201)

    permission = has_permission(membership.role, "episode:read")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    appointments = Appointment.objects.filter(
        organization=membership.organization
    ).order_by("-scheduled_at")
    status_filter = request.GET.get("status")
    if status_filter:
        appointments = appointments.filter(status=status_filter)
    patient_filter = request.GET.get("patient_id")
    if patient_filter:
        appointments = appointments.filter(patient_id=patient_filter)
    episode_filter = request.GET.get("episode_id")
    if episode_filter:
        appointments = appointments.filter(episode_id=episode_filter)
    scheduled_before = request.GET.get("scheduled_before")
    if scheduled_before:
        before_dt = parse_datetime(scheduled_before)
        if not before_dt:
            return JsonResponse(
                {"detail": "scheduled_before must be ISO datetime"}, status=400
            )
        appointments = appointments.filter(scheduled_at__lte=before_dt)
    scheduled_after = request.GET.get("scheduled_after")
    if scheduled_after:
        after_dt = parse_datetime(scheduled_after)
        if not after_dt:
            return JsonResponse(
                {"detail": "scheduled_after must be ISO datetime"}, status=400
            )
        appointments = appointments.filter(scheduled_at__gte=after_dt)
    try:
        page = max(int(request.GET.get("page", "1")), 1)
    except ValueError:
        page = 1
    try:
        page_size = min(max(int(request.GET.get("page_size", "50")), 1), 200)
    except ValueError:
        page_size = 50
    total = appointments.count()
    start = (page - 1) * page_size
    appointments = appointments[start : start + page_size]
    payload = [_appointment_payload(item) for item in appointments]
    return JsonResponse(
        {"results": payload, "count": total, "page": page, "page_size": page_size}
    )


def appointment_transition(request, appointment_id: int):
    membership = request.membership  # type: ignore[attr-defined]
    permission = has_permission(membership.role, "episode:write")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    appointment = Appointment.objects.filter(
        organization=membership.organization, id=appointment_id
    ).first()
    if not appointment:
        return JsonResponse({"detail": "Not found."}, status=404)
    payload = json.loads(request.body or "{}")
    to_state = str(payload.get("to_state") or payload.get("to_status") or "").strip()
    if not to_state:
        return JsonResponse({"detail": "to_state is required"}, status=400)
    allowed = APPOINTMENT_TRANSITIONS.get(appointment.status, set())
    if to_state not in allowed:
        return JsonResponse({"detail": "Invalid transition."}, status=400)
    from_state = appointment.status
    appointment.status = to_state
    appointment.save(update_fields=["status", "updated_at"])
    AuditEvent.objects.create(
        organization=membership.organization,
        actor=request.user,
        action="appointment.transition",
        target_type="Appointment",
        target_id=str(appointment.id),
        metadata={"from_state": from_state, "to_state": to_state},
    )
    if appointment.episode_id:
        EpisodeEvent.objects.create(
            organization=membership.organization,
            episode=appointment.episode,
            created_by=request.user,
            event_type="appointment.transition",
            from_state=from_state,
            to_state=to_state,
            payload_json={"appointment_id": appointment.id},
        )
    return JsonResponse({"id": appointment.id, "status": appointment.status})


def _appointment_payload(appointment: Appointment) -> dict:
    return {
        "id": appointment.id,
        "patient_id": appointment.patient_id,
        "episode_id": appointment.episode_id,
        "scheduled_at": appointment.scheduled_at.isoformat(),
        "duration_minutes": appointment.duration_minutes,
        "location": appointment.location,
        "status": appointment.status,
        "notes": appointment.notes,
        "created_by": appointment.created_by_id,
        "created_at": appointment.created_at.isoformat(),
        "updated_at": appointment.updated_at.isoformat(),
    }
