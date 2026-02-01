export type EvidenceItem = {
  id: number;
  title: string;
  kind: string;
  episode_id: number | null;
  patient_id: number | null;
  file_name: string;
  content_type: string;
  size_bytes: number;
  storage_key?: string;
  sha256: string;
  tags: string[];
  retention_class?: string;
  retention_until?: string | null;
  created_at: string;
};

export type EvidenceListResponse = {
  results: EvidenceItem[];
  count?: number;
  page?: number;
  page_size?: number;
};

export type EvidenceClientOptions = {
  baseUrl: string;
  fetch?: typeof fetch;
};

export function createEvidenceClient(options: EvidenceClientOptions) {
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

  function buildQuery(params: Record<string, string | number | undefined | null>): string {
    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== "") {
        searchParams.set(key, String(value));
      }
    });
    const query = searchParams.toString();
    return query ? `?${query}` : "";
  }

  return {
    listEvidence: (filters: {
      episode?: string | number;
      patient?: string | number;
      tags?: string;
      kind?: string;
      page?: number;
      page_size?: number;
    } = {}) => request<EvidenceListResponse>(`/evidence/${buildQuery(filters)}`),
    createEvidence: (payload: FormData) =>
      request<EvidenceItem>("/evidence/", {
        method: "POST",
        body: payload
      }),
    getEvidence: (evidenceId: number) =>
      request<EvidenceItem>(`/evidence/${evidenceId}/`),
    downloadEvidence: async (evidenceId: number): Promise<Blob> => {
      const response = await fetcher(`${baseUrl}/evidence/${evidenceId}/?download=1`, {
        method: "GET"
      });
      if (!response.ok) {
        throw new Error(`Request failed: ${response.status}`);
      }
      return response.blob();
    },
    listEpisodeEvidence: (episodeId: number) =>
      request<EvidenceListResponse>(`/episodes/${episodeId}/evidence/`),
    createEpisodeEvidence: (episodeId: number, payload: FormData) =>
      request<EvidenceItem>(`/episodes/${episodeId}/evidence/`, {
        method: "POST",
        body: payload
      }),
    linkEpisodeEvidence: (episodeId: number, evidenceId: number) =>
      request<{ id: number; episode_id: number }>(
        `/episodes/${episodeId}/evidence/${evidenceId}/`,
        { method: "POST" }
      ),
    linkEvidence: (evidenceId: number, payload: { episode_id?: number; patient_id?: number }) =>
      request<{ id: number; episode_id: number | null; patient_id: number | null }>(
        `/evidence/${evidenceId}/link/`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        }
      ),
    tagEvidence: (evidenceId: number, tags: string[]) =>
      request<{ id: number; tags: string[] }>(`/evidence/${evidenceId}/tag/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ tags })
      })
  };
}
