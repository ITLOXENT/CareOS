"use client";

import { useEffect, useState } from "react";

import type { Integration, InteropMessage } from "@careos/sdk";

import { apiClient } from "../../lib/api";

export default function InteropPage() {
  const [messages, setMessages] = useState<InteropMessage[]>([]);
  const [integrations, setIntegrations] = useState<Integration[]>([]);
  const [apiKey, setApiKey] = useState("");
  const [sender, setSender] = useState("");
  const [status, setStatus] = useState("");

  const loadMessages = () => {
    apiClient
      .listInteropMessages()
      .then((payload) => setMessages(payload.results))
      .catch((error) => setStatus(String(error)));
  };

  const loadIntegrations = () => {
    apiClient
      .listIntegrations()
      .then((payload) => setIntegrations(payload.results))
      .catch((error) => setStatus(String(error)));
  };

  useEffect(() => {
    loadMessages();
    loadIntegrations();
  }, []);

  const handleProcess = async () => {
    setStatus("Processing outbox...");
    try {
      const result = await apiClient.processInteropOutbox();
      setStatus(`Processed ${result.processed} message(s).`);
      loadMessages();
    } catch (error) {
      setStatus(String(error));
    }
  };

  const handleConnect = async () => {
    setStatus("Connecting integration...");
    try {
      await apiClient.connectIntegration("email", { api_key: apiKey.trim(), sender: sender.trim() });
      setApiKey("");
      setSender("");
      loadIntegrations();
      setStatus("");
    } catch (error) {
      setStatus(String(error));
    }
  };

  const handleTest = async () => {
    setStatus("Testing integration...");
    try {
      await apiClient.testIntegration("email");
      loadIntegrations();
      setStatus("");
    } catch (error) {
      setStatus(String(error));
    }
  };

  const handleDisconnect = async () => {
    setStatus("Disconnecting integration...");
    try {
      await apiClient.disconnectIntegration("email");
      loadIntegrations();
      setStatus("");
    } catch (error) {
      setStatus(String(error));
    }
  };

  return (
    <section className="panel">
      <h2>Integrations</h2>
      <p className="status">Manage integrations and interoperability messages.</p>

      <div className="form">
        <h3>Email integration</h3>
        <input
          className="input"
          placeholder="API key"
          value={apiKey}
          onChange={(event) => setApiKey(event.target.value)}
        />
        <input
          className="input"
          placeholder="Sender"
          value={sender}
          onChange={(event) => setSender(event.target.value)}
        />
        <div className="row">
          <button className="button" type="button" onClick={handleConnect}>
            Connect
          </button>
          <button className="button secondary" type="button" onClick={handleTest}>
            Test
          </button>
          <button className="button secondary" type="button" onClick={handleDisconnect}>
            Disconnect
          </button>
        </div>
      </div>

      <div style={{ marginTop: "16px" }}>
        {integrations.map((integration) => (
          <div key={integration.id} className="row" style={{ marginBottom: "8px" }}>
            <div>
              <div>{integration.provider}</div>
              <div className="status">
                {integration.status} · last tested{" "}
                {integration.last_tested_at ?? "never"} · sender{" "}
                {(integration.config?.sender as string) || "n/a"}
              </div>
              {integration.last_error ? (
                <div className="status">Error: {integration.last_error}</div>
              ) : null}
            </div>
          </div>
        ))}
        {integrations.length === 0 ? <p className="status">No integrations yet.</p> : null}
      </div>

      <div style={{ marginTop: "24px" }}>
        <h3>Interop Messages</h3>
        <button className="button" type="button" onClick={handleProcess}>
          Process outbox
        </button>
        {status ? <p className="status">{status}</p> : null}
        {messages.length === 0 ? (
          <p className="status">No messages yet.</p>
        ) : (
          <div className="form">
            {messages.map((message) => (
              <div key={message.id} className="panel">
                <div>
                  #{message.id} {message.external_system} · {message.status}
                </div>
                <div className="status">Attempts: {message.attempts}</div>
                <div className="status">External ID: {message.external_id || "n/a"}</div>
                <div className="status">
                  Simulator: {message.simulator_mode ? "Enabled" : "Disabled"}
                </div>
                <div className="status">Events:</div>
                <ul>
                  {message.status_events.map((event) => (
                    <li key={`${message.id}-${event.created_at}`}>
                      {event.created_at}: {event.status} ({event.detail || "ok"})
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
