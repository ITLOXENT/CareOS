export type ConsentRecord = {
  id: number;
  subject_type: string;
  subject_id: string;
  consent_type: string;
  policy_version: string;
  channel?: string;
  granted: boolean;
  metadata?: Record<string, unknown>;
  recorded_at: string;
  created_at: string;
};

export type ConsentRecordListResponse = {
  results: ConsentRecord[];
};

export type DsarExport = {
  id: number;
  subject_type: string;
  subject_id: string;
  status: string;
  created_at: string;
  finished_at: string | null;
  artifact_path: string | null;
};

export type DsarExportListResponse = {
  results: DsarExport[];
};

export type PrivacyClientOptions = {
  baseUrl: string;
  fetch?: typeof fetch;
};

export function createPrivacyClient(options: PrivacyClientOptions) {
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
    listConsents: (filters: { subject_type?: string; subject_id?: string } = {}) => {
      const params = new URLSearchParams();
      if (filters.subject_type) {
        params.set("subject_type", filters.subject_type);
      }
      if (filters.subject_id) {
        params.set("subject_id", filters.subject_id);
      }
      const query = params.toString();
      return request<ConsentRecordListResponse>(`/privacy/consents/${query ? `?${query}` : ""}`);
    },
    createConsent: (payload: {
      subject_type: string;
      subject_id: string;
      consent_type: string;
      policy_version: string;
      channel?: string;
      granted?: boolean;
      metadata?: Record<string, unknown>;
    }) =>
      request<ConsentRecord>("/privacy/consents/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      }),
    listDsarExports: () => request<DsarExportListResponse>("/privacy/dsar/exports/"),
    requestDsarExport: (payload: { subject_type?: string; subject_id?: string }) =>
      request<DsarExport>("/privacy/dsar/export/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      }),
    requestDsarDelete: (payload: { subject_type: string; subject_id: string }) =>
      request<{ status: string }>("/privacy/dsar/delete/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      }),
    downloadDsarExport: async (exportId: number): Promise<Blob> => {
      const response = await fetcher(`${baseUrl}/privacy/dsar/exports/${exportId}/download/`);
      if (!response.ok) {
        throw new Error(`Request failed: ${response.status}`);
      }
      return response.blob();
    }
  };
}
