from __future__ import annotations

import hmac
import json
import time
from hashlib import sha256

import pytest
from django.contrib.auth import get_user_model
from django.test.utils import override_settings

from core.models import Membership, Organization, OrganizationSubscription
from core.rbac import Role


def _sign_payload(secret: str, payload: str) -> str:
    timestamp = int(time.time())
    signed_payload = f"{timestamp}.{payload}".encode("utf-8")
    signature = hmac.new(secret.encode("utf-8"), signed_payload, sha256).hexdigest()
    return f"t={timestamp},v1={signature}"


@pytest.mark.django_db
@override_settings(
    STRIPE_WEBHOOK_SECRET="whsec_test",
    BILLING_PLANS=[{"code": "starter", "name": "Starter", "price_id": "price_123", "seats": 5}],
)
def test_webhook_signature_and_status_update(client) -> None:
    org = Organization.objects.create(name="CareOS", slug="careos")
    payload = {
        "type": "customer.subscription.updated",
        "data": {
            "object": {
                "id": "sub_123",
                "status": "active",
                "customer": "cus_123",
                "current_period_end": int(time.time()) + 3600,
                "items": {"data": [{"price": {"id": "price_123"}}]},
                "metadata": {"organization_id": org.id, "plan_code": "starter"},
            }
        },
    }
    body = json.dumps(payload)
    signature = _sign_payload("whsec_test", body)
    response = client.post(
        "/billing/webhook/",
        data=body,
        content_type="application/json",
        HTTP_STRIPE_SIGNATURE=signature,
    )
    assert response.status_code == 200
    subscription = OrganizationSubscription.objects.get(organization=org)
    assert subscription.status == "active"
    assert subscription.plan_code == "starter"
    assert subscription.seat_limit == 5


@pytest.mark.django_db
def test_billing_subscription_tenant_isolation(client) -> None:
    admin = get_user_model().objects.create_user(username="admin", password="pass")
    org_a = Organization.objects.create(name="CareOS A", slug="careos-a")
    org_b = Organization.objects.create(name="CareOS B", slug="careos-b")
    Membership.objects.create(user=admin, organization=org_a, role=Role.ADMIN)
    OrganizationSubscription.objects.create(
        organization=org_b, plan_code="starter", status="active", seat_limit=5
    )

    client.force_login(admin)
    response = client.get("/billing/subscription/")
    assert response.status_code == 200
    assert response.json()["status"] == "inactive"


@pytest.mark.django_db
def test_seat_limit_blocks_invites(client) -> None:
    admin = get_user_model().objects.create_user(username="admin2", password="pass")
    org = Organization.objects.create(name="CareOS", slug="careos2")
    Membership.objects.create(user=admin, organization=org, role=Role.ADMIN)
    OrganizationSubscription.objects.create(
        organization=org, plan_code="starter", status="active", seat_limit=1
    )

    client.force_login(admin)
    response = client.post(
        "/orgs/invites/",
        data=json.dumps({"email": "invite@example.com", "role": "VIEWER"}),
        content_type="application/json",
    )
    assert response.status_code == 400
