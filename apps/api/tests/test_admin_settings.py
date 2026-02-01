from __future__ import annotations

import json

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from core.models import Membership, Organization
from core.rbac import Role


@pytest.mark.django_db
def test_admin_can_update_org_profile(client) -> None:
    user = get_user_model().objects.create_user(username="admin", password="pass")
    org = Organization.objects.create(name="CareOS", slug="careos")
    Membership.objects.create(user=user, organization=org, role=Role.ADMIN)

    client.force_login(user)
    response = client.patch(
        "/orgs/current/",
        data=json.dumps({"name": "CareOS HQ"}),
        content_type="application/json",
    )
    assert response.status_code == 200
    org.refresh_from_db()
    assert org.name == "CareOS HQ"


@pytest.mark.django_db
def test_staff_cannot_update_org_profile(client) -> None:
    user = get_user_model().objects.create_user(username="staff", password="pass")
    org = Organization.objects.create(name="CareOS", slug="careos2")
    Membership.objects.create(user=user, organization=org, role=Role.STAFF)

    client.force_login(user)
    response = client.patch(
        "/orgs/current/",
        data=json.dumps({"name": "Blocked"}),
        content_type="application/json",
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_invite_requires_admin_and_sets_expiry(client) -> None:
    user = get_user_model().objects.create_user(username="admin2", password="pass")
    org = Organization.objects.create(name="CareOS", slug="careos3")
    Membership.objects.create(user=user, organization=org, role=Role.ADMIN)

    client.force_login(user)
    response = client.post(
        "/orgs/invites/",
        data=json.dumps({"email": "invite@example.com", "role": "VIEWER", "expires_in_hours": 24}),
        content_type="application/json",
    )
    assert response.status_code == 201
    expires_at = response.json()["expires_at"]
    assert expires_at


@pytest.mark.django_db
def test_role_change_and_deactivate_are_tenant_scoped(client) -> None:
    admin = get_user_model().objects.create_user(username="admin3", password="pass")
    org_a = Organization.objects.create(name="CareOS A", slug="careos-a")
    org_b = Organization.objects.create(name="CareOS B", slug="careos-b")
    Membership.objects.create(user=admin, organization=org_a, role=Role.ADMIN)
    other_user = get_user_model().objects.create_user(username="other", password="pass")
    member_b = Membership.objects.create(user=other_user, organization=org_b, role=Role.VIEWER)

    client.force_login(admin)
    response = client.post(
        f"/orgs/members/{member_b.id}/role/",
        data=json.dumps({"role": "STAFF"}),
        content_type="application/json",
    )
    assert response.status_code == 404

    deactivate = client.post(f"/orgs/members/{member_b.id}/deactivate/")
    assert deactivate.status_code == 404


@pytest.mark.django_db
def test_admin_can_deactivate_member(client) -> None:
    admin = get_user_model().objects.create_user(username="admin4", password="pass")
    member_user = get_user_model().objects.create_user(username="member", password="pass")
    org = Organization.objects.create(name="CareOS", slug="careos4")
    Membership.objects.create(user=admin, organization=org, role=Role.ADMIN)
    member = Membership.objects.create(user=member_user, organization=org, role=Role.VIEWER)

    client.force_login(admin)
    response = client.post(f"/orgs/members/{member.id}/deactivate/")
    assert response.status_code == 200
    member.refresh_from_db()
    assert member.is_active is False
    assert member.deactivated_at is not None
