"use client";

import { useEffect, useMemo, useState } from "react";

import type { EvidenceItem } from "@careos/sdk";

import { apiClient } from "../../lib/api";
import { PaginationControls } from "../../components/PaginationControls";

export default function EvidencePage() {
  const [items, setItems] = useState<EvidenceItem[]>([]);
  const [filters, setFilters] = useState({
    episode: "",
    patient: "",
    kind: "",
    tags: ""
  });
  const [draftFilters, setDraftFilters] = useState({
    episode: "",
    patient: "",
    kind: "",
    tags: ""
  });
  const [title, setTitle] = useState("");
  const [kind, setKind] = useState("");
  const [episodeId, setEpisodeId] = useState("");
  const [patientId, setPatientId] = useState("");
  const [tags, setTags] = useState("");
  const [file, setFile] = useState<File | null>(null);
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

  const loadEvidence = async () => {
    setIsLoading(true);
    setError("");
    try {
      const payload = await apiClient.listEvidence({
        episode: filters.episode || undefined,
        patient: filters.patient || undefined,
        kind: filters.kind || undefined,
        tags: filters.tags || undefined,
        page,
        page_size: pageSize
      });
      setItems(payload.results);
      setTotalCount(payload.count ?? payload.results.length);
      setIsLoading(false);
    } catch (error) {
      setError(String(error));
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadEvidence();
  }, [filters, page, pageSize]);

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
    const reset = { episode: "", patient: "", kind: "", tags: "" };
    setDraftFilters(reset);
    setFilters(reset);
    setPage(1);
  };

  const handleUpload = async () => {
    if (!file) {
      setStatusMessage("Select a file to upload.");
      return;
    }
    if (!kind.trim()) {
      setStatusMessage("Kind is required.");
      return;
    }
    setStatusMessage("Uploading evidence...");
    setError("");
    const formData = new FormData();
    formData.append("file", file);
    if (title.trim()) {
      formData.append("title", title.trim());
    }
    formData.append("kind", kind.trim());
    if (episodeId) {
      formData.append("episode_id", episodeId);
    }
    if (patientId) {
      formData.append("patient_id", patientId);
    }
    if (tags.trim()) {
      formData.append("tags", tags.trim());
    }
    try {
      await apiClient.createEvidence(formData);
      setTitle("");
      setKind("");
      setEpisodeId("");
      setPatientId("");
      setTags("");
      setFile(null);
      await loadEvidence();
    } catch (error) {
      setError(String(error));
    }
  };

  return (
    <section className="panel">
      <h2>Evidence</h2>
      <p className="status">Upload evidence, tag, and link to episodes or patients.</p>

      <div className="row" style={{ marginTop: "12px", flexWrap: "wrap" }}>
        <label className="status">
          Episode id
          <input
            className="input"
            value={draftFilters.episode}
            onChange={(event) =>
              setDraftFilters((prev) => ({ ...prev, episode: event.target.value }))
            }
          />
        </label>
        <label className="status">
          Patient id
          <input
            className="input"
            value={draftFilters.patient}
            onChange={(event) =>
              setDraftFilters((prev) => ({ ...prev, patient: event.target.value }))
            }
          />
        </label>
        <label className="status">
          Kind
          <input
            className="input"
            value={draftFilters.kind}
            onChange={(event) =>
              setDraftFilters((prev) => ({ ...prev, kind: event.target.value }))
            }
          />
        </label>
        <label className="status">
          Tags (comma separated)
          <input
            className="input"
            value={draftFilters.tags}
            onChange={(event) =>
              setDraftFilters((prev) => ({ ...prev, tags: event.target.value }))
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
        {isLoading ? <p className="status">Loading evidence...</p> : null}
        {!isLoading &&
          items.map((item) => (
            <div key={item.id} className="row" style={{ marginBottom: "8px" }}>
              <div>
                <div>{item.title}</div>
                <div className="status">
                  {item.kind} · episode {item.episode_id ?? "n/a"} · patient{" "}
                  {item.patient_id ?? "n/a"}
                </div>
              </div>
            </div>
          ))}
        {!isLoading && items.length === 0 ? (
          <p className="status">No evidence found.</p>
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
        <h3>Upload evidence</h3>
        <label className="status">
          Title (optional)
          <input
            className="input"
            value={title}
            onChange={(event) => setTitle(event.target.value)}
          />
        </label>
        <label className="status">
          Kind
          <input
            className="input"
            value={kind}
            onChange={(event) => setKind(event.target.value)}
          />
        </label>
        <label className="status">
          Episode id (optional)
          <input
            className="input"
            value={episodeId}
            onChange={(event) => setEpisodeId(event.target.value)}
          />
        </label>
        <label className="status">
          Patient id (optional)
          <input
            className="input"
            value={patientId}
            onChange={(event) => setPatientId(event.target.value)}
          />
        </label>
        <label className="status">
          Tags (comma separated)
          <input
            className="input"
            value={tags}
            onChange={(event) => setTags(event.target.value)}
          />
        </label>
        <label className="status">
          File
          <input
            className="input"
            type="file"
            onChange={(event) => setFile(event.target.files?.[0] ?? null)}
          />
        </label>
        <button className="button" type="button" onClick={handleUpload}>
          Upload evidence
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
