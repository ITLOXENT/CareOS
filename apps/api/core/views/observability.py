from __future__ import annotations

from django.http import JsonResponse

from careos_api.observability import metrics


def metrics_snapshot(request):
    snapshot = metrics.snapshot()
    return JsonResponse(
        {
            "total_requests": snapshot.total_requests,
            "last_duration_ms": snapshot.last_duration_ms,
        }
    )


def sentry_debug(request):
    return 1 / 0
