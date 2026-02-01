from __future__ import annotations

import json
from datetime import datetime

import pytest
from django.contrib.auth import get_user_model
from zoneinfo import ZoneInfo

from core.evidence import build_manifest, verify_hash_chain
from core.models import Episode, EpisodeEvent, FormResponse, FormTemplate, Membership, Organization, Signature
from core.rbac import Role


@pytest.mark.django_db
def test_evidence_pack_determinism() -> None:
    user = get_user_model().objects.create_user(username="admin", password="pass")
    org = Organization.objects.create(name="CareOS", slug="careos")
    Membership.objects.create(user=user, organization=org, role=Role.ADMIN)
    episode = Episode.objects.create(organization=org, title="Episode A", created_by=user)

    event1 = EpisodeEvent.objects.create(
        organization=org,
        episode=episode,
        created_by=user,
        event_type="episode.created",
        from_state="",
        to_state="new",
        note="created",
    )
    event2 = EpisodeEvent.objects.create(
        organization=org,
        episode=episode,
        created_by=user,
        event_type="episode.transition",
        from_state="new",
        to_state="in_progress",
        note="progress",
    )
    EpisodeEvent.objects.filter(id=event1.id).update(created_at=datetime(2026, 1, 1, tzinfo=ZoneInfo("UTC")))
    EpisodeEvent.objects.filter(id=event2.id).update(created_at=datetime(2026, 1, 2, tzinfo=ZoneInfo("UTC")))

    template = FormTemplate.objects.create(name="Test", version=1, schema={"required": []})
    response = FormResponse.objects.create(
        organization=org, episode=episode, template=template, data={}, created_by=user
    )
    Signature.objects.create(response=response, signer=user, template_version=1)

    events = EpisodeEvent.objects.filter(episode=episode).order_by("created_at", "id")
    signatures = Signature.objects.filter(response__episode=episode).order_by("signed_at")
    manifest_a = build_manifest(events, signatures)
    manifest_b = build_manifest(events, signatures)

    assert json.dumps(manifest_a, sort_keys=True) == json.dumps(manifest_b, sort_keys=True)
    assert verify_hash_chain(manifest_a["events"]) is True


@pytest.mark.django_db
def test_hash_chain_verification_detects_tamper() -> None:
    user = get_user_model().objects.create_user(username="admin2", password="pass")
    org = Organization.objects.create(name="CareOS", slug="careos2")
    episode = Episode.objects.create(organization=org, title="Episode B", created_by=user)
    event = EpisodeEvent.objects.create(
        organization=org,
        episode=episode,
        created_by=user,
        event_type="episode.created",
        from_state="",
        to_state="new",
        note="created",
    )
    events = EpisodeEvent.objects.filter(episode=episode).order_by("created_at", "id")
    manifest = build_manifest(events, [])
    manifest["events"][0]["note"] = "tampered"

    assert verify_hash_chain(manifest["events"]) is False
