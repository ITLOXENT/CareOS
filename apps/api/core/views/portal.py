from __future__ import annotations

import json
import secrets
import hashlib
from datetime import timedelta

from django.http import JsonResponse
from django.utils import timezone

from ..models import (
    AuditEvent,
    CareCircleMember,
    ConsentRecord,
    Episode,
    EpisodeEvent,
    PortalInvite,
    PortalNotification,
    PortalSession,
)
from .utils import parse_datetime
from ..security import rate_limit_or_429


def _get_portal_session(request) -> PortalSession | None:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    token_value = auth_header.replace("Bearer ", "").strip()
    session = PortalSession.objects.filter(token=token_value).select_related(
        "patient", "organization"
    ).first()
    if not session:
        return None
    if session.expires_at < timezone.now():
        return None
    return session


def portal_accept_invite(request):
    rate_limited = rate_limit_or_429(
        request,
        key=f"portal_accept:{request.META.get('REMOTE_ADDR', '')}",
        limit=5,
        window_seconds=300,
    )
    if rate_limited:
        return rate_limited
    payload = json.loads(request.body or "{}")
    token = str(payload.get("token", "")).strip()
    if not token:
        return JsonResponse({"detail": "token is required"}, status=400)
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    invite = PortalInvite.objects.filter(token_hash=token_hash).select_related(
        "patient", "organization"
    ).first()
    if not invite:
        return JsonResponse({"detail": "Invalid token"}, status=404)
    if invite.expires_at < timezone.now():
        return JsonResponse({"detail": "Invite expired"}, status=400)
    if not invite.accepted_at:
        invite.accepted_at = timezone.now()
        invite.save(update_fields=["accepted_at"])
    session_token = secrets.token_hex(32)
    session = PortalSession.objects.create(
        organization=invite.organization,
        patient=invite.patient,
        role=invite.role,
        token=session_token,
        expires_at=timezone.now() + timedelta(hours=24),
    )
    AuditEvent.objects.create(
        organization=invite.organization,
        actor=None,
        action="portal.invite.accepted",
        target_type="PortalInvite",
        target_id=str(invite.id),
    )
    return JsonResponse(
        {
            "token": session.token,
            "role": session.role,
            "patient_id": session.patient_id,
            "organization_id": session.organization_id,
            "expires_at": session.expires_at.isoformat(),
        }
    )


def portal_login(request):
    rate_limited = rate_limit_or_429(
        request,
        key=f"portal_login:{request.META.get('REMOTE_ADDR', '')}",
        limit=10,
        window_seconds=300,
    )
    if rate_limited:
        return rate_limited
    payload = json.loads(request.body or "{}")
    email = str(payload.get("email", "")).strip().lower()
    phone = str(payload.get("phone", "")).strip()
    if not email and not phone:
        return JsonResponse({"detail": "email or phone required"}, status=400)
    invites = PortalInvite.objects.filter(accepted_at__isnull=False)
    if email:
        invites = invites.filter(email=email)
    if phone:
        invites = invites.filter(phone=phone)
    invite = invites.order_by("-created_at").first()
    if not invite:
        return JsonResponse({"detail": "No invite found"}, status=404)
    if invite.expires_at < timezone.now():
        return JsonResponse({"detail": "Invite expired"}, status=400)
    session_token = secrets.token_hex(32)
    session = PortalSession.objects.create(
        organization=invite.organization,
        patient=invite.patient,
        role=invite.role,
        token=session_token,
        expires_at=timezone.now() + timedelta(hours=24),
    )
    AuditEvent.objects.create(
        organization=invite.organization,
        actor=None,
        action="portal.login",
        target_type="PortalSession",
        target_id=str(session.id),
    )
    return JsonResponse(
        {
            "token": session.token,
            "role": session.role,
            "patient_id": session.patient_id,
            "organization_id": session.organization_id,
            "expires_at": session.expires_at.isoformat(),
        }
    )


def portal_me(request):
    session = _get_portal_session(request)
    if not session:
        return JsonResponse({"detail": "Unauthorized"}, status=401)
    patient = session.patient
    return JsonResponse(
        {
            "patient_id": patient.id,
            "organization_id": session.organization_id,
            "role": session.role,
            "given_name": patient.given_name,
            "family_name": patient.family_name,
            "email": patient.email,
            "phone": patient.phone,
        }
    )


def portal_episodes(request):
    session = _get_portal_session(request)
    if not session:
        return JsonResponse({"detail": "Unauthorized"}, status=401)
    episodes = Episode.objects.filter(
        organization=session.organization, patient=session.patient
    ).order_by("-created_at")
    payload = [
        {
            "id": episode.id,
            "title": episode.title,
            "description": episode.description,
            "status": episode.status,
            "created_at": episode.created_at.isoformat(),
            "updated_at": episode.updated_at.isoformat(),
        }
        for episode in episodes
    ]
    return JsonResponse({"results": payload})


def portal_episode_detail(request, episode_id: int):
    session = _get_portal_session(request)
    if not session:
        return JsonResponse({"detail": "Unauthorized"}, status=401)
    episode = Episode.objects.filter(
        organization=session.organization, patient=session.patient, id=episode_id
    ).first()
    if not episode:
        return JsonResponse({"detail": "Not found"}, status=404)
    events = EpisodeEvent.objects.filter(
        organization=session.organization, episode=episode
    ).order_by("created_at", "id")
    payload = {
        "episode": {
            "id": episode.id,
            "title": episode.title,
            "description": episode.description,
            "status": episode.status,
            "created_at": episode.created_at.isoformat(),
            "updated_at": episode.updated_at.isoformat(),
        },
        "timeline": [
            {
                "id": event.id,
                "event_type": event.event_type,
                "from_state": event.from_state,
                "to_state": event.to_state,
                "note": event.note,
                "created_at": event.created_at.isoformat(),
            }
            for event in events
        ],
    }
    return JsonResponse(payload)


def portal_notifications(request):
    session = _get_portal_session(request)
    if not session:
        return JsonResponse({"detail": "Unauthorized"}, status=401)
    notifications = PortalNotification.objects.filter(
        organization=session.organization, patient=session.patient
    ).order_by("-created_at")
    unread_only = request.GET.get("unread_only")
    if unread_only in {"1", "true", "True"}:
        notifications = notifications.filter(unread=True)
    try:
        page = max(int(request.GET.get("page", "1")), 1)
    except ValueError:
        page = 1
    try:
        page_size = min(max(int(request.GET.get("page_size", "50")), 1), 200)
    except ValueError:
        page_size = 50
    total = notifications.count()
    start_index = (page - 1) * page_size
    notifications = notifications[start_index : start_index + page_size]
    payload = [
        {
            "id": item.id,
            "kind": item.kind,
            "title": item.title,
            "body": item.body,
            "url": item.url,
            "unread": item.unread,
            "read_at": item.read_at.isoformat() if item.read_at else None,
            "created_at": item.created_at.isoformat(),
        }
        for item in notifications
    ]
    return JsonResponse(
        {"results": payload, "count": total, "page": page, "page_size": page_size}
    )


def portal_notification_mark_read(request, notification_id: int):
    session = _get_portal_session(request)
    if not session:
        return JsonResponse({"detail": "Unauthorized"}, status=401)
    notification = PortalNotification.objects.filter(
        organization=session.organization,
        patient=session.patient,
        id=notification_id,
    ).first()
    if not notification:
        return JsonResponse({"detail": "Not found"}, status=404)
    notification.unread = False
    notification.read_at = parse_datetime(request.GET.get("read_at", "")) or timezone.now()
    notification.save(update_fields=["unread", "read_at"])
    return JsonResponse(
        {
            "id": notification.id,
            "unread": notification.unread,
            "read_at": notification.read_at.isoformat() if notification.read_at else None,
        }
    )


def portal_care_circle(request):
    session = _get_portal_session(request)
    if not session:
        return JsonResponse({"detail": "Unauthorized"}, status=401)
    if request.method == "POST":
        payload = json.loads(request.body or "{}")
        person_name = str(payload.get("person_name", "")).strip()
        relationship = str(payload.get("relationship", "")).strip()
        if not person_name or not relationship:
            return JsonResponse(
                {"detail": "person_name and relationship are required"}, status=400
            )
        member = CareCircleMember.objects.create(
            organization=session.organization,
            patient=session.patient,
            person_name=person_name,
            relationship=relationship,
            contact=str(payload.get("contact", "")).strip(),
            notes=str(payload.get("notes", "")).strip(),
        )
        AuditEvent.objects.create(
            organization=session.organization,
            actor=None,
            action="portal.care_circle.created",
            target_type="CareCircleMember",
            target_id=str(member.id),
            metadata={"patient_id": session.patient_id},
        )
        return JsonResponse(_care_circle_payload(member), status=201)
    members = CareCircleMember.objects.filter(
        organization=session.organization, patient=session.patient
    ).order_by("created_at")
    return JsonResponse({"results": [_care_circle_payload(m) for m in members]})


def portal_care_circle_detail(request, member_id: int):
    session = _get_portal_session(request)
    if not session:
        return JsonResponse({"detail": "Unauthorized"}, status=401)
    member = CareCircleMember.objects.filter(
        organization=session.organization, patient=session.patient, id=member_id
    ).first()
    if not member:
        return JsonResponse({"detail": "Not found."}, status=404)
    if request.method == "DELETE":
        member.delete()
        AuditEvent.objects.create(
            organization=session.organization,
            actor=None,
            action="portal.care_circle.deleted",
            target_type="CareCircleMember",
            target_id=str(member_id),
            metadata={"patient_id": session.patient_id},
        )
        return JsonResponse({"status": "deleted"})
    if request.method == "PATCH":
        payload = json.loads(request.body or "{}")
        for field in ["person_name", "relationship", "contact", "notes"]:
            if field in payload:
                setattr(member, field, str(payload.get(field, "")).strip())
        member.save()
        AuditEvent.objects.create(
            organization=session.organization,
            actor=None,
            action="portal.care_circle.updated",
            target_type="CareCircleMember",
            target_id=str(member.id),
            metadata={"patient_id": session.patient_id},
        )
        return JsonResponse(_care_circle_payload(member))
    return JsonResponse({"detail": "Method not allowed."}, status=405)


def portal_consents(request):
    session = _get_portal_session(request)
    if not session:
        return JsonResponse({"detail": "Unauthorized"}, status=401)
    if request.method == "POST":
        payload = json.loads(request.body or "{}")
        scope = str(payload.get("scope", "")).strip()
        lawful_basis = str(payload.get("lawful_basis", "")).strip()
        granted_by = str(payload.get("granted_by", "")).strip()
        if not scope or not lawful_basis or not granted_by:
            return JsonResponse(
                {"detail": "scope, lawful_basis, granted_by are required"}, status=400
            )
        expires_at = (
            parse_datetime(payload.get("expires_at"))
            if payload.get("expires_at")
            else None
        )
        consent = ConsentRecord.objects.create(
            organization=session.organization,
            patient=session.patient,
            subject_type="patient",
            subject_id=str(session.patient_id),
            consent_type=scope,
            scope=scope,
            lawful_basis=lawful_basis,
            granted_by=granted_by,
            expires_at=expires_at,
            policy_version=str(payload.get("policy_version", "v1")),
            channel=str(payload.get("channel", "")),
            granted=True,
            metadata=payload.get("metadata") or {},
        )
        AuditEvent.objects.create(
            organization=session.organization,
            actor=None,
            action="portal.consent.granted",
            target_type="ConsentRecord",
            target_id=str(consent.id),
            metadata={"patient_id": session.patient_id, "scope": scope},
        )
        return JsonResponse(_consent_payload(consent), status=201)
    consents = ConsentRecord.objects.filter(
        organization=session.organization, patient=session.patient
    ).order_by("-recorded_at", "-id")
    return JsonResponse({"results": [_consent_payload(c) for c in consents]})


def portal_consent_revoke(request, consent_id: int):
    session = _get_portal_session(request)
    if not session:
        return JsonResponse({"detail": "Unauthorized"}, status=401)
    consent = ConsentRecord.objects.filter(
        organization=session.organization, patient=session.patient, id=consent_id
    ).first()
    if not consent:
        return JsonResponse({"detail": "Not found."}, status=404)
    consent.granted = False
    consent.revoked_at = timezone.now()
    consent.save(update_fields=["granted", "revoked_at"])
    AuditEvent.objects.create(
        organization=session.organization,
        actor=None,
        action="portal.consent.revoked",
        target_type="ConsentRecord",
        target_id=str(consent.id),
        metadata={"patient_id": session.patient_id, "scope": consent.scope},
    )
    return JsonResponse(_consent_payload(consent))


def _care_circle_payload(member: CareCircleMember) -> dict:
    return {
        "id": member.id,
        "person_name": member.person_name,
        "relationship": member.relationship,
        "contact": member.contact,
        "notes": member.notes,
        "created_at": member.created_at.isoformat(),
    }


def _consent_payload(consent: ConsentRecord) -> dict:
    return {
        "id": consent.id,
        "scope": consent.scope or consent.consent_type,
        "lawful_basis": consent.lawful_basis,
        "granted_by": consent.granted_by,
        "expires_at": consent.expires_at.isoformat() if consent.expires_at else None,
        "granted": consent.granted,
        "revoked_at": consent.revoked_at.isoformat() if consent.revoked_at else None,
        "policy_version": consent.policy_version,
        "channel": consent.channel,
        "recorded_at": consent.recorded_at.isoformat(),
    }
