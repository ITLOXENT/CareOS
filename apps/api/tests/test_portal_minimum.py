from __future__ import annotations

import hashlib
import json
from datetime import timedelta

import pytest
from django.utils import timezone

from core.models import Episode, EpisodeEvent, Organization, Patient, PortalInvite, PortalNotification


def _portal_token(client, org, patient) -> str:
    token = "portal-token"
    invite = PortalInvite.objects.create(
        organization=org,
        patient=patient,
        email="portal@example.com",
        role="PATIENT",
        token_hash="",
        expires_at=timezone.now() + timedelta(hours=2),
        accepted_at=timezone.now(),
    )
    invite.token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    invite.save(update_fields=["token_hash"])

    login = client.post(
        "/portal/auth/login/",
        data=json.dumps({"email": "portal@example.com"}),
        content_type="application/json",
    )
    assert login.status_code == 200
    return login.json()["token"]


@pytest.mark.django_db
def test_portal_episode_list_and_detail(client) -> None:
    org = Organization.objects.create(name="CareOS", slug="careos-portal")
    patient = Patient.objects.create(organization=org, given_name="Ada", family_name="Lovelace")
    episode = Episode.objects.create(organization=org, patient=patient, title="Episode A")
    EpisodeEvent.objects.create(
        organization=org,
        episode=episode,
        event_type="episode.created",
        from_state="",
        to_state="new",
        note="created",
    )
    token = _portal_token(client, org, patient)

    listing = client.get("/portal/episodes/", HTTP_AUTHORIZATION=f"Bearer {token}")
    assert listing.status_code == 200
    assert listing.json()["results"][0]["id"] == episode.id

    detail = client.get(
        f"/portal/episodes/{episode.id}/", HTTP_AUTHORIZATION=f"Bearer {token}"
    )
    assert detail.status_code == 200
    assert detail.json()["episode"]["id"] == episode.id
    assert len(detail.json()["timeline"]) == 1


@pytest.mark.django_db
def test_portal_notifications_list_and_mark_read(client) -> None:
    org = Organization.objects.create(name="CareOS", slug="careos-portal2")
    patient = Patient.objects.create(organization=org, given_name="Bob", family_name="Jones")
    token = _portal_token(client, org, patient)
    notification = PortalNotification.objects.create(
        organization=org,
        patient=patient,
        title="Reminder",
        body="Check in",
    )

    listing = client.get("/portal/notifications/", HTTP_AUTHORIZATION=f"Bearer {token}")
    assert listing.status_code == 200
    assert listing.json()["results"][0]["id"] == notification.id

    mark = client.post(
        f"/portal/notifications/{notification.id}/read/",
        HTTP_AUTHORIZATION=f"Bearer {token}",
    )
    assert mark.status_code == 200
    assert mark.json()["unread"] is False
