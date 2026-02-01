from __future__ import annotations

import json

from django.http import JsonResponse
from django.utils import timezone

from ..ai import build_ai_content, redact_prompt
from ..models import AIArtifact, AuditEvent, Episode, EpisodeEvent
from ..rbac import has_permission


def ai_list(request):
    membership = request.membership  # type: ignore[attr-defined]
    permission = has_permission(membership.role, "ai:review")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    status_filter = request.GET.get("status", "pending")
    artifacts = AIArtifact.objects.filter(
        organization=membership.organization, status=status_filter
    ).order_by("-created_at")
    payload = [
        {
            "id": artifact.id,
            "episode_id": artifact.episode_id,
            "artifact_type": artifact.artifact_type,
            "confidence": artifact.confidence,
            "status": artifact.status,
            "policy_version": artifact.policy_version,
            "created_at": artifact.created_at.isoformat(),
        }
        for artifact in artifacts
    ]
    return JsonResponse({"results": payload})


def ai_create_artifact(request, artifact_type: str):
    membership = request.membership  # type: ignore[attr-defined]
    permission = has_permission(membership.role, "ai:write")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    payload = json.loads(request.body or "{}")
    episode_id = payload.get("episode_id")
    if not episode_id:
        return JsonResponse({"detail": "episode_id required"}, status=400)
    episode = Episode.objects.filter(
        organization=membership.organization, id=episode_id
    ).first()
    if not episode:
        return JsonResponse({"detail": "Episode not found"}, status=404)
    artifact = AIArtifact.objects.create(
        organization=membership.organization,
        episode=episode,
        artifact_type=artifact_type,
        version=1,
        confidence=float(payload.get("confidence", 0.5)),
        policy_version=str(payload.get("policy_version", "v1")),
        status="pending",
        content=build_ai_content(artifact_type, payload),
        prompt_redacted=redact_prompt(payload),
        created_by=request.user,
    )
    EpisodeEvent.objects.create(
        organization=membership.organization,
        episode=episode,
        created_by=request.user,
        event_type=f"ai.{artifact_type}.created",
        from_state="",
        to_state=episode.status,
        note=f"artifact:{artifact.id}",
        payload_json={"artifact_id": artifact.id, "artifact_type": artifact_type},
    )
    return JsonResponse({"id": artifact.id, "status": artifact.status}, status=201)


def ai_triage_suggest(request):
    return ai_create_artifact(request, "triage")


def ai_note_draft(request):
    return ai_create_artifact(request, "note")


def ai_completeness_check(request):
    return ai_create_artifact(request, "completeness")


def ai_approve(request, artifact_id: int):
    membership = request.membership  # type: ignore[attr-defined]
    permission = has_permission(membership.role, "ai:review")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    artifact = AIArtifact.objects.filter(
        organization=membership.organization, id=artifact_id
    ).first()
    if not artifact:
        return JsonResponse({"detail": "Not found"}, status=404)
    artifact.status = "approved"
    artifact.approved_by = request.user
    artifact.approved_at = timezone.now()
    artifact.rejected_by = None
    artifact.rejected_at = None
    artifact.rejection_reason = ""
    artifact.save(
        update_fields=[
            "status",
            "approved_by",
            "approved_at",
            "rejected_by",
            "rejected_at",
            "rejection_reason",
        ]
    )
    AuditEvent.objects.create(
        organization=membership.organization,
        actor=request.user,
        action="ai.approved",
        target_type="AIArtifact",
        target_id=str(artifact.id),
    )
    return JsonResponse({"id": artifact.id, "status": artifact.status})


def ai_reject(request, artifact_id: int):
    membership = request.membership  # type: ignore[attr-defined]
    permission = has_permission(membership.role, "ai:review")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    artifact = AIArtifact.objects.filter(
        organization=membership.organization, id=artifact_id
    ).first()
    if not artifact:
        return JsonResponse({"detail": "Not found"}, status=404)
    payload = json.loads(request.body or "{}")
    reason = str(payload.get("reason", "")).strip()
    artifact.status = "rejected"
    artifact.rejected_by = request.user
    artifact.rejected_at = timezone.now()
    artifact.rejection_reason = reason
    artifact.approved_by = None
    artifact.approved_at = None
    artifact.save(
        update_fields=[
            "status",
            "rejected_by",
            "rejected_at",
            "rejection_reason",
            "approved_by",
            "approved_at",
        ]
    )
    AuditEvent.objects.create(
        organization=membership.organization,
        actor=request.user,
        action="ai.rejected",
        target_type="AIArtifact",
        target_id=str(artifact.id),
        metadata={"reason": reason},
    )
    return JsonResponse({"id": artifact.id, "status": artifact.status})
