from __future__ import annotations

import json
import tempfile

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test.utils import override_settings
from django.utils import timezone

from core.models import ConsentRecord, Episode, EvidenceItem, Membership, Organization, Patient
from core.rbac import Role
from core.views.privacy import purge_retention


@pytest.mark.django_db
def test_consent_records_create_and_list(client) -> None:
    user = get_user_model().objects.create_user(username="admin", password="pass")
    org = Organization.objects.create(name="CareOS", slug="careos")
    Membership.objects.create(user=user, organization=org, role=Role.ADMIN)

    client.force_login(user)
    create = client.post(
        "/privacy/consents/",
        data=json.dumps(
            {
                "subject_type": "patient",
                "subject_id": "123",
                "consent_type": "care",
                "policy_version": "v1",
                "channel": "portal",
                "granted": True,
            }
        ),
        content_type="application/json",
    )
    assert create.status_code == 201
    listing = client.get("/privacy/consents/?subject_type=patient&subject_id=123")
    assert listing.status_code == 200
    assert len(listing.json()["results"]) == 1


@pytest.mark.django_db
def test_dsar_export_and_download(client) -> None:
    user = get_user_model().objects.create_user(username="admin2", password="pass")
    org = Organization.objects.create(name="CareOS", slug="careos2")
    Membership.objects.create(user=user, organization=org, role=Role.ADMIN)
    patient = Patient.objects.create(
        organization=org, given_name="Ada", family_name="Lovelace"
    )
    ConsentRecord.objects.create(
        organization=org,
        subject_type="patient",
        subject_id=str(patient.id),
        consent_type="care",
        policy_version="v1",
        granted=True,
    )
    EvidenceItem.objects.create(
        organization=org,
        patient=patient,
        title="Evidence",
        kind="note",
        file_name="file.txt",
        content_type="text/plain",
        size_bytes=4,
        storage_path="/tmp/file.txt",
        sha256="abc",
    )

    client.force_login(user)
    with tempfile.TemporaryDirectory() as tmpdir:
        with override_settings(EXPORT_STORAGE_DIR=tmpdir):
            response = client.post(
                "/privacy/dsar/export/",
                data=json.dumps({"subject_type": "patient", "subject_id": str(patient.id)}),
                content_type="application/json",
            )
            assert response.status_code == 201
            export_id = response.json()["id"]
            download = client.get(f"/privacy/dsar/exports/{export_id}/download/")
            assert download.status_code == 200
            payload = json.loads(b"".join(download.streaming_content))
            assert payload["subject_type"] == "patient"
            assert payload["patient"]["id"] == patient.id


@pytest.mark.django_db
def test_dsar_delete_anonymizes_patient(client) -> None:
    user = get_user_model().objects.create_user(username="admin3", password="pass")
    org = Organization.objects.create(name="CareOS", slug="careos3")
    Membership.objects.create(user=user, organization=org, role=Role.ADMIN)
    patient = Patient.objects.create(
        organization=org,
        given_name="Ada",
        family_name="Lovelace",
        phone="123",
        email="ada@example.com",
    )
    episode = Episode.objects.create(
        organization=org, title="Episode", description="Details", patient=patient
    )

    client.force_login(user)
    response = client.post(
        "/privacy/dsar/delete/",
        data=json.dumps({"subject_type": "patient", "subject_id": str(patient.id)}),
        content_type="application/json",
    )
    assert response.status_code == 200
    patient.refresh_from_db()
    episode.refresh_from_db()
    assert patient.given_name == "Redacted"
    assert patient.email == ""
    assert episode.patient_id is None


@pytest.mark.django_db
def test_retention_purge_removes_evidence(client) -> None:
    org = Organization.objects.create(name="CareOS", slug="careos4")
    evidence = EvidenceItem.objects.create(
        organization=org,
        title="Evidence",
        kind="note",
        file_name="file.txt",
        content_type="text/plain",
        size_bytes=4,
        storage_path="/tmp/retention.txt",
        sha256="abc",
        retention_class="delete",
        retention_until=timezone.now().date(),
    )
    purge_retention(now=timezone.now().date())
    assert not EvidenceItem.objects.filter(id=evidence.id).exists()
