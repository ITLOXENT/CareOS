from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import FileResponse, JsonResponse
from django.utils import timezone

from ..models import (
    AuditEvent,
    ConsentRecord,
    DsarExport,
    Episode,
    EvidenceItem,
    Organization,
    Patient,
)
from ..rbac import has_permission


def _consent_payload(record: ConsentRecord) -> dict:
    return {
        "id": record.id,
        "subject_type": record.subject_type,
        "subject_id": record.subject_id,
        "consent_type": record.consent_type,
        "policy_version": record.policy_version,
        "channel": record.channel,
        "granted": record.granted,
        "metadata": record.metadata,
        "recorded_at": record.recorded_at.isoformat(),
        "created_at": record.created_at.isoformat(),
    }


def _export_payload(export: DsarExport) -> dict:
    return {
        "id": export.id,
        "subject_type": export.subject_type,
        "subject_id": export.subject_id,
        "status": export.status,
        "created_at": export.created_at.isoformat(),
        "finished_at": export.finished_at.isoformat() if export.finished_at else None,
        "artifact_path": export.artifact_path or None,
    }


def _anonymize_patient(patient: Patient, actor) -> None:
    patient.given_name = "Redacted"
    patient.family_name = "Redacted"
    patient.date_of_birth = None
    patient.nhs_number = None
    patient.phone = ""
    patient.email = ""
    patient.address_line1 = ""
    patient.address_line2 = ""
    patient.city = ""
    patient.region = ""
    patient.postal_code = ""
    patient.country = ""
    patient.save(
        update_fields=[
            "given_name",
            "family_name",
            "date_of_birth",
            "nhs_number",
            "phone",
            "email",
            "address_line1",
            "address_line2",
            "city",
            "region",
            "postal_code",
            "country",
            "updated_at",
        ]
    )
    Episode.objects.filter(organization=patient.organization, patient=patient).update(
        patient=None,
        title="Redacted episode",
        description="",
    )
    AuditEvent.objects.create(
        organization=patient.organization,
        actor=actor,
        action="privacy.patient.anonymized",
        target_type="Patient",
        target_id=str(patient.id),
    )


def _anonymize_user(user_id: int, organization: Organization, actor) -> None:
    user_model = get_user_model()
    user = user_model.objects.filter(id=user_id).first()
    if not user:
        return
    user.email = ""
    user.username = f"deactivated-{user.id}"
    user.is_active = False
    user.save(update_fields=["email", "username", "is_active"])
    AuditEvent.objects.create(
        organization=organization,
        actor=actor,
        action="privacy.user.anonymized",
        target_type="User",
        target_id=str(user.id),
    )


def consent_records(request):
    membership = request.membership  # type: ignore[attr-defined]
    permission = has_permission(membership.role, "org:manage")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    if request.method == "POST":
        payload = json.loads(request.body or "{}")
        subject_type = str(payload.get("subject_type", "")).strip()
        subject_id = str(payload.get("subject_id", "")).strip()
        consent_type = str(payload.get("consent_type", "")).strip()
        policy_version = str(payload.get("policy_version", "")).strip()
        if not subject_type or not subject_id or not consent_type or not policy_version:
            return JsonResponse(
                {"detail": "subject_type, subject_id, consent_type, policy_version required"},
                status=400,
            )
        record = ConsentRecord.objects.create(
            organization=membership.organization,
            subject_type=subject_type,
            subject_id=subject_id,
            consent_type=consent_type,
            policy_version=policy_version,
            channel=str(payload.get("channel", "")).strip(),
            granted=bool(payload.get("granted", True)),
            metadata=payload.get("metadata", {}) or {},
        )
        AuditEvent.objects.create(
            organization=membership.organization,
            actor=request.user,
            action="privacy.consent.recorded",
            target_type="ConsentRecord",
            target_id=str(record.id),
        )
        return JsonResponse(_consent_payload(record), status=201)
    records = ConsentRecord.objects.filter(organization=membership.organization)
    subject_type = request.GET.get("subject_type")
    subject_id = request.GET.get("subject_id")
    if subject_type:
        records = records.filter(subject_type=subject_type)
    if subject_id:
        records = records.filter(subject_id=subject_id)
    payload = [_consent_payload(record) for record in records.order_by("-recorded_at")]
    return JsonResponse({"results": payload})


def dsar_exports(request):
    membership = request.membership  # type: ignore[attr-defined]
    permission = has_permission(membership.role, "org:manage")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    exports = DsarExport.objects.filter(organization=membership.organization).order_by(
        "-created_at"
    )
    return JsonResponse({"results": [_export_payload(export) for export in exports]})


def dsar_export_request(request):
    membership = request.membership  # type: ignore[attr-defined]
    permission = has_permission(membership.role, "org:manage")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    payload = json.loads(request.body or "{}")
    subject_type = str(payload.get("subject_type", "")).strip() or "org"
    subject_id = str(payload.get("subject_id", "")).strip()
    if subject_type == "org":
        subject_id = subject_id or str(membership.organization_id)
    if not subject_id:
        return JsonResponse({"detail": "subject_id required"}, status=400)
    export = DsarExport.objects.create(
        organization=membership.organization,
        requested_by=request.user,
        subject_type=subject_type,
        subject_id=subject_id,
        status="running",
        params_json=payload,
    )
    artifact_path = _build_dsar_export(export)
    export.status = "done"
    export.finished_at = timezone.now()
    export.artifact_path = artifact_path
    export.save(update_fields=["status", "finished_at", "artifact_path"])
    AuditEvent.objects.create(
        organization=membership.organization,
        actor=request.user,
        action="privacy.dsar.exported",
        target_type="DsarExport",
        target_id=str(export.id),
        metadata={"subject_type": subject_type, "subject_id": subject_id},
    )
    return JsonResponse(_export_payload(export), status=201)


def dsar_export_download(request, export_id: int):
    membership = request.membership  # type: ignore[attr-defined]
    permission = has_permission(membership.role, "org:manage")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    export = DsarExport.objects.filter(
        organization=membership.organization, id=export_id
    ).first()
    if not export or not export.artifact_path:
        return JsonResponse({"detail": "Not found."}, status=404)
    base_dir = Path(settings.EXPORT_STORAGE_DIR).resolve()
    path = Path(export.artifact_path).resolve()
    if base_dir not in path.parents and path != base_dir:
        return JsonResponse({"detail": "Not found."}, status=404)
    if not path.exists():
        return JsonResponse({"detail": "Not found."}, status=404)
    return FileResponse(path.open("rb"), as_attachment=True, filename=path.name)


def dsar_delete(request):
    membership = request.membership  # type: ignore[attr-defined]
    permission = has_permission(membership.role, "org:manage")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    payload = json.loads(request.body or "{}")
    subject_type = str(payload.get("subject_type", "")).strip()
    subject_id = payload.get("subject_id")
    if not subject_type or not subject_id:
        return JsonResponse({"detail": "subject_type and subject_id required"}, status=400)
    if subject_type == "patient":
        patient = Patient.objects.filter(
            organization=membership.organization, id=subject_id
        ).first()
        if not patient:
            return JsonResponse({"detail": "Not found."}, status=404)
        _anonymize_patient(patient, request.user)
    elif subject_type == "user":
        _anonymize_user(int(subject_id), membership.organization, request.user)
    else:
        return JsonResponse({"detail": "Unsupported subject_type"}, status=400)
    return JsonResponse({"status": "ok"})


def _build_dsar_export(export: DsarExport) -> str:
    org = export.organization
    payload: dict[str, Any] = {
        "organization": {"id": org.id, "name": org.name, "slug": org.slug},
        "generated_at": timezone.now().isoformat(),
        "subject_type": export.subject_type,
        "subject_id": export.subject_id,
    }
    if export.subject_type == "patient":
        patient = Patient.objects.filter(
            organization=org, id=export.subject_id
        ).first()
        if patient:
            payload["patient"] = {
                "id": patient.id,
                "given_name": patient.given_name,
                "family_name": patient.family_name,
                "date_of_birth": patient.date_of_birth.isoformat()
                if patient.date_of_birth
                else None,
                "nhs_number": patient.nhs_number,
                "phone": patient.phone,
                "email": patient.email,
                "address": {
                    "line1": patient.address_line1,
                    "line2": patient.address_line2,
                    "city": patient.city,
                    "region": patient.region,
                    "postal_code": patient.postal_code,
                    "country": patient.country,
                },
            }
            episodes = Episode.objects.filter(organization=org, patient=patient)
            payload["episodes"] = [
                {
                    "id": episode.id,
                    "title": episode.title,
                    "status": episode.status,
                    "created_at": episode.created_at.isoformat(),
                    "updated_at": episode.updated_at.isoformat(),
                }
                for episode in episodes
            ]
            evidence = EvidenceItem.objects.filter(organization=org, patient=patient)
            payload["evidence"] = [
                {
                    "id": item.id,
                    "title": item.title,
                    "kind": item.kind,
                    "file_name": item.file_name,
                    "created_at": item.created_at.isoformat(),
                    "retention_class": item.retention_class,
                    "retention_until": item.retention_until.isoformat()
                    if item.retention_until
                    else None,
                }
                for item in evidence
            ]
            consents = ConsentRecord.objects.filter(
                organization=org, subject_type="patient", subject_id=str(patient.id)
            )
            payload["consents"] = [_consent_payload(record) for record in consents]
    export_dir = Path(settings.EXPORT_STORAGE_DIR).resolve()
    export_dir.mkdir(parents=True, exist_ok=True)
    filename = f"dsar_{export.subject_type}_{export.subject_id}_{export.id}.json"
    path = export_dir / filename
    path.write_text(json.dumps(payload, indent=2))
    return str(path)


def purge_retention(now=None) -> dict:
    timestamp = now or timezone.now().date()
    results = {"evidence_deleted": 0, "patients_anonymized": 0, "episodes_anonymized": 0}
    evidence = EvidenceItem.objects.filter(retention_until__lte=timestamp).exclude(
        retention_until__isnull=True
    )
    for item in evidence:
        path = Path(item.storage_path)
        if path.exists():
            path.unlink()
        AuditEvent.objects.create(
            organization=item.organization,
            actor=None,
            action="privacy.evidence.purged",
            target_type="EvidenceItem",
            target_id=str(item.id),
        )
        item.delete()
        results["evidence_deleted"] += 1
    patients = Patient.objects.filter(retention_until__lte=timestamp).exclude(
        retention_until__isnull=True
    )
    for patient in patients:
        _anonymize_patient(patient, actor=None)
        patient.retention_class = "purged"
        patient.retention_until = None
        patient.save(update_fields=["retention_class", "retention_until", "updated_at"])
        results["patients_anonymized"] += 1
    episodes = Episode.objects.filter(retention_until__lte=timestamp).exclude(
        retention_until__isnull=True
    )
    for episode in episodes:
        episode.title = "Redacted episode"
        episode.description = ""
        episode.patient = None
        episode.retention_class = "purged"
        episode.retention_until = None
        episode.save(
            update_fields=[
                "title",
                "description",
                "patient",
                "retention_class",
                "retention_until",
                "updated_at",
            ]
        )
        AuditEvent.objects.create(
            organization=episode.organization,
            actor=None,
            action="privacy.episode.purged",
            target_type="Episode",
            target_id=str(episode.id),
        )
        results["episodes_anonymized"] += 1
    return results
