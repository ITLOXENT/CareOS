"use client";

import { useEffect, useState } from "react";

import type { Patient } from "@careos/sdk";

import { apiClient } from "../../lib/api";

export default function PatientsPage() {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [search, setSearch] = useState("");
  const [givenName, setGivenName] = useState("");
  const [familyName, setFamilyName] = useState("");
  const [nhsNumber, setNhsNumber] = useState("");
  const [status, setStatus] = useState("");

  const loadPatients = async () => {
    setStatus("Loading patients...");
    try {
      const payload = await apiClient.listPatients({ search });
      setPatients(payload.results);
      setStatus("");
    } catch (error) {
      setStatus(String(error));
    }
  };

  useEffect(() => {
    loadPatients();
  }, [search]);

  const handleCreate = async () => {
    if (!givenName.trim() || !familyName.trim()) {
      setStatus("Given name and family name are required.");
      return;
    }
    setStatus("Creating patient...");
    try {
      await apiClient.createPatient({
        given_name: givenName.trim(),
        family_name: familyName.trim(),
        nhs_number: nhsNumber.trim() || undefined
      });
      setGivenName("");
      setFamilyName("");
      setNhsNumber("");
      await loadPatients();
    } catch (error) {
      setStatus(String(error));
    }
  };

  return (
    <section className="panel">
      <h2>Patients</h2>
      <p className="status">Search and manage patient directory entries.</p>

      <div className="row" style={{ marginTop: "12px", flexWrap: "wrap" }}>
        <input
          className="input"
          placeholder="Search patients"
          value={search}
          onChange={(event) => setSearch(event.target.value)}
        />
      </div>

      <div style={{ marginTop: "16px" }}>
        {patients.map((patient) => (
          <div key={patient.id} className="row" style={{ marginBottom: "8px" }}>
            <div>
              <div>
                {patient.given_name} {patient.family_name}
              </div>
              <div className="status">
                NHS {patient.nhs_number ?? "n/a"} · {patient.email || patient.phone || "no contact"}
              </div>
            </div>
          </div>
        ))}
        {patients.length === 0 ? <p className="status">No patients found.</p> : null}
      </div>

      <div className="form" style={{ marginTop: "24px" }}>
        <h3>Create patient</h3>
        <input
          className="input"
          placeholder="Given name"
          value={givenName}
          onChange={(event) => setGivenName(event.target.value)}
        />
        <input
          className="input"
          placeholder="Family name"
          value={familyName}
          onChange={(event) => setFamilyName(event.target.value)}
        />
        <input
          className="input"
          placeholder="NHS number (10 digits)"
          value={nhsNumber}
          onChange={(event) => setNhsNumber(event.target.value)}
        />
        <button className="button" type="button" onClick={handleCreate}>
          Create patient
        </button>
      </div>
      {status ? <p className="status">{status}</p> : null}
    </section>
  );
}
