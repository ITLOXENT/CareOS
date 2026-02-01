from __future__ import annotations

from dataclasses import dataclass


class Role:
    ADMIN = "ADMIN"
    STAFF = "STAFF"
    VIEWER = "VIEWER"

    @classmethod
    def choices(cls) -> list[tuple[str, str]]:
        return [
            (cls.ADMIN, "Admin"),
            (cls.STAFF, "Staff"),
            (cls.VIEWER, "Viewer"),
        ]


PERMISSIONS = {
    Role.ADMIN: {
        "audit:view",
        "org:manage",
        "team:manage",
        "org:read",
        "episode:read",
        "episode:write",
        "work:read",
        "work:write",
        "ai:write",
        "ai:review",
        "patient:read",
        "patient:write",
        "patient:merge",
        "evidence:read",
        "evidence:write",
        "evidence:link",
        "evidence:tag",
        "notification:read",
        "notification:write",
        "message:read",
        "message:write",
        "integration:read",
        "integration:write",
    },
    Role.STAFF: {
        "org:read",
        "episode:read",
        "episode:write",
        "work:read",
        "work:write",
        "ai:write",
        "ai:review",
        "patient:read",
        "patient:write",
        "patient:merge",
        "evidence:read",
        "evidence:write",
        "evidence:link",
        "evidence:tag",
        "notification:read",
        "notification:write",
        "message:read",
        "message:write",
        "integration:read",
        "integration:write",
    },
    Role.VIEWER: {
        "org:read",
        "episode:read",
        "work:read",
        "evidence:read",
        "notification:read",
        "notification:write",
        "message:read",
        "integration:read",
    },
}


@dataclass(frozen=True)
class PermissionCheck:
    allowed: bool
    reason: str


def has_permission(role: str, permission: str) -> PermissionCheck:
    permissions = PERMISSIONS.get(role, set())
    if permission in permissions:
        return PermissionCheck(True, "allowed")
    return PermissionCheck(False, f"role {role} lacks {permission}")


def is_valid_role(role: str) -> bool:
    return role in {Role.ADMIN, Role.STAFF, Role.VIEWER}
