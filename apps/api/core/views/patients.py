from __future__ import annotations

import json
import os
import secrets
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.http import JsonResponse
from django.utils import timezone

from ..models import (
    AuditEvent,
    CaregiverInvite,
    CareCircleMember,
    ConsentRecord,
    Episode,
    EpisodeEvent,
    Feedback,
    MedicationDoseEvent,
    MedicationSchedule,
    Organization,
    Patient,
    PatientAddress,
    PatientContactMethod,
    PatientIdentifier,
    PatientOTP,
    PatientProfile,
    PatientToken,
    WorkItem,
)
from ..rbac import has_permission
from ..security import rate_limit_or_429
from .utils import normalize_nhs_number, parse_date, parse_datetime, validate_nhs_number


def patients_list(request):
    membership = request.membership  # type: ignore[attr-defined]
    if request.method == "POST":
        permission = has_permission(membership.role, "patient:write")
        if not permission.allowed:
            return JsonResponse({"detail": "Not authorized."}, status=403)
        payload = json.loads(request.body or "{}")
        given_name = str(payload.get("given_name", "")).strip()
        family_name = str(payload.get("family_name", "")).strip()
        if not given_name or not family_name:
            return JsonResponse(
                {"detail": "given_name and family_name are required"}, status=400
            )
        date_of_birth = parse_date(payload.get("date_of_birth"))
        if payload.get("date_of_birth") and date_of_birth is None:
            return JsonResponse({"detail": "date_of_birth must be ISO date"}, status=400)
        nhs_number = normalize_nhs_number(payload.get("nhs_number"))
        if not validate_nhs_number(nhs_number):
            return JsonResponse({"detail": "nhs_number must be 10 digits"}, status=400)
        patient = Patient.objects.create(
            organization=membership.organization,
            given_name=given_name,
            family_name=family_name,
            date_of_birth=date_of_birth,
            nhs_number=nhs_number,
            phone=str(payload.get("phone", "")).strip(),
            email=str(payload.get("email", "")).strip(),
            address_line1=str(payload.get("address_line1", "")).strip(),
            address_line2=str(payload.get("address_line2", "")).strip(),
            city=str(payload.get("city", "")).strip(),
            region=str(payload.get("region", "")).strip(),
            postal_code=str(payload.get("postal_code", "")).strip(),
            country=str(payload.get("country", "")).strip(),
            restricted=bool(payload.get("restricted", False)),
        )
        _replace_patient_profiles(
            patient,
            identifiers=payload.get("identifiers"),
            addresses=payload.get("addresses"),
            contacts=payload.get("contacts"),
        )
        return JsonResponse(
            _patient_payload(patient, include_profiles=True),
            status=201,
        )

    permission = has_permission(membership.role, "patient:read")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    patients = Patient.objects.filter(
        organization=membership.organization, merged_into=None
    )
    search = request.GET.get("search", "").strip()
    if search:
        patients = patients.filter(
            models.Q(given_name__icontains=search)
            | models.Q(family_name__icontains=search)
            | models.Q(nhs_number__icontains=search)
            | models.Q(phone__icontains=search)
            | models.Q(email__icontains=search)
        )
    try:
        page = max(int(request.GET.get("page", "1")), 1)
    except ValueError:
        page = 1
    try:
        page_size = min(max(int(request.GET.get("page_size", "20")), 1), 100)
    except ValueError:
        page_size = 20
    total = patients.count()
    start = (page - 1) * page_size
    patients = patients.order_by("family_name", "given_name")[
        start : start + page_size
    ]
    payload = [
        _patient_payload(patient)
        for patient in patients
    ]
    return JsonResponse(
        {"results": payload, "count": total, "page": page, "page_size": page_size}
    )


def patient_detail(request, patient_id: int):
    membership = request.membership  # type: ignore[attr-defined]
    if request.method == "PATCH":
        permission = has_permission(membership.role, "patient:write")
        if not permission.allowed:
            return JsonResponse({"detail": "Not authorized."}, status=403)
    else:
        permission = has_permission(membership.role, "patient:read")
        if not permission.allowed:
            return JsonResponse({"detail": "Not authorized."}, status=403)
    patient = Patient.objects.filter(
        organization=membership.organization, id=patient_id, merged_into=None
    ).first()
    if not patient:
        return JsonResponse({"detail": "Not found."}, status=404)
    if request.method == "PATCH":
        payload = json.loads(request.body or "{}")
        for field in [
            "given_name",
            "family_name",
            "phone",
            "email",
            "address_line1",
            "address_line2",
            "city",
            "region",
            "postal_code",
            "country",
            "restricted",
        ]:
            if field in payload:
                if field == "restricted":
                    patient.restricted = bool(payload.get(field))
                else:
                    setattr(patient, field, str(payload.get(field, "")).strip())
        if "date_of_birth" in payload:
            date_of_birth = parse_date(payload.get("date_of_birth"))
            if payload.get("date_of_birth") and date_of_birth is None:
                return JsonResponse(
                    {"detail": "date_of_birth must be ISO date"}, status=400
                )
            patient.date_of_birth = date_of_birth
        if "nhs_number" in payload:
            nhs_number = normalize_nhs_number(payload.get("nhs_number"))
            if not validate_nhs_number(nhs_number):
                return JsonResponse(
                    {"detail": "nhs_number must be 10 digits"}, status=400
                )
            patient.nhs_number = nhs_number
        patient.save()
        _replace_patient_profiles(
            patient,
            identifiers=payload.get("identifiers"),
            addresses=payload.get("addresses"),
            contacts=payload.get("contacts"),
        )
        return JsonResponse(_patient_payload(patient, include_profiles=True))

    return JsonResponse(_patient_payload(patient, include_profiles=True))


def patient_search(request):
    membership = request.membership  # type: ignore[attr-defined]
    permission = has_permission(membership.role, "patient:read")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    query = request.GET.get("q", "").strip()
    patients = Patient.objects.filter(
        organization=membership.organization, merged_into=None
    )
    if query:
        patients = patients.filter(
            models.Q(given_name__icontains=query)
            | models.Q(family_name__icontains=query)
            | models.Q(nhs_number__icontains=query)
            | models.Q(phone__icontains=query)
            | models.Q(email__icontains=query)
        )
    try:
        page = max(int(request.GET.get("page", "1")), 1)
    except ValueError:
        page = 1
    try:
        page_size = min(max(int(request.GET.get("page_size", "20")), 1), 100)
    except ValueError:
        page_size = 20
    total = patients.count()
    start = (page - 1) * page_size
    patients = patients.order_by("family_name", "given_name")[
        start : start + page_size
    ]
    payload = [_patient_payload(patient) for patient in patients]
    return JsonResponse(
        {"results": payload, "count": total, "page": page, "page_size": page_size}
    )


def patient_episodes(request, patient_id: int):
    membership = request.membership  # type: ignore[attr-defined]
    permission = has_permission(membership.role, "patient:read")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    patient = Patient.objects.filter(
        organization=membership.organization, id=patient_id, merged_into=None
    ).first()
    if not patient:
        return JsonResponse({"detail": "Not found."}, status=404)
    if _requires_episode_consent(patient) and not _has_active_consent(
        patient, "episodes.read"
    ):
        return JsonResponse({"detail": "Consent required."}, status=403)
    episodes = Episode.objects.filter(
        organization=membership.organization, patient=patient
    ).order_by("-created_at")
    payload = [
        {
            "id": episode.id,
            "title": episode.title,
            "status": episode.status,
            "created_at": episode.created_at.isoformat(),
            "updated_at": episode.updated_at.isoformat(),
        }
        for episode in episodes
    ]
    return JsonResponse({"results": payload})


def _patient_payload(patient: Patient, include_profiles: bool = False) -> dict:
    payload = {
        "id": patient.id,
        "given_name": patient.given_name,
        "family_name": patient.family_name,
        "date_of_birth": patient.date_of_birth.isoformat()
        if patient.date_of_birth
        else None,
        "nhs_number": patient.nhs_number,
        "phone": patient.phone,
        "email": patient.email,
        "address_line1": patient.address_line1,
        "address_line2": patient.address_line2,
        "city": patient.city,
        "region": patient.region,
        "postal_code": patient.postal_code,
        "country": patient.country,
        "restricted": patient.restricted,
        "created_at": patient.created_at.isoformat(),
        "updated_at": patient.updated_at.isoformat(),
    }
    if not include_profiles:
        return payload
    payload["identifiers"] = [
        {
            "id": item.id,
            "kind": item.kind,
            "value": item.value,
            "system": item.system,
            "is_primary": item.is_primary,
        }
        for item in PatientIdentifier.objects.filter(patient=patient).order_by("id")
    ]
    payload["addresses"] = [
        {
            "id": item.id,
            "address_type": item.address_type,
            "line1": item.line1,
            "line2": item.line2,
            "city": item.city,
            "region": item.region,
            "postal_code": item.postal_code,
            "country": item.country,
            "is_primary": item.is_primary,
        }
        for item in PatientAddress.objects.filter(patient=patient).order_by("id")
    ]
    payload["contacts"] = [
        {
            "id": item.id,
            "kind": item.kind,
            "value": item.value,
            "notes": item.notes,
            "is_primary": item.is_primary,
        }
        for item in PatientContactMethod.objects.filter(patient=patient).order_by("id")
    ]
    return payload


def _replace_patient_profiles(
    patient: Patient,
    identifiers=None,
    addresses=None,
    contacts=None,
) -> None:
    if identifiers is not None:
        PatientIdentifier.objects.filter(patient=patient).delete()
        for entry in identifiers or []:
            kind = str(entry.get("kind", "")).strip()
            value = str(entry.get("value", "")).strip()
            if not kind or not value:
                continue
            PatientIdentifier.objects.create(
                organization=patient.organization,
                patient=patient,
                kind=kind,
                value=value,
                system=str(entry.get("system", "")).strip(),
                is_primary=bool(entry.get("is_primary", False)),
            )
    if addresses is not None:
        PatientAddress.objects.filter(patient=patient).delete()
        for entry in addresses or []:
            line1 = str(entry.get("line1", "")).strip()
            if not line1:
                continue
            PatientAddress.objects.create(
                organization=patient.organization,
                patient=patient,
                address_type=str(entry.get("address_type", "home")).strip() or "home",
                line1=line1,
                line2=str(entry.get("line2", "")).strip(),
                city=str(entry.get("city", "")).strip(),
                region=str(entry.get("region", "")).strip(),
                postal_code=str(entry.get("postal_code", "")).strip(),
                country=str(entry.get("country", "")).strip(),
                is_primary=bool(entry.get("is_primary", False)),
            )
    if contacts is not None:
        PatientContactMethod.objects.filter(patient=patient).delete()
        for entry in contacts or []:
            kind = str(entry.get("kind", "")).strip()
            value = str(entry.get("value", "")).strip()
            if not kind or not value:
                continue
            PatientContactMethod.objects.create(
                organization=patient.organization,
                patient=patient,
                kind=kind,
                value=value,
                notes=str(entry.get("notes", "")).strip(),
                is_primary=bool(entry.get("is_primary", False)),
            )


def _requires_episode_consent(patient: Patient) -> bool:
    return bool(patient.restricted)


def _has_active_consent(patient: Patient, scope: str) -> bool:
    now = timezone.now()
    return ConsentRecord.objects.filter(
        organization=patient.organization,
        patient=patient,
        scope=scope,
        granted=True,
        revoked_at__isnull=True,
    ).filter(models.Q(expires_at__isnull=True) | models.Q(expires_at__gte=now)).exists()


def patient_care_circle(request, patient_id: int):
    membership = request.membership  # type: ignore[attr-defined]
    patient = Patient.objects.filter(
        organization=membership.organization, id=patient_id, merged_into=None
    ).first()
    if not patient:
        return JsonResponse({"detail": "Not found."}, status=404)
    if request.method == "POST":
        permission = has_permission(membership.role, "patient:write")
        if not permission.allowed:
            return JsonResponse({"detail": "Not authorized."}, status=403)
        payload = json.loads(request.body or "{}")
        person_name = str(payload.get("person_name", "")).strip()
        relationship = str(payload.get("relationship", "")).strip()
        if not person_name or not relationship:
            return JsonResponse(
                {"detail": "person_name and relationship are required"}, status=400
            )
        member = CareCircleMember.objects.create(
            organization=membership.organization,
            patient=patient,
            person_name=person_name,
            relationship=relationship,
            contact=str(payload.get("contact", "")).strip(),
            notes=str(payload.get("notes", "")).strip(),
        )
        AuditEvent.objects.create(
            organization=membership.organization,
            actor=request.user,
            action="care_circle.created",
            target_type="CareCircleMember",
            target_id=str(member.id),
            metadata={"patient_id": patient.id},
        )
        return JsonResponse(_care_circle_payload(member), status=201)

    permission = has_permission(membership.role, "patient:read")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    members = CareCircleMember.objects.filter(
        organization=membership.organization, patient=patient
    ).order_by("created_at")
    return JsonResponse({"results": [_care_circle_payload(m) for m in members]})


def patient_care_circle_detail(request, patient_id: int, member_id: int):
    membership = request.membership  # type: ignore[attr-defined]
    patient = Patient.objects.filter(
        organization=membership.organization, id=patient_id, merged_into=None
    ).first()
    if not patient:
        return JsonResponse({"detail": "Not found."}, status=404)
    member = CareCircleMember.objects.filter(
        organization=membership.organization, patient=patient, id=member_id
    ).first()
    if not member:
        return JsonResponse({"detail": "Not found."}, status=404)
    if request.method == "DELETE":
        permission = has_permission(membership.role, "patient:write")
        if not permission.allowed:
            return JsonResponse({"detail": "Not authorized."}, status=403)
        member.delete()
        AuditEvent.objects.create(
            organization=membership.organization,
            actor=request.user,
            action="care_circle.deleted",
            target_type="CareCircleMember",
            target_id=str(member_id),
            metadata={"patient_id": patient.id},
        )
        return JsonResponse({"status": "deleted"})
    if request.method == "PATCH":
        permission = has_permission(membership.role, "patient:write")
        if not permission.allowed:
            return JsonResponse({"detail": "Not authorized."}, status=403)
        payload = json.loads(request.body or "{}")
        for field in ["person_name", "relationship", "contact", "notes"]:
            if field in payload:
                setattr(member, field, str(payload.get(field, "")).strip())
        member.save()
        AuditEvent.objects.create(
            organization=membership.organization,
            actor=request.user,
            action="care_circle.updated",
            target_type="CareCircleMember",
            target_id=str(member.id),
            metadata={"patient_id": patient.id},
        )
        return JsonResponse(_care_circle_payload(member))
    return JsonResponse({"detail": "Method not allowed."}, status=405)


def patient_consents(request, patient_id: int):
    membership = request.membership  # type: ignore[attr-defined]
    patient = Patient.objects.filter(
        organization=membership.organization, id=patient_id, merged_into=None
    ).first()
    if not patient:
        return JsonResponse({"detail": "Not found."}, status=404)
    if request.method == "POST":
        permission = has_permission(membership.role, "patient:write")
        if not permission.allowed:
            return JsonResponse({"detail": "Not authorized."}, status=403)
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
            organization=membership.organization,
            patient=patient,
            subject_type="patient",
            subject_id=str(patient.id),
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
            organization=membership.organization,
            actor=request.user,
            action="consent.granted",
            target_type="ConsentRecord",
            target_id=str(consent.id),
            metadata={"patient_id": patient.id, "scope": scope},
        )
        return JsonResponse(_consent_payload(consent), status=201)

    permission = has_permission(membership.role, "patient:read")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    consents = ConsentRecord.objects.filter(
        organization=membership.organization, patient=patient
    ).order_by("-recorded_at", "-id")
    return JsonResponse({"results": [_consent_payload(c) for c in consents]})


def patient_consent_revoke(request, patient_id: int, consent_id: int):
    membership = request.membership  # type: ignore[attr-defined]
    permission = has_permission(membership.role, "patient:write")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    patient = Patient.objects.filter(
        organization=membership.organization, id=patient_id, merged_into=None
    ).first()
    if not patient:
        return JsonResponse({"detail": "Not found."}, status=404)
    consent = ConsentRecord.objects.filter(
        organization=membership.organization, patient=patient, id=consent_id
    ).first()
    if not consent:
        return JsonResponse({"detail": "Not found."}, status=404)
    consent.granted = False
    consent.revoked_at = timezone.now()
    consent.save(update_fields=["granted", "revoked_at"])
    AuditEvent.objects.create(
        organization=membership.organization,
        actor=request.user,
        action="consent.revoked",
        target_type="ConsentRecord",
        target_id=str(consent.id),
        metadata={"patient_id": patient.id, "scope": consent.scope},
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


def patient_merge(request, patient_id: int):
    membership = request.membership  # type: ignore[attr-defined]
    permission = has_permission(membership.role, "patient:merge")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    target = Patient.objects.filter(
        organization=membership.organization, id=patient_id, merged_into=None
    ).first()
    if not target:
        return JsonResponse({"detail": "Not found."}, status=404)
    payload = json.loads(request.body or "{}")
    source_id = payload.get("source_id")
    if not source_id:
        return JsonResponse({"detail": "source_id is required"}, status=400)
    if int(source_id) == target.id:
        return JsonResponse({"detail": "source_id must differ from target"}, status=400)
    source = Patient.objects.filter(
        organization=membership.organization, id=source_id, merged_into=None
    ).first()
    if not source:
        return JsonResponse({"detail": "source not found"}, status=404)
    source.merged_into = target
    source.merged_at = timezone.now()
    source.save(update_fields=["merged_into", "merged_at"])
    Episode.objects.filter(organization=membership.organization, patient=source).update(
        patient=target
    )
    AuditEvent.objects.create(
        organization=membership.organization,
        actor=request.user,
        action="patient.merged",
        target_type="Patient",
        target_id=str(target.id),
        metadata={"source_id": source.id},
    )
    return JsonResponse({"id": target.id, "merged_source_id": source.id})


def _get_patient_token(request):
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    token_value = auth_header.replace("Bearer ", "").strip()
    return PatientToken.objects.select_related("patient").filter(
        token=token_value
    ).first()


def _require_patient(request):
    token = _get_patient_token(request)
    if not token or token.expires_at < timezone.now():
        return None
    return token.patient


def patient_request_otp(request):
    rate_limited = rate_limit_or_429(
        request,
        key=f"patient_request_otp:{request.META.get('REMOTE_ADDR', '')}",
        limit=5,
        window_seconds=300,
    )
    if rate_limited:
        return rate_limited
    payload = json.loads(request.body or "{}")
    phone = str(payload.get("phone", "")).strip()
    if not phone:
        return JsonResponse({"detail": "phone is required"}, status=400)
    code = f"{secrets.randbelow(1000000):06d}"
    otp = PatientOTP.objects.create(
        phone=phone,
        code=code,
        expires_at=timezone.now() + timedelta(minutes=10),
    )
    org_slug = os.environ.get("PATIENT_DEFAULT_ORG_SLUG", "careos-patients")
    org, _ = Organization.objects.get_or_create(
        slug=org_slug, defaults={"name": "CareOS Patients"}
    )
    AuditEvent.objects.create(
        organization=org,
        actor=None,
        action="patient.otp.requested",
        target_type="PatientOTP",
        target_id=str(otp.id),
        metadata={"phone": phone},
    )
    response = {"status": "sent"}
    if settings.DEBUG:
        response["code"] = otp.code
    return JsonResponse(response)


def patient_verify_otp(request):
    rate_limited = rate_limit_or_429(
        request,
        key=f"patient_verify_otp:{request.META.get('REMOTE_ADDR', '')}",
        limit=10,
        window_seconds=300,
    )
    if rate_limited:
        return rate_limited
    payload = json.loads(request.body or "{}")
    phone = str(payload.get("phone", "")).strip()
    code = str(payload.get("code", "")).strip()
    if not phone or not code:
        return JsonResponse({"detail": "phone and code are required"}, status=400)
    otp = (
        PatientOTP.objects.filter(phone=phone, code=code, used=False)
        .order_by("-created_at")
        .first()
    )
    if not otp or otp.expires_at < timezone.now():
        return JsonResponse({"detail": "invalid or expired code"}, status=400)
    otp.used = True
    otp.save(update_fields=["used"])
    user_model = get_user_model()
    user, _ = user_model.objects.get_or_create(username=f"patient_{phone}")
    org_slug = os.environ.get("PATIENT_DEFAULT_ORG_SLUG", "careos-patients")
    org, _ = Organization.objects.get_or_create(
        slug=org_slug, defaults={"name": "CareOS Patients"}
    )
    patient, _ = PatientProfile.objects.get_or_create(
        user=user, defaults={"organization": org, "phone": phone}
    )
    if patient.phone != phone:
        patient.phone = phone
        patient.save(update_fields=["phone"])
    token_value = secrets.token_hex(32)
    token = PatientToken.objects.create(
        patient=patient,
        token=token_value,
        expires_at=timezone.now() + timedelta(days=7),
    )
    AuditEvent.objects.create(
        organization=patient.organization,
        actor=None,
        action="patient.otp.verified",
        target_type="PatientToken",
        target_id=str(token.id),
        metadata={"phone": phone},
    )
    return JsonResponse({"token": token.token, "patient_id": patient.id})


def patient_schedules_list(request):
    patient = _require_patient(request)
    if not patient:
        return JsonResponse({"detail": "Unauthorized"}, status=401)
    if request.method == "POST":
        payload = json.loads(request.body or "{}")
        name = str(payload.get("name", "")).strip()
        times = payload.get("times", [])
        start_date_raw = payload.get("start_date")
        if not name or not times or not start_date_raw:
            return JsonResponse(
                {"detail": "name, times, start_date required"}, status=400
            )
        try:
            start_date = datetime.fromisoformat(str(start_date_raw)).date()
        except ValueError:
            return JsonResponse({"detail": "start_date must be ISO date"}, status=400)
        end_date = None
        if payload.get("end_date"):
            try:
                end_date = datetime.fromisoformat(str(payload.get("end_date"))).date()
            except ValueError:
                return JsonResponse({"detail": "end_date must be ISO date"}, status=400)
        schedule = MedicationSchedule.objects.create(
            patient=patient,
            name=name,
            dosage=str(payload.get("dosage", "")),
            instructions=str(payload.get("instructions", "")),
            times=times,
            timezone=str(payload.get("timezone", "UTC")),
            start_date=start_date,
            end_date=end_date,
            active=bool(payload.get("active", True)),
        )
        return JsonResponse({"id": schedule.id, "name": schedule.name}, status=201)

    schedules = MedicationSchedule.objects.filter(patient=patient).order_by(
        "-created_at"
    )
    payload = [
        {
            "id": schedule.id,
            "name": schedule.name,
            "dosage": schedule.dosage,
            "instructions": schedule.instructions,
            "times": schedule.times,
            "timezone": schedule.timezone,
            "start_date": schedule.start_date.isoformat(),
            "end_date": schedule.end_date.isoformat() if schedule.end_date else None,
            "active": schedule.active,
        }
        for schedule in schedules
    ]
    return JsonResponse({"results": payload})


def patient_schedule_detail(request, schedule_id: int):
    patient = _require_patient(request)
    if not patient:
        return JsonResponse({"detail": "Unauthorized"}, status=401)
    schedule = MedicationSchedule.objects.filter(
        patient=patient, id=schedule_id
    ).first()
    if not schedule:
        return JsonResponse({"detail": "Not found"}, status=404)
    if request.method == "DELETE":
        schedule.delete()
        return JsonResponse({"status": "deleted"})
    payload = json.loads(request.body or "{}")
    for field in ["name", "dosage", "instructions", "times", "timezone", "active"]:
        if field in payload:
            setattr(schedule, field, payload[field])
    if "start_date" in payload:
        try:
            schedule.start_date = datetime.fromisoformat(
                str(payload["start_date"])
            ).date()
        except ValueError:
            return JsonResponse({"detail": "start_date must be ISO date"}, status=400)
    if "end_date" in payload:
        try:
            schedule.end_date = (
                datetime.fromisoformat(str(payload["end_date"])).date()
                if payload["end_date"]
                else None
            )
        except ValueError:
            return JsonResponse({"detail": "end_date must be ISO date"}, status=400)
    schedule.save()
    return JsonResponse({"id": schedule.id, "name": schedule.name})


def patient_schedule_confirm(request, schedule_id: int):
    patient = _require_patient(request)
    if not patient:
        return JsonResponse({"detail": "Unauthorized"}, status=401)
    schedule = MedicationSchedule.objects.filter(
        patient=patient, id=schedule_id
    ).first()
    if not schedule:
        return JsonResponse({"detail": "Not found"}, status=404)
    payload = json.loads(request.body or "{}")
    status = str(payload.get("status", "")).strip()
    scheduled_for_raw = payload.get("scheduled_for")
    if status not in {"taken", "missed"} or not scheduled_for_raw:
        return JsonResponse({"detail": "status and scheduled_for required"}, status=400)
    try:
        scheduled_for = datetime.fromisoformat(str(scheduled_for_raw))
    except ValueError:
        return JsonResponse(
            {"detail": "scheduled_for must be ISO timestamp"}, status=400
        )
    event = MedicationDoseEvent.objects.create(
        patient=patient,
        schedule=schedule,
        status=status,
        scheduled_for=scheduled_for,
    )
    return JsonResponse({"id": event.id, "status": event.status})


def patient_feedback(request):
    patient = _require_patient(request)
    if not patient:
        return JsonResponse({"detail": "Unauthorized"}, status=401)
    payload = json.loads(request.body or "{}")
    message = str(payload.get("message", "")).strip()
    if not message:
        return JsonResponse({"detail": "message required"}, status=400)
    feedback = Feedback.objects.create(
        patient=patient,
        message=message,
        category=str(payload.get("category", "")),
    )
    episode = Episode.objects.create(
        organization=patient.organization,
        title="Patient feedback",
        description=feedback.message,
    )
    EpisodeEvent.objects.create(
        organization=patient.organization,
        episode=episode,
        event_type="feedback.created",
        from_state="",
        to_state=episode.status,
        payload_json={"feedback_id": feedback.id},
    )
    WorkItem.objects.create(
        organization=patient.organization,
        episode=episode,
        kind="feedback.review",
        status="open",
    )
    return JsonResponse({"status": "received"})


def patient_caregivers(request):
    patient = _require_patient(request)
    if not patient:
        return JsonResponse({"detail": "Unauthorized"}, status=401)
    if request.method == "POST":
        payload = json.loads(request.body or "{}")
        contact = str(payload.get("contact", "")).strip()
        if not contact:
            return JsonResponse({"detail": "contact required"}, status=400)
        invite = CaregiverInvite.objects.create(
            patient=patient,
            contact=contact,
            channel=str(payload.get("channel", "sms")),
            permissions=payload.get("permissions", ["alerts"]),
        )
        return JsonResponse({"id": invite.id, "status": invite.status}, status=201)
    invites = CaregiverInvite.objects.filter(patient=patient).order_by("-created_at")
    payload = [
        {
            "id": invite.id,
            "contact": invite.contact,
            "channel": invite.channel,
            "status": invite.status,
            "permissions": invite.permissions,
        }
        for invite in invites
    ]
    return JsonResponse({"results": payload})
