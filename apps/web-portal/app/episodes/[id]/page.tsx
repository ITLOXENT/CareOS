"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";

import type { PortalEpisodeDetail } from "@careos/sdk";

import { portalClient } from "../../../lib/api";

export default function PortalEpisodeDetailPage() {
  const router = useRouter();
  const params = useParams<{ id: string }>();
  const episodeId = Number(params.id);
  const [detail, setDetail] = useState<PortalEpisodeDetail | null>(null);
  const [status, setStatus] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("portalToken");
    if (!token) {
      router.push("/login");
      return;
    }
    if (!episodeId) {
      return;
    }
    setStatus("Loading episode...");
    portalClient
      .getEpisode(token, episodeId)
      .then((payload) => {
        setDetail(payload);
        setStatus("");
      })
      .catch((error) => setStatus(String(error)));
  }, [episodeId, router]);

  return (
    <main>
      <h1>Episode Detail</h1>
      {detail ? (
        <div>
          <h2>{detail.episode.title}</h2>
          <p>{detail.episode.description}</p>
          <p>
            Status: {detail.episode.status} · Updated {detail.episode.updated_at}
          </p>
          <h3>Timeline</h3>
          {detail.timeline.map((event: PortalEpisodeDetail["timeline"][number]) => (
            <div key={event.id} style={{ marginBottom: "8px" }}>
              <div>{event.event_type}</div>
              <div>
                {event.from_state ? `${event.from_state} → ${event.to_state}` : event.to_state}
                {" · "}
                {event.created_at}
              </div>
            </div>
          ))}
          {detail.timeline.length === 0 ? <p>No events yet.</p> : null}
        </div>
      ) : null}
      {status ? <p role="status">{status}</p> : null}
    </main>
  );
}
