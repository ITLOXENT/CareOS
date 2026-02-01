from __future__ import annotations

import csv
import io
from datetime import timedelta
from pathlib import Path

from django.conf import settings
from django.utils import timezone

from .models import AuditEvent, Episode


def _export_dir() -> Path:
    base_dir = Path(settings.EXPORT_STORAGE_DIR)
    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir


def _write_csv(rows: list[dict], fieldnames: list[str], filename: str) -> str:
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
    content = output.getvalue()
    path = _export_dir() / filename
    path.write_text(content, encoding="utf-8")
    return str(path)


def export_episodes_csv(*, organization, days: int, filename: str) -> str:
    since = timezone.now() - timedelta(days=days)
    episodes = (
        Episode.objects.filter(organization=organization, created_at__gte=since)
        .order_by("created_at")
        .values(
            "id",
            "title",
            "description",
            "status",
            "created_at",
            "updated_at",
            "assigned_to_id",
            "created_by_id",
            "patient_id",
        )
    )
    fieldnames = [
        "id",
        "title",
        "description",
        "status",
        "created_at",
        "updated_at",
        "assigned_to_id",
        "created_by_id",
        "patient_id",
    ]
    rows = [
        {
            **row,
            "created_at": row["created_at"].isoformat() if row["created_at"] else "",
            "updated_at": row["updated_at"].isoformat() if row["updated_at"] else "",
        }
        for row in episodes
    ]
    return _write_csv(rows, fieldnames, filename)


def export_audit_events_csv(*, organization, days: int, filename: str) -> str:
    since = timezone.now() - timedelta(days=days)
    events = (
        AuditEvent.objects.filter(organization=organization, created_at__gte=since)
        .order_by("created_at")
        .values("id", "action", "target_type", "target_id", "actor_id", "created_at")
    )
    fieldnames = ["id", "action", "target_type", "target_id", "actor_id", "created_at"]
    rows = [
        {
            **row,
            "created_at": row["created_at"].isoformat() if row["created_at"] else "",
        }
        for row in events
    ]
    return _write_csv(rows, fieldnames, filename)
