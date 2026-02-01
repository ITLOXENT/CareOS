"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import type { PortalMeResponse } from "@careos/sdk";

import { portalClient } from "../../lib/api";

export default function PortalProfilePage() {
  const router = useRouter();
  const [profile, setProfile] = useState<PortalMeResponse | null>(null);
  const [status, setStatus] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("portalToken");
    if (!token) {
      router.push("/login");
      return;
    }
    portalClient
      .me(token)
      .then((payload) => setProfile(payload))
      .catch((error) => {
        setStatus(String(error));
        localStorage.removeItem("portalToken");
      });
  }, [router]);

  const handleLogout = () => {
    localStorage.removeItem("portalToken");
    router.push("/login");
  };

  return (
    <main>
      <h1>Portal Profile</h1>
      {profile ? (
        <div>
          <p>
            {profile.given_name} {profile.family_name}
          </p>
          <p>Role: {profile.role}</p>
          <p>Organization: {profile.organization_id}</p>
          <div style={{ marginTop: "12px" }}>
            <a href="/episodes">View episodes</a>
          </div>
          <div style={{ marginTop: "8px" }}>
            <a href="/notifications">View notifications</a>
          </div>
          <button style={{ marginTop: "12px" }} type="button" onClick={handleLogout}>
            Sign out
          </button>
        </div>
      ) : (
        <p>{status || "Loading..."}</p>
      )}
    </main>
  );
}
