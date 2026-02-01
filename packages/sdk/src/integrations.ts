export type Integration = {
  id: number;
  provider: string;
  status: string;
  last_tested_at: string | null;
  last_error: string;
  config: Record<string, unknown>;
};

export type IntegrationListResponse = {
  results: Integration[];
};

export type IntegrationApiKey = {
  id: number;
  name: string;
  prefix: string;
  created_at: string;
  revoked_at: string | null;
  created_by: number | null;
};

export type IntegrationApiKeyListResponse = {
  results: IntegrationApiKey[];
};

export type IntegrationApiKeyCreateResponse = {
  id: number;
  name: string;
  prefix: string;
  created_at: string;
  revoked_at: string | null;
  token: string;
};

export type IntegrationsClientOptions = {
  baseUrl: string;
  fetch?: typeof fetch;
};

export function createIntegrationsClient(options: IntegrationsClientOptions) {
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
    listIntegrations: () => request<IntegrationListResponse>("/integrations/"),
    connect: (provider: string, payload: { api_key: string; sender: string }) =>
      request<{ id: number; provider: string; status: string }>(
        `/integrations/${provider}/connect/`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        }
      ),
    test: (provider: string) =>
      request<{ provider: string; status: string; tested_at: string }>(
        `/integrations/${provider}/test/`,
        { method: "POST" }
      ),
    disconnect: (provider: string) =>
      request<{ id: number; provider: string; status: string }>(
        `/integrations/${provider}/disconnect/`,
        { method: "POST" }
      ),
    listApiKeys: () => request<IntegrationApiKeyListResponse>("/integrations/api-keys/"),
    createApiKey: (payload: { name: string }) =>
      request<IntegrationApiKeyCreateResponse>("/integrations/api-keys/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      }),
    revokeApiKey: (keyId: number) =>
      request<{ id: number; revoked_at: string | null }>(
        `/integrations/api-keys/${keyId}/revoke/`,
        { method: "POST" }
      ),
  };
}
