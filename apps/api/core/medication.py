from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo


@dataclass(frozen=True)
class ReminderWindow:
    scheduled_at: datetime


def next_reminders(
    *,
    times: list[str],
    now: datetime,
    timezone: str,
) -> list[ReminderWindow]:
    tz = ZoneInfo(timezone)
    localized_now = now.astimezone(tz)
    results: list[ReminderWindow] = []
    for entry in sorted(times):
        hour, minute = entry.split(":")
        scheduled = datetime.combine(
            localized_now.date(),
            time(int(hour), int(minute)),
            tzinfo=tz,
        )
        if scheduled < localized_now:
            scheduled += timedelta(days=1)
        results.append(ReminderWindow(scheduled_at=scheduled))
    return results
