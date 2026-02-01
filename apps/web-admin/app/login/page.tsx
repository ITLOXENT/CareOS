"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [otp, setOtp] = useState("");
  const [error, setError] = useState("");
  const [pending, setPending] = useState(false);

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setPending(true);
    setError("");

    const response = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password, otp })
    });

    if (!response.ok) {
      const payload = await response.json().catch(() => ({ detail: "Login failed." }));
      setError(payload.detail ?? "Login failed.");
      setPending(false);
      return;
    }

    router.push("/inbox");
  };

  return (
    <main className="main">
      <section className="panel">
        <h2>Staff Login</h2>
        <p className="status">Use your staff credentials to access the admin console.</p>
        <form className="form" onSubmit={handleSubmit}>
          <input
            className="input"
            name="username"
            placeholder="Username"
            value={username}
            onChange={(event) => setUsername(event.target.value)}
            autoComplete="username"
            required
          />
          <input
            className="input"
            name="password"
            placeholder="Password"
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            autoComplete="current-password"
            required
          />
          <input
            className="input"
            name="otp"
            placeholder="MFA code (if enabled)"
            value={otp}
            onChange={(event) => setOtp(event.target.value)}
            autoComplete="one-time-code"
          />
          {error ? <div className="status">{error}</div> : null}
          <button className="button" type="submit" disabled={pending}>
            {pending ? "Signing in..." : "Sign in"}
          </button>
        </form>
      </section>
    </main>
  );
}
