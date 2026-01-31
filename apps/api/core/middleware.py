from __future__ import annotations

from django.http import JsonResponse

from .models import Membership


class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith("/health"):
            return self.get_response(request)
        if not request.user.is_authenticated:
            return JsonResponse({"detail": "Authentication required."}, status=401)

        membership = self._resolve_membership(request)
        if membership is None:
            return JsonResponse({"detail": "No organization membership."}, status=403)

        request.organization = membership.organization  # type: ignore[attr-defined]
        request.membership = membership  # type: ignore[attr-defined]
        return self.get_response(request)

    def _resolve_membership(self, request) -> Membership | None:
        org_id = request.headers.get("X-Org-ID")
        memberships = Membership.objects.filter(user=request.user).select_related(
            "organization"
        )
        if org_id:
            try:
                return memberships.get(organization_id=org_id)
            except Membership.DoesNotExist:
                return None
        return memberships.first()
