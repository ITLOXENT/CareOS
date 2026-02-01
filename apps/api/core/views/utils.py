from __future__ import annotations

import json
from datetime import datetime

from django.utils import timezone


def parse_date(date_value: str | None) -> datetime.date | None:
    if not date_value:
        return None
    try:
        return datetime.fromisoformat(date_value).date()
    except ValueError:
        return None


def normalize_nhs_number(raw_value: str | None) -> str | None:
    if raw_value is None:
        return None
    value = "".join(str(raw_value).strip().split())
    if not value:
        return None
    return value


def validate_nhs_number(value: str | None) -> bool:
    if value is None:
        return True
    return value.isdigit() and len(value) == 10


def parse_tags(raw_value) -> list[str]:
    if raw_value is None:
        return []
    if isinstance(raw_value, list):
        return [str(item).strip() for item in raw_value if str(item).strip()]
    if isinstance(raw_value, str):
        value = raw_value.strip()
        if not value:
            return []
        if value.startswith("["):
            try:
                parsed = json.loads(value)
                if isinstance(parsed, list):
                    return [str(item).strip() for item in parsed if str(item).strip()]
            except json.JSONDecodeError:
                return [tag.strip() for tag in value.split(",") if tag.strip()]
        return [tag.strip() for tag in value.split(",") if tag.strip()]
    return []


def parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    if timezone.is_naive(parsed):
        return timezone.make_aware(parsed, timezone=timezone.get_current_timezone())
    return parsed
