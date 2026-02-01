from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from core.models import AuditEvent, Episode, EpisodeEvent, Membership, Organization
from core.rbac import Role


@pytest.mark.django_db
def test_episode_transition_validation(client) -> None:
    user = get_user_model().objects.create_user(username="admin", password="pass")
    org = Organization.objects.create(name="CareOS", slug="careos")
    Membership.objects.create(user=user, organization=org, role=Role.ADMIN)
    episode = Episode.objects.create(organization=org, title="Episode A", created_by=user)

    client.force_login(user)
    response = client.post(
        f"/episodes/{episode.id}/transition/",
        data='{"to_state": "resolved"}',
        content_type="application/json",
    )
    assert response.status_code == 400

    ok = client.post(
        f"/episodes/{episode.id}/transition/",
        data='{"to_state": "triage"}',
        content_type="application/json",
    )
    assert ok.status_code == 200
    assert ok.json()["status"] == "triage"


@pytest.mark.django_db
def test_rbac_blocks_episode_write_for_viewer(client) -> None:
    user = get_user_model().objects.create_user(username="viewer", password="pass")
    org = Organization.objects.create(name="CareOS", slug="careos")
    Membership.objects.create(user=user, organization=org, role=Role.VIEWER)

    client.force_login(user)
    response = client.post(
        "/episodes/",
        data='{"title": "Episode A"}',
        content_type="application/json",
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_rbac_allows_episode_write_for_admin(client) -> None:
    user = get_user_model().objects.create_user(username="admin2", password="pass")
    org = Organization.objects.create(name="CareOS", slug="careos")
    Membership.objects.create(user=user, organization=org, role=Role.ADMIN)

    client.force_login(user)
    response = client.post(
        "/episodes/",
        data='{"title": "Episode B"}',
        content_type="application/json",
    )
    assert response.status_code == 201


@pytest.mark.django_db
def test_rbac_blocks_episode_write_for_staff(client) -> None:
    user = get_user_model().objects.create_user(username="staffer", password="pass")
    org = Organization.objects.create(name="CareOS Staff", slug="careos-staff")
    Membership.objects.create(user=user, organization=org, role=Role.STAFF)

    client.force_login(user)
    response = client.post(
        "/episodes/",
        data='{"title": "Episode Staff"}',
        content_type="application/json",
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_tenant_isolation_on_episode_detail(client) -> None:
    user = get_user_model().objects.create_user(username="staff", password="pass")
    org_a = Organization.objects.create(name="CareOS A", slug="careos-a")
    org_b = Organization.objects.create(name="CareOS B", slug="careos-b")
    Membership.objects.create(user=user, organization=org_a, role=Role.STAFF)
    episode = Episode.objects.create(organization=org_b, title="Episode C")

    client.force_login(user)
    response = client.get(f"/episodes/{episode.id}/")
    assert response.status_code == 404


@pytest.mark.django_db
def test_transition_creates_episode_event_and_audit_event(client) -> None:
    user = get_user_model().objects.create_user(username="admin3", password="pass")
    org = Organization.objects.create(name="CareOS", slug="careos3")
    Membership.objects.create(user=user, organization=org, role=Role.ADMIN)
    episode = Episode.objects.create(organization=org, title="Episode D", created_by=user)

    client.force_login(user)
    response = client.post(
        f"/episodes/{episode.id}/transition/",
        data='{"to_state": "triage"}',
        content_type="application/json",
    )

    assert response.status_code == 200
    assert EpisodeEvent.objects.filter(
        organization=org, episode=episode, event_type="episode.transition"
    ).exists()
    assert AuditEvent.objects.filter(
        organization=org, action="episode.transition", target_id=str(episode.id)
    ).exists()


@pytest.mark.django_db
def test_episode_timeline_pagination(client) -> None:
    user = get_user_model().objects.create_user(username="admin4", password="pass")
    org = Organization.objects.create(name="CareOS", slug="careos4")
    Membership.objects.create(user=user, organization=org, role=Role.ADMIN)
    episode = Episode.objects.create(organization=org, title="Episode E", created_by=user)
    event1 = EpisodeEvent.objects.create(
        organization=org,
        episode=episode,
        created_by=user,
        event_type="episode.created",
        from_state="",
        to_state="new",
    )
    event2 = EpisodeEvent.objects.create(
        organization=org,
        episode=episode,
        created_by=user,
        event_type="episode.transition",
        from_state="new",
        to_state="triage",
    )
    now = timezone.now()
    EpisodeEvent.objects.filter(id__in=[event1.id, event2.id]).update(created_at=now)

    client.force_login(user)
    page1 = client.get(f"/episodes/{episode.id}/timeline/?page=1&page_size=1")
    page2 = client.get(f"/episodes/{episode.id}/timeline/?page=2&page_size=1")
    assert page1.status_code == 200
    assert page2.status_code == 200
    assert page1.json()["count"] == 2
    assert page1.json()["results"][0]["id"] == event1.id
    assert page2.json()["results"][0]["id"] == event2.id


@pytest.mark.django_db
def test_staff_transition_requires_assignment_or_triage(client) -> None:
    user = get_user_model().objects.create_user(username="staff5", password="pass")
    org = Organization.objects.create(name="CareOS Staff5", slug="careos-staff5")
    Membership.objects.create(user=user, organization=org, role=Role.STAFF)
    episode = Episode.objects.create(
        organization=org, title="Episode F", status="in_progress"
    )

    client.force_login(user)
    response = client.post(
        f"/episodes/{episode.id}/transition/",
        data='{"to_state": "waiting"}',
        content_type="application/json",
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_admin_can_cancel_episode(client) -> None:
    user = get_user_model().objects.create_user(username="admin_cancel", password="pass")
    org = Organization.objects.create(name="CareOS Cancel", slug="careos-cancel")
    Membership.objects.create(user=user, organization=org, role=Role.ADMIN)
    episode = Episode.objects.create(organization=org, title="Episode G")

    client.force_login(user)
    response = client.post(
        f"/episodes/{episode.id}/transition/",
        data='{"to_state": "cancelled"}',
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"
