"use client";

import { useEffect, useMemo, useState } from "react";

import type { Notification } from "@careos/sdk";

import { apiClient } from "../../lib/api";
import { PaginationControls } from "../../components/PaginationControls";

export default function NotificationsPage() {
  const [items, setItems] = useState<Notification[]>([]);
  const [showUnread, setShowUnread] = useState(false);
  const [draftShowUnread, setDraftShowUnread] = useState(false);
  const [statusMessage, setStatusMessage] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(25);
  const [totalCount, setTotalCount] = useState(0);

  const totalPages = useMemo(
    () => Math.max(Math.ceil(totalCount / pageSize), 1),
    [totalCount, pageSize]
  );

  const loadNotifications = async () => {
    setIsLoading(true);
    setError("");
    try {
      const payload = await apiClient.listNotifications({
        unread_only: showUnread || undefined,
        page,
        page_size: pageSize
      });
      setItems(payload.results);
      setTotalCount(payload.count ?? payload.results.length);
      setIsLoading(false);
    } catch (error) {
      setError(String(error));
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadNotifications();
  }, [showUnread, page, pageSize]);

  useEffect(() => {
    if (page > totalPages) {
      setPage(totalPages);
    }
  }, [page, totalPages]);

  const handleApplyFilters = () => {
    setShowUnread(draftShowUnread);
    setPage(1);
  };

  const handleMarkRead = async (notificationId: number) => {
    const previous = items;
    setStatusMessage("Marking as read...");
    setError("");
    setItems((current) =>
      current.map((item) =>
        item.id === notificationId ? { ...item, unread: false, read_at: item.read_at } : item
      )
    );
    try {
      await apiClient.markNotificationRead(notificationId);
      await loadNotifications();
      setStatusMessage("");
    } catch (error) {
      setItems(previous);
      setError(String(error));
    }
  };

  return (
    <section className="panel">
      <h2>Notifications</h2>
      <p className="status">Review SLA alerts and other notifications.</p>

      <div className="row" style={{ marginTop: "12px", flexWrap: "wrap" }}>
        <label className="status">
          <input
            type="checkbox"
            checked={draftShowUnread}
            onChange={(event) => setDraftShowUnread(event.target.checked)}
          />{" "}
          Unread only
        </label>
        <button className="button secondary" type="button" onClick={handleApplyFilters}>
          Apply filters
        </button>
      </div>

      <div style={{ marginTop: "16px" }}>
        {isLoading ? <p className="status">Loading notifications...</p> : null}
        {!isLoading &&
          items.map((item) => (
            <div key={item.id} className="row" style={{ marginBottom: "8px" }}>
              <div>
                <div>
                  {item.title}
                  {item.kind ? ` · ${item.kind}` : ""}
                </div>
                <div className="status">
                  {item.unread ? "Unread" : "Read"} · {item.created_at}
                </div>
                {item.body ? <div className="status">{item.body}</div> : null}
              </div>
              {item.unread ? (
                <button
                  className="button secondary"
                  type="button"
                  onClick={() => handleMarkRead(item.id)}
                >
                  Mark read
                </button>
              ) : null}
            </div>
          ))}
        {!isLoading && items.length === 0 ? (
          <p className="status">No notifications found.</p>
        ) : null}
      </div>
      <PaginationControls
        page={page}
        pageSize={pageSize}
        totalCount={totalCount}
        onPageChange={setPage}
        onPageSizeChange={(size) => {
          setPageSize(size);
          setPage(1);
        }}
      />
      {statusMessage ? (
        <p className="status" role="status" aria-live="polite">
          {statusMessage}
        </p>
      ) : null}
      {error ? (
        <p className="status" role="alert">
          {error}
        </p>
      ) : null}
    </section>
  );
}
