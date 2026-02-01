"use client";

import { useEffect, useState } from "react";

type SessionInfo = {
  tokenHash: string;
  username: string;
  issuedAt: number;
  lastSeenAt: number;
  revokedAt: number | null;
};

export default function AccountSecurityPage() {
  const [sessions, setSessions] = useState<SessionInfo[]>([]);
  const [status, setStatus] = useState("");

  const loadSessions = async () => {
    try {
      const response = await fetch("/api/auth/sessions");
      if (!response.ok) {
        throw new Error("Unable to load sessions.");
      }
      const payload = await response.json();
      setSessions(payload.results ?? []);
    } catch (error) {
      setStatus(String(error));
    }
  };

  useEffect(() => {
    loadSessions();
  }, []);

  const handleRevoke = async (tokenHash: string) => {
    setStatus("Revoking session...");
    try {
      const response = await fetch("/api/auth/sessions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token_hash: tokenHash })
      });
      if (!response.ok) {
        throw new Error("Failed to revoke session.");
      }
      await loadSessions();
      setStatus("");
    } catch (error) {
      setStatus(String(error));
    }
  };

  return (
    <section className="panel">
      <h2>Account Security</h2>
      <p className="status">Manage MFA and active sessions.</p>

      <div style={{ marginTop: "16px" }}>
        <h3>Active sessions</h3>
        {sessions.map((session) => (
          <div key={session.tokenHash} className="row" style={{ marginBottom: "8px" }}>
            <div>
              <div>{session.username}</div>
              <div className="status">
                issued {new Date(session.issuedAt * 1000).toISOString()} · last seen{" "}
                {new Date(session.lastSeenAt * 1000).toISOString()}
              </div>
            </div>
            <button className="button secondary" onClick={() => handleRevoke(session.tokenHash)}>
              Revoke
            </button>
          </div>
        ))}
        {sessions.length === 0 ? <p className="status">No active sessions.</p> : null}
      </div>
      {status ? <p className="status">{status}</p> : null}
    </section>
  );
}
