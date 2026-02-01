export type FormTemplate = {
  id: number;
  name: string;
  version: number;
  schema: Record<string, unknown>;
};

export type FormResponse = {
  id: number;
  validated: boolean;
  validation_errors: string[];
};

export type EvidencePack = {
  id: number;
  manifest: Record<string, unknown>;
};

export type FormsClientOptions = {
  baseUrl: string;
  fetch?: typeof fetch;
};

export function createFormsClient(options: FormsClientOptions) {
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
    listTemplates: () => request<{ results: FormTemplate[] }>("/forms/templates/"),
    createResponse: (payload: {
      episode_id: number;
      template_id: number;
      data: Record<string, unknown>;
    }) =>
      request<FormResponse>("/forms/responses/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      }),
    signResponse: (responseId: number) =>
      request<{ id: number; signed_at: string }>(`/forms/responses/${responseId}/sign/`, {
        method: "POST"
      }),
    generateEvidencePack: (episodeId: number) =>
      request<{ id: number }>(`/episodes/${episodeId}/evidence-pack/generate/`, {
        method: "POST"
      }),
    getEvidencePack: (packId: number) =>
      request<EvidencePack>(`/evidence-packs/${packId}/`),
    downloadEvidencePack: async (packId: number): Promise<Blob> => {
      const response = await fetcher(
        `${baseUrl}/evidence-packs/${packId}/?format=pdf`,
        { method: "GET" }
      );
      if (!response.ok) {
        throw new Error(`Request failed: ${response.status}`);
      }
      return response.blob();
    }
  };
}
