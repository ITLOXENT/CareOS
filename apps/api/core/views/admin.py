from __future__ import annotations

import json
from pathlib import Path

import stripe
from django.conf import settings
from django.http import FileResponse, JsonResponse
from django.utils import timezone

from ..billing import (
    create_checkout_session,
    entitlements_for_org,
    get_plans,
    resolve_plan_code,
    upsert_subscription_from_stripe,
)
from ..exports import export_audit_events_csv, export_episodes_csv
from ..models import AuditEvent, ExportJob, OrganizationSubscription
from ..rbac import Role, has_permission


def billing_plans(request):
    membership = request.membership  # type: ignore[attr-defined]
    permission = has_permission(membership.role, "org:manage")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    currency = request.GET.get("currency")
    payload = [
        {
            "code": plan.get("code"),
            "name": plan.get("name"),
            "seats": plan.get("seats", 0),
            "currency": plan.get("currency"),
            "entitlements": plan.get("entitlements", {}),
        }
        for plan in get_plans(currency=currency)
    ]
    return JsonResponse({"results": payload})


def billing_checkout_session(request):
    membership = request.membership  # type: ignore[attr-defined]
    permission = has_permission(membership.role, "org:manage")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    payload = json.loads(request.body or "{}")
    plan_code = str(payload.get("plan_code", "")).strip()
    success_url = str(payload.get("success_url", "")).strip()
    cancel_url = str(payload.get("cancel_url", "")).strip()
    currency = str(payload.get("currency", "")).strip() or None
    if not plan_code or not success_url or not cancel_url:
        return JsonResponse(
            {"detail": "plan_code, success_url, cancel_url required"}, status=400
        )
    try:
        session = create_checkout_session(
            membership.organization, plan_code, success_url, cancel_url, currency=currency
        )
    except ValueError:
        return JsonResponse({"detail": "Invalid plan_code"}, status=400)
    except RuntimeError as exc:
        return JsonResponse({"detail": str(exc)}, status=400)
    return JsonResponse({"id": session["id"], "url": session["url"]})


def billing_subscription(request):
    membership = request.membership  # type: ignore[attr-defined]
    permission = has_permission(membership.role, "org:manage")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    subscription = OrganizationSubscription.objects.filter(
        organization=membership.organization
    ).first()
    entitlements = entitlements_for_org(membership.organization)
    currency = getattr(settings, "BILLING_DEFAULT_CURRENCY", "GBP")
    if not subscription:
        return JsonResponse(
            {
                "status": "inactive",
                "plan_code": resolve_plan_code(None),
                "seat_limit": entitlements.get("max_users", 0) or 0,
                "entitlements": entitlements,
                "currency": currency,
                "current_period_end": None,
            }
        )
    return JsonResponse(
        {
            "plan_code": subscription.plan_code,
            "status": subscription.status,
            "current_period_end": subscription.current_period_end.isoformat()
            if subscription.current_period_end
            else None,
            "seat_limit": subscription.seat_limit,
            "entitlements": entitlements,
            "currency": currency,
        }
    )


def billing_webhook(request):
    secret = settings.STRIPE_WEBHOOK_SECRET
    if not secret:
        return JsonResponse({"detail": "Webhook secret not configured"}, status=400)
    if settings.STRIPE_SECRET_KEY:
        stripe.api_key = settings.STRIPE_SECRET_KEY
    payload = request.body
    signature = request.headers.get("Stripe-Signature", "")
    try:
        event = stripe.Webhook.construct_event(payload, signature, secret)
    except Exception:
        return JsonResponse({"detail": "Invalid signature"}, status=400)

    event_type = event.get("type", "")
    data_object = event.get("data", {}).get("object", {})
    updated = None
    if event_type in {
        "customer.subscription.updated",
        "customer.subscription.deleted",
        "invoice.paid",
        "invoice.payment_failed",
    }:
        if event_type.startswith("invoice."):
            subscription = data_object.get("subscription")
            if subscription:
                data_object = stripe.Subscription.retrieve(subscription)
        updated = upsert_subscription_from_stripe(data_object)
    if updated:
        AuditEvent.objects.create(
            organization=updated.organization,
            actor=None,
            action="billing.subscription.updated",
            target_type="OrganizationSubscription",
            target_id=str(updated.id),
            metadata={"status": updated.status, "plan_code": updated.plan_code},
        )
    return JsonResponse({"status": "ok"})


def exports_list(request):
    membership = request.membership  # type: ignore[attr-defined]
    if membership.role != Role.ADMIN:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    if request.method == "POST":
        payload = json.loads(request.body or "{}")
        kind = str(payload.get("kind", "")).strip()
        last_days = int(payload.get("last_days", 7))
        if kind in {"audit", "audit-events"}:
            kind = "audit_events"
        if kind not in {"episodes", "audit_events"}:
            return JsonResponse(
                {"detail": "kind must be episodes or audit_events"}, status=400
            )
        job = ExportJob.objects.create(
            organization=membership.organization,
            requested_by=request.user,
            kind=kind,
            params_json={"last_days": last_days},
            status="running",
        )
        AuditEvent.objects.create(
            organization=membership.organization,
            actor=request.user,
            action="export.requested",
            target_type="ExportJob",
            target_id=str(job.id),
            metadata={"kind": kind, "last_days": last_days},
        )
        try:
            filename = f"export_{job.id}_{kind}.csv"
            if kind == "episodes":
                artifact_path = export_episodes_csv(
                    organization=membership.organization,
                    days=last_days,
                    filename=filename,
                )
            else:
                artifact_path = export_audit_events_csv(
                    organization=membership.organization,
                    days=last_days,
                    filename=filename,
                )
            job.status = "done"
            job.finished_at = timezone.now()
            job.artifact_path = artifact_path
            job.save(update_fields=["status", "finished_at", "artifact_path"])
        except Exception:
            job.status = "failed"
            job.finished_at = timezone.now()
            job.save(update_fields=["status", "finished_at"])
            return JsonResponse({"detail": "Export failed."}, status=500)
        return JsonResponse(_export_job_payload(job), status=201)

    jobs = ExportJob.objects.filter(organization=membership.organization).order_by(
        "-created_at"
    )
    return JsonResponse({"results": [_export_job_payload(job) for job in jobs]})


def export_detail(request, export_id: int):
    membership = request.membership  # type: ignore[attr-defined]
    if membership.role != Role.ADMIN:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    job = ExportJob.objects.filter(
        organization=membership.organization, id=export_id
    ).first()
    if not job:
        return JsonResponse({"detail": "Not found."}, status=404)
    return JsonResponse(_export_job_payload(job))


def export_download(request, export_id: int):
    membership = request.membership  # type: ignore[attr-defined]
    if membership.role != Role.ADMIN:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    job = ExportJob.objects.filter(
        organization=membership.organization, id=export_id
    ).first()
    if not job or job.status != "done" or not job.artifact_path:
        return JsonResponse({"detail": "Not found."}, status=404)
    base_dir = Path(settings.EXPORT_STORAGE_DIR).resolve()
    path = Path(job.artifact_path).resolve()
    if base_dir not in path.parents and path != base_dir:
        return JsonResponse({"detail": "Not found."}, status=404)
    if not path.exists():
        return JsonResponse({"detail": "Not found."}, status=404)
    AuditEvent.objects.create(
        organization=membership.organization,
        actor=request.user,
        action="export.downloaded",
        target_type="ExportJob",
        target_id=str(job.id),
        metadata={"kind": job.kind},
    )
    return FileResponse(path.open("rb"), as_attachment=True, filename=path.name)


def _export_job_payload(job: ExportJob) -> dict:
    return {
        "id": job.id,
        "kind": job.kind,
        "status": job.status,
        "params": job.params_json,
        "created_at": job.created_at.isoformat(),
        "finished_at": job.finished_at.isoformat() if job.finished_at else None,
        "artifact_path": job.artifact_path,
    }
