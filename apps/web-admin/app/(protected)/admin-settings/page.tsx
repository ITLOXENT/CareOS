"use client";

import { useEffect, useState } from "react";

import type {
  BillingPlan,
  BillingSubscription,
  ExportJob,
  Integration,
  IntegrationApiKey,
  IntegrationApiKeyCreateResponse,
  OrgInvite,
  OrgMember
} from "@careos/sdk";

import { apiClient } from "../../lib/api";

const ROLE_OPTIONS = ["ADMIN", "STAFF", "VIEWER"];

export default function AdminSettingsPage() {
  const [orgName, setOrgName] = useState("");
  const [orgSlug, setOrgSlug] = useState("");
  const [members, setMembers] = useState<OrgMember[]>([]);
  const [invites, setInvites] = useState<OrgInvite[]>([]);
  const [inviteEmail, setInviteEmail] = useState("");
  const [inviteRole, setInviteRole] = useState("VIEWER");
  const [inviteExpiry, setInviteExpiry] = useState("72");
  const [plans, setPlans] = useState<BillingPlan[]>([]);
  const [subscription, setSubscription] = useState<BillingSubscription | null>(null);
  const [integrations, setIntegrations] = useState<Integration[]>([]);
  const [integrationKeys, setIntegrationKeys] = useState<IntegrationApiKey[]>([]);
  const [integrationKeyName, setIntegrationKeyName] = useState("");
  const [createdKey, setCreatedKey] = useState<IntegrationApiKeyCreateResponse | null>(
    null
  );
  const [emailApiKey, setEmailApiKey] = useState("");
  const [emailSender, setEmailSender] = useState("");
  const [integrationStatus, setIntegrationStatus] = useState("");
  const [auditEvents, setAuditEvents] = useState<
    {
      id: number;
      action: string;
      target_type: string;
      target_id: string;
      actor_id: number | null;
      created_at: string;
    }[]
  >([]);
  const [auditAction, setAuditAction] = useState("");
  const [auditActor, setAuditActor] = useState("");
  const [auditTargetType, setAuditTargetType] = useState("");
  const [auditTargetId, setAuditTargetId] = useState("");
  const [auditStart, setAuditStart] = useState("");
  const [auditEnd, setAuditEnd] = useState("");
  const [auditPage, setAuditPage] = useState(1);
  const [auditTotal, setAuditTotal] = useState(0);
  const [exports, setExports] = useState<ExportJob[]>([]);
  const [exportKind, setExportKind] = useState("episodes");
  const [exportDays, setExportDays] = useState("7");
  const [status, setStatus] = useState("");

  const loadOrg = async () => {
    try {
      const profile = await apiClient.getOrgProfile();
      setOrgName(profile.name);
      setOrgSlug(profile.slug);
    } catch (error) {
      setStatus(String(error));
    }
  };

  const loadMembers = async () => {
    try {
      const payload = await apiClient.listOrgMembers();
      setMembers(payload.results);
    } catch (error) {
      setStatus(String(error));
    }
  };

  const loadInvites = async () => {
    try {
      const payload = await apiClient.listOrgInvites();
      setInvites(payload.results);
    } catch (error) {
      setStatus(String(error));
    }
  };

  const loadBilling = async () => {
    try {
      const plansPayload = await apiClient.listBillingPlans();
      setPlans(plansPayload.results);
      const subPayload = await apiClient.getBillingSubscription();
      setSubscription(subPayload);
    } catch (error) {
      setStatus(String(error));
    }
  };

  const loadIntegrations = async () => {
    try {
      const payload = await apiClient.listIntegrations();
      setIntegrations(payload.results);
      const keysPayload = await apiClient.listIntegrationApiKeys();
      setIntegrationKeys(keysPayload.results);
    } catch (error) {
      setStatus(String(error));
    }
  };

  const loadAudit = async () => {
    const params = new URLSearchParams();
    params.set("page", String(auditPage));
    params.set("page_size", "20");
    if (auditAction) {
      params.set("action", auditAction);
    }
    if (auditActor) {
      params.set("actor", auditActor);
    }
    if (auditTargetType) {
      params.set("target_type", auditTargetType);
    }
    if (auditTargetId) {
      params.set("target_id", auditTargetId);
    }
    if (auditStart) {
      params.set("start", auditStart);
    }
    if (auditEnd) {
      params.set("end", auditEnd);
    }
    try {
      const response = await fetch(`/audit-events/?${params.toString()}`);
      if (!response.ok) {
        throw new Error(`Request failed: ${response.status}`);
      }
      const payload = await response.json();
      setAuditEvents(payload.results ?? []);
      setAuditTotal(payload.count ?? 0);
    } catch (error) {
      setStatus(String(error));
    }
  };

  const loadExports = async () => {
    try {
      const payload = await apiClient.listExports();
      setExports(payload.results);
    } catch (error) {
      setStatus(String(error));
    }
  };

  useEffect(() => {
    loadOrg();
    loadMembers();
    loadInvites();
    loadAudit();
    loadBilling();
    loadIntegrations();
    loadExports();
  }, []);

  useEffect(() => {
    loadAudit();
  }, [auditAction, auditActor, auditTargetType, auditTargetId, auditStart, auditEnd, auditPage]);

  const handleUpdateOrg = async () => {
    setStatus("Updating organization...");
    try {
      await apiClient.updateOrgProfile({ name: orgName });
      await loadOrg();
      setStatus("");
    } catch (error) {
      setStatus(String(error));
    }
  };

  const handleRoleChange = async (memberId: number, role: string) => {
    setStatus("Updating role...");
    try {
      await apiClient.changeOrgMemberRole(memberId, role);
      await loadMembers();
      setStatus("");
    } catch (error) {
      setStatus(String(error));
    }
  };

  const handleDeactivate = async (memberId: number) => {
    setStatus("Deactivating member...");
    try {
      await apiClient.deactivateOrgMember(memberId);
      await loadMembers();
      setStatus("");
    } catch (error) {
      setStatus(String(error));
    }
  };

  const handleInvite = async () => {
    if (!inviteEmail.trim()) {
      setStatus("Invite email is required.");
      return;
    }
    setStatus("Creating invite...");
    try {
      await apiClient.createOrgInvite({
        email: inviteEmail.trim(),
        role: inviteRole,
        expires_in_hours: Number(inviteExpiry) || 72
      });
      setInviteEmail("");
      setInviteRole("VIEWER");
      setInviteExpiry("72");
      await loadInvites();
      setStatus("");
    } catch (error) {
      setStatus(String(error));
    }
  };

  const handleCheckout = async (planCode: string) => {
    setStatus("Starting checkout...");
    try {
      const origin = window.location.origin;
      const payload = await apiClient.createBillingCheckout({
        plan_code: planCode,
        success_url: `${origin}/admin-settings`,
        cancel_url: `${origin}/admin-settings`,
      });
      window.location.href = payload.url;
    } catch (error) {
      setStatus(String(error));
    }
  };

  const handleRequestExport = async () => {
    setStatus("Requesting export...");
    try {
      await apiClient.requestExport({
        kind: exportKind as "episodes" | "audit_events",
        last_days: Number(exportDays) || 7
      });
      await loadExports();
      setStatus("");
    } catch (error) {
      setStatus(String(error));
    }
  };

  const handleCreateIntegrationKey = async () => {
    if (!integrationKeyName.trim()) {
      setStatus("API key name is required.");
      return;
    }
    setStatus("Creating API key...");
    try {
      const created = await apiClient.createIntegrationApiKey({
        name: integrationKeyName.trim()
      });
      setIntegrationKeyName("");
      setCreatedKey(created);
      await loadIntegrations();
      setStatus("");
    } catch (error) {
      setStatus(String(error));
    }
  };

  const handleRevokeIntegrationKey = async (keyId: number) => {
    setStatus("Revoking API key...");
    try {
      await apiClient.revokeIntegrationApiKey(keyId);
      await loadIntegrations();
      setStatus("");
    } catch (error) {
      setStatus(String(error));
    }
  };

  const handleConnectEmailIntegration = async () => {
    if (!emailApiKey.trim() || !emailSender.trim()) {
      setStatus("Email API key and sender are required.");
      return;
    }
    setIntegrationStatus("Connecting email integration...");
    try {
      await apiClient.connectIntegration("email", {
        api_key: emailApiKey.trim(),
        sender: emailSender.trim(),
      });
      setEmailApiKey("");
      setEmailSender("");
      await loadIntegrations();
      setIntegrationStatus("");
    } catch (error) {
      setIntegrationStatus(String(error));
    }
  };

  const handleTestEmailIntegration = async () => {
    setIntegrationStatus("Testing email integration...");
    try {
      await apiClient.testIntegration("email");
      setIntegrationStatus("Email integration OK.");
    } catch (error) {
      setIntegrationStatus(String(error));
    }
  };

  const handleDisconnectEmailIntegration = async () => {
    setIntegrationStatus("Disconnecting email integration...");
    try {
      await apiClient.disconnectIntegration("email");
      await loadIntegrations();
      setIntegrationStatus("");
    } catch (error) {
      setIntegrationStatus(String(error));
    }
  };

  const handleDownloadExport = async (exportId: number) => {
    setStatus("Downloading export...");
    try {
      const blob = await apiClient.downloadExport(exportId);
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `export-${exportId}.csv`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
      setStatus("");
    } catch (error) {
      setStatus(String(error));
    }
  };

  return (
    <section className="panel">
      <h2>Admin Settings</h2>
      <p className="status">Manage organization, team, and invites.</p>

      <div style={{ marginTop: "16px" }}>
        <h3>Organization</h3>
        <div className="form">
          <input
            className="input"
            placeholder="Organization name"
            value={orgName}
            onChange={(event) => setOrgName(event.target.value)}
          />
          <input className="input" value={orgSlug} disabled />
          <button className="button" type="button" onClick={handleUpdateOrg}>
            Save organization
          </button>
        </div>
      </div>

      <div style={{ marginTop: "24px" }}>
        <h3>Team</h3>
        {members.map((member) => (
          <div key={member.id} className="row" style={{ marginBottom: "8px" }}>
            <div>
              <div>{member.email || member.username}</div>
              <div className="status">
                {member.role} · {member.is_active ? "active" : "inactive"}
              </div>
            </div>
            <select
              className="input"
              value={member.role}
              onChange={(event) => handleRoleChange(member.id, event.target.value)}
            >
              {ROLE_OPTIONS.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
            <button
              className="button secondary"
              type="button"
              onClick={() => handleDeactivate(member.id)}
              disabled={!member.is_active}
            >
              Deactivate
            </button>
          </div>
        ))}
        {members.length === 0 ? <p className="status">No members found.</p> : null}
      </div>

      <div style={{ marginTop: "24px" }}>
        <h3>Invites</h3>
        <div className="form">
          <input
            className="input"
            placeholder="Invite email"
            value={inviteEmail}
            onChange={(event) => setInviteEmail(event.target.value)}
          />
          <select
            className="input"
            value={inviteRole}
            onChange={(event) => setInviteRole(event.target.value)}
          >
            {ROLE_OPTIONS.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
          <input
            className="input"
            placeholder="Expiry hours"
            value={inviteExpiry}
            onChange={(event) => setInviteExpiry(event.target.value)}
          />
          <button className="button" type="button" onClick={handleInvite}>
            Create invite
          </button>
        </div>

        <div style={{ marginTop: "12px" }}>
          {invites.map((invite) => (
            <div key={invite.id} className="row" style={{ marginBottom: "8px" }}>
              <div>
                <div>{invite.email}</div>
                <div className="status">
                  {invite.role} · expires {invite.expires_at}
                </div>
              </div>
            </div>
          ))}
          {invites.length === 0 ? <p className="status">No active invites.</p> : null}
        </div>
      </div>

      <div style={{ marginTop: "24px" }}>
        <h3>Billing</h3>
        <p className="status">
          Status: {subscription?.status ?? "inactive"} · Plan{" "}
          {subscription?.plan_code ?? "n/a"} · Seats {subscription?.seat_limit ?? 0}
        </p>
        <p className="status">
          <a href="#" className="link">
            Manage billing
          </a>
        </p>
        <div className="row" style={{ flexWrap: "wrap" }}>
          {plans.map((plan) => (
            <button
              key={plan.code}
              className="button secondary"
              type="button"
              onClick={() => handleCheckout(plan.code)}
            >
              {plan.name} ({plan.seats} seats)
            </button>
          ))}
          {plans.length === 0 ? <span className="status">No plans configured.</span> : null}
        </div>
      </div>

      <div style={{ marginTop: "24px" }}>
        <h3>Integrations</h3>
        <p className="status">Configure delivery providers and API keys.</p>
        <div className="form">
          <h4>Email</h4>
          <input
            className="input"
            placeholder="Email API key"
            value={emailApiKey}
            onChange={(event) => setEmailApiKey(event.target.value)}
          />
          <input
            className="input"
            placeholder="Sender address"
            value={emailSender}
            onChange={(event) => setEmailSender(event.target.value)}
          />
          <div className="row">
            <button className="button secondary" type="button" onClick={handleConnectEmailIntegration}>
              Connect
            </button>
            <button className="button secondary" type="button" onClick={handleTestEmailIntegration}>
              Test
            </button>
            <button className="button secondary" type="button" onClick={handleDisconnectEmailIntegration}>
              Disconnect
            </button>
          </div>
          {integrationStatus ? <p className="status">{integrationStatus}</p> : null}
        </div>

        <div style={{ marginTop: "16px" }}>
          <h4>Integration status</h4>
          {integrations.map((integration) => (
            <div key={integration.id} className="row" style={{ marginBottom: "8px" }}>
              <div>
                <div>{integration.provider}</div>
                <div className="status">
                  {integration.status} · last tested{" "}
                  {integration.last_tested_at ?? "never"}
                </div>
              </div>
            </div>
          ))}
          {integrations.length === 0 ? (
            <p className="status">No integrations configured.</p>
          ) : null}
        </div>

        <div style={{ marginTop: "16px" }}>
          <h4>API keys</h4>
          <div className="row" style={{ flexWrap: "wrap" }}>
            <input
              className="input"
              placeholder="Key name"
              value={integrationKeyName}
              onChange={(event) => setIntegrationKeyName(event.target.value)}
            />
            <button className="button" type="button" onClick={handleCreateIntegrationKey}>
              Create key
            </button>
          </div>
          {createdKey ? (
            <div className="status" style={{ marginTop: "8px" }}>
              New key: {createdKey.token} (copy now; it will not be shown again)
            </div>
          ) : null}
          <div style={{ marginTop: "12px" }}>
            {integrationKeys.map((key) => (
              <div key={key.id} className="row" style={{ marginBottom: "8px" }}>
                <div>
                  <div>{key.name}</div>
                  <div className="status">
                    {key.prefix} · created {key.created_at} ·{" "}
                    {key.revoked_at ? `revoked ${key.revoked_at}` : "active"}
                  </div>
                </div>
                {!key.revoked_at ? (
                  <button
                    className="button secondary"
                    type="button"
                    onClick={() => handleRevokeIntegrationKey(key.id)}
                  >
                    Revoke
                  </button>
                ) : null}
              </div>
            ))}
            {integrationKeys.length === 0 ? (
              <p className="status">No API keys yet.</p>
            ) : null}
          </div>
        </div>
      </div>

      <div style={{ marginTop: "24px" }}>
        <h3>Exports</h3>
        <div className="row" style={{ flexWrap: "wrap" }}>
          <select
            className="input"
            value={exportKind}
            onChange={(event) => setExportKind(event.target.value)}
          >
            <option value="episodes">Episodes</option>
            <option value="audit_events">Audit events</option>
          </select>
          <select
            className="input"
            value={exportDays}
            onChange={(event) => setExportDays(event.target.value)}
          >
            <option value="7">Last 7 days</option>
            <option value="30">Last 30 days</option>
            <option value="90">Last 90 days</option>
          </select>
          <button className="button" type="button" onClick={handleRequestExport}>
            Request export
          </button>
        </div>
        <div style={{ marginTop: "12px" }}>
          {exports.map((job) => (
            <div key={job.id} className="row" style={{ marginBottom: "8px" }}>
              <div>
                <div>
                  {job.kind} · {job.status}
                </div>
                <div className="status">
                  created {job.created_at}
                  {job.finished_at ? ` · finished ${job.finished_at}` : ""}
                </div>
              </div>
              {job.status === "done" ? (
                <button
                  className="button secondary"
                  type="button"
                  onClick={() => handleDownloadExport(job.id)}
                >
                  Download
                </button>
              ) : null}
            </div>
          ))}
          {exports.length === 0 ? <p className="status">No exports yet.</p> : null}
        </div>
      </div>

      <div style={{ marginTop: "24px" }}>
        <h3>Audit</h3>
        <div className="row" style={{ flexWrap: "wrap" }}>
          <input
            className="input"
            placeholder="Action"
            value={auditAction}
            onChange={(event) => {
              setAuditPage(1);
              setAuditAction(event.target.value);
            }}
          />
          <input
            className="input"
            placeholder="Actor id"
            value={auditActor}
            onChange={(event) => {
              setAuditPage(1);
              setAuditActor(event.target.value);
            }}
          />
          <input
            className="input"
            placeholder="Target type"
            value={auditTargetType}
            onChange={(event) => {
              setAuditPage(1);
              setAuditTargetType(event.target.value);
            }}
          />
          <input
            className="input"
            placeholder="Target id"
            value={auditTargetId}
            onChange={(event) => {
              setAuditPage(1);
              setAuditTargetId(event.target.value);
            }}
          />
          <input
            className="input"
            placeholder="Start (ISO datetime)"
            value={auditStart}
            onChange={(event) => {
              setAuditPage(1);
              setAuditStart(event.target.value);
            }}
          />
          <input
            className="input"
            placeholder="End (ISO datetime)"
            value={auditEnd}
            onChange={(event) => {
              setAuditPage(1);
              setAuditEnd(event.target.value);
            }}
          />
        </div>
        <div style={{ marginTop: "12px" }}>
          {auditEvents.map((event) => (
            <div key={event.id} className="row" style={{ marginBottom: "8px" }}>
              <div>
                <div>{event.action}</div>
                <div className="status">
                  {event.target_type} {event.target_id} · actor {event.actor_id ?? "n/a"} ·{" "}
                  {event.created_at}
                </div>
              </div>
            </div>
          ))}
          {auditEvents.length === 0 ? <p className="status">No audit events found.</p> : null}
        </div>
        <div className="row" style={{ marginTop: "12px" }}>
          <button
            className="button secondary"
            type="button"
            disabled={auditPage <= 1}
            onClick={() => setAuditPage((prev) => Math.max(prev - 1, 1))}
          >
            Previous
          </button>
          <button
            className="button secondary"
            type="button"
            disabled={auditPage * 20 >= auditTotal}
            onClick={() => setAuditPage((prev) => prev + 1)}
          >
            Next
          </button>
          <div className="status">
            Page {auditPage} · {auditTotal} total
          </div>
        </div>
      </div>

      {status ? <p className="status">{status}</p> : null}
    </section>
  );
}
