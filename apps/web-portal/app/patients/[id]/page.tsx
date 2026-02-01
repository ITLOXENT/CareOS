"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";

import type {
  PortalCareCircleMember,
  PortalConsent,
  PortalEpisode,
  PortalMeResponse
} from "@careos/sdk";

import { portalClient } from "../../../lib/api";

export default function PortalPatientDetailPage() {
  const router = useRouter();
  const params = useParams<{ id: string }>();
  const patientId = Number(params?.id);
  const [patient, setPatient] = useState<PortalMeResponse | null>(null);
  const [episodes, setEpisodes] = useState<PortalEpisode[]>([]);
  const [careCircle, setCareCircle] = useState<PortalCareCircleMember[]>([]);
  const [consents, setConsents] = useState<PortalConsent[]>([]);
  const [careName, setCareName] = useState("");
  const [careRelationship, setCareRelationship] = useState("");
  const [careContact, setCareContact] = useState("");
  const [consentScope, setConsentScope] = useState("episodes.read");
  const [consentBasis, setConsentBasis] = useState("");
  const [consentGrantedBy, setConsentGrantedBy] = useState("");
  const [status, setStatus] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("portalToken");
    if (!token) {
      router.push("/login");
      return;
    }
    if (!patientId) {
      router.push("/patients");
      return;
    }
    setStatus("Loading patient...");
    Promise.all([
      portalClient.me(token),
      portalClient.listEpisodes(token),
      portalClient.listCareCircle(token),
      portalClient.listConsents(token)
    ])
      .then(([mePayload, episodePayload, carePayload, consentPayload]) => {
        if (mePayload.patient_id !== patientId) {
          router.push("/patients");
          return;
        }
        setPatient(mePayload);
        setEpisodes(episodePayload.results);
        setCareCircle(carePayload.results);
        setConsents(consentPayload.results);
        setStatus("");
      })
      .catch((error) => setStatus(String(error)));
  }, [patientId, router]);

  const handleAddCareCircle = (token: string) => {
    if (!careName.trim() || !careRelationship.trim()) {
      setStatus("Care circle name and relationship are required.");
      return;
    }
    portalClient
      .createCareCircleMember(token, {
        person_name: careName.trim(),
        relationship: careRelationship.trim(),
        contact: careContact.trim() || undefined
      })
      .then((member) => {
        setCareCircle((prev) => [...prev, member]);
        setCareName("");
        setCareRelationship("");
        setCareContact("");
      })
      .catch((error) => setStatus(String(error)));
  };

  const handleRemoveCareCircle = (token: string, memberId: number) => {
    portalClient
      .deleteCareCircleMember(token, memberId)
      .then(() => setCareCircle((prev) => prev.filter((item) => item.id !== memberId)))
      .catch((error) => setStatus(String(error)));
  };

  const handleGrantConsent = (token: string) => {
    if (!consentScope.trim() || !consentBasis.trim() || !consentGrantedBy.trim()) {
      setStatus("Consent scope, lawful basis, and granted by are required.");
      return;
    }
    portalClient
      .createConsent(token, {
        scope: consentScope.trim(),
        lawful_basis: consentBasis.trim(),
        granted_by: consentGrantedBy.trim()
      })
      .then((consent) => {
        setConsents((prev) => [consent, ...prev]);
        setConsentBasis("");
        setConsentGrantedBy("");
      })
      .catch((error) => setStatus(String(error)));
  };

  const handleRevokeConsent = (token: string, consentId: number) => {
    portalClient
      .revokeConsent(token, consentId)
      .then((updated) => {
        setConsents((prev) => prev.map((item) => (item.id === consentId ? updated : item)));
      })
      .catch((error) => setStatus(String(error)));
  };

  return (
    <main>
      <h1>Patient Profile</h1>
      {patient ? (
        <section>
          <p>
            {patient.given_name} {patient.family_name}
          </p>
          <p>{patient.email || patient.phone}</p>
        </section>
      ) : null}
      <section>
        <h2>Episodes</h2>
        {episodes.map((episode) => (
          <div key={episode.id} style={{ marginBottom: "12px" }}>
            <a href={`/episodes/${episode.id}`}>{episode.title}</a>
            <div>
              {episode.status} · {episode.created_at}
            </div>
          </div>
        ))}
        {episodes.length === 0 && !status ? <p>No episodes available.</p> : null}
      </section>
      <section>
        <h2>Care Circle</h2>
        {patient ? (
          <div style={{ marginBottom: "12px" }}>
            <input
              placeholder="Name"
              value={careName}
              onChange={(event) => setCareName(event.target.value)}
            />
            <input
              placeholder="Relationship"
              value={careRelationship}
              onChange={(event) => setCareRelationship(event.target.value)}
            />
            <input
              placeholder="Contact"
              value={careContact}
              onChange={(event) => setCareContact(event.target.value)}
            />
            <button
              type="button"
              onClick={() => {
                const token = localStorage.getItem("portalToken");
                if (token) {
                  handleAddCareCircle(token);
                }
              }}
            >
              Add member
            </button>
          </div>
        ) : null}
        {careCircle.map((member) => (
          <div key={member.id} style={{ marginBottom: "8px" }}>
            <div>
              {member.person_name} · {member.relationship}
            </div>
            {member.contact ? <div>{member.contact}</div> : null}
            <button
              type="button"
              onClick={() => {
                const token = localStorage.getItem("portalToken");
                if (token) {
                  handleRemoveCareCircle(token, member.id);
                }
              }}
            >
              Remove
            </button>
          </div>
        ))}
        {careCircle.length === 0 && !status ? <p>No care circle members.</p> : null}
      </section>
      <section>
        <h2>Consents</h2>
        {patient ? (
          <div style={{ marginBottom: "12px" }}>
            <input
              placeholder="Scope"
              value={consentScope}
              onChange={(event) => setConsentScope(event.target.value)}
            />
            <input
              placeholder="Lawful basis"
              value={consentBasis}
              onChange={(event) => setConsentBasis(event.target.value)}
            />
            <input
              placeholder="Granted by"
              value={consentGrantedBy}
              onChange={(event) => setConsentGrantedBy(event.target.value)}
            />
            <button
              type="button"
              onClick={() => {
                const token = localStorage.getItem("portalToken");
                if (token) {
                  handleGrantConsent(token);
                }
              }}
            >
              Grant consent
            </button>
          </div>
        ) : null}
        {consents.map((consent) => (
          <div key={consent.id} style={{ marginBottom: "8px" }}>
            <div>
              {consent.scope} · {consent.lawful_basis}
            </div>
            <div>{consent.granted ? "Active" : "Revoked"}</div>
            {consent.granted ? (
              <button
                type="button"
                onClick={() => {
                  const token = localStorage.getItem("portalToken");
                  if (token) {
                    handleRevokeConsent(token, consent.id);
                  }
                }}
              >
                Revoke
              </button>
            ) : null}
          </div>
        ))}
        {consents.length === 0 && !status ? <p>No consents recorded.</p> : null}
      </section>
      {status ? <p role="status">{status}</p> : null}
    </main>
  );
}
