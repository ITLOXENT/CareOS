from __future__ import annotations

import os

from django.db import connections
from django.http import JsonResponse
from django.utils import timezone


def health(_request):
    version = os.environ.get("APP_VERSION", "unknown")
    build_sha = os.environ.get("BUILD_SHA", "unknown")
    db_ok = True
    try:
        connections["default"].ensure_connection()
    except Exception:
        db_ok = False
    return JsonResponse(
        {
            "status": "ok" if db_ok else "degraded",
            "timestamp": timezone.now().isoformat(),
            "version": version,
            "build_sha": build_sha,
            "db_ok": db_ok,
        }
    )


def healthz(_request):
    return JsonResponse({"status": "ok"})


def readyz(_request):
    try:
        connections["default"].ensure_connection()
    except Exception:
        return JsonResponse({"status": "unavailable"}, status=503)
    return JsonResponse({"status": "ok"})
