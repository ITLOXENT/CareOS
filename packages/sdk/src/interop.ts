export type InteropStatusEvent = {
  status: string;
  detail: string;
  created_at: string;
};

export type InteropMessage = {
  id: number;
  external_system: string;
  status: string;
  attempts: number;
  external_id: string;
  simulator_mode: boolean;
  created_at: string;
  status_events: InteropStatusEvent[];
};

export type InteropListResponse = {
  results: InteropMessage[];
};

export type InteropClientOptions = {
  baseUrl: string;
  fetch?: typeof fetch;
};

export function createInteropClient(options: InteropClientOptions) {
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
    listMessages: () => request<InteropListResponse>("/interop/messages/"),
    processOutbox: () =>
      request<{ processed: number }>("/interop/process/", { method: "POST" }),
  };
}
