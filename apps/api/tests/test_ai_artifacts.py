from __future__ import annotations

import json

import pytest
from django.contrib.auth import get_user_model

from core.models import AIArtifact, AuditEvent, Episode, Membership, Organization
from core.rbac import Role


@pytest.mark.django_db
def test_ai_artifacts_require_approval_for_evidence_pack(client) -> None:
    user = get_user_model().objects.create_user(username="admin", password="pass")
    org = Organization.objects.create(name="CareOS", slug="careos")
    Membership.objects.create(user=user, organization=org, role=Role.ADMIN)
    episode = Episode.objects.create(organization=org, title="Episode A", created_by=user)

    client.force_login(user)
    response = client.post(
        "/ai/triage/suggest/",
        data=json.dumps({"episode_id": episode.id, "input": "Vitals: 120/80"}),
        content_type="application/json",
    )
    assert response.status_code == 201

    blocked = client.post(f"/episodes/{episode.id}/evidence-pack/generate/")
    assert blocked.status_code == 400

    artifact_id = response.json()["id"]
    approve = client.post(f"/ai/{artifact_id}/approve/")
    assert approve.status_code == 200

    ok = client.post(f"/episodes/{episode.id}/evidence-pack/generate/")
    assert ok.status_code == 200


@pytest.mark.django_db
def test_ai_approval_creates_audit_event(client) -> None:
    user = get_user_model().objects.create_user(username="admin2", password="pass")
    org = Organization.objects.create(name="CareOS", slug="careos2")
    Membership.objects.create(user=user, organization=org, role=Role.ADMIN)
    episode = Episode.objects.create(organization=org, title="Episode B", created_by=user)
    artifact = AIArtifact.objects.create(
        organization=org,
        episode=episode,
        artifact_type="note",
        version=1,
        confidence=0.7,
        policy_version="v1",
        status="pending",
        content={"summary": "Draft note"},
        prompt_redacted={"input": "note"},
        created_by=user,
    )

    client.force_login(user)
    response = client.post(f"/ai/{artifact.id}/approve/")
    assert response.status_code == 200

    events = list(
        AuditEvent.objects.filter(
            organization=org, action="ai.approved", target_id=str(artifact.id)
        )
    )
    assert events


@pytest.mark.django_db
def test_ai_prompt_redaction_masks_sensitive_fields(client) -> None:
    user = get_user_model().objects.create_user(username="admin3", password="pass")
    org = Organization.objects.create(name="CareOS", slug="careos3")
    Membership.objects.create(user=user, organization=org, role=Role.ADMIN)
    episode = Episode.objects.create(organization=org, title="Episode C", created_by=user)

    client.force_login(user)
    response = client.post(
        "/ai/note/draft/",
        data=json.dumps(
            {
                "episode_id": episode.id,
                "prompt": "Call +15551234567 or email test@example.com",
                "token": "abcdefghijklmnopqrstuvwxyz1234567890",
            }
        ),
        content_type="application/json",
    )
    assert response.status_code == 201
    artifact = AIArtifact.objects.get(id=response.json()["id"])
    redacted = json.dumps(artifact.prompt_redacted)
    assert "test@example.com" not in redacted
    assert "+15551234567" not in redacted
