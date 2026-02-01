from __future__ import annotations

import json

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from core.models import AuditEvent, Membership, Organization
from core.rbac import Role


@pytest.mark.django_db
def test_audit_events_filters_and_tenant_isolation(client) -> None:
    user = get_user_model().objects.create_user(username="admin", password="pass")
    org_a = Organization.objects.create(name="CareOS A", slug="careos-a")
    org_b = Organization.objects.create(name="CareOS B", slug="careos-b")
    Membership.objects.create(user=user, organization=org_a, role=Role.ADMIN)
    AuditEvent.objects.create(
        organization=org_a,
        actor=user,
        action="org.updated",
        target_type="Organization",
        target_id=str(org_a.id),
        metadata={"field": "name"},
    )
    AuditEvent.objects.create(
        organization=org_b,
        actor=user,
        action="org.updated",
        target_type="Organization",
        target_id=str(org_b.id),
    )

    client.force_login(user)
    response = client.get(
        f"/audit-events/?action=org.updated&target_type=Organization&target_id={org_a.id}"
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 1
    assert payload["results"][0]["target_id"] == str(org_a.id)


@pytest.mark.django_db
def test_audit_events_pagination_is_stable(client) -> None:
    user = get_user_model().objects.create_user(username="admin2", password="pass")
    org = Organization.objects.create(name="CareOS", slug="careos")
    Membership.objects.create(user=user, organization=org, role=Role.ADMIN)
    event1 = AuditEvent.objects.create(
        organization=org,
        actor=user,
        action="event.a",
        target_type="Test",
        target_id="1",
    )
    event2 = AuditEvent.objects.create(
        organization=org,
        actor=user,
        action="event.a",
        target_type="Test",
        target_id="2",
    )
    event3 = AuditEvent.objects.create(
        organization=org,
        actor=user,
        action="event.a",
        target_type="Test",
        target_id="3",
    )
    now = timezone.now()
    AuditEvent.objects.filter(id__in=[event1.id, event2.id, event3.id]).update(created_at=now)

    client.force_login(user)
    page1 = client.get("/audit-events/?page=1&page_size=2")
    page2 = client.get("/audit-events/?page=2&page_size=2")
    assert page1.status_code == 200
    assert page2.status_code == 200

    ids_page1 = [row["id"] for row in page1.json()["results"]]
    ids_page2 = [row["id"] for row in page2.json()["results"]]
    assert ids_page1 == sorted(ids_page1, reverse=True)
    assert ids_page1[-1] > ids_page2[0]
