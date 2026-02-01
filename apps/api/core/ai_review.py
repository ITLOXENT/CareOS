from __future__ import annotations

from dataclasses import dataclass

from django.conf import settings


@dataclass(frozen=True)
class AIReviewResult:
    output: dict
    model_provider: str
    model_name: str
    model_version: str


def run_review(input_type: str, payload: dict) -> AIReviewResult:
    provider = getattr(settings, "AI_REVIEW_PROVIDER", "mock")
    if provider == "mock":
        summary = f"Mock summary for {input_type}"
        if payload.get("text"):
            summary = f"Mock summary for {input_type}: {payload.get('text')[:120]}"
        return AIReviewResult(
            output={"summary": summary},
            model_provider="mock",
            model_name="mock-model",
            model_version="v1",
        )
    raise RuntimeError("AI_REVIEW_PROVIDER not supported")
