from __future__ import annotations

import json
import hashlib
from datetime import timedelta

from django.core import signing
from django.http import JsonResponse
from django.utils import timezone

from ..models import AuditEvent, Membership, OrgInvite, OrganizationSubscription
from ..rbac import Role, has_permission, is_valid_role


def org_members_list(request):
    membership = request.membership  # type: ignore[attr-defined]
    permission = has_permission(membership.role, "org:manage")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    members = (
        Membership.objects.filter(organization=membership.organization)
        .select_related("user")
        .order_by("user__username")
    )
    payload = [
        {
            "id": member.id,
            "user_id": member.user_id,
            "email": member.user.email,
            "username": member.user.username,
            "role": member.role,
            "is_active": member.is_active,
        }
        for member in members
    ]
    return JsonResponse({"results": payload})


def org_invites(request):
    membership = request.membership  # type: ignore[attr-defined]
    permission = has_permission(membership.role, "org:manage")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    if request.method == "POST":
        payload = json.loads(request.body or "{}")
        email = str(payload.get("email", "")).strip().lower()
        role = str(payload.get("role", Role.VIEWER))
        if not email:
            return JsonResponse({"detail": "email is required"}, status=400)
        if not is_valid_role(role):
            return JsonResponse({"detail": "invalid role"}, status=400)
        subscription = OrganizationSubscription.objects.filter(
            organization=membership.organization
        ).first()
        if subscription and subscription.seat_limit:
            active_members = Membership.objects.filter(
                organization=membership.organization, is_active=True
            ).count()
            pending_invites = OrgInvite.objects.filter(
                organization=membership.organization, accepted_at__isnull=True
            ).count()
            if active_members + pending_invites >= subscription.seat_limit:
                return JsonResponse({"detail": "seat limit reached"}, status=400)
        expires_in_hours = int(payload.get("expires_in_hours", 72))
        expires_at = timezone.now() + timedelta(hours=expires_in_hours)
        token_payload = {
            "org_id": membership.organization_id,
            "email": email,
            "role": role,
            "exp": expires_at.isoformat(),
        }
        token = signing.dumps(token_payload, salt="org-invite")
        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
        invite = OrgInvite.objects.create(
            organization=membership.organization,
            email=email,
            role=role,
            token_hash=token_hash,
            expires_at=expires_at,
            invited_by=request.user,
        )
        AuditEvent.objects.create(
            organization=membership.organization,
            actor=request.user,
            action="org.invite.created",
            target_type="OrgInvite",
            target_id=str(invite.id),
            metadata={"email": email, "role": role},
        )
        return JsonResponse(
            {
                "id": invite.id,
                "email": invite.email,
                "role": invite.role,
                "expires_at": invite.expires_at.isoformat(),
                "token": token,
            },
            status=201,
        )
    invites = OrgInvite.objects.filter(
        organization=membership.organization, accepted_at__isnull=True
    ).order_by("-created_at")
    payload = [
        {
            "id": invite.id,
            "email": invite.email,
            "role": invite.role,
            "expires_at": invite.expires_at.isoformat(),
            "created_at": invite.created_at.isoformat(),
        }
        for invite in invites
    ]
    return JsonResponse({"results": payload})


def org_member_change_role(request, member_id: int):
    membership = request.membership  # type: ignore[attr-defined]
    permission = has_permission(membership.role, "org:manage")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    target = Membership.objects.filter(
        organization=membership.organization, id=member_id
    ).first()
    if not target:
        return JsonResponse({"detail": "Not found."}, status=404)
    payload = json.loads(request.body or "{}")
    role = str(payload.get("role", "")).strip()
    if not is_valid_role(role):
        return JsonResponse({"detail": "invalid role"}, status=400)
    target.role = role
    target.save(update_fields=["role"])
    AuditEvent.objects.create(
        organization=membership.organization,
        actor=request.user,
        action="org.member.role_changed",
        target_type="Membership",
        target_id=str(target.id),
        metadata={"role": role},
    )
    return JsonResponse({"id": target.id, "role": target.role})


def org_member_deactivate(request, member_id: int):
    membership = request.membership  # type: ignore[attr-defined]
    permission = has_permission(membership.role, "org:manage")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    target = Membership.objects.filter(
        organization=membership.organization, id=member_id
    ).first()
    if not target:
        return JsonResponse({"detail": "Not found."}, status=404)
    target.is_active = False
    target.deactivated_at = timezone.now()
    target.save(update_fields=["is_active", "deactivated_at"])
    AuditEvent.objects.create(
        organization=membership.organization,
        actor=request.user,
        action="org.member.deactivated",
        target_type="Membership",
        target_id=str(target.id),
    )
    return JsonResponse({"id": target.id, "is_active": target.is_active})
