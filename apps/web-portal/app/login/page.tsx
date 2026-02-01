"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import { portalClient } from "../../lib/api";

export default function PortalLoginPage() {
  const router = useRouter();
  const [inviteToken, setInviteToken] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [status, setStatus] = useState("");

  const handleAcceptInvite = async () => {
    if (!inviteToken.trim()) {
      setStatus("Invite token required.");
      return;
    }
    setStatus("Accepting invite...");
    try {
      const payload = await portalClient.acceptInvite({ token: inviteToken.trim() });
      localStorage.setItem("portalToken", payload.token);
      router.push("/profile");
    } catch (error) {
      setStatus(String(error));
    }
  };

  const handleLogin = async () => {
    if (!email.trim() && !phone.trim()) {
      setStatus("Provide email or phone.");
      return;
    }
    setStatus("Logging in...");
    try {
      const payload = await portalClient.login({
        email: email.trim() || undefined,
        phone: phone.trim() || undefined
      });
      localStorage.setItem("portalToken", payload.token);
      router.push("/profile");
    } catch (error) {
      setStatus(String(error));
    }
  };

  return (
    <main>
      <h1>CareOS Portal Login</h1>
      <p>Accept an invite or sign in.</p>

      <section>
        <h3>Accept invite</h3>
        <label>
          Invite token
          <input
            value={inviteToken}
            onChange={(event) => setInviteToken(event.target.value)}
            placeholder="Invite token"
          />
        </label>
        <button type="button" onClick={handleAcceptInvite}>
          Accept invite
        </button>
      </section>

      <section>
        <h3>Login</h3>
        <label>
          Email
          <input value={email} onChange={(event) => setEmail(event.target.value)} placeholder="Email" />
        </label>
        <label>
          Phone
          <input value={phone} onChange={(event) => setPhone(event.target.value)} placeholder="Phone" />
        </label>
        <button type="button" onClick={handleLogin}>
          Login
        </button>
      </section>
      {status ? <p role="status">{status}</p> : null}
    </main>
  );
}
