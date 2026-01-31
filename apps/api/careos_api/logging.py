from __future__ import annotations

import re


SENSITIVE_FIELDS = [
    "password",
    "secret",
    "token",
    "authorization",
    "api_key",
    "access_token",
    "refresh_token",
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
