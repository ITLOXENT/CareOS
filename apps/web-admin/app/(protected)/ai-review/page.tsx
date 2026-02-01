"use client";

import { useEffect, useState } from "react";

import type { AiReviewItem } from "@careos/sdk";

import { apiClient } from "../../lib/api";

export default function AiReviewPage() {
  const [items, setItems] = useState<AiReviewItem[]>([]);
  const [selected, setSelected] = useState<AiReviewItem | null>(null);
  const [decisionNote, setDecisionNote] = useState("");
  const [status, setStatus] = useState("");
  const [role, setRole] = useState<string | null>(null);

  const loadItems = () => {
    apiClient
      .listAiReviewItems(true)
      .then((payload) => {
        setItems(payload.results);
        setSelected(payload.results[0] ?? null);
      })
      .catch((error) => setStatus(String(error)));
  };

  useEffect(() => {
    apiClient
      .me()
      .then((payload) => setRole(payload.role))
      .catch(() => setRole(null));
    loadItems();
  }, []);

  const handleDecide = async (decision: "approved" | "rejected") => {
    if (!selected) {
      return;
    }
    setStatus(`${decision}ing...`);
    try {
      await apiClient.decideAiReviewItem(selected.id, decision, decisionNote);
      setDecisionNote("");
      loadItems();
      setStatus("");
    } catch (error) {
      setStatus(String(error));
    }
  };

  return (
    <section className="panel">
      <h2>AI Review Queue</h2>
      <p className="status">Review pending AI items before release.</p>

      <div className="row" style={{ marginTop: "16px" }}>
        <div style={{ minWidth: "240px" }}>
          <h3>Pending</h3>
          {items.map((item) => (
            <button
              key={item.id}
              className="button secondary"
              type="button"
              style={{ marginBottom: "8px" }}
              onClick={() => setSelected(item)}
            >
              #{item.id} {item.kind}
            </button>
          ))}
          {items.length === 0 ? <p className="status">No pending items.</p> : null}
        </div>
        <div style={{ flex: 1 }}>
          <h3>Detail</h3>
          {selected ? (
            <div className="panel">
              <div className="status">
                Episode {selected.episode_id ?? "n/a"} · {selected.status}
              </div>
              <pre className="status" style={{ whiteSpace: "pre-wrap" }}>
                {JSON.stringify(selected.payload_json, null, 2)}
              </pre>
              {role === "ADMIN" ? (
                <div className="form" style={{ marginTop: "12px" }}>
                  <textarea
                    className="input"
                    rows={2}
                    placeholder="Decision note (optional)"
                    value={decisionNote}
                    onChange={(event) => setDecisionNote(event.target.value)}
                  />
                  <div className="row">
                    <button
                      className="button"
                      type="button"
                      onClick={() => handleDecide("approved")}
                    >
                      Approve
                    </button>
                    <button
                      className="button secondary"
                      type="button"
                      onClick={() => handleDecide("rejected")}
                    >
                      Reject
                    </button>
                  </div>
                </div>
              ) : (
                <p className="status">Only admins can decide.</p>
              )}
            </div>
          ) : (
            <p className="status">Select an item to review.</p>
          )}
        </div>
      </div>

      {status ? <p className="status">{status}</p> : null}
    </section>
  );
}
