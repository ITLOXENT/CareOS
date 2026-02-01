"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import type { PortalNotification } from "@careos/sdk";

import { portalClient } from "../../lib/api";

export default function PortalNotificationsPage() {
  const router = useRouter();
  const [items, setItems] = useState<PortalNotification[]>([]);
  const [showUnread, setShowUnread] = useState(false);
  const [status, setStatus] = useState("");

  const loadNotifications = async (token: string) => {
    setStatus("Loading notifications...");
    try {
      const payload = await portalClient.listNotifications(token, {
        unread_only: showUnread || undefined
      });
      setItems(payload.results);
      setStatus("");
    } catch (error) {
      setStatus(String(error));
    }
  };

  useEffect(() => {
    const token = localStorage.getItem("portalToken");
    if (!token) {
      router.push("/login");
      return;
    }
    loadNotifications(token);
  }, [router, showUnread]);

  const handleMarkRead = async (notificationId: number) => {
    const token = localStorage.getItem("portalToken");
    if (!token) {
      router.push("/login");
      return;
    }
    setStatus("Marking as read...");
    try {
      await portalClient.markNotificationRead(token, notificationId);
      await loadNotifications(token);
      setStatus("");
    } catch (error) {
      setStatus(String(error));
    }
  };

  return (
    <main>
      <h1>Notifications</h1>
      <label>
        <input
          type="checkbox"
          checked={showUnread}
          onChange={(event) => setShowUnread(event.target.checked)}
        />{" "}
        Unread only
      </label>
      <div style={{ marginTop: "12px" }}>
        {items.map((item) => (
          <div key={item.id} style={{ marginBottom: "12px" }}>
            <div>
              {item.title}
              {item.kind ? ` · ${item.kind}` : ""}
            </div>
            <div>
              {item.unread ? "Unread" : "Read"} · {item.created_at}
            </div>
            {item.body ? <div>{item.body}</div> : null}
            {item.unread ? (
              <button type="button" onClick={() => handleMarkRead(item.id)}>
                Mark read
              </button>
            ) : null}
          </div>
        ))}
        {items.length === 0 && !status ? <p>No notifications.</p> : null}
      </div>
      {status ? <p role="status">{status}</p> : null}
    </main>
  );
}
