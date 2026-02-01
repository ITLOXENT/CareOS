from __future__ import annotations

import json

import pytest
from django.contrib.auth import get_user_model

from core.models import AuditEvent, Membership, Organization
from core.rbac import Role


@pytest.mark.django_db
def test_request_id_in_response_and_audit(client) -> None:
    user = get_user_model().objects.create_user(username="admin", password="pass")
    org = Organization.objects.create(name="CareOS", slug="careos-observe")
    Membership.objects.create(user=user, organization=org, role=Role.ADMIN)

    client.force_login(user)
    response = client.post(
        "/privacy/consents/",
        data=json.dumps(
            {
                "subject_type": "patient",
                "subject_id": "123",
                "consent_type": "care",
                "policy_version": "v1",
            }
        ),
        content_type="application/json",
    )
    assert response.status_code == 201
    request_id = response["X-Request-ID"]
    event = AuditEvent.objects.filter(
        organization=org, action="privacy.consent.recorded"
    ).first()
    assert event is not None
    assert event.request_id == request_id


@pytest.mark.django_db
def test_metrics_endpoint_returns_snapshot(client) -> None:
    response = client.get("/health/")
    assert response.status_code == 200
    metrics = client.get("/metrics/")
    assert metrics.status_code == 200
    payload = metrics.json()
    assert "total_requests" in payload
    assert "last_duration_ms" in payload
