from __future__ import annotations

import json

import pytest
from django.contrib.auth import get_user_model
from django.test.utils import override_settings

from core.models import AIReviewRequest, Membership, Organization
from core.rbac import Role


@pytest.mark.django_db
@override_settings(AI_REVIEW_PROVIDER="mock")
def test_staff_can_create_ai_review_and_get_result(client) -> None:
    user = get_user_model().objects.create_user(username="staff", password="pass")
    org = Organization.objects.create(name="CareOS", slug="careos")
    Membership.objects.create(user=user, organization=org, role=Role.STAFF)

    client.force_login(user)
    create = client.post(
        "/ai/review/",
        data=json.dumps({"input_type": "episode.summary", "payload": {"text": "Hello"}}),
        content_type="application/json",
    )
    assert create.status_code == 201
    review_id = create.json()["id"]

    detail = client.get(f"/ai/review/{review_id}/")
    assert detail.status_code == 200
    assert detail.json()["status"] in {"processing", "completed"}
    assert "output" in detail.json()


@pytest.mark.django_db
@override_settings(
    AI_REVIEW_PROVIDER="mock",
    BILLING_ENTITLEMENTS={"starter": {"ai_review_quota": 1}},
    BILLING_DEFAULT_PLAN="starter",
)
def test_ai_review_quota_enforced(client) -> None:
    user = get_user_model().objects.create_user(username="quota", password="pass")
    org = Organization.objects.create(name="CareOS Quota", slug="careos-quota")
    Membership.objects.create(user=user, organization=org, role=Role.STAFF)

    client.force_login(user)
    first = client.post(
        "/ai/review/",
        data=json.dumps({"input_type": "episode.summary", "payload": {"text": "Hello"}}),
        content_type="application/json",
    )
    assert first.status_code == 201

    second = client.post(
        "/ai/review/",
        data=json.dumps({"input_type": "episode.summary", "payload": {"text": "Again"}}),
        content_type="application/json",
    )
    assert second.status_code == 402
    assert second.json()["code"] == "billing.ai_review_quota"


@pytest.mark.django_db
def test_viewer_cannot_create_ai_review(client) -> None:
    user = get_user_model().objects.create_user(username="viewer", password="pass")
    org = Organization.objects.create(name="CareOS", slug="careos2")
    Membership.objects.create(user=user, organization=org, role=Role.VIEWER)

    client.force_login(user)
    response = client.post(
        "/ai/review/",
        data=json.dumps({"input_type": "episode.summary"}),
        content_type="application/json",
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_ai_review_tenant_isolation(client) -> None:
    user = get_user_model().objects.create_user(username="admin", password="pass")
    org_a = Organization.objects.create(name="CareOS A", slug="careos-a")
    org_b = Organization.objects.create(name="CareOS B", slug="careos-b")
    Membership.objects.create(user=user, organization=org_a, role=Role.ADMIN)
    review = AIReviewRequest.objects.create(
        organization=org_b, input_type="episode.summary", payload={}, status="pending"
    )

    client.force_login(user)
    response = client.get(f"/ai/review/{review.id}/")
    assert response.status_code == 404
