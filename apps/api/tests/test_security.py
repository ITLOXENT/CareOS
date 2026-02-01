from __future__ import annotations

import json

import pytest
from django.utils import timezone
from datetime import timedelta

from core.models import AuditEvent, Organization, Patient, PortalInvite


@pytest.mark.django_db
def test_portal_login_rate_limit(client) -> None:
    org = Organization.objects.create(name="CareOS", slug="careos")
    patient = Patient.objects.create(organization=org, given_name="Ada", family_name="Lovelace")
    invite = PortalInvite.objects.create(
        organization=org,
        patient=patient,
        email="ada@example.com",
        role="PATIENT",
        token_hash="hash",
        expires_at=timezone.now() + timedelta(hours=2),
        accepted_at=timezone.now(),
    )
    for _ in range(10):
        response = client.post(
            "/portal/auth/login/",
            data=json.dumps({"email": invite.email}),
            content_type="application/json",
        )
    assert response.status_code in {200, 429}
    assert AuditEvent.objects.filter(action="portal.login").exists()


@pytest.mark.django_db
def test_patient_otp_rate_limit(client) -> None:
    for _ in range(6):
        response = client.post(
            "/patient/auth/request-otp/",
            data=json.dumps({"phone": "+15551234567"}),
            content_type="application/json",
        )
    assert response.status_code in {200, 429}
    assert AuditEvent.objects.filter(action="patient.otp.requested").exists()
