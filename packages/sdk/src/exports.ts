export type ExportJob = {
  id: number;
  kind: string;
  status: string;
  params: Record<string, unknown>;
  created_at: string;
  finished_at: string | null;
  artifact_path: string;
};

export type ExportJobListResponse = {
  results: ExportJob[];
};

export type ExportJobRequest = {
  kind: "episodes" | "audit_events";
  last_days?: number;
};

export type ExportsClientOptions = {
  baseUrl: string;
  fetch?: typeof fetch;
};

export function createExportsClient(options: ExportsClientOptions) {
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
    listExports: () => request<ExportJobListResponse>("/exports/"),
    requestExport: (payload: ExportJobRequest) =>
      request<ExportJob>("/exports/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      }),
    getExport: (exportId: number) => request<ExportJob>(`/exports/${exportId}/`),
    downloadExport: async (exportId: number) => {
      const response = await fetcher(`${baseUrl}/exports/${exportId}/download/`);
      if (!response.ok) {
        const payload = await response.json().catch(() => ({}));
        throw new Error(payload.detail ?? `Request failed: ${response.status}`);
      }
      return response.blob();
    }
  };
}
