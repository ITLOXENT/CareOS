from __future__ import annotations

from datetime import timedelta

from django.conf import settings
from django.db import models
from django.core.mail import send_mail
from django.utils import timezone

from .models import AuditEvent, Notification, WorkItem


def send_notification_email(notification: Notification) -> None:
    recipient = notification.recipient
    if not recipient or not recipient.email:
        return
    subject = f"[CareOS] {notification.title}"
    body = notification.body or notification.title
    send_mail(
        subject=subject,
        message=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[recipient.email],
        fail_silently=True,
    )


def create_notification(
    *,
    organization,
    recipient,
    kind: str,
    title: str,
    body: str,
    url: str,
    dedupe_key: str | None = None,
    actor=None,
    metadata: dict | None = None,
) -> tuple[Notification, bool]:
    notification, created = Notification.objects.get_or_create(
        organization=organization,
        recipient=recipient,
        dedupe_key=dedupe_key,
        defaults={
            "kind": kind,
            "title": title,
            "body": body,
            "url": url,
        },
    )
    if created:
        AuditEvent.objects.create(
            organization=organization,
            actor=actor,
            action="notification.created",
            target_type="Notification",
            target_id=str(notification.id),
            metadata=metadata or {},
        )
        send_notification_email(notification)
    return notification, created


def check_sla_notifications(now=None) -> int:
    now = now or timezone.now()
    warning_minutes = getattr(settings, "SLA_WARNING_MINUTES", 60)
    warning_threshold = now + timedelta(minutes=warning_minutes)

    items = WorkItem.objects.filter(
        status__in=["open", "assigned"],
        assigned_to__isnull=False,
    ).filter(
        (
            models.Q(sla_breach_at__isnull=False, sla_breach_at__lte=warning_threshold)
            | models.Q(sla_breach_at__isnull=True, due_at__isnull=False, due_at__lte=warning_threshold)
        )
    )

    created_count = 0
    for item in items.select_related("organization", "episode", "assigned_to"):
        breach_at = item.sla_breach_at or item.due_at
        if not breach_at:
            continue
        status = "breach" if breach_at <= now else "warning"
        dedupe_key = f"sla:{status}:{item.id}"
        title = "Work item SLA breached" if status == "breach" else "Work item SLA warning"
        body = f"{item.kind} work item {item.id} is {status}."
        url = f"/episodes/{item.episode_id}" if item.episode_id else "/inbox"
        _notification, created = create_notification(
            organization=item.organization,
            recipient=item.assigned_to,
            kind="sla",
            title=title,
            body=body,
            url=url,
            dedupe_key=dedupe_key,
            actor=None,
            metadata={"work_item_id": item.id, "status": status},
        )
        if created:
            created_count += 1
    return created_count
