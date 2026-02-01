from __future__ import annotations

from django.http import HttpResponse, JsonResponse

from ..evidence import build_manifest, build_pdf, verify_hash_chain
from ..models import AIArtifact, Episode, EpisodeEvent, EvidencePack, Signature
from ..rbac import has_permission


def evidence_pack_generate(request, episode_id: int):
    membership = request.membership  # type: ignore[attr-defined]
    permission = has_permission(membership.role, "episode:write")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    episode = Episode.objects.filter(
        organization=membership.organization, id=episode_id
    ).first()
    if not episode:
        return JsonResponse({"detail": "Episode not found"}, status=404)
    unapproved = AIArtifact.objects.filter(
        organization=membership.organization, episode=episode
    ).exclude(status="approved")
    if unapproved.exists():
        return JsonResponse(
            {"detail": "AI artifacts must be approved before export."}, status=400
        )
    events = EpisodeEvent.objects.filter(
        organization=membership.organization, episode=episode
    ).order_by("created_at", "id")
    signatures = Signature.objects.filter(response__episode=episode).order_by(
        "signed_at"
    )
    manifest = build_manifest(events, signatures)
    if not verify_hash_chain(manifest["events"]):
        return JsonResponse({"detail": "Hash chain invalid"}, status=400)
    pdf = build_pdf(
        [
            "CareOS Evidence Pack",
            f"Episode: {episode.id}",
            f"Events: {len(manifest['events'])}",
            f"Signatures: {len(manifest['signatures'])}",
            f"Final hash: {manifest['final_hash']}",
        ]
    )
    pack = EvidencePack.objects.create(
        organization=membership.organization,
        episode=episode,
        manifest=manifest,
        pdf_bytes=pdf,
    )
    EpisodeEvent.objects.create(
        organization=membership.organization,
        episode=episode,
        created_by=request.user,
        event_type="evidence_pack.generated",
        from_state="",
        to_state=episode.status,
        note=f"evidence_pack:{pack.id}",
        payload_json={"evidence_pack_id": pack.id},
    )
    return JsonResponse({"id": pack.id})


def evidence_pack_detail(request, pack_id: int):
    membership = request.membership  # type: ignore[attr-defined]
    permission = has_permission(membership.role, "episode:read")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    pack = EvidencePack.objects.filter(
        organization=membership.organization, id=pack_id
    ).first()
    if not pack:
        return JsonResponse({"detail": "Not found"}, status=404)
    if request.GET.get("format") == "pdf":
        response = HttpResponse(pack.pdf_bytes, content_type="application/pdf")
        response[
            "Content-Disposition"
        ] = f"attachment; filename=evidence-pack-{pack.id}.pdf"
        return response
    return JsonResponse({"id": pack.id, "manifest": pack.manifest})
