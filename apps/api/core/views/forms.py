from __future__ import annotations

import json

from django.http import JsonResponse

from ..models import Episode, EpisodeEvent, FormResponse, FormTemplate, Signature
from ..rbac import has_permission


def form_templates(request):
    templates = FormTemplate.objects.filter(active=True).order_by("name", "-version")
    payload = [
        {
            "id": template.id,
            "name": template.name,
            "version": template.version,
            "schema": template.schema,
        }
        for template in templates
    ]
    return JsonResponse({"results": payload})


def form_responses(request):
    membership = request.membership  # type: ignore[attr-defined]
    permission = has_permission(membership.role, "episode:write")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    payload = json.loads(request.body or "{}")
    episode_id = payload.get("episode_id")
    template_id = payload.get("template_id")
    data = payload.get("data", {})
    if not episode_id or not template_id:
        return JsonResponse({"detail": "episode_id and template_id required"}, status=400)
    episode = Episode.objects.filter(
        organization=membership.organization, id=episode_id
    ).first()
    if not episode:
        return JsonResponse({"detail": "Episode not found"}, status=404)
    template = FormTemplate.objects.filter(id=template_id, active=True).first()
    if not template:
        return JsonResponse({"detail": "Template not found"}, status=404)
    required = template.schema.get("required", [])
    missing = [field for field in required if field not in data]
    response = FormResponse.objects.create(
        organization=membership.organization,
        episode=episode,
        template=template,
        data=data,
        validated=not missing,
        validation_errors=missing,
        created_by=request.user,
    )
    EpisodeEvent.objects.create(
        organization=membership.organization,
        episode=episode,
        created_by=request.user,
        event_type="form.response",
        from_state="",
        to_state=episode.status,
        note=f"response:{response.id}",
        payload_json={"response_id": response.id, "validated": response.validated},
    )
    return JsonResponse(
        {
            "id": response.id,
            "validated": response.validated,
            "validation_errors": response.validation_errors,
        },
        status=201,
    )


def form_response_sign(request, response_id: int):
    membership = request.membership  # type: ignore[attr-defined]
    permission = has_permission(membership.role, "episode:write")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    response = FormResponse.objects.filter(
        organization=membership.organization, id=response_id
    ).first()
    if not response:
        return JsonResponse({"detail": "Response not found"}, status=404)
    signature = Signature.objects.create(
        response=response,
        signer=request.user,
        template_version=response.template.version,
    )
    EpisodeEvent.objects.create(
        organization=membership.organization,
        episode=response.episode,
        created_by=request.user,
        event_type="form.signed",
        from_state="",
        to_state=response.episode.status,
        note=f"signature:{signature.id}",
        payload_json={"signature_id": signature.id},
    )
    return JsonResponse(
        {"id": signature.id, "signed_at": signature.signed_at.isoformat()}
    )
