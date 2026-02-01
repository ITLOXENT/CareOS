export type Appointment = {
  id: number;
  patient_id: number | null;
  episode_id: number | null;
  scheduled_at: string;
  duration_minutes: number;
  location: string;
  status: string;
  notes?: string;
  created_by: number | null;
  created_at: string;
  updated_at: string;
};

export type AppointmentListResponse = {
  results: Appointment[];
  count?: number;
  page?: number;
  page_size?: number;
};

export type AppointmentsClientOptions = {
  baseUrl: string;
  fetch?: typeof fetch;
};

export function createAppointmentsClient(options: AppointmentsClientOptions) {
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
    listAppointments: (filters: {
      status?: string;
      patient_id?: string | number;
      episode_id?: string | number;
      scheduled_before?: string;
      scheduled_after?: string;
      page?: number;
      page_size?: number;
    } = {}) => request<AppointmentListResponse>(`/appointments/${buildQuery(filters)}`),
    createAppointment: (payload: {
      patient_id?: number | null;
      episode_id?: number | null;
      scheduled_at: string;
      duration_minutes?: number;
      location?: string;
      status?: string;
      notes?: string;
    }) =>
      request<Appointment>("/appointments/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      }),
    transitionAppointment: (appointmentId: number, payload: { to_state: string }) =>
      request<{ id: number; status: string }>(`/appointments/${appointmentId}/transition/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      })
  };
}
