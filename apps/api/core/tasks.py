from __future__ import annotations

from celery import shared_task

from .ai_review import run_review
from .models import AIReviewRequest, AuditEvent
from .notifications import check_sla_notifications
from .compliance import run_due_report_jobs
from .views.privacy import purge_retention


@shared_task
def check_sla_notifications_task() -> int:
    return check_sla_notifications()


@shared_task
def process_ai_review_request(request_id: int) -> None:
    review = AIReviewRequest.objects.filter(id=request_id).select_related(
        "organization"
    ).first()
    if not review:
        return
    review.status = "processing"
    review.save(update_fields=["status"])
    try:
        result = run_review(review.input_type, review.payload or {})
        review.status = "completed"
        review.output = result.output
        review.model_provider = result.model_provider
        review.model_name = result.model_name
        review.model_version = result.model_version
        review.error = ""
        review.save(
            update_fields=[
                "status",
                "output",
                "model_provider",
                "model_name",
                "model_version",
                "error",
            ]
        )
        AuditEvent.objects.create(
            organization=review.organization,
            actor=None,
            action="ai.review.completed",
            target_type="AIReviewRequest",
            target_id=str(review.id),
        )
    except Exception as exc:  # pragma: no cover - defensive
        review.status = "failed"
        review.error = str(exc)
        review.save(update_fields=["status", "error"])


@shared_task
def purge_retention_task() -> dict:
    return purge_retention()


@shared_task
def run_report_jobs_task() -> int:
    return run_due_report_jobs()
