export type EvidenceBundle = {
  id: number;
  episode_id: number;
  created_at: string;
  artifact_path?: string | null;
  manifest?: Record<string, unknown>;
};

export type EvidenceBundleListResponse = {
  results: EvidenceBundle[];
};

export type ReportJob = {
  id: number;
  name: string;
  report_type: string;
  status: string;
  interval_days: number;
  next_run_at?: string | null;
  last_run_at?: string | null;
  artifact_path?: string | null;
};

export type ReportJobListResponse = {
  results: ReportJob[];
};

export type SubmissionRecord = {
  id: number;
  episode_id?: number | null;
  due_date: string;
  submitted_at?: string | null;
  status: string;
  notes?: string;
};

export type SubmissionRecordListResponse = {
  results: SubmissionRecord[];
};

export type ComplianceClientOptions = {
  baseUrl: string;
  fetch?: typeof fetch;
};

export function createComplianceClient(options: ComplianceClientOptions) {
  const fetcher = options.fetch ?? fetch;
  const baseUrl = options.baseUrl.replace(/\/$/, "");

  async function request<T>(path: string, init?: RequestInit): Promise<T> {
    const response = await fetcher(`${baseUrl}${path}`, init);
    if (!response.ok) {
      const payload = await response.json().catch(() => ({}));
      const requestId = response.headers.get("x-request-id");
      const detail = payload.detail ?? `Request failed: ${response.status}`;
      throw new Error(requestId ? `${detail} (request_id: ${requestId})` : detail);
    }
    return response.json() as Promise<T>;
  }

  return {
    listEpisodeBundles: (episodeId: number) =>
      request<EvidenceBundleListResponse>(`/episodes/${episodeId}/compliance/bundles/`),
    generateEpisodeBundle: (episodeId: number) =>
      request<EvidenceBundle>(`/episodes/${episodeId}/compliance/bundles/`, {
        method: "POST"
      }),
    downloadEpisodeBundle: async (bundleId: number): Promise<Blob> => {
      const response = await fetcher(
        `${baseUrl}/compliance/bundles/${bundleId}/download/`
      );
      if (!response.ok) {
        throw new Error(`Request failed: ${response.status}`);
      }
      return response.blob();
    },
    listReportJobs: () => request<ReportJobListResponse>("/compliance/reports/"),
    createReportJob: (payload: {
      name: string;
      report_type: string;
      interval_days?: number;
      next_run_at?: string;
      params?: Record<string, unknown>;
    }) =>
      request<ReportJob>("/compliance/reports/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      }),
    runReportJob: (jobId: number) =>
      request<ReportJob>(`/compliance/reports/${jobId}/run/`, { method: "POST" }),
    listSubmissionRecords: (episodeId?: number) => {
      const query = episodeId ? `?episode_id=${episodeId}` : "";
      return request<SubmissionRecordListResponse>(`/compliance/submissions/${query}`);
    },
    createSubmissionRecord: (payload: {
      episode_id?: number;
      due_date: string;
      submitted_at?: string;
      status?: string;
      notes?: string;
    }) =>
      request<SubmissionRecord>("/compliance/submissions/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      })
  };
}
