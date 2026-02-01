"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import type { Episode, Patient } from "@careos/sdk";

import { apiClient } from "../../lib/api";
import { PaginationControls } from "../../components/PaginationControls";

const STATUS_OPTIONS = ["new", "triage", "in_progress", "waiting", "resolved", "closed", "cancelled"];

export default function EpisodesPage() {
  const router = useRouter();
  const [episodes, setEpisodes] = useState<Episode[]>([]);
  const [filters, setFilters] = useState({
    status: "",
    assignedTo: "",
    createdBy: "",
    search: ""
  });
  const [draftFilters, setDraftFilters] = useState({
    status: "",
    assignedTo: "",
    createdBy: "",
    search: ""
  });
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [patients, setPatients] = useState<Patient[]>([]);
  const [patientId, setPatientId] = useState("");
  const [statusMessage, setStatusMessage] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(25);
  const [totalCount, setTotalCount] = useState(0);

  const totalPages = useMemo(
    () => Math.max(Math.ceil(totalCount / pageSize), 1),
    [totalCount, pageSize]
  );

  const loadEpisodes = async () => {
    setIsLoading(true);
    setError("");
    try {
      const payload = await apiClient.listEpisodes({
        status: filters.status || undefined,
        assigned_to: filters.assignedTo || undefined,
        created_by: filters.createdBy || undefined,
        search: filters.search || undefined,
        page,
        page_size: pageSize
      });
      setEpisodes(payload.results);
      setTotalCount(payload.count ?? payload.results.length);
      setIsLoading(false);
    } catch (error) {
      setError(String(error));
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadEpisodes();
  }, [filters, page, pageSize]);

  useEffect(() => {
    apiClient
      .listPatients({ page_size: 50 })
      .then((payload) => setPatients(payload.results))
      .catch((error) => setError(String(error)));
  }, []);

  useEffect(() => {
    if (page > totalPages) {
      setPage(totalPages);
    }
  }, [page, totalPages]);

  const handleApplyFilters = () => {
    setFilters(draftFilters);
    setPage(1);
  };

  const handleClearFilters = () => {
    const reset = { status: "", assignedTo: "", createdBy: "", search: "" };
    setDraftFilters(reset);
    setFilters(reset);
    setPage(1);
  };

  const handleCreate = async () => {
    if (!title.trim()) {
      setStatusMessage("Title is required.");
      return;
    }
    setStatusMessage("Creating episode...");
    setError("");
    try {
      const created = await apiClient.createEpisode({
        title: title.trim(),
        description: description.trim(),
        patient_id: patientId ? Number(patientId) : undefined
      });
      setTitle("");
      setDescription("");
      setPatientId("");
      router.push(`/episodes/${created.id}`);
    } catch (error) {
      setError(String(error));
    }
  };

  return (
    <section className="panel">
      <h2>Episodes</h2>
      <p className="status">Track and review care episodes end-to-end.</p>

      <div className="row" style={{ marginTop: "12px", flexWrap: "wrap" }}>
        <label className="status">
          Status
          <select
            className="input"
            value={draftFilters.status}
            onChange={(event) =>
              setDraftFilters((prev) => ({ ...prev, status: event.target.value }))
            }
          >
            <option value="">All statuses</option>
            {STATUS_OPTIONS.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </label>
        <label className="status">
          Assigned to (user id)
          <input
            className="input"
            value={draftFilters.assignedTo}
            onChange={(event) =>
              setDraftFilters((prev) => ({ ...prev, assignedTo: event.target.value }))
            }
          />
        </label>
        <label className="status">
          Created by (user id)
          <input
            className="input"
            value={draftFilters.createdBy}
            onChange={(event) =>
              setDraftFilters((prev) => ({ ...prev, createdBy: event.target.value }))
            }
          />
        </label>
        <label className="status">
          Search title
          <input
            className="input"
            value={draftFilters.search}
            onChange={(event) =>
              setDraftFilters((prev) => ({ ...prev, search: event.target.value }))
            }
          />
        </label>
        <button className="button secondary" type="button" onClick={handleApplyFilters}>
          Apply filters
        </button>
        <button className="button secondary" type="button" onClick={handleClearFilters}>
          Clear
        </button>
      </div>

      <div style={{ marginTop: "16px" }}>
        {isLoading ? <p className="status">Loading episodes...</p> : null}
        {!isLoading &&
          episodes.map((episode) => (
            <div key={episode.id} className="row" style={{ marginBottom: "8px" }}>
              <Link href={`/episodes/${episode.id}`} className="button secondary">
                Episode {episode.id}
              </Link>
              <div>
                <div>{episode.title}</div>
                <div className="status">
                  {episode.status} · assigned {episode.assigned_to ?? "unassigned"}
                </div>
              </div>
            </div>
          ))}
        {!isLoading && episodes.length === 0 ? (
          <p className="status">No episodes found.</p>
        ) : null}
      </div>
      <PaginationControls
        page={page}
        pageSize={pageSize}
        totalCount={totalCount}
        onPageChange={setPage}
        onPageSizeChange={(size) => {
          setPageSize(size);
          setPage(1);
        }}
      />

      <div className="form" style={{ marginTop: "24px" }}>
        <h3>Create episode</h3>
        <label className="status">
          Title
          <input
            className="input"
            value={title}
            onChange={(event) => setTitle(event.target.value)}
          />
        </label>
        <label className="status">
          Description
          <textarea
            className="input"
            rows={3}
            value={description}
            onChange={(event) => setDescription(event.target.value)}
          />
        </label>
        <label className="status">
          Link patient (optional)
          <select
            className="input"
            value={patientId}
            onChange={(event) => setPatientId(event.target.value)}
          >
            <option value="">Select patient</option>
            {patients.map((patient) => (
              <option key={patient.id} value={patient.id}>
                {patient.given_name} {patient.family_name}
              </option>
            ))}
          </select>
        </label>
        <button className="button" type="button" onClick={handleCreate}>
          Create episode
        </button>
      </div>
      {statusMessage ? (
        <p className="status" role="status" aria-live="polite">
          {statusMessage}
        </p>
      ) : null}
      {error ? (
        <p className="status" role="alert">
          {error}
        </p>
      ) : null}
    </section>
  );
}
