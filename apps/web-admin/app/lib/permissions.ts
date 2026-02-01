export type NavItem = {
  label: string;
  href: string;
  permissions: string[];
};

export const NAV_ITEMS: NavItem[] = [
  { label: "Inbox", href: "/inbox", permissions: ["org:read"] },
  { label: "Episodes", href: "/episodes", permissions: ["org:read"] },
  { label: "Patients", href: "/patients", permissions: ["patient:read"] },
  { label: "Account Security", href: "/account-security", permissions: ["org:read"] },
  { label: "Notifications", href: "/notifications", permissions: ["org:read"] },
  { label: "Evidence", href: "/evidence", permissions: ["org:read"] },
  { label: "AI Review", href: "/ai-review", permissions: ["org:read"] },
  { label: "Integrations", href: "/interop", permissions: ["integration:read"] },
  { label: "Admin Settings", href: "/admin-settings", permissions: ["org:manage"] }
];

const ROLE_PERMISSIONS: Record<string, string[]> = {
  ADMIN: [
    "audit:view",
    "org:manage",
    "team:manage",
    "org:read",
    "integration:read",
    "patient:read",
    "patient:write",
    "patient:merge"
  ],
  STAFF: ["org:read", "integration:read", "patient:read", "patient:write", "patient:merge"],
  VIEWER: ["org:read", "integration:read", "patient:read"]
};

export function hasPermission(role: string, permission: string): boolean {
  const perms = ROLE_PERMISSIONS[role] ?? [];
  return perms.includes(permission);
}
