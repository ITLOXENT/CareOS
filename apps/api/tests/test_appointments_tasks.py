from __future__ import annotations

import json
from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from core.models import Appointment, Membership, Organization, Task
from core.rbac import Role


@pytest.mark.django_db
def test_appointment_transitions(client) -> None:
    user = get_user_model().objects.create_user(username="staff_appt", password="pass")
    org = Organization.objects.create(name="CareOS", slug="careos-appt")
    Membership.objects.create(user=user, organization=org, role=Role.STAFF)
    appointment = Appointment.objects.create(
        organization=org, scheduled_at=timezone.now() + timedelta(hours=2)
    )

    client.force_login(user)
    bad = client.post(
        f"/appointments/{appointment.id}/transition/",
        data=json.dumps({"to_state": "completed"}),
        content_type="application/json",
    )
    assert bad.status_code == 200
    appointment.refresh_from_db()
    assert appointment.status == "completed"

    invalid = client.post(
        f"/appointments/{appointment.id}/transition/",
        data=json.dumps({"to_state": "scheduled"}),
        content_type="application/json",
    )
    assert invalid.status_code == 400


@pytest.mark.django_db
def test_task_assign_and_complete(client) -> None:
    user = get_user_model().objects.create_user(username="staff_task", password="pass")
    org = Organization.objects.create(name="CareOS", slug="careos-task")
    Membership.objects.create(user=user, organization=org, role=Role.STAFF)

    client.force_login(user)
    created = client.post(
        "/tasks/",
        data=json.dumps({"title": "Follow up"}),
        content_type="application/json",
    )
    assert created.status_code == 201
    task_id = created.json()["id"]

    assign = client.post(
        f"/tasks/{task_id}/assign/",
        data=json.dumps({}),
        content_type="application/json",
    )
    assert assign.status_code == 200
    task = Task.objects.get(id=task_id)
    assert task.assigned_to_id == user.id
    assert task.status == "assigned"
    assert task.work_item_id is not None

    complete = client.post(f"/tasks/{task.id}/complete/")
    assert complete.status_code == 200
    task.refresh_from_db()
    assert task.status == "completed"
