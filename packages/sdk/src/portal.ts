export type PortalAcceptInviteRequest = {
  token: string;
};

export type PortalLoginRequest = {
  email?: string;
  phone?: string;
};

export type PortalAuthResponse = {
  token: string;
  role: string;
  patient_id: number;
  organization_id: number;
  expires_at: string;
};

export type PortalMeResponse = {
  patient_id: number;
  organization_id: number;
  role: string;
  given_name: string;
  family_name: string;
  email: string;
  phone: string;
};

export type PortalEpisode = {
  id: number;
  title: string;
  description: string;
  status: string;
  created_at: string;
  updated_at: string;
};

export type PortalEpisodeEvent = {
  id: number;
  event_type: string;
  from_state: string;
  to_state: string;
  note: string;
  created_at: string;
};

export type PortalEpisodeListResponse = {
  results: PortalEpisode[];
};

export type PortalEpisodeDetail = {
  episode: PortalEpisode;
  timeline: PortalEpisodeEvent[];
};

export type PortalNotification = {
  id: number;
  kind?: string;
  title: string;
  body: string;
  url: string;
  unread: boolean;
  read_at: string | null;
  created_at: string;
};

export type PortalNotificationListResponse = {
  results: PortalNotification[];
  count?: number;
  page?: number;
  page_size?: number;
};

export type PortalCareCircleMember = {
  id: number;
  person_name: string;
  relationship: string;
  contact?: string;
  notes?: string;
  created_at: string;
};

export type PortalConsent = {
  id: number;
  scope: string;
  lawful_basis: string;
  granted_by: string;
  expires_at: string | null;
  granted: boolean;
  revoked_at: string | null;
  policy_version: string;
  channel: string;
  recorded_at: string;
};

export type PortalClientOptions = {
  baseUrl: string;
  fetch?: typeof fetch;
};

export function createPortalClient(options: PortalClientOptions) {
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
    acceptInvite: (payload: PortalAcceptInviteRequest) =>
      request<PortalAuthResponse>("/portal/auth/accept-invite/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      }),
    login: (payload: PortalLoginRequest) =>
      request<PortalAuthResponse>("/portal/auth/login/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      }),
    me: (token: string) =>
      request<PortalMeResponse>("/portal/me/", {
        headers: { Authorization: `Bearer ${token}` }
      }),
    listEpisodes: (token: string) =>
      request<PortalEpisodeListResponse>("/portal/episodes/", {
        headers: { Authorization: `Bearer ${token}` }
      }),
    getEpisode: (token: string, episodeId: number) =>
      request<PortalEpisodeDetail>(`/portal/episodes/${episodeId}/`, {
        headers: { Authorization: `Bearer ${token}` }
      }),
    listNotifications: (
      token: string,
      options: { unread_only?: boolean; page?: number; page_size?: number } = {}
    ) => {
      const params = new URLSearchParams();
      Object.entries(options).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params.set(key, String(value));
        }
      });
      const query = params.toString();
      return request<PortalNotificationListResponse>(
        `/portal/notifications/${query ? `?${query}` : ""}`,
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
    },
    markNotificationRead: (token: string, notificationId: number) =>
      request<{ id: number; unread: boolean; read_at: string | null }>(
        `/portal/notifications/${notificationId}/read/`,
        {
          method: "POST",
          headers: { Authorization: `Bearer ${token}` }
        }
      ),
    listCareCircle: (token: string) =>
      request<{ results: PortalCareCircleMember[] }>("/portal/care-circle/", {
        headers: { Authorization: `Bearer ${token}` }
      }),
    createCareCircleMember: (token: string, payload: {
      person_name: string;
      relationship: string;
      contact?: string;
      notes?: string;
    }) =>
      request<PortalCareCircleMember>("/portal/care-circle/", {
        method: "POST",
        headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      }),
    updateCareCircleMember: (token: string, memberId: number, payload: {
      person_name?: string;
      relationship?: string;
      contact?: string;
      notes?: string;
    }) =>
      request<PortalCareCircleMember>(`/portal/care-circle/${memberId}/`, {
        method: "PATCH",
        headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      }),
    deleteCareCircleMember: (token: string, memberId: number) =>
      request<{ status: string }>(`/portal/care-circle/${memberId}/`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` }
      }),
    listConsents: (token: string) =>
      request<{ results: PortalConsent[] }>("/portal/consents/", {
        headers: { Authorization: `Bearer ${token}` }
      }),
    createConsent: (token: string, payload: {
      scope: string;
      lawful_basis: string;
      granted_by: string;
      expires_at?: string | null;
      policy_version?: string;
      channel?: string;
      metadata?: Record<string, unknown>;
    }) =>
      request<PortalConsent>("/portal/consents/", {
        method: "POST",
        headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      }),
    revokeConsent: (token: string, consentId: number) =>
      request<PortalConsent>(`/portal/consents/${consentId}/revoke/`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` }
      })
  };
}
