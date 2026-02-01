"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";

import type { WorkItem } from "@careos/sdk";

import { apiClient } from "../../lib/api";
import { PaginationControls } from "../../components/PaginationControls";

const STATUS_OPTIONS = ["open", "assigned", "done"];
const SLA_OPTIONS = [
  { value: "", label: "All SLA" },
  { value: "overdue", label: "Overdue" },
  { value: "next24", label: "Next 24h" }
];
const ASSIGNEE_OPTIONS = [
  { value: "", label: "All assignees" },
  { value: "me", label: "Me" },
  { value: "unassigned", label: "Unassigned" }
];
const APPOINTMENT_OPTIONS = [
  { value: "", label: "All items" },
  { value: "linked", label: "With appointment" },
  { value: "unlinked", label: "Without appointment" }
];

export default function InboxPage() {
  const [items, setItems] = useState<WorkItem[]>([]);
  const [filters, setFilters] = useState({
    status: "",
    assignedTo: "",
    sla: "",
    appointment: ""
  });
  const [draftFilters, setDraftFilters] = useState({
    status: "",
    assignedTo: "",
    sla: "",
    appointment: ""
  });
  const [statusMessage, setStatusMessage] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [currentUserId, setCurrentUserId] = useState<number | null>(null);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(25);
  const [totalCount, setTotalCount] = useState(0);
  const warningMinutes = 60;

  const totalPages = useMemo(
    () => Math.max(Math.ceil(totalCount / pageSize), 1),
    [totalCount, pageSize]
  );

  const loadItems = async () => {
    setIsLoading(true);
    setError("");
    try {
      let assignedTo: number | undefined;
      if (filters.assignedTo === "me") {
        assignedTo = currentUserId ?? undefined;
      }
      const statusValue = filters.status === "done" ? "completed" : filters.status;
      const dueBefore =
        filters.sla === "next24" ? new Date(Date.now() + 24 * 60 * 60 * 1000) : null;
      const payload = await apiClient.listWorkItems({
        status: statusValue || undefined,
        assigned_to: assignedTo,
        sla: filters.sla === "overdue" ? "breached" : undefined,
        due_before: dueBefore ? dueBefore.toISOString() : undefined,
        appointment: filters.appointment || undefined,
        page,
        page_size: pageSize
      });
      const filtered = payload.results.filter((item) => {
        if (filters.assignedTo === "unassigned") {
          return !item.assigned_to;
        }
        return true;
      });
      setItems(filtered);
      setTotalCount(payload.count ?? payload.results.length);
      setIsLoading(false);
    } catch (error) {
      setError(String(error));
      setIsLoading(false);
    }
  };

  useEffect(() => {
    apiClient
      .me()
      .then((payload) => setCurrentUserId(payload.id))
      .catch(() => setCurrentUserId(null));
  }, []);

  useEffect(() => {
    loadItems();
  }, [filters, currentUserId, page, pageSize]);

  useEffect(() => {
    if (page > totalPages) {
      setPage(totalPages);
    }
  }, [page, totalPages]);

  const handleApplyFilters = () => {
    setFilters(draftFilters);
    setPage(1);
  };

  const handleClearFilters = () => {
    const reset = { status: "", assignedTo: "", sla: "", appointment: "" };
    setDraftFilters(reset);
    setFilters(reset);
    setPage(1);
  };

  return (
    <section className="panel">
      <h2>Inbox</h2>
      <p className="status">Review new items and staff tasks.</p>

      <div className="row" style={{ marginTop: "12px", flexWrap: "wrap" }}>
        <label className="status">
          Status
          <select
            className="input"
            value={draftFilters.status}
            onChange={(event) =>
              setDraftFilters((prev) => ({ ...prev, status: event.target.value }))
            }
          >
            <option value="">All statuses</option>
            {STATUS_OPTIONS.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </label>
        <label className="status">
          Assignee
          <select
            className="input"
            value={draftFilters.assignedTo}
            onChange={(event) =>
              setDraftFilters((prev) => ({ ...prev, assignedTo: event.target.value }))
            }
          >
            {ASSIGNEE_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </label>
        <label className="status">
          SLA window
          <select
            className="input"
            value={draftFilters.sla}
            onChange={(event) => setDraftFilters((prev) => ({ ...prev, sla: event.target.value }))}
          >
            {SLA_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </label>
        <label className="status">
          Appointment
          <select
            className="input"
            value={draftFilters.appointment}
            onChange={(event) =>
              setDraftFilters((prev) => ({ ...prev, appointment: event.target.value }))
            }
          >
            {APPOINTMENT_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </label>
        <button className="button secondary" type="button" onClick={handleApplyFilters}>
          Apply filters
        </button>
        <button className="button secondary" type="button" onClick={handleClearFilters}>
          Clear
        </button>
      </div>

      <div style={{ marginTop: "16px" }}>
        {isLoading ? <p className="status">Loading work items...</p> : null}
        {!isLoading &&
          items.map((item) => (
            <div key={item.id} className="row" style={{ marginBottom: "8px" }}>
              {item.episode_id ? (
                <Link href={`/episodes/${item.episode_id}`} className="button secondary">
                  Episode {item.episode_id}
                </Link>
              ) : (
                <span className="button secondary">No episode</span>
              )}
              {item.appointment_id ? (
                <span className="button secondary">Appt {item.appointment_id}</span>
              ) : null}
              <div>
                <div>
                  {item.kind} · {item.status === "completed" ? "done" : item.status}
                </div>
                <div className="status">
                  assigned {item.assigned_to ?? "unassigned"}
                  {item.sla_breached ? " · SLA breached" : ""}
                  {!item.sla_breached && item.due_at
                    ? (() => {
                        const due = new Date(item.due_at).getTime();
                        const now = Date.now();
                        const warningMs = warningMinutes * 60 * 1000;
                        return due - now <= warningMs && due - now > 0
                          ? " · SLA soon"
                          : "";
                      })()
                    : ""}
                </div>
              </div>
            </div>
          ))}
        {!isLoading && items.length === 0 ? (
          <p className="status">No work items found.</p>
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
