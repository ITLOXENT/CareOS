from __future__ import annotations

import hashlib
import json
from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from core.models import Membership, Organization, Patient, PortalInvite
from core.rbac import Role


@pytest.mark.django_db
def test_accept_invite_creates_session(client) -> None:
    user = get_user_model().objects.create_user(username="admin", password="pass")
    org = Organization.objects.create(name="CareOS", slug="careos")
    Membership.objects.create(user=user, organization=org, role=Role.ADMIN)
    patient = Patient.objects.create(organization=org, given_name="Ada", family_name="Lovelace")
    token = "invite-token"
    invite = PortalInvite.objects.create(
        organization=org,
        patient=patient,
        email="ada@example.com",
        role="PATIENT",
        token_hash="",
        expires_at=timezone.now() + timedelta(hours=2),
    )
    invite.token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    invite.save(update_fields=["token_hash"])

    response = client.post(
        "/portal/auth/accept-invite/",
        data=json.dumps({"token": token}),
        content_type="application/json",
    )
    assert response.status_code == 200
    assert "token" in response.json()


@pytest.mark.django_db
def test_portal_tenant_isolation(client) -> None:
    org = Organization.objects.create(name="CareOS", slug="careos2")
    patient = Patient.objects.create(organization=org, given_name="Bob", family_name="Jones")
    token = "invite-token-2"
    invite = PortalInvite.objects.create(
        organization=org,
        patient=patient,
        email="bob@example.com",
        role="PATIENT",
        token_hash="",
        expires_at=timezone.now() + timedelta(hours=2),
        accepted_at=timezone.now(),
    )
    invite.token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    invite.save(update_fields=["token_hash"])

    login = client.post(
        "/portal/auth/login/",
        data=json.dumps({"email": "bob@example.com"}),
        content_type="application/json",
    )
    assert login.status_code == 200
    portal_token = login.json()["token"]

    me = client.get("/portal/me/", HTTP_AUTHORIZATION=f"Bearer {portal_token}")
    assert me.status_code == 200
    assert me.json()["patient_id"] == patient.id

    staff_endpoint = client.get("/episodes/")
    assert staff_endpoint.status_code == 401
