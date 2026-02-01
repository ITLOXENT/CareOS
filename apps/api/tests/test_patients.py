from __future__ import annotations

import json
from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from core.models import AuditEvent, ConsentRecord, Episode, Membership, Organization, Patient
from core.rbac import Role


@pytest.mark.django_db
def test_admin_can_create_and_view_patient(client) -> None:
    user = get_user_model().objects.create_user(username="admin", password="pass")
    org = Organization.objects.create(name="CareOS", slug="careos")
    Membership.objects.create(user=user, organization=org, role=Role.ADMIN)

    client.force_login(user)
    create = client.post(
        "/patients/",
        data=json.dumps({"given_name": "Ada", "family_name": "Lovelace", "nhs_number": "1234567890"}),
        content_type="application/json",
    )
    assert create.status_code == 201
    patient_id = create.json()["id"]

    detail = client.get(f"/patients/{patient_id}/")
    assert detail.status_code == 200
    assert detail.json()["given_name"] == "Ada"


@pytest.mark.django_db
def test_viewer_cannot_create_patient(client) -> None:
    user = get_user_model().objects.create_user(username="viewer", password="pass")
    org = Organization.objects.create(name="CareOS", slug="careos2")
    Membership.objects.create(user=user, organization=org, role=Role.VIEWER)

    client.force_login(user)
    response = client.post(
        "/patients/",
        data=json.dumps({"given_name": "Bob", "family_name": "Jones"}),
        content_type="application/json",
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_viewer_cannot_read_patients(client) -> None:
    user = get_user_model().objects.create_user(username="viewer-read", password="pass")
    org = Organization.objects.create(name="CareOS", slug="careos-read")
    Membership.objects.create(user=user, organization=org, role=Role.VIEWER)

    client.force_login(user)
    response = client.get("/patients/")
    assert response.status_code == 403


@pytest.mark.django_db
def test_tenant_isolation_on_patient_detail(client) -> None:
    user = get_user_model().objects.create_user(username="staff", password="pass")
    org_a = Organization.objects.create(name="CareOS A", slug="careos-a")
    org_b = Organization.objects.create(name="CareOS B", slug="careos-b")
    Membership.objects.create(user=user, organization=org_a, role=Role.STAFF)
    patient = Patient.objects.create(organization=org_b, given_name="Other", family_name="Org")

    client.force_login(user)
    response = client.get(f"/patients/{patient.id}/")
    assert response.status_code == 404


@pytest.mark.django_db
def test_staff_can_search_and_list_episodes(client) -> None:
    user = get_user_model().objects.create_user(username="staff3", password="pass")
    org = Organization.objects.create(name="CareOS", slug="careos-search")
    Membership.objects.create(user=user, organization=org, role=Role.STAFF)
    patient = Patient.objects.create(organization=org, given_name="Zed", family_name="Alpha")
    Episode.objects.create(organization=org, title="Episode A", patient=patient)
    Episode.objects.create(organization=org, title="Episode B", patient=patient)

    client.force_login(user)
    search = client.get("/patients/search/?q=zed")
    assert search.status_code == 200
    assert search.json()["results"][0]["id"] == patient.id

    episodes = client.get(f"/patients/{patient.id}/episodes/")
    assert episodes.status_code == 200
    assert len(episodes.json()["results"]) == 2


@pytest.mark.django_db
def test_care_circle_and_consents_require_patient_write(client) -> None:
    user = get_user_model().objects.create_user(username="staff-cc", password="pass")
    org = Organization.objects.create(name="CareOS", slug="careos-cc")
    Membership.objects.create(user=user, organization=org, role=Role.STAFF)
    patient = Patient.objects.create(organization=org, given_name="Care", family_name="Circle")

    client.force_login(user)
    create_member = client.post(
        f"/patients/{patient.id}/care-circle/",
        data=json.dumps({"person_name": "Jane Doe", "relationship": "Sister"}),
        content_type="application/json",
    )
    assert create_member.status_code == 201
    member_id = create_member.json()["id"]

    update_member = client.patch(
        f"/patients/{patient.id}/care-circle/{member_id}/",
        data=json.dumps({"contact": "jane@example.com"}),
        content_type="application/json",
    )
    assert update_member.status_code == 200

    delete_member = client.delete(f"/patients/{patient.id}/care-circle/{member_id}/")
    assert delete_member.status_code == 200

    grant = client.post(
        f"/patients/{patient.id}/consents/",
        data=json.dumps(
            {"scope": "episodes.read", "lawful_basis": "consent", "granted_by": "patient"}
        ),
        content_type="application/json",
    )
    assert grant.status_code == 201
    consent_id = grant.json()["id"]

    revoke = client.post(f"/patients/{patient.id}/consents/{consent_id}/revoke/")
    assert revoke.status_code == 200


@pytest.mark.django_db
def test_restricted_episode_requires_consent(client) -> None:
    user = get_user_model().objects.create_user(username="staff-consent", password="pass")
    org = Organization.objects.create(name="CareOS", slug="careos-consent")
    Membership.objects.create(user=user, organization=org, role=Role.STAFF)
    patient = Patient.objects.create(
        organization=org,
        given_name="Restricted",
        family_name="Patient",
        restricted=True,
    )
    episode = Episode.objects.create(organization=org, patient=patient, title="Episode A")

    client.force_login(user)
    detail = client.get(f"/episodes/{episode.id}/")
    assert detail.status_code == 403

    ConsentRecord.objects.create(
        organization=org,
        patient=patient,
        subject_type="patient",
        subject_id=str(patient.id),
        consent_type="episodes.read",
        scope="episodes.read",
        lawful_basis="consent",
        granted_by="patient",
        policy_version="v1",
        expires_at=timezone.now() + timedelta(days=1),
        granted=True,
    )

    detail_ok = client.get(f"/episodes/{episode.id}/")
    assert detail_ok.status_code == 200


@pytest.mark.django_db
def test_care_circle_tenant_isolation(client) -> None:
    user = get_user_model().objects.create_user(username="staff-tenant", password="pass")
    org_a = Organization.objects.create(name="CareOS A", slug="careos-a1")
    org_b = Organization.objects.create(name="CareOS B", slug="careos-b1")
    Membership.objects.create(user=user, organization=org_a, role=Role.STAFF)
    patient = Patient.objects.create(organization=org_b, given_name="Other", family_name="Org")

    client.force_login(user)
    response = client.get(f"/patients/{patient.id}/care-circle/")
    assert response.status_code == 404


@pytest.mark.django_db
def test_staff_can_merge_patient_and_emit_audit(client) -> None:
    user = get_user_model().objects.create_user(username="staff2", password="pass")
    org = Organization.objects.create(name="CareOS", slug="careos3")
    Membership.objects.create(user=user, organization=org, role=Role.STAFF)
    target = Patient.objects.create(organization=org, given_name="Target", family_name="One")
    source = Patient.objects.create(organization=org, given_name="Source", family_name="Two")
    episode = Episode.objects.create(organization=org, title="Episode", patient=source)

    client.force_login(user)
    response = client.post(
        f"/patients/{target.id}/merge/",
        data=json.dumps({"source_id": source.id}),
        content_type="application/json",
    )

    assert response.status_code == 200
    source.refresh_from_db()
    episode.refresh_from_db()
    assert source.merged_into_id == target.id
    assert episode.patient_id == target.id
    assert AuditEvent.objects.filter(
        organization=org, action="patient.merged", target_id=str(target.id)
    ).exists()


@pytest.mark.django_db
def test_viewer_cannot_merge_patient(client) -> None:
    user = get_user_model().objects.create_user(username="viewer2", password="pass")
    org = Organization.objects.create(name="CareOS", slug="careos4")
    Membership.objects.create(user=user, organization=org, role=Role.VIEWER)
    target = Patient.objects.create(organization=org, given_name="Target", family_name="Three")
    source = Patient.objects.create(organization=org, given_name="Source", family_name="Four")

    client.force_login(user)
    response = client.post(
        f"/patients/{target.id}/merge/",
        data=json.dumps({"source_id": source.id}),
        content_type="application/json",
    )
    assert response.status_code == 403
