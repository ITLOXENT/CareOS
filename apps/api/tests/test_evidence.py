from __future__ import annotations

import json
import tempfile

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test.utils import override_settings
from django.utils import timezone

from core.models import (
    AuditEvent,
    Episode,
    EpisodeEvidence,
    EvidenceEvent,
    EvidenceItem,
    Membership,
    Organization,
    Patient,
)
from core.rbac import Role


@pytest.mark.django_db
def test_staff_can_upload_link_and_tag_evidence(client) -> None:
    user = get_user_model().objects.create_user(username="staff", password="pass")
    org = Organization.objects.create(name="CareOS", slug="careos")
    Membership.objects.create(user=user, organization=org, role=Role.STAFF)
    episode = Episode.objects.create(organization=org, title="Episode A", created_by=user)
    patient = Patient.objects.create(organization=org, given_name="Ada", family_name="Lovelace")

    client.force_login(user)
    with tempfile.TemporaryDirectory() as tmpdir:
        with override_settings(EVIDENCE_STORAGE_DIR=tmpdir):
            upload = SimpleUploadedFile("note.txt", b"evidence payload", content_type="text/plain")
            create = client.post(
                "/evidence/",
                data={
                    "title": "Initial note",
                    "kind": "note",
                    "episode_id": str(episode.id),
                    "file": upload,
                },
            )
            assert create.status_code == 201
            evidence_id = create.json()["id"]
            assert EpisodeEvidence.objects.filter(
                organization=org, episode=episode, evidence_id=evidence_id
            ).exists()

            link = client.post(
                f"/evidence/{evidence_id}/link/",
                data=json.dumps({"patient_id": patient.id}),
                content_type="application/json",
            )
            assert link.status_code == 200

            tag = client.post(
                f"/evidence/{evidence_id}/tag/",
                data=json.dumps({"tags": ["urgent", "lab"]}),
                content_type="application/json",
            )
            assert tag.status_code == 200

    assert EvidenceEvent.objects.filter(
        organization=org, evidence_id=evidence_id, event_type="evidence.linked"
    ).exists()
    assert EvidenceEvent.objects.filter(
        organization=org, evidence_id=evidence_id, event_type="evidence.tagged"
    ).exists()
    assert AuditEvent.objects.filter(
        organization=org, action="evidence.linked", target_id=str(evidence_id)
    ).exists()
    assert AuditEvent.objects.filter(
        organization=org, action="evidence.tagged", target_id=str(evidence_id)
    ).exists()


@pytest.mark.django_db
def test_episode_evidence_endpoints(client) -> None:
    user = get_user_model().objects.create_user(username="staff4", password="pass")
    org = Organization.objects.create(name="CareOS", slug="careos5")
    Membership.objects.create(user=user, organization=org, role=Role.STAFF)
    episode = Episode.objects.create(organization=org, title="Episode B", created_by=user)

    client.force_login(user)
    with tempfile.TemporaryDirectory() as tmpdir:
        with override_settings(EVIDENCE_STORAGE_DIR=tmpdir):
            upload = SimpleUploadedFile(
                "episode-note.txt", b"episode evidence", content_type="text/plain"
            )
            create = client.post(
                f"/episodes/{episode.id}/evidence/",
                data={
                    "title": "Episode evidence",
                    "kind": "note",
                    "retention_class": "clinical",
                    "retention_until": "2030-01-01",
                    "file": upload,
                },
            )
            assert create.status_code == 201
            evidence_id = create.json()["id"]

            listing = client.get(f"/episodes/{episode.id}/evidence/")
            assert listing.status_code == 200
            assert listing.json()["results"][0]["id"] == evidence_id
            assert listing.json()["results"][0]["retention_class"] == "clinical"

            download = client.get(f"/evidence/{evidence_id}/?download=1")
            assert download.status_code == 200
            content = b"".join(download.streaming_content)
            assert content == b"episode evidence"

            assert AuditEvent.objects.filter(
                organization=org,
                action="evidence.downloaded",
                target_id=str(evidence_id),
            ).exists()


@pytest.mark.django_db
def test_viewer_cannot_upload_or_tag_evidence(client) -> None:
    user = get_user_model().objects.create_user(username="viewer", password="pass")
    org = Organization.objects.create(name="CareOS", slug="careos2")
    Membership.objects.create(user=user, organization=org, role=Role.VIEWER)

    client.force_login(user)
    upload = SimpleUploadedFile("note.txt", b"payload", content_type="text/plain")
    response = client.post(
        "/evidence/",
        data={"title": "Viewer upload", "kind": "note", "file": upload},
    )
    assert response.status_code == 403

    evidence = EvidenceItem.objects.create(
        organization=org,
        title="Existing",
        kind="note",
        file_name="existing.txt",
        content_type="text/plain",
        size_bytes=3,
        storage_path="/tmp/existing.txt",
        sha256="abc",
    )
    tag = client.post(
        f"/evidence/{evidence.id}/tag/",
        data=json.dumps({"tags": ["x"]}),
        content_type="application/json",
    )
    assert tag.status_code == 403


@pytest.mark.django_db
def test_tenant_isolation_on_evidence_detail(client) -> None:
    user = get_user_model().objects.create_user(username="staff2", password="pass")
    org_a = Organization.objects.create(name="CareOS A", slug="careos-a")
    org_b = Organization.objects.create(name="CareOS B", slug="careos-b")
    Membership.objects.create(user=user, organization=org_a, role=Role.STAFF)
    evidence = EvidenceItem.objects.create(
        organization=org_b,
        title="Other org",
        kind="note",
        file_name="file.txt",
        content_type="text/plain",
        size_bytes=4,
        storage_path="/tmp/other.txt",
        sha256="def",
    )

    client.force_login(user)
    response = client.get(f"/evidence/{evidence.id}/")
    assert response.status_code == 404


@pytest.mark.django_db
@override_settings(
    BILLING_ENTITLEMENTS={"starter": {"evidence_storage_mb": 0}},
    BILLING_DEFAULT_PLAN="starter",
)
def test_evidence_upload_enforces_storage_limit(client) -> None:
    user = get_user_model().objects.create_user(username="staff_limit", password="pass")
    org = Organization.objects.create(name="CareOS Limit", slug="careos-limit")
    Membership.objects.create(user=user, organization=org, role=Role.STAFF)

    client.force_login(user)
    with tempfile.TemporaryDirectory() as tmpdir:
        with override_settings(EVIDENCE_STORAGE_DIR=tmpdir):
            upload = SimpleUploadedFile("note.txt", b"payload", content_type="text/plain")
            response = client.post(
                "/evidence/",
                data={"title": "Limited", "kind": "note", "file": upload},
            )
            assert response.status_code == 402
            assert response.json()["code"] == "billing.evidence_storage_limit"


@pytest.mark.django_db
def test_evidence_events_pagination(client) -> None:
    user = get_user_model().objects.create_user(username="staff3", password="pass")
    org = Organization.objects.create(name="CareOS", slug="careos4")
    Membership.objects.create(user=user, organization=org, role=Role.STAFF)
    evidence = EvidenceItem.objects.create(
        organization=org,
        title="Evidence",
        kind="note",
        file_name="file.txt",
        content_type="text/plain",
        size_bytes=4,
        storage_path="/tmp/file.txt",
        sha256="abc",
        created_by=user,
    )
    event1 = EvidenceEvent.objects.create(
        organization=org,
        evidence=evidence,
        event_type="evidence.created",
        created_by=user,
    )
    event2 = EvidenceEvent.objects.create(
        organization=org,
        evidence=evidence,
        event_type="evidence.tagged",
        created_by=user,
    )
    now = timezone.now()
    EvidenceEvent.objects.filter(id__in=[event1.id, event2.id]).update(created_at=now)

    client.force_login(user)
    page1 = client.get(f"/evidence/{evidence.id}/events/?page=1&page_size=1")
    page2 = client.get(f"/evidence/{evidence.id}/events/?page=2&page_size=1")
    assert page1.status_code == 200
    assert page2.status_code == 200
    assert page1.json()["count"] == 2
    assert page1.json()["results"][0]["id"] == event1.id
    assert page2.json()["results"][0]["id"] == event2.id


@pytest.mark.django_db
def test_evidence_list_pagination(client) -> None:
    user = get_user_model().objects.create_user(username="staff_list", password="pass")
    org = Organization.objects.create(name="CareOS List", slug="careos-list")
    Membership.objects.create(user=user, organization=org, role=Role.STAFF)

    EvidenceItem.objects.create(
        organization=org,
        title="Evidence 1",
        kind="note",
        file_name="file1.txt",
        content_type="text/plain",
        size_bytes=4,
        storage_path="/tmp/file1.txt",
        sha256="abc",
    )
    EvidenceItem.objects.create(
        organization=org,
        title="Evidence 2",
        kind="note",
        file_name="file2.txt",
        content_type="text/plain",
        size_bytes=4,
        storage_path="/tmp/file2.txt",
        sha256="def",
    )
    EvidenceItem.objects.create(
        organization=org,
        title="Evidence 3",
        kind="note",
        file_name="file3.txt",
        content_type="text/plain",
        size_bytes=4,
        storage_path="/tmp/file3.txt",
        sha256="ghi",
    )

    client.force_login(user)
    response = client.get("/evidence/?page=1&page_size=2")
    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 3
    assert payload["page"] == 1
    assert payload["page_size"] == 2
    assert len(payload["results"]) == 2
