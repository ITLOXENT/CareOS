from __future__ import annotations


EPISODE_STATES = [
    ("new", "New"),
    ("triage", "Triage"),
    ("in_progress", "In progress"),
    ("waiting", "Waiting"),
    ("resolved", "Resolved"),
    ("closed", "Closed"),
    ("cancelled", "Cancelled"),
]

EPISODE_TRANSITIONS = {
    "new": {"triage"},
    "triage": {"in_progress"},
    "in_progress": {"waiting", "resolved"},
    "waiting": {"in_progress"},
    "resolved": {"closed"},
    "closed": set(),
    "cancelled": set(),
}

WORK_ITEM_STATUSES = [
    ("open", "Open"),
    ("assigned", "Assigned"),
    ("completed", "Completed"),
]

PICKUP_STATUSES = [
    ("not_ready", "Not ready"),
    ("ready", "Ready"),
    ("picked_up", "Picked up"),
]

CAREGIVER_STATUSES = [
    ("invited", "Invited"),
    ("accepted", "Accepted"),
    ("revoked", "Revoked"),
]

MEDICATION_STATUSES = [
    ("taken", "Taken"),
    ("missed", "Missed"),
]

AI_ARTIFACT_STATUSES = [
    ("pending", "Pending"),
    ("approved", "Approved"),
    ("rejected", "Rejected"),
]

INTEROP_STATUSES = [
    ("draft", "Draft"),
    ("queued", "Queued"),
    ("sent", "Sent"),
    ("delivered", "Delivered"),
    ("failed", "Failed"),
]

APPOINTMENT_STATUSES = [
    ("scheduled", "Scheduled"),
    ("in_progress", "In progress"),
    ("completed", "Completed"),
    ("cancelled", "Cancelled"),
    ("missed", "Missed"),
]

APPOINTMENT_TRANSITIONS = {
    "scheduled": {"in_progress", "completed", "cancelled", "missed"},
    "in_progress": {"completed", "cancelled"},
    "completed": set(),
    "cancelled": set(),
    "missed": set(),
}

TASK_STATUSES = [
    ("open", "Open"),
    ("assigned", "Assigned"),
    ("in_progress", "In progress"),
    ("completed", "Completed"),
    ("cancelled", "Cancelled"),
]

TASK_TRANSITIONS = {
    "open": {"assigned", "in_progress", "cancelled"},
    "assigned": {"in_progress", "completed", "cancelled"},
    "in_progress": {"completed", "cancelled"},
    "completed": set(),
    "cancelled": set(),
}

TASK_PRIORITIES = [
    ("low", "Low"),
    ("medium", "Medium"),
    ("high", "High"),
    ("urgent", "Urgent"),
]
