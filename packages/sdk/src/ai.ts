export type AiArtifact = {
  id: number;
  episode_id: number;
  artifact_type: string;
  confidence: number;
  status: string;
  policy_version: string;
  created_at: string;
};

export type AiListResponse = {
  results: AiArtifact[];
};

export type AiClientOptions = {
  baseUrl: string;
  fetch?: typeof fetch;
};

export function createAiClient(options: AiClientOptions) {
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
    listArtifacts: (status = "pending") =>
      request<AiListResponse>(`/ai/?status=${encodeURIComponent(status)}`),
    approve: (artifactId: number) =>
      request<{ id: number; status: string }>(`/ai/${artifactId}/approve/`, {
        method: "POST"
      }),
    reject: (artifactId: number, reason: string) =>
      request<{ id: number; status: string }>(`/ai/${artifactId}/reject/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ reason })
      })
  };
}
