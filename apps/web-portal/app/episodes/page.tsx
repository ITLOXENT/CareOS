"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import type { PortalEpisode } from "@careos/sdk";

import { portalClient } from "../../lib/api";

export default function PortalEpisodesPage() {
  const router = useRouter();
  const [episodes, setEpisodes] = useState<PortalEpisode[]>([]);
  const [status, setStatus] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("portalToken");
    if (!token) {
      router.push("/login");
      return;
    }
    setStatus("Loading episodes...");
    portalClient
      .listEpisodes(token)
      .then((payload) => {
        setEpisodes(payload.results);
        setStatus("");
      })
      .catch((error) => setStatus(String(error)));
  }, [router]);

  return (
    <main>
      <h1>Your Episodes</h1>
      {episodes.map((episode) => (
        <div key={episode.id} style={{ marginBottom: "12px" }}>
          <a href={`/episodes/${episode.id}`}>{episode.title}</a>
          <div>
            {episode.status} · {episode.created_at}
          </div>
        </div>
      ))}
      {episodes.length === 0 && !status ? <p>No episodes available.</p> : null}
      {status ? <p role="status">{status}</p> : null}
    </main>
  );
}
