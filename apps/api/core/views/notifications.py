from __future__ import annotations

from django.http import JsonResponse
from django.utils import timezone

from ..models import AuditEvent, Notification
from ..rbac import has_permission


def notifications_list(request):
    membership = request.membership  # type: ignore[attr-defined]
    permission = has_permission(membership.role, "notification:read")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    notifications = Notification.objects.filter(
        organization=membership.organization, recipient=request.user
    ).order_by("-created_at")
    unread_filter = request.GET.get("unread_only") or request.GET.get("unread")
    if unread_filter in {"1", "true", "True"}:
        notifications = notifications.filter(unread=True)
    try:
        page = max(int(request.GET.get("page", "1")), 1)
    except ValueError:
        page = 1
    limit = request.GET.get("limit")
    if limit:
        page_size_value = limit
    else:
        page_size_value = request.GET.get("page_size", "50")
    try:
        page_size = min(max(int(page_size_value), 1), 200)
    except ValueError:
        page_size = 50
    total = notifications.count()
    start_index = (page - 1) * page_size
    notifications = notifications[start_index : start_index + page_size]
    payload = [
        {
            "id": notification.id,
            "kind": notification.kind,
            "title": notification.title,
            "body": notification.body,
            "url": notification.url,
            "unread": notification.unread,
            "read_at": notification.read_at.isoformat()
            if notification.read_at
            else None,
            "created_at": notification.created_at.isoformat(),
        }
        for notification in notifications
    ]
    return JsonResponse(
        {"results": payload, "count": total, "page": page, "page_size": page_size}
    )


def notification_mark_read(request, notification_id: int):
    membership = request.membership  # type: ignore[attr-defined]
    permission = has_permission(membership.role, "notification:write")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    notification = Notification.objects.filter(
        organization=membership.organization,
        recipient=request.user,
        id=notification_id,
    ).first()
    if not notification:
        return JsonResponse({"detail": "Not found."}, status=404)
    if notification.unread:
        notification.unread = False
        notification.read_at = timezone.now()
        notification.save(update_fields=["unread", "read_at"])
        AuditEvent.objects.create(
            organization=membership.organization,
            actor=request.user,
            action="notification.read",
            target_type="Notification",
            target_id=str(notification.id),
        )
    return JsonResponse(
        {
            "id": notification.id,
            "unread": notification.unread,
            "read_at": notification.read_at.isoformat()
            if notification.read_at
            else None,
        }
    )
