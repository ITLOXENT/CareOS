from __future__ import annotations

import json
import tempfile

import pytest
from django.contrib.auth import get_user_model
from django.test.utils import override_settings

from core.models import AuditEvent, Episode, Membership, Organization
from core.rbac import Role


@pytest.mark.django_db
def test_admin_can_request_and_download_export(client) -> None:
    user = get_user_model().objects.create_user(username="admin", password="pass")
    org = Organization.objects.create(name="CareOS", slug="careos")
    Membership.objects.create(user=user, organization=org, role=Role.ADMIN)
    Episode.objects.create(organization=org, title="Episode A", created_by=user)
    AuditEvent.objects.create(
        organization=org,
        actor=user,
        action="episode.created",
        target_type="Episode",
        target_id="1",
    )

    client.force_login(user)
    with tempfile.TemporaryDirectory() as tmpdir:
        with override_settings(EXPORT_STORAGE_DIR=tmpdir):
            response = client.post(
                "/exports/",
                data=json.dumps({"kind": "episodes", "last_days": 7}),
                content_type="application/json",
            )
            assert response.status_code == 201
            export_id = response.json()["id"]
            download = client.get(f"/exports/{export_id}/download/")
            assert download.status_code == 200


@pytest.mark.django_db
def test_staff_cannot_request_exports(client) -> None:
    user = get_user_model().objects.create_user(username="staff", password="pass")
    org = Organization.objects.create(name="CareOS2", slug="careos2")
    Membership.objects.create(user=user, organization=org, role=Role.STAFF)

    client.force_login(user)
    response = client.post(
        "/exports/",
        data=json.dumps({"kind": "audit_events", "last_days": 7}),
        content_type="application/json",
    )
    assert response.status_code == 403
