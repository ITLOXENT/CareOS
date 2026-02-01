from __future__ import annotations

import json
from pathlib import Path

from django.conf import settings
from django.http import FileResponse, JsonResponse

from ..billing import check_evidence_storage_limit
from ..models import (
    AuditEvent,
    Episode,
    EpisodeEvidence,
    EvidenceEvent,
    EvidenceItem,
    Patient,
)
from ..rbac import has_permission
from ..storage import EvidenceStorage
from .utils import parse_date, parse_tags


def _evidence_payload(item: EvidenceItem) -> dict:
    return {
        "id": item.id,
        "title": item.title,
        "kind": item.kind,
        "episode_id": item.episode_id,
        "patient_id": item.patient_id,
        "file_name": item.file_name,
        "content_type": item.content_type,
        "size_bytes": item.size_bytes,
        "storage_key": item.storage_key,
        "sha256": item.sha256,
        "tags": item.tags,
        "retention_class": item.retention_class,
        "retention_until": item.retention_until.isoformat()
        if item.retention_until
        else None,
        "created_at": item.created_at.isoformat(),
    }


def _evidence_file_response(request, item: EvidenceItem):
    base_dir = Path(settings.EVIDENCE_STORAGE_DIR).resolve()
    path = Path(item.storage_path).resolve()
    if base_dir not in path.parents and path != base_dir:
        return JsonResponse({"detail": "Not found."}, status=404)
    if not path.exists():
        return JsonResponse({"detail": "Not found."}, status=404)
    membership = request.membership  # type: ignore[attr-defined]
    AuditEvent.objects.create(
        organization=membership.organization,
        actor=request.user,
        action="evidence.downloaded",
        target_type="EvidenceItem",
        target_id=str(item.id),
    )
    return FileResponse(
        path.open("rb"),
        as_attachment=True,
        filename=item.file_name,
        content_type=item.content_type or None,
    )


def _create_evidence_from_request(request, episode: Episode | None) -> EvidenceItem | JsonResponse:
    membership = request.membership  # type: ignore[attr-defined]
    upload = request.FILES.get("file")
    if not upload:
        return JsonResponse({"detail": "file is required"}, status=400)
    title = str(request.POST.get("title", "")).strip() or upload.name
    kind = str(request.POST.get("kind", "")).strip()
    if not kind:
        return JsonResponse({"detail": "kind is required"}, status=400)
    patient = None
    if request.POST.get("patient_id"):
        patient = Patient.objects.filter(
            organization=membership.organization, id=request.POST.get("patient_id")
        ).first()
        if not patient:
            return JsonResponse({"detail": "patient not found"}, status=404)
    if episode is None and request.POST.get("episode_id"):
        episode = Episode.objects.filter(
            organization=membership.organization, id=request.POST.get("episode_id")
        ).first()
        if not episode:
            return JsonResponse({"detail": "episode not found"}, status=404)
    retention_class = str(request.POST.get("retention_class", "")).strip()
    retention_until_raw = request.POST.get("retention_until")
    retention_until = parse_date(retention_until_raw)
    if retention_until_raw and retention_until is None:
        return JsonResponse({"detail": "retention_until must be ISO date"}, status=400)
    additional_bytes = int(getattr(upload, "size", 0) or 0)
    allowed, usage = check_evidence_storage_limit(
        membership.organization, additional_bytes
    )
    if not allowed:
        return JsonResponse(
            {
                "detail": "Evidence storage limit exceeded.",
                "code": "billing.evidence_storage_limit",
                "limit_bytes": usage.get("limit_bytes"),
                "used_bytes": usage.get("used_bytes"),
            },
            status=402,
        )
    storage = EvidenceStorage()
    storage_key, sha256, size = storage.save(upload)
    storage_path = str(storage.base_dir / storage_key)
    tags = parse_tags(request.POST.get("tags"))
    evidence = EvidenceItem.objects.create(
        organization=membership.organization,
        episode=episode,
        patient=patient,
        title=title,
        kind=kind,
        file_name=upload.name,
        content_type=str(getattr(upload, "content_type", "")),
        size_bytes=size,
        storage_path=storage_path,
        storage_key=storage_key,
        sha256=sha256,
        tags=tags,
        retention_class=retention_class,
        retention_until=retention_until,
        created_by=request.user,
        uploaded_by=request.user,
    )
    if episode:
        EpisodeEvidence.objects.get_or_create(
            organization=membership.organization,
            episode=episode,
            evidence=evidence,
            defaults={"added_by": request.user},
        )
    EvidenceEvent.objects.create(
        organization=membership.organization,
        evidence=evidence,
        event_type="evidence.created",
        payload_json={
            "tags": tags,
            "episode_id": evidence.episode_id,
            "patient_id": evidence.patient_id,
        },
        created_by=request.user,
    )
    AuditEvent.objects.create(
        organization=membership.organization,
        actor=request.user,
        action="evidence.created",
        target_type="EvidenceItem",
        target_id=str(evidence.id),
    )
    return evidence


def evidence_list(request):
    membership = request.membership  # type: ignore[attr-defined]
    if request.method == "POST":
        permission = has_permission(membership.role, "evidence:write")
        if not permission.allowed:
            return JsonResponse({"detail": "Not authorized."}, status=403)
        created = _create_evidence_from_request(request, episode=None)
        if isinstance(created, JsonResponse):
            return created
        return JsonResponse(_evidence_payload(created), status=201)

    permission = has_permission(membership.role, "evidence:read")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    items = EvidenceItem.objects.filter(organization=membership.organization)
    episode_filter = request.GET.get("episode")
    if episode_filter:
        items = items.filter(episode_id=episode_filter)
    patient_filter = request.GET.get("patient")
    if patient_filter:
        items = items.filter(patient_id=patient_filter)
    kind_filter = request.GET.get("kind")
    if kind_filter:
        items = items.filter(kind=kind_filter)
    tags_filter = parse_tags(request.GET.get("tags"))
    if tags_filter:
        items = items.filter(tags__contains=tags_filter)
    items = items.order_by("-created_at")
    try:
        page = max(int(request.GET.get("page", "1")), 1)
    except ValueError:
        page = 1
    try:
        page_size = min(max(int(request.GET.get("page_size", "50")), 1), 200)
    except ValueError:
        page_size = 50
    total = items.count()
    start_index = (page - 1) * page_size
    page_items = items[start_index : start_index + page_size]
    payload = [_evidence_payload(item) for item in page_items]
    return JsonResponse(
        {"results": payload, "count": total, "page": page, "page_size": page_size}
    )


def evidence_detail(request, evidence_id: int):
    membership = request.membership  # type: ignore[attr-defined]
    permission = has_permission(membership.role, "evidence:read")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    item = EvidenceItem.objects.filter(
        organization=membership.organization, id=evidence_id
    ).first()
    if not item:
        return JsonResponse({"detail": "Not found."}, status=404)
    if request.GET.get("download") in {"1", "true", "True"} or request.GET.get(
        "format"
    ) in {"file", "download"}:
        return _evidence_file_response(request, item)
    return JsonResponse(_evidence_payload(item))


def evidence_events(request, evidence_id: int):
    membership = request.membership  # type: ignore[attr-defined]
    permission = has_permission(membership.role, "evidence:read")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    item = EvidenceItem.objects.filter(
        organization=membership.organization, id=evidence_id
    ).first()
    if not item:
        return JsonResponse({"detail": "Not found."}, status=404)
    events = EvidenceEvent.objects.filter(
        organization=membership.organization, evidence=item
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
            "payload_json": event.payload_json,
            "created_by": event.created_by_id,
            "created_at": event.created_at.isoformat(),
        }
        for event in events
    ]
    return JsonResponse(
        {"results": payload, "count": total, "page": page, "page_size": page_size}
    )


def evidence_link(request, evidence_id: int):
    membership = request.membership  # type: ignore[attr-defined]
    permission = has_permission(membership.role, "evidence:link")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    item = EvidenceItem.objects.filter(
        organization=membership.organization, id=evidence_id
    ).first()
    if not item:
        return JsonResponse({"detail": "Not found."}, status=404)
    payload = json.loads(request.body or "{}")
    episode = None
    if payload.get("episode_id"):
        episode = Episode.objects.filter(
            organization=membership.organization, id=payload.get("episode_id")
        ).first()
        if not episode:
            return JsonResponse({"detail": "episode not found"}, status=404)
    patient = None
    if payload.get("patient_id"):
        patient = Patient.objects.filter(
            organization=membership.organization, id=payload.get("patient_id")
        ).first()
        if not patient:
            return JsonResponse({"detail": "patient not found"}, status=404)
    item.episode = episode
    item.patient = patient
    item.save(update_fields=["episode", "patient"])
    if episode:
        EpisodeEvidence.objects.get_or_create(
            organization=membership.organization,
            episode=episode,
            evidence=item,
            defaults={"added_by": request.user},
        )
    EvidenceEvent.objects.create(
        organization=membership.organization,
        evidence=item,
        event_type="evidence.linked",
        payload_json={"episode_id": item.episode_id, "patient_id": item.patient_id},
        created_by=request.user,
    )
    AuditEvent.objects.create(
        organization=membership.organization,
        actor=request.user,
        action="evidence.linked",
        target_type="EvidenceItem",
        target_id=str(item.id),
        metadata={"episode_id": item.episode_id, "patient_id": item.patient_id},
    )
    return JsonResponse(
        {"id": item.id, "episode_id": item.episode_id, "patient_id": item.patient_id}
    )


def episode_evidence_collection(request, episode_id: int):
    membership = request.membership  # type: ignore[attr-defined]
    episode = Episode.objects.filter(
        organization=membership.organization, id=episode_id
    ).first()
    if not episode:
        return JsonResponse({"detail": "Not found."}, status=404)
    if request.method == "POST":
        permission = has_permission(membership.role, "evidence:write")
        if not permission.allowed:
            return JsonResponse({"detail": "Not authorized."}, status=403)
        created = _create_evidence_from_request(request, episode=episode)
        if isinstance(created, JsonResponse):
            return created
        return JsonResponse(_evidence_payload(created), status=201)

    permission = has_permission(membership.role, "evidence:read")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    links = EpisodeEvidence.objects.filter(
        organization=membership.organization, episode=episode
    ).select_related("evidence")
    payload = [_evidence_payload(link.evidence) for link in links.order_by("-created_at")]
    return JsonResponse({"results": payload})


def episode_evidence_link(request, episode_id: int, evidence_id: int):
    membership = request.membership  # type: ignore[attr-defined]
    permission = has_permission(membership.role, "evidence:link")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    episode = Episode.objects.filter(
        organization=membership.organization, id=episode_id
    ).first()
    if not episode:
        return JsonResponse({"detail": "Episode not found."}, status=404)
    evidence = EvidenceItem.objects.filter(
        organization=membership.organization, id=evidence_id
    ).first()
    if not evidence:
        return JsonResponse({"detail": "Evidence not found."}, status=404)
    EpisodeEvidence.objects.get_or_create(
        organization=membership.organization,
        episode=episode,
        evidence=evidence,
        defaults={"added_by": request.user},
    )
    if evidence.episode_id != episode.id:
        evidence.episode = episode
        evidence.save(update_fields=["episode"])
    EvidenceEvent.objects.create(
        organization=membership.organization,
        evidence=evidence,
        event_type="evidence.linked",
        payload_json={"episode_id": episode.id},
        created_by=request.user,
    )
    AuditEvent.objects.create(
        organization=membership.organization,
        actor=request.user,
        action="evidence.linked",
        target_type="EvidenceItem",
        target_id=str(evidence.id),
        metadata={"episode_id": episode.id},
    )
    return JsonResponse({"id": evidence.id, "episode_id": episode.id})


def evidence_tag(request, evidence_id: int):
    membership = request.membership  # type: ignore[attr-defined]
    permission = has_permission(membership.role, "evidence:tag")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    item = EvidenceItem.objects.filter(
        organization=membership.organization, id=evidence_id
    ).first()
    if not item:
        return JsonResponse({"detail": "Not found."}, status=404)
    payload = json.loads(request.body or "{}")
    tags = parse_tags(payload.get("tags"))
    if not tags:
        return JsonResponse({"detail": "tags are required"}, status=400)
    existing = set(item.tags or [])
    updated = sorted(existing.union(tags))
    item.tags = updated
    item.save(update_fields=["tags"])
    EvidenceEvent.objects.create(
        organization=membership.organization,
        evidence=item,
        event_type="evidence.tagged",
        payload_json={"tags": tags},
        created_by=request.user,
    )
    AuditEvent.objects.create(
        organization=membership.organization,
        actor=request.user,
        action="evidence.tagged",
        target_type="EvidenceItem",
        target_id=str(item.id),
        metadata={"tags": tags},
    )
    return JsonResponse({"id": item.id, "tags": item.tags})
