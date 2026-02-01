import type { ReactNode } from "react";

import { redirect } from "next/navigation";

import Navigation from "../components/Navigation";
import OrgSwitcher from "../components/OrgSwitcher";
import UserMenu from "../components/UserMenu";
import { getSession } from "../lib/auth";

export default async function ProtectedLayout({ children }: { children: ReactNode }) {
  const session = await getSession();
  if (!session) {
    redirect("/login");
  }
  if (!session.mfaVerified) {
    redirect("/login");
  }

  const parsedOrgId = session.orgId ? Number(session.orgId) : 0;
  const fallbackOrg = session.orgId
    ? [
        {
          id: Number.isFinite(parsedOrgId) ? parsedOrgId : 0,
          name: session.orgName ?? "Primary org",
          slug: session.orgName
            ? session.orgName.toLowerCase().replace(/\s+/g, "-")
            : "primary-org"
        }
      ]
    : [
        {
          id: 0,
          name: "Primary org",
          slug: "primary-org"
        }
      ];

  return (
    <div className="layout">
      <aside className="sidebar">
        <h1>CareOS Admin</h1>
        <Navigation initialRole={session.role} />
      </aside>
      <div className="content">
        <header className="topbar">
          <OrgSwitcher fallbackOrgs={fallbackOrg} />
          <UserMenu username={session.username} role={session.role} />
        </header>
        <main className="main">{children}</main>
      </div>
    </div>
  );
}
