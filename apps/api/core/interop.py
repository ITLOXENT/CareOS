from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Protocol

from django.utils import timezone

from .models import AuditEvent, InteropMessage, InteropStatusEvent


class InteropAdapter(Protocol):
    system_name: str

    def send(self, message: InteropMessage) -> "InteropResult":
        ...


@dataclass(frozen=True)
class InteropResult:
    external_id: str
    delivered: bool
    detail: str = ""


class SimulatorAdapter:
    def __init__(self, system_name: str) -> None:
        self.system_name = system_name

    def send(self, message: InteropMessage) -> InteropResult:
        payload = json.dumps(message.payload, sort_keys=True)
        digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        external_id = f"sim-{self.system_name.lower()}-{digest[:12]}"
        return InteropResult(external_id=external_id, delivered=True, detail="simulated")


def record_status(message: InteropMessage, status: str, detail: str = "") -> None:
    message.status = status
    message.status_reason = detail
    message.save(update_fields=["status", "status_reason", "updated_at"])
    InteropStatusEvent.objects.create(message=message, status=status, detail=detail)


def enqueue_message(message: InteropMessage) -> None:
    record_status(message, "queued", "queued for delivery")
    AuditEvent.objects.create(
        organization=message.organization,
        actor=message.created_by,
        action="interop.queued",
        target_type="InteropMessage",
        target_id=str(message.id),
    )


def process_message(message: InteropMessage, adapter: InteropAdapter) -> None:
    message.attempts += 1
    message.save(update_fields=["attempts", "updated_at"])
    record_status(message, "sent", "sent to adapter")
    result = adapter.send(message)
    message.external_id = result.external_id
    message.save(update_fields=["external_id", "updated_at"])
    if result.delivered:
        record_status(message, "delivered", result.detail)
    else:
        record_status(message, "failed", result.detail)
    AuditEvent.objects.create(
        organization=message.organization,
        actor=message.created_by,
        action="interop.delivered" if result.delivered else "interop.failed",
        target_type="InteropMessage",
        target_id=str(message.id),
        metadata={"external_id": result.external_id, "detail": result.detail},
    )


def process_outbox(messages: list[InteropMessage], adapter: InteropAdapter) -> int:
    processed = 0
    for message in messages:
        process_message(message, adapter)
        processed += 1
    return processed
