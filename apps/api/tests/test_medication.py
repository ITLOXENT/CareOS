from __future__ import annotations

from datetime import datetime

import pytest
from zoneinfo import ZoneInfo

from core.medication import next_reminders
from core.models import PatientOTP


def test_next_reminders_rolls_forward() -> None:
    now = datetime(2026, 1, 31, 20, 30, tzinfo=ZoneInfo("UTC"))
    reminders = next_reminders(times=["08:00", "20:00"], now=now, timezone="UTC")
    assert reminders[0].scheduled_at.hour == 8
    assert reminders[0].scheduled_at.day == 1
    assert reminders[1].scheduled_at.hour == 20
    assert reminders[1].scheduled_at.day == 1


@pytest.mark.django_db
def test_schedule_sync_flow(client) -> None:
    response = client.post(
        "/patient/auth/request-otp/",
        data='{"phone": "+15551234567"}',
        content_type="application/json",
    )
    assert response.status_code == 200
    otp = PatientOTP.objects.latest("created_at")

    verify = client.post(
        "/patient/auth/verify-otp/",
        data=f'{{"phone": "+15551234567", "code": "{otp.code}"}}',
        content_type="application/json",
    )
    assert verify.status_code == 200
    token = verify.json()["token"]

    create = client.post(
        "/patient/medication-schedules/",
        data='{"name": "Amoxicillin", "times": ["08:00", "20:00"], "start_date": "2026-01-31"}',
        content_type="application/json",
        **{"HTTP_AUTHORIZATION": f"Bearer {token}"},
    )
    assert create.status_code == 201

    listing = client.get(
        "/patient/medication-schedules/",
        **{"HTTP_AUTHORIZATION": f"Bearer {token}"},
    )
    assert listing.status_code == 200
    assert listing.json()["results"]
