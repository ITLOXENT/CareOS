from __future__ import annotations

import json
from pathlib import Path

from django.conf import settings
from django.http import FileResponse, JsonResponse
from django.utils import timezone

from ..compliance import build_episode_bundle, run_due_report_jobs
from ..models import EvidenceBundle, Episode, ReportJob, SubmissionRecord
from ..rbac import has_permission
from .utils import parse_date, parse_datetime


def _bundle_payload(bundle: EvidenceBundle) -> dict:
    return {
        "id": bundle.id,
        "episode_id": bundle.episode_id,
        "created_at": bundle.created_at.isoformat(),
        "artifact_path": bundle.artifact_path or None,
        "manifest": bundle.manifest,
    }


def episode_bundles(request, episode_id: int):
    membership = request.membership  # type: ignore[attr-defined]
    if request.method == "POST":
        permission = has_permission(membership.role, "episode:write")
        if not permission.allowed:
            return JsonResponse({"detail": "Not authorized."}, status=403)
        episode = Episode.objects.filter(
            organization=membership.organization, id=episode_id
        ).first()
        if not episode:
            return JsonResponse({"detail": "Episode not found"}, status=404)
        bundle = build_episode_bundle(episode, request.user)
        return JsonResponse(_bundle_payload(bundle), status=201)

    permission = has_permission(membership.role, "episode:read")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    bundles = EvidenceBundle.objects.filter(
        organization=membership.organization, episode_id=episode_id
    ).order_by("-created_at")
    return JsonResponse({"results": [_bundle_payload(item) for item in bundles]})


def bundle_download(request, bundle_id: int):
    membership = request.membership  # type: ignore[attr-defined]
    permission = has_permission(membership.role, "episode:read")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    bundle = EvidenceBundle.objects.filter(
        organization=membership.organization, id=bundle_id
    ).first()
    if not bundle or not bundle.artifact_path:
        return JsonResponse({"detail": "Not found."}, status=404)
    base_dir = Path(settings.EXPORT_STORAGE_DIR).resolve()
    path = Path(bundle.artifact_path).resolve()
    if base_dir not in path.parents and path != base_dir:
        return JsonResponse({"detail": "Not found."}, status=404)
    if not path.exists():
        return JsonResponse({"detail": "Not found."}, status=404)
    return FileResponse(path.open("rb"), as_attachment=True, filename=path.name)


def report_jobs(request):
    membership = request.membership  # type: ignore[attr-defined]
    permission = has_permission(membership.role, "org:manage")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    if request.method == "POST":
        payload = json.loads(request.body or "{}")
        name = str(payload.get("name", "")).strip()
        report_type = str(payload.get("report_type", "")).strip()
        try:
            interval_days = int(payload.get("interval_days", 30))
        except (TypeError, ValueError):
            return JsonResponse({"detail": "interval_days must be an integer"}, status=400)
        if not name or not report_type:
            return JsonResponse({"detail": "name and report_type required"}, status=400)
        next_run_at = parse_datetime(payload.get("next_run_at") or "")
        if not next_run_at:
            next_run_at = timezone.now()
        job = ReportJob.objects.create(
            organization=membership.organization,
            name=name,
            report_type=report_type,
            interval_days=interval_days,
            next_run_at=next_run_at,
            created_by=request.user,
            params_json=payload.get("params", {}) or {},
        )
        return JsonResponse(
            {
                "id": job.id,
                "name": job.name,
                "report_type": job.report_type,
                "status": job.status,
                "interval_days": job.interval_days,
                "next_run_at": job.next_run_at.isoformat() if job.next_run_at else None,
                "last_run_at": job.last_run_at.isoformat() if job.last_run_at else None,
                "artifact_path": job.artifact_path or None,
            },
            status=201,
        )
    jobs = ReportJob.objects.filter(organization=membership.organization).order_by(
        "-created_at"
    )
    payload = [
        {
            "id": job.id,
            "name": job.name,
            "report_type": job.report_type,
            "status": job.status,
            "interval_days": job.interval_days,
            "next_run_at": job.next_run_at.isoformat() if job.next_run_at else None,
            "last_run_at": job.last_run_at.isoformat() if job.last_run_at else None,
            "artifact_path": job.artifact_path or None,
        }
        for job in jobs
    ]
    return JsonResponse({"results": payload})


def report_job_run(request, job_id: int):
    membership = request.membership  # type: ignore[attr-defined]
    permission = has_permission(membership.role, "org:manage")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    job = ReportJob.objects.filter(
        organization=membership.organization, id=job_id
    ).first()
    if not job:
        return JsonResponse({"detail": "Not found."}, status=404)
    if job.next_run_at is None:
        job.next_run_at = timezone.now()
        job.save(update_fields=["next_run_at"])
    run_due_report_jobs(now=timezone.now())
    job.refresh_from_db()
    return JsonResponse(
        {
            "id": job.id,
            "name": job.name,
            "report_type": job.report_type,
            "status": job.status,
            "interval_days": job.interval_days,
            "next_run_at": job.next_run_at.isoformat() if job.next_run_at else None,
            "last_run_at": job.last_run_at.isoformat() if job.last_run_at else None,
            "artifact_path": job.artifact_path or None,
        }
    )


def submission_records(request):
    membership = request.membership  # type: ignore[attr-defined]
    permission = has_permission(membership.role, "org:manage")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    if request.method == "POST":
        payload = json.loads(request.body or "{}")
        due_date = parse_date(payload.get("due_date", ""))
        if not due_date:
            return JsonResponse({"detail": "due_date required"}, status=400)
        episode_id = payload.get("episode_id")
        submitted_at = parse_datetime(payload.get("submitted_at") or "")
        record = SubmissionRecord.objects.create(
            organization=membership.organization,
            episode_id=episode_id,
            due_date=due_date,
            status=str(payload.get("status", "pending")).strip() or "pending",
            notes=str(payload.get("notes", "")).strip(),
            created_by=request.user,
            submitted_at=submitted_at,
        )
        return JsonResponse(
            {
                "id": record.id,
                "episode_id": record.episode_id,
                "due_date": record.due_date.isoformat(),
                "submitted_at": record.submitted_at.isoformat()
                if record.submitted_at
                else None,
                "status": record.status,
                "notes": record.notes,
            },
            status=201,
        )
    records = SubmissionRecord.objects.filter(
        organization=membership.organization
    ).order_by("-created_at")
    episode_id = request.GET.get("episode_id")
    if episode_id:
        records = records.filter(episode_id=episode_id)
    payload = [
        {
            "id": record.id,
            "episode_id": record.episode_id,
            "due_date": record.due_date.isoformat(),
            "submitted_at": record.submitted_at.isoformat()
            if record.submitted_at
            else None,
            "status": record.status,
            "notes": record.notes,
        }
        for record in records
    ]
    return JsonResponse({"results": payload})
