from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model

from core.models import AuditEvent, Membership, Organization
from core.rbac import Role


@pytest.mark.django_db
def test_health_route_is_registered(client) -> None:
    response = client.get("/health/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.django_db
def test_tenant_scoping_sets_current_org(client) -> None:
    user = get_user_model().objects.create_user(username="alice", password="pass")
    org = Organization.objects.create(name="CareOS", slug="careos")
    Membership.objects.create(user=user, organization=org, role=Role.OWNER)

    client.force_login(user)
    response = client.get("/orgs/current/")

    assert response.status_code == 200
    assert response.json()["id"] == org.id


@pytest.mark.django_db
def test_rbac_denies_audit_events_for_member(client) -> None:
    user = get_user_model().objects.create_user(username="bob", password="pass")
    org = Organization.objects.create(name="CareOS", slug="careos")
    Membership.objects.create(user=user, organization=org, role=Role.MEMBER)
    AuditEvent.objects.create(
        organization=org,
        actor=None,
        action="org.created",
        target_type="Organization",
        target_id=str(org.id),
    )

    client.force_login(user)
    response = client.get("/audit-events/")

    assert response.status_code == 403


@pytest.mark.django_db
def test_rbac_allows_audit_events_for_auditor(client) -> None:
    user = get_user_model().objects.create_user(username="cora", password="pass")
    org = Organization.objects.create(name="CareOS", slug="careos")
    Membership.objects.create(user=user, organization=org, role=Role.AUDITOR)
    AuditEvent.objects.create(
        organization=org,
        actor=None,
        action="org.created",
        target_type="Organization",
        target_id=str(org.id),
    )

    client.force_login(user)
    response = client.get("/audit-events/")

    assert response.status_code == 200
    assert response.json()["results"]


@pytest.mark.django_db
def test_audit_event_created_on_org_write() -> None:
    org = Organization.objects.create(name="CareOS", slug="careos")
    events = AuditEvent.objects.filter(
        organization=org, target_type="Organization", target_id=str(org.id)
    )
    assert events.exists()
