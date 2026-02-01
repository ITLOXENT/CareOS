from __future__ import annotations

from django.http import JsonResponse

from careos_api.observability import org_id_ctx, user_id_ctx

from .models import Membership


class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (
            request.path.startswith("/health")
            or request.path.startswith("/healthz")
            or request.path.startswith("/readyz")
            or request.path.startswith("/metrics")
            or request.path.startswith("/patient/")
            or request.path.startswith("/portal/")
            or request.path.startswith("/billing/webhook/")
        ):
            return self.get_response(request)
        if not request.user.is_authenticated:
            return JsonResponse({"detail": "Authentication required."}, status=401)

        membership = self._resolve_membership(request)
        if membership is None:
            return JsonResponse({"detail": "No organization membership."}, status=403)

        request.organization = membership.organization  # type: ignore[attr-defined]
        request.membership = membership  # type: ignore[attr-defined]
        org_id_ctx.set(str(membership.organization_id))
        user_id_ctx.set(str(request.user.id))
        return self.get_response(request)

    def _resolve_membership(self, request) -> Membership | None:
        org_id = request.headers.get("X-Org-ID")
        memberships = Membership.objects.filter(
            user=request.user, is_active=True
        ).select_related("organization")
        if org_id:
            try:
                return memberships.get(organization_id=org_id)
            except Membership.DoesNotExist:
                return None
        return memberships.first()
