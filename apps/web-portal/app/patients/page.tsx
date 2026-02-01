"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import type { PortalMeResponse } from "@careos/sdk";

import { portalClient } from "../../lib/api";

export default function PortalPatientsPage() {
  const router = useRouter();
  const [patient, setPatient] = useState<PortalMeResponse | null>(null);
  const [status, setStatus] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("portalToken");
    if (!token) {
      router.push("/login");
      return;
    }
    setStatus("Loading patient...");
    portalClient
      .me(token)
      .then((payload) => {
        setPatient(payload);
        setStatus("");
      })
      .catch((error) => setStatus(String(error)));
  }, [router]);

  return (
    <main>
      <h1>Patients</h1>
      {patient ? (
        <div style={{ marginBottom: "12px" }}>
          <a href={`/patients/${patient.patient_id}`}>
            {patient.given_name} {patient.family_name}
          </a>
          <div>{patient.email || patient.phone}</div>
        </div>
      ) : null}
      {!patient && !status ? <p>No patients available.</p> : null}
      {status ? <p role="status">{status}</p> : null}
    </main>
  );
}
