from __future__ import annotations

import io
import json
import tempfile
import zipfile

from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.test.utils import override_settings
from django.utils import timezone

from core.compliance import run_due_report_jobs
from core.models import (
    AuditEvent,
    EvidenceItem,
    Episode,
    Membership,
    Organization,
    ReportJob,
)
from core.rbac import Role


@pytest.mark.django_db
def test_episode_bundle_generation(client) -> None:
    user = get_user_model().objects.create_user(username="admin", password="pass")
    org = Organization.objects.create(name="CareOS", slug="careos")
    Membership.objects.create(user=user, organization=org, role=Role.ADMIN)
    episode = Episode.objects.create(organization=org, title="Episode A", created_by=user)
    evidence = EvidenceItem.objects.create(
        organization=org,
        episode=episode,
        title="Evidence",
        kind="note",
        file_name="file.txt",
        content_type="text/plain",
        size_bytes=4,
        storage_path="/tmp/file.txt",
        sha256="abc",
    )
    AuditEvent.objects.create(
        organization=org,
        actor=user,
        action="episode.read",
        target_type="Episode",
        target_id=str(episode.id),
    )

    client.force_login(user)
    with tempfile.TemporaryDirectory() as tmpdir:
        with override_settings(EXPORT_STORAGE_DIR=tmpdir):
            response = client.post(f"/episodes/{episode.id}/compliance/bundles/")
            assert response.status_code == 201
            bundle_id = response.json()["id"]
            download = client.get(f"/compliance/bundles/{bundle_id}/download/")
            assert download.status_code == 200
            buffer = io.BytesIO(b"".join(download.streaming_content))
            with zipfile.ZipFile(buffer) as archive:
                assert "manifest.json" in archive.namelist()
                manifest = json.loads(archive.read("manifest.json"))
                assert manifest["episode"]["id"] == episode.id
                evidence_payload = json.loads(archive.read("evidence.json"))
                assert evidence_payload[0]["id"] == evidence.id


@pytest.mark.django_db
def test_report_job_runs_bundle() -> None:
    user = get_user_model().objects.create_user(username="admin2", password="pass")
    org = Organization.objects.create(name="CareOS", slug="careos2")
    Membership.objects.create(user=user, organization=org, role=Role.ADMIN)
    episode = Episode.objects.create(organization=org, title="Episode B", created_by=user)
    job = ReportJob.objects.create(
        organization=org,
        name="Episode bundle",
        report_type="episode_bundle",
        interval_days=30,
        next_run_at=timezone.now() - timedelta(hours=1),
        created_by=user,
        params_json={"episode_id": episode.id},
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        with override_settings(EXPORT_STORAGE_DIR=tmpdir):
            processed = run_due_report_jobs(now=timezone.now())
            assert processed == 1
            job.refresh_from_db()
            assert job.artifact_path


@pytest.mark.django_db
def test_submission_record_create_and_list(client) -> None:
    user = get_user_model().objects.create_user(username="admin3", password="pass")
    org = Organization.objects.create(name="CareOS", slug="careos3")
    Membership.objects.create(user=user, organization=org, role=Role.ADMIN)
    client.force_login(user)

    response = client.post(
        "/compliance/submissions/",
        data=json.dumps({"due_date": "2026-02-01", "status": "pending"}),
        content_type="application/json",
    )
    assert response.status_code == 201
    listing = client.get("/compliance/submissions/")
    assert listing.status_code == 200
    assert len(listing.json()["results"]) == 1
