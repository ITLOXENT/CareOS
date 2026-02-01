from __future__ import annotations

import json

from django.http import JsonResponse
from django.utils import timezone

from ..billing import check_ai_review_quota
from ..models import AIReviewItem, AIReviewRequest, AuditEvent
from ..rbac import Role, has_permission
from ..tasks import process_ai_review_request


def ai_review_collection(request):
    if request.method == "GET":
        return ai_review_list(request)
    return ai_review_create(request)


def ai_review_create(request):
    membership = request.membership  # type: ignore[attr-defined]
    permission = has_permission(membership.role, "ai:write")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    payload = json.loads(request.body or "{}")
    input_type = str(payload.get("input_type", "")).strip()
    if not input_type:
        return JsonResponse({"detail": "input_type required"}, status=400)
    allowed, usage = check_ai_review_quota(membership.organization)
    if not allowed:
        return JsonResponse(
            {
                "detail": "AI review quota exceeded.",
                "code": "billing.ai_review_quota",
                "limit": usage.get("limit"),
                "used": usage.get("used"),
            },
            status=402,
        )
    review = AIReviewRequest.objects.create(
        organization=membership.organization,
        input_type=input_type,
        payload=payload.get("payload", {}),
        status="pending",
        created_by=request.user,
    )
    AuditEvent.objects.create(
        organization=membership.organization,
        actor=request.user,
        action="ai.review.created",
        target_type="AIReviewRequest",
        target_id=str(review.id),
    )
    process_ai_review_request.delay(review.id)
    return JsonResponse(
        {
            "id": review.id,
            "status": review.status,
            "input_type": review.input_type,
            "created_at": review.created_at.isoformat(),
        },
        status=201,
    )


def ai_review_list(request):
    membership = request.membership  # type: ignore[attr-defined]
    permission = has_permission(membership.role, "ai:review")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    reviews = AIReviewRequest.objects.filter(
        organization=membership.organization
    ).order_by("-created_at")[:50]
    payload = [
        {
            "id": review.id,
            "input_type": review.input_type,
            "status": review.status,
            "output": review.output,
            "model_provider": review.model_provider,
            "model_name": review.model_name,
            "model_version": review.model_version,
            "created_at": review.created_at.isoformat(),
        }
        for review in reviews
    ]
    return JsonResponse({"results": payload})


def ai_review_detail(request, review_id: int):
    membership = request.membership  # type: ignore[attr-defined]
    permission = has_permission(membership.role, "ai:review")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    review = AIReviewRequest.objects.filter(
        organization=membership.organization, id=review_id
    ).first()
    if not review:
        return JsonResponse({"detail": "Not found."}, status=404)
    return JsonResponse(
        {
            "id": review.id,
            "input_type": review.input_type,
            "payload": review.payload,
            "status": review.status,
            "output": review.output,
            "model_provider": review.model_provider,
            "model_name": review.model_name,
            "model_version": review.model_version,
            "error": review.error,
            "created_at": review.created_at.isoformat(),
        }
    )


def ai_review_items_list(request):
    membership = request.membership  # type: ignore[attr-defined]
    permission = has_permission(membership.role, "ai:review")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    items = AIReviewItem.objects.filter(organization=membership.organization).order_by(
        "-created_at"
    )
    status_filter = request.GET.get("status")
    if status_filter:
        items = items.filter(status=status_filter)
    elif request.GET.get("pending_only") in {"1", "true", "True", None, ""}:
        items = items.filter(status="pending")
    payload = [
        {
            "id": item.id,
            "episode_id": item.episode_id,
            "kind": item.kind,
            "payload_json": item.payload_json,
            "status": item.status,
            "decided_at": item.decided_at.isoformat() if item.decided_at else None,
            "decided_by": item.decided_by_id,
            "decision_note": item.decision_note,
            "created_at": item.created_at.isoformat(),
        }
        for item in items
    ]
    return JsonResponse({"results": payload})


def ai_review_item_decide(request, item_id: int):
    membership = request.membership  # type: ignore[attr-defined]
    permission = has_permission(membership.role, "ai:review")
    if not permission.allowed or membership.role != Role.ADMIN:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    item = AIReviewItem.objects.filter(
        organization=membership.organization, id=item_id
    ).first()
    if not item:
        return JsonResponse({"detail": "Not found."}, status=404)
    if item.status != "pending":
        return JsonResponse({"detail": "Already decided."}, status=400)
    payload = json.loads(request.body or "{}")
    decision = str(payload.get("decision", "")).strip().lower()
    note = str(payload.get("note", "")).strip()
    if decision not in {"approved", "rejected"}:
        return JsonResponse(
            {"detail": "decision must be approved or rejected"}, status=400
        )
    item.status = decision
    item.decided_at = timezone.now()
    item.decided_by = request.user
    item.decision_note = note
    item.save(update_fields=["status", "decided_at", "decided_by", "decision_note"])
    AuditEvent.objects.create(
        organization=membership.organization,
        actor=request.user,
        action="ai_review_item.decided",
        target_type="AIReviewItem",
        target_id=str(item.id),
        metadata={"decision": decision},
    )
    return JsonResponse(
        {"id": item.id, "status": item.status, "decision_note": item.decision_note}
    )
