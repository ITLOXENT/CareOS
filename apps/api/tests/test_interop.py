from __future__ import annotations

import json

import pytest
from django.contrib.auth import get_user_model
from django.test.utils import override_settings

from core.models import InteropMessage, Membership, Organization
from core.rbac import Role


@pytest.mark.django_db
@override_settings(INTEROP_SIMULATOR_ENABLED=True)
def test_interop_message_lifecycle(client) -> None:
    user = get_user_model().objects.create_user(username="admin", password="pass")
    org = Organization.objects.create(name="CareOS", slug="careos")
    Membership.objects.create(user=user, organization=org, role=Role.ADMIN)

    client.force_login(user)
    create = client.post(
        "/interop/messages/",
        data=json.dumps(
            {
                "external_system": "NHS",
                "payload": {"patient_id": "123", "action": "update"},
                "simulator": True,
            }
        ),
        content_type="application/json",
    )
    assert create.status_code == 201
    message_id = create.json()["id"]

    process = client.post("/interop/process/")
    assert process.status_code == 200
    message = InteropMessage.objects.get(id=message_id)
    assert message.status == "delivered"
    assert message.status_events.exists()


@pytest.mark.django_db
@override_settings(INTEROP_SIMULATOR_ENABLED=True)
def test_interop_simulator_determinism(client) -> None:
    user = get_user_model().objects.create_user(username="admin2", password="pass")
    org = Organization.objects.create(name="CareOS", slug="careos2")
    Membership.objects.create(user=user, organization=org, role=Role.ADMIN)

    client.force_login(user)
    payload = {"external_system": "US", "payload": {"patient_id": "A1"}, "simulator": True}
    create1 = client.post("/interop/messages/", data=json.dumps(payload), content_type="application/json")
    create2 = client.post("/interop/messages/", data=json.dumps(payload), content_type="application/json")
    assert create1.status_code == 201
    assert create2.status_code == 201

    client.post("/interop/process/")
    client.post("/interop/process/")
    msg1 = InteropMessage.objects.get(id=create1.json()["id"])
    msg2 = InteropMessage.objects.get(id=create2.json()["id"])
    assert msg1.external_id == msg2.external_id
