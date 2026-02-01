from __future__ import annotations

import json

import pytest
from django.contrib.auth import get_user_model

from core.models import AIReviewItem, AuditEvent, Membership, Organization
from core.rbac import Role


@pytest.mark.django_db
def test_ai_review_items_list_pending_only(client) -> None:
    user = get_user_model().objects.create_user(username="staff", password="pass")
    org = Organization.objects.create(name="CareOS", slug="careos")
    Membership.objects.create(user=user, organization=org, role=Role.STAFF)
    AIReviewItem.objects.create(
        organization=org, kind="episode.summary", payload_json={"text": "a"}, status="pending"
    )
    AIReviewItem.objects.create(
        organization=org,
        kind="episode.summary",
        payload_json={"text": "b"},
        status="approved",
    )

    client.force_login(user)
    response = client.get("/ai-review-items/")
    assert response.status_code == 200
    assert len(response.json()["results"]) == 1


@pytest.mark.django_db
def test_admin_can_decide_ai_review_item(client) -> None:
    admin = get_user_model().objects.create_user(username="admin", password="pass")
    org = Organization.objects.create(name="CareOS2", slug="careos2")
    Membership.objects.create(user=admin, organization=org, role=Role.ADMIN)
    item = AIReviewItem.objects.create(
        organization=org, kind="episode.summary", payload_json={"text": "x"}
    )

    client.force_login(admin)
    response = client.post(
        f"/ai-review-items/{item.id}/decide/",
        data=json.dumps({"decision": "approved", "note": "looks good"}),
        content_type="application/json",
    )
    assert response.status_code == 200
    item.refresh_from_db()
    assert item.status == "approved"
    assert AuditEvent.objects.filter(
        organization=org, action="ai_review_item.decided", target_id=str(item.id)
    ).exists()


@pytest.mark.django_db
def test_staff_cannot_decide_ai_review_item(client) -> None:
    user = get_user_model().objects.create_user(username="staff2", password="pass")
    org = Organization.objects.create(name="CareOS3", slug="careos3")
    Membership.objects.create(user=user, organization=org, role=Role.STAFF)
    item = AIReviewItem.objects.create(
        organization=org, kind="episode.summary", payload_json={"text": "x"}
    )

    client.force_login(user)
    response = client.post(
        f"/ai-review-items/{item.id}/decide/",
        data=json.dumps({"decision": "approved"}),
        content_type="application/json",
    )
    assert response.status_code == 403
