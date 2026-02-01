from __future__ import annotations

import json
from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.test.utils import override_settings
from django.utils import timezone

from core.models import Episode, Membership, Notification, Organization, WorkItem
from core.notifications import check_sla_notifications
from core.rbac import Role


@pytest.mark.django_db
def test_notifications_list_and_mark_read(client) -> None:
    user = get_user_model().objects.create_user(username="viewer", password="pass")
    org = Organization.objects.create(name="CareOS", slug="careos")
    Membership.objects.create(user=user, organization=org, role=Role.VIEWER)
    notification = Notification.objects.create(
        organization=org,
        recipient=user,
        title="SLA warning",
        body="Work item is due soon.",
    )

    client.force_login(user)
    response = client.get("/notifications/")
    assert response.status_code == 200
    assert response.json()["results"][0]["id"] == notification.id

    read = client.post(f"/notifications/{notification.id}/read/")
    assert read.status_code == 200
    notification.refresh_from_db()
    assert notification.unread is False


@pytest.mark.django_db
def test_notification_tenancy_and_recipient_scope(client) -> None:
    user = get_user_model().objects.create_user(username="staff", password="pass")
    other = get_user_model().objects.create_user(username="other", password="pass")
    org = Organization.objects.create(name="CareOS", slug="careos2")
    Membership.objects.create(user=user, organization=org, role=Role.STAFF)
    Membership.objects.create(user=other, organization=org, role=Role.STAFF)
    notification = Notification.objects.create(
        organization=org,
        recipient=other,
        title="Private",
    )

    client.force_login(user)
    response = client.post(f"/notifications/{notification.id}/read/")
    assert response.status_code == 404


@pytest.mark.django_db
@override_settings(SLA_WARNING_MINUTES=60)
def test_sla_escalation_creates_notification(client) -> None:
    user = get_user_model().objects.create_user(username="staff2", password="pass")
    org = Organization.objects.create(name="CareOS", slug="careos3")
    Membership.objects.create(user=user, organization=org, role=Role.STAFF)
    now = timezone.now()
    work_item = WorkItem.objects.create(
        organization=org,
        kind="episode.triage",
        status="open",
        assigned_to=user,
        due_at=now + timedelta(minutes=30),
    )

    created = check_sla_notifications(now=now)
    assert created == 1
    assert Notification.objects.filter(
        organization=org, recipient=user, dedupe_key=f"sla:warning:{work_item.id}"
    ).exists()


@pytest.mark.django_db
def test_work_item_assignment_creates_notification(client) -> None:
    user = get_user_model().objects.create_user(username="staff4", password="pass")
    org = Organization.objects.create(name="CareOS", slug="careos4")
    Membership.objects.create(user=user, organization=org, role=Role.STAFF)
    item = WorkItem.objects.create(
        organization=org,
        kind="episode_triage",
        status="open",
    )

    client.force_login(user)
    response = client.post(
        f"/work-items/{item.id}/assign/",
        data=json.dumps({}),
        content_type="application/json",
    )
    assert response.status_code == 200
    assert Notification.objects.filter(
        organization=org, recipient=user, kind="work_item.assigned"
    ).exists()


@pytest.mark.django_db
def test_episode_transition_creates_notification(client) -> None:
    user = get_user_model().objects.create_user(username="staff5", password="pass")
    org = Organization.objects.create(name="CareOS", slug="careos5")
    Membership.objects.create(user=user, organization=org, role=Role.STAFF)
    episode = Episode.objects.create(
        organization=org, title="Episode A", status="triage", assigned_to=user
    )

    client.force_login(user)
    response = client.post(
        f"/episodes/{episode.id}/transition/",
        data=json.dumps({"to_state": "in_progress"}),
        content_type="application/json",
    )
    assert response.status_code == 200
    assert Notification.objects.filter(
        organization=org, recipient=user, kind="episode.transition"
    ).exists()
