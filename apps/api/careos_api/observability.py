from __future__ import annotations

import importlib.util
import os
import time
import uuid
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Callable

from django.http import HttpRequest, HttpResponse


request_id_ctx: ContextVar[str] = ContextVar("request_id", default="-")
trace_id_ctx: ContextVar[str] = ContextVar("trace_id", default="-")
org_id_ctx: ContextVar[str] = ContextVar("org_id", default="-")
user_id_ctx: ContextVar[str] = ContextVar("user_id", default="-")


@dataclass
class MetricsSnapshot:
    total_requests: int
    last_duration_ms: float


class MetricsCollector:
    def __init__(self) -> None:
        self.total_requests = 0
        self.last_duration_ms = 0.0

    def record(self, duration_ms: float) -> None:
        self.total_requests += 1
        self.last_duration_ms = duration_ms

    def snapshot(self) -> MetricsSnapshot:
        return MetricsSnapshot(
            total_requests=self.total_requests,
            last_duration_ms=self.last_duration_ms,
        )


metrics = MetricsCollector()


class RequestContextMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request_id_ctx.set(request_id)
        trace_id_ctx.set(request.headers.get("X-Trace-ID", request_id))
        org_id_ctx.set("-")
        user_id_ctx.set("-")
        start = time.time()
        response = self.get_response(request)
        duration_ms = (time.time() - start) * 1000
        metrics.record(duration_ms)
        response["X-Request-ID"] = request_id
        return response


def init_error_reporting() -> None:
    dsn = os.environ.get("SENTRY_DSN")
    if not dsn:
        return
    if importlib.util.find_spec("sentry_sdk") is None:
        return
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    traces_sample_rate = float(os.environ.get("SENTRY_TRACES_SAMPLE_RATE", "0.0"))
    send_default_pii = (
        os.environ.get("SENTRY_SEND_DEFAULT_PII", "false").lower() == "true"
    )
    environment = os.environ.get("SENTRY_ENVIRONMENT", os.environ.get("DJANGO_ENV", "dev"))
    release = os.environ.get("SENTRY_RELEASE")
    sentry_sdk.init(
        dsn=dsn,
        integrations=[DjangoIntegration()],
        traces_sample_rate=traces_sample_rate,
        environment=environment,
        release=release,
        send_default_pii=send_default_pii,
    )
