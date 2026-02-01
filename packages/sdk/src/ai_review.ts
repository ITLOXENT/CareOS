export type AiReviewRequest = {
  id: number;
  input_type: string;
  payload: Record<string, unknown>;
  status: string;
  output: Record<string, unknown>;
  model_provider: string;
  model_name: string;
  model_version: string;
  error: string;
  created_at: string;
};

export type AiReviewListResponse = {
  results: AiReviewRequest[];
};

export type AiReviewItem = {
  id: number;
  episode_id: number | null;
  kind: string;
  payload_json: Record<string, unknown>;
  status: string;
  decided_at: string | null;
  decided_by: number | null;
  decision_note: string;
  created_at: string;
};

export type AiReviewItemListResponse = {
  results: AiReviewItem[];
};

export type AiReviewClientOptions = {
  baseUrl: string;
  fetch?: typeof fetch;
};

export function createAiReviewClient(options: AiReviewClientOptions) {
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
    list: () => request<AiReviewListResponse>("/ai/review/"),
    create: (payload: { input_type: string; payload?: Record<string, unknown> }) =>
      request<{ id: number; status: string; input_type: string; created_at: string }>(
        "/ai/review/",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        }
      ),
    get: (reviewId: number) => request<AiReviewRequest>(`/ai/review/${reviewId}/`),
    listItems: (pendingOnly = true) =>
      request<AiReviewItemListResponse>(
        `/ai-review-items/${pendingOnly ? "?pending_only=1" : ""}`
      ),
    decideItem: (itemId: number, decision: "approved" | "rejected", note = "") =>
      request<{ id: number; status: string; decision_note: string }>(
        `/ai-review-items/${itemId}/decide/`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ decision, note })
        }
      )
  };
}
