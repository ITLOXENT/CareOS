from __future__ import annotations

from dataclasses import dataclass


class Role:
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"
    AUDITOR = "AUDITOR"

    @classmethod
    def choices(cls) -> list[tuple[str, str]]:
        return [
            (cls.OWNER, "Owner"),
            (cls.ADMIN, "Admin"),
            (cls.MEMBER, "Member"),
            (cls.AUDITOR, "Auditor"),
        ]


PERMISSIONS = {
    Role.OWNER: {"audit:view", "org:manage", "team:manage"},
    Role.ADMIN: {"audit:view", "org:manage", "team:manage"},
    Role.MEMBER: {"org:read"},
    Role.AUDITOR: {"audit:view", "org:read"},
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
    return role in {Role.OWNER, Role.ADMIN, Role.MEMBER, Role.AUDITOR}
