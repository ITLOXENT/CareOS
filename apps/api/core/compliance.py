from __future__ import annotations

import io
import json
import zipfile
from datetime import timedelta
from pathlib import Path
from typing import Any

from django.conf import settings
from django.utils import timezone

from .models import AuditEvent, EvidenceBundle, EvidenceItem, Episode, EpisodeEvent, ReportJob


def _bundle_dir() -> Path:
    base = Path(settings.EXPORT_STORAGE_DIR).resolve()
    path = base / "compliance"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _episode_evidence(episode: Episode) -> list[EvidenceItem]:
    direct = EvidenceItem.objects.filter(
        organization=episode.organization, episode=episode
    )
    linked_ids = (
        episode.episodeevidence_set.values_list("evidence_id", flat=True).distinct()
    )
    if linked_ids:
        linked = EvidenceItem.objects.filter(
            organization=episode.organization, id__in=linked_ids
        )
        return list((direct | linked).distinct())
    return list(direct)


def build_episode_bundle(episode: Episode, actor) -> EvidenceBundle:
    events = list(
        EpisodeEvent.objects.filter(
            organization=episode.organization, episode=episode
        ).order_by("created_at", "id")
    )
    evidence = _episode_evidence(episode)
    audit_targets = [str(episode.id)] + [str(item.id) for item in evidence]
    audit_events = list(
        AuditEvent.objects.filter(
            organization=episode.organization,
            target_id__in=audit_targets,
        ).order_by("created_at", "id")
    )

    manifest: dict[str, Any] = {
        "episode": {
            "id": episode.id,
            "title": episode.title,
            "status": episode.status,
            "created_at": episode.created_at.isoformat(),
        },
        "counts": {
            "timeline": len(events),
            "evidence": len(evidence),
            "audit_events": len(audit_events),
        },
        "generated_at": timezone.now().isoformat(),
    }

    payload_timeline = [
        {
            "id": event.id,
            "event_type": event.event_type,
            "from_state": event.from_state,
            "to_state": event.to_state,
            "note": event.note,
            "payload_json": event.payload_json,
            "created_at": event.created_at.isoformat(),
        }
        for event in events
    ]
    payload_evidence = [
        {
            "id": item.id,
            "title": item.title,
            "kind": item.kind,
            "file_name": item.file_name,
            "content_type": item.content_type,
            "size_bytes": item.size_bytes,
            "sha256": item.sha256,
            "tags": item.tags,
            "created_at": item.created_at.isoformat(),
        }
        for item in evidence
    ]
    payload_audit = [
        {
            "id": event.id,
            "action": event.action,
            "target_type": event.target_type,
            "target_id": event.target_id,
            "actor_id": event.actor_id,
            "metadata": event.metadata,
            "request_id": event.request_id,
            "created_at": event.created_at.isoformat(),
        }
        for event in audit_events
    ]

    bundle = EvidenceBundle.objects.create(
        organization=episode.organization,
        episode=episode,
        created_by=actor,
        manifest=manifest,
    )
    bundle_dir = _bundle_dir()
    zip_path = bundle_dir / f"episode-{episode.id}-bundle-{bundle.id}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("manifest.json", json.dumps(manifest, indent=2, sort_keys=True))
        archive.writestr("timeline.json", json.dumps(payload_timeline, indent=2))
        archive.writestr("evidence.json", json.dumps(payload_evidence, indent=2))
        archive.writestr("audit.json", json.dumps(payload_audit, indent=2))

    bundle.artifact_path = str(zip_path)
    bundle.save(update_fields=["artifact_path"])
    return bundle


def run_due_report_jobs(now=None) -> int:
    timestamp = now or timezone.now()
    jobs = ReportJob.objects.filter(status="active").filter(
        next_run_at__lte=timestamp
    )
    processed = 0
    for job in jobs:
        if job.report_type == "episode_bundle":
            episode_id = job.params_json.get("episode_id")
            episode = Episode.objects.filter(
                organization=job.organization, id=episode_id
            ).first()
            if episode:
                bundle = build_episode_bundle(episode, actor=job.created_by)
                job.artifact_path = bundle.artifact_path
        job.last_run_at = timestamp
        job.next_run_at = timestamp + timedelta(days=job.interval_days)
        job.save(update_fields=["artifact_path", "last_run_at", "next_run_at"])
        processed += 1
    return processed
