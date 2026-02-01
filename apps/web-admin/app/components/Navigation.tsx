"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";

import type { MeResponse } from "@careos/types";

import { apiClient } from "../lib/api";
import { hasPermission, NAV_ITEMS } from "../lib/permissions";

type Props = {
  initialRole: string;
};

export default function Navigation({ initialRole }: Props) {
  const pathname = usePathname();
  const [role, setRole] = useState(initialRole);
  const [status, setStatus] = useState<"loading" | "ready" | "error">("loading");

  useEffect(() => {
    let mounted = true;
    apiClient
      .me()
      .then((profile: MeResponse) => {
        if (!mounted) {
          return;
        }
        setRole(profile.role);
        setStatus("ready");
      })
      .catch(() => {
        if (!mounted) {
          return;
        }
        setStatus("error");
      });
    return () => {
      mounted = false;
    };
  }, []);

  const items = NAV_ITEMS.filter((item) =>
    item.permissions.every((permission) => hasPermission(role, permission))
  );

  return (
    <nav>
      {items.map((item) => {
        const active = pathname === item.href;
        return (
          <Link
            key={item.href}
            href={item.href}
            className={`nav-item${active ? " active" : ""}`}
          >
            <div>{item.label}</div>
            <div className="nav-meta">{item.href}</div>
          </Link>
        );
      })}
      {status === "error" ? (
        <div className="status">API profile unavailable, using local role.</div>
      ) : null}
    </nav>
  );
}
