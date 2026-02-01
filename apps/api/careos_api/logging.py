from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timezone

from .observability import org_id_ctx, request_id_ctx, trace_id_ctx, user_id_ctx


SENSITIVE_FIELDS = [
    "password",
    "secret",
    "token",
    "authorization",
    "cookie",
    "set-cookie",
    "api_key",
    "access_token",
    "refresh_token",
    "email",
    "phone",
    "address",
    "dob",
    "ssn",
]


class RedactionFilter:
    def __init__(self) -> None:
        pattern = "|".join(re.escape(field) for field in SENSITIVE_FIELDS)
        self._regex = re.compile(rf'("{pattern}"\s*:\s*)"([^"]+)"', re.IGNORECASE)

    def filter(self, record) -> bool:  # type: ignore[no-untyped-def]
        message = record.getMessage()
        redacted = self._regex.sub(r'\1"***"', message)
        if redacted != message:
            record.msg = redacted
            record.args = ()
        return True


class RequestIdFilter:
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_ctx.get("-")
        record.trace_id = trace_id_ctx.get("-")
        record.org_id = org_id_ctx.get("-")
        record.user_id = user_id_ctx.get("-")
        return True


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", "-"),
            "trace_id": getattr(record, "trace_id", "-"),
            "org_id": getattr(record, "org_id", "-"),
            "user_id": getattr(record, "user_id", "-"),
        }
        return json.dumps(payload, sort_keys=True)
