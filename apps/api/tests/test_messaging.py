from __future__ import annotations

import json

import pytest
from django.contrib.auth import get_user_model

from core.models import AuditEvent, Conversation, Membership, Message, MessageRead, Organization
from core.rbac import Role


@pytest.mark.django_db
def test_staff_can_create_conversation_send_and_read(client) -> None:
    sender = get_user_model().objects.create_user(username="staff", password="pass")
    recipient = get_user_model().objects.create_user(username="staff2", password="pass")
    org = Organization.objects.create(name="CareOS", slug="careos")
    Membership.objects.create(user=sender, organization=org, role=Role.STAFF)
    Membership.objects.create(user=recipient, organization=org, role=Role.STAFF)

    client.force_login(sender)
    create = client.post(
        "/conversations/",
        data=json.dumps({"participants": [recipient.id]}),
        content_type="application/json",
    )
    assert create.status_code == 201
    conversation_id = create.json()["id"]

    send = client.post(
        f"/conversations/{conversation_id}/messages/",
        data=json.dumps({"body": "Hello"}),
        content_type="application/json",
    )
    assert send.status_code == 201
    message_id = send.json()["id"]
    assert AuditEvent.objects.filter(
        organization=org, action="message.sent", target_id=str(message_id)
    ).exists()

    read = client.post(f"/messages/{message_id}/read/")
    assert read.status_code == 200
    assert MessageRead.objects.filter(message_id=message_id, reader=sender).exists()


@pytest.mark.django_db
def test_viewer_cannot_send_messages(client) -> None:
    sender = get_user_model().objects.create_user(username="viewer", password="pass")
    org = Organization.objects.create(name="CareOS", slug="careos2")
    Membership.objects.create(user=sender, organization=org, role=Role.VIEWER)
    conversation = Conversation.objects.create(organization=org)
    conversation.participants.add(sender)

    client.force_login(sender)
    send = client.post(
        f"/conversations/{conversation.id}/messages/",
        data=json.dumps({"body": "Nope"}),
        content_type="application/json",
    )
    assert send.status_code == 403


@pytest.mark.django_db
def test_conversation_tenant_isolation(client) -> None:
    user = get_user_model().objects.create_user(username="staff3", password="pass")
    org_a = Organization.objects.create(name="CareOS A", slug="careos-a")
    org_b = Organization.objects.create(name="CareOS B", slug="careos-b")
    Membership.objects.create(user=user, organization=org_a, role=Role.STAFF)
    conversation = Conversation.objects.create(organization=org_b)

    client.force_login(user)
    response = client.get(f"/conversations/{conversation.id}/")
    assert response.status_code == 404
