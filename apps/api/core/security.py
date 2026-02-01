from __future__ import annotations

import time
from collections import defaultdict, deque

from django.http import HttpRequest, JsonResponse


class RateLimiter:
    def __init__(self) -> None:
        self._events: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, key: str, limit: int, window_seconds: int) -> bool:
        now = time.time()
        window_start = now - window_seconds
        events = self._events[key]
        while events and events[0] < window_start:
            events.popleft()
        if len(events) >= limit:
            return False
        events.append(now)
        return True


rate_limiter = RateLimiter()


def rate_limit_or_429(
    request: HttpRequest, key: str, limit: int, window_seconds: int
) -> JsonResponse | None:
    if not rate_limiter.allow(key, limit, window_seconds):
        return JsonResponse({"detail": "Too many requests."}, status=429)
    return None


class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response["X-Content-Type-Options"] = "nosniff"
        response["X-Frame-Options"] = "DENY"
        response["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response["Content-Security-Policy"] = "default-src 'self'"
        response["Permissions-Policy"] = "geolocation=(), microphone=()"
        return response


class LoginRateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self._paths = {
            "/portal/auth/login/",
            "/patient/auth/request-otp/",
            "/patient/auth/verify-otp/",
        }

    def __call__(self, request):
        if request.path in self._paths:
            key = f"{request.path}:{request.META.get('REMOTE_ADDR', '')}"
            limited = rate_limit_or_429(request, key=key, limit=10, window_seconds=300)
            if limited:
                return limited
        return self.get_response(request)
