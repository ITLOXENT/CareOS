from __future__ import annotations

import json

import pytest
from django.contrib.auth import get_user_model

from core.models import AuditEvent, Integration, Membership, Organization
from core.rbac import Role


@pytest.mark.django_db
def test_admin_can_connect_test_disconnect_integration(client) -> None:
    user = get_user_model().objects.create_user(username="admin", password="pass")
    org = Organization.objects.create(name="CareOS", slug="careos")
    Membership.objects.create(user=user, organization=org, role=Role.ADMIN)

    client.force_login(user)
    connect = client.post(
        "/integrations/email/connect/",
        data=json.dumps({"api_key": "secret_key", "sender": "noreply@example.com"}),
        content_type="application/json",
    )
    assert connect.status_code == 200
    integration_id = connect.json()["id"]

    test = client.post("/integrations/email/test/")
    assert test.status_code == 200

    disconnect = client.post("/integrations/email/disconnect/")
    assert disconnect.status_code == 200

    assert AuditEvent.objects.filter(
        organization=org, action="integration.connected", target_id=str(integration_id)
    ).exists()
    assert AuditEvent.objects.filter(
        organization=org, action="integration.disconnected", target_id=str(integration_id)
    ).exists()


@pytest.mark.django_db
def test_integration_list_hides_api_key(client) -> None:
    user = get_user_model().objects.create_user(username="admin2", password="pass")
    org = Organization.objects.create(name="CareOS", slug="careos2")
    Membership.objects.create(user=user, organization=org, role=Role.ADMIN)
    Integration.objects.create(
        organization=org,
        provider="email",
        status="connected",
        config_json={"api_key": "secret_key", "sender": "noreply@example.com"},
    )

    client.force_login(user)
    response = client.get("/integrations/")
    assert response.status_code == 200
    payload = response.json()["results"][0]
    assert "api_key" not in json.dumps(payload)


@pytest.mark.django_db
def test_integration_tenant_isolation(client) -> None:
    user = get_user_model().objects.create_user(username="admin3", password="pass")
    org_a = Organization.objects.create(name="CareOS A", slug="careos-a")
    org_b = Organization.objects.create(name="CareOS B", slug="careos-b")
    Membership.objects.create(user=user, organization=org_a, role=Role.ADMIN)
    Integration.objects.create(
        organization=org_b, provider="email", status="connected", config_json={}
    )

    client.force_login(user)
    response = client.get("/integrations/")
    assert response.status_code == 200
    assert response.json()["results"] == []


@pytest.mark.django_db
def test_admin_can_manage_integration_api_keys(client) -> None:
    user = get_user_model().objects.create_user(username="admin4", password="pass")
    org = Organization.objects.create(name="CareOS Keys", slug="careos-keys")
    Membership.objects.create(user=user, organization=org, role=Role.ADMIN)

    client.force_login(user)
    create = client.post(
        "/integrations/api-keys/",
        data=json.dumps({"name": "Primary"}),
        content_type="application/json",
    )
    assert create.status_code == 201
    payload = create.json()
    assert payload["token"]

    listing = client.get("/integrations/api-keys/")
    assert listing.status_code == 200
    assert listing.json()["results"][0]["name"] == "Primary"

    revoke = client.post(f"/integrations/api-keys/{payload['id']}/revoke/")
    assert revoke.status_code == 200


@pytest.mark.django_db
def test_viewer_cannot_manage_integration_api_keys(client) -> None:
    user = get_user_model().objects.create_user(username="viewer", password="pass")
    org = Organization.objects.create(name="CareOS Viewer", slug="careos-viewer")
    Membership.objects.create(user=user, organization=org, role=Role.VIEWER)

    client.force_login(user)
    create = client.post(
        "/integrations/api-keys/",
        data=json.dumps({"name": "Primary"}),
        content_type="application/json",
    )
    assert create.status_code == 403
