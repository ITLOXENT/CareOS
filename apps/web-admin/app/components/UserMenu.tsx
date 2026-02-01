"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { apiClient } from "../lib/api";

type Props = {
  username: string;
  role: string;
};

export default function UserMenu({ username, role }: Props) {
  const router = useRouter();
  const [pending, setPending] = useState(false);
  const [unreadCount, setUnreadCount] = useState<number | null>(null);

  useEffect(() => {
    let mounted = true;
    apiClient
      .listNotifications(true)
      .then((payload) => {
        if (!mounted) {
          return;
        }
        setUnreadCount(payload.results.length);
      })
      .catch(() => {
        if (!mounted) {
          return;
        }
        setUnreadCount(null);
      });
    return () => {
      mounted = false;
    };
  }, []);

  const handleLogout = async () => {
    setPending(true);
    await fetch("/api/auth/logout", { method: "POST" });
    router.push("/login");
  };

  return (
    <div className="row">
      <div>
        <div>{username}</div>
        <div className="status">
          {role}
          {unreadCount !== null ? ` · ${unreadCount} unread` : ""}
        </div>
      </div>
      <button className="button secondary" onClick={handleLogout} disabled={pending}>
        Sign out
      </button>
    </div>
  );
}
