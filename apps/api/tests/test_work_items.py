from __future__ import annotations

import json
from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.test.utils import override_settings
from django.utils import timezone

from core.models import AuditEvent, Episode, Membership, Organization, WorkItem
from core.rbac import Role


@pytest.mark.django_db
def test_work_items_list_filters(client) -> None:
    user = get_user_model().objects.create_user(username="staff", password="pass")
    org = Organization.objects.create(name="CareOS", slug="careos")
    Membership.objects.create(user=user, organization=org, role=Role.STAFF)
    episode = Episode.objects.create(organization=org, title="Episode A")
    WorkItem.objects.create(
        organization=org,
        episode=episode,
        kind="episode_triage",
        status="open",
        assigned_to=user,
        due_at=timezone.now() + timedelta(hours=1),
    )
    WorkItem.objects.create(
        organization=org,
        episode=episode,
        kind="call_back",
        status="assigned",
        assigned_to=user,
        due_at=timezone.now() + timedelta(hours=3),
    )

    client.force_login(user)
    response = client.get("/work-items/?status=open&kind=episode_triage")
    assert response.status_code == 200
    assert len(response.json()["results"]) == 1


@pytest.mark.django_db
def test_work_item_assign_defaults_to_current_user(client) -> None:
    user = get_user_model().objects.create_user(username="staff2", password="pass")
    org = Organization.objects.create(name="CareOS2", slug="careos2")
    Membership.objects.create(user=user, organization=org, role=Role.STAFF)
    item = WorkItem.objects.create(
        organization=org, kind="episode_triage", status="open", assigned_to=None
    )

    client.force_login(user)
    response = client.post(f"/work-items/{item.id}/assign/", data="{}", content_type="application/json")
    assert response.status_code == 200
    item.refresh_from_db()
    assert item.assigned_to_id == user.id


@pytest.mark.django_db
def test_work_item_complete_requires_assignee_or_admin(client) -> None:
    user = get_user_model().objects.create_user(username="staff3", password="pass")
    admin = get_user_model().objects.create_user(username="admin", password="pass")
    org = Organization.objects.create(name="CareOS3", slug="careos3")
    Membership.objects.create(user=user, organization=org, role=Role.STAFF)
    Membership.objects.create(user=admin, organization=org, role=Role.ADMIN)
    item = WorkItem.objects.create(
        organization=org,
        kind="episode_triage",
        status="assigned",
        assigned_to=admin,
    )

    client.force_login(user)
    response = client.post(f"/work-items/{item.id}/complete/")
    assert response.status_code == 403

    client.force_login(admin)
    response = client.post(f"/work-items/{item.id}/complete/")
    assert response.status_code == 200


@pytest.mark.django_db
@override_settings(SLA_DEFAULT_MINUTES=30)
def test_episode_creation_creates_work_item_with_due_at(client) -> None:
    user = get_user_model().objects.create_user(username="admin2", password="pass")
    org = Organization.objects.create(name="CareOS4", slug="careos4")
    Membership.objects.create(user=user, organization=org, role=Role.ADMIN)

    client.force_login(user)
    response = client.post(
        "/episodes/",
        data=json.dumps({"title": "Episode B"}),
        content_type="application/json",
    )
    assert response.status_code == 201
    episode_id = response.json()["id"]
    work_item = WorkItem.objects.filter(organization=org, episode_id=episode_id).first()
    assert work_item is not None
    assert work_item.kind == "episode_triage"
    assert work_item.due_at is not None


@pytest.mark.django_db
def test_transition_auto_completes_work_items(client) -> None:
    user = get_user_model().objects.create_user(username="admin3", password="pass")
    org = Organization.objects.create(name="CareOS5", slug="careos5")
    Membership.objects.create(user=user, organization=org, role=Role.ADMIN)
    episode = Episode.objects.create(organization=org, title="Episode C", status="in_progress")
    item = WorkItem.objects.create(
        organization=org, episode=episode, kind="episode_triage", status="open"
    )

    client.force_login(user)
    response = client.post(
        f"/episodes/{episode.id}/transition/",
        data=json.dumps({"to_state": "resolved"}),
        content_type="application/json",
    )
    assert response.status_code == 200
    item.refresh_from_db()
    assert item.status == "completed"
    assert AuditEvent.objects.filter(
        organization=org, action="work_item.auto_completed", target_id=str(item.id)
    ).exists()


@pytest.mark.django_db
def test_work_item_tenant_isolation(client) -> None:
    user = get_user_model().objects.create_user(username="staff_tenant", password="pass")
    org_a = Organization.objects.create(name="Org A", slug="org-a")
    org_b = Organization.objects.create(name="Org B", slug="org-b")
    Membership.objects.create(user=user, organization=org_a, role=Role.STAFF)
    item = WorkItem.objects.create(
        organization=org_b, kind="episode_triage", status="open"
    )

    client.force_login(user)
    response = client.get("/work-items/")
    assert response.status_code == 200
    assert response.json()["results"] == []

    assign = client.post(
        f"/work-items/{item.id}/assign/",
        data=json.dumps({}),
        content_type="application/json",
    )
    assert assign.status_code == 404

    complete = client.post(f"/work-items/{item.id}/complete/")
    assert complete.status_code == 404


@pytest.mark.django_db
def test_work_item_sla_filter_returns_overdue(client) -> None:
    user = get_user_model().objects.create_user(username="staff_sla", password="pass")
    org = Organization.objects.create(name="CareOS SLA", slug="careos-sla")
    Membership.objects.create(user=user, organization=org, role=Role.STAFF)
    WorkItem.objects.create(
        organization=org,
        kind="episode_triage",
        status="open",
        due_at=timezone.now() - timedelta(minutes=10),
    )
    WorkItem.objects.create(
        organization=org,
        kind="episode_triage",
        status="open",
        due_at=timezone.now() + timedelta(hours=2),
    )

    client.force_login(user)
    response = client.get("/work-items/?sla=breached")
    assert response.status_code == 200
    assert len(response.json()["results"]) == 1
