from __future__ import annotations

import re


REDACT_PATTERNS = [
    (re.compile(r"\b[\w\.-]+@[\w\.-]+\.\w+\b"), "[REDACTED_EMAIL]"),
    (re.compile(r"\+?\d[\d\-\s]{7,}\d"), "[REDACTED_PHONE]"),
    (re.compile(r"\b[A-Za-z0-9_\-]{24,}\b"), "[REDACTED_TOKEN]"),
]


def redact_prompt(payload: dict) -> dict:
    def _redact_value(value):
        if isinstance(value, str):
            redacted = value
            for pattern, replacement in REDACT_PATTERNS:
                redacted = pattern.sub(replacement, redacted)
            return redacted
        if isinstance(value, dict):
            return {key: _redact_value(val) for key, val in value.items()}
        if isinstance(value, list):
            return [_redact_value(item) for item in value]
        return value

    return _redact_value(payload)


def build_ai_content(artifact_type: str, payload: dict) -> dict:
    summary = f"{artifact_type} suggestion generated"
    return {
        "summary": summary,
        "input_keys": sorted(payload.keys()),
        "recommendations": payload.get("recommendations", []),
    }
