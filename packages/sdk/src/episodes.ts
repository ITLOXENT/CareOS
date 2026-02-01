export type Episode = {
  id: number;
  title: string;
  description: string;
  status: string;
  created_at: string;
  updated_at: string;
  assigned_to: number | null;
  created_by: number | null;
  patient_id: number | null;
};

export type EpisodeListResponse = {
  results: Episode[];
  count?: number;
  page?: number;
  page_size?: number;
};

export type EpisodeEvent = {
  id: number;
  event_type: string;
  from_state: string;
  to_state: string;
  from_status?: string;
  to_status?: string;
  note: string;
  payload_json: Record<string, unknown>;
  created_by: number | null;
  created_at: string;
};

export type EpisodeTimelineResponse = {
  results: EpisodeEvent[];
};

export type WorkItem = {
  id: number;
  episode_id: number | null;
  appointment_id?: number | null;
  kind: string;
  status: string;
  assigned_to: number | null;
  due_at: string | null;
  sla_breach_at: string | null;
  created_by: number | null;
  created_at: string;
  completed_at: string | null;
  sla_breached: boolean;
};

export type WorkItemListResponse = {
  results: WorkItem[];
  count?: number;
  page?: number;
  page_size?: number;
};

export type EpisodesClientOptions = {
  baseUrl: string;
  fetch?: typeof fetch;
};

export function createEpisodesClient(options: EpisodesClientOptions) {
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
    listEpisodes: (filters: {
      status?: string;
      assigned_to?: string | number;
      created_by?: string | number;
      search?: string;
      page?: number;
      page_size?: number;
      limit?: number;
    } = {}) =>
      request<EpisodeListResponse>(`/episodes/${buildQuery(filters)}`),
    createEpisode: (payload: {
      title: string;
      description?: string;
      patient_id?: number | null;
      assigned_to_id?: number | null;
    }) =>
      request<Episode>("/episodes/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      }),
    getEpisode: (episodeId: number) => request<Episode>(`/episodes/${episodeId}/`),
    transitionEpisode: (
      episodeId: number,
      payload: { to_state: string; note?: string; payload_json?: Record<string, unknown> }
    ) =>
      request<{ id: number; status: string }>(`/episodes/${episodeId}/transition/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      }),
    getEpisodeTimeline: (episodeId: number) =>
      request<EpisodeTimelineResponse>(`/episodes/${episodeId}/timeline/`),
    listWorkItems: (filters: {
      status?: string;
      assigned_to?: string | number;
      assignee?: string | number;
      sla?: string;
      episode_id?: string | number;
      appointment_id?: string | number;
      appointment?: string;
      kind?: string;
      due_before?: string;
      page?: number;
      page_size?: number;
      limit?: number;
    } = {}) => request<WorkItemListResponse>(`/work-items/${buildQuery(filters)}`),
    assignWorkItem: (itemId: number, assignedToId: number) =>
      request<{ id: number; status: string; assigned_to: number | null }>(
        `/work-items/${itemId}/assign/`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ assigned_to_id: assignedToId })
        }
      ),
    completeWorkItem: (itemId: number) =>
      request<{ id: number; status: string }>(`/work-items/${itemId}/complete/`, {
        method: "POST"
      })
  };
}
