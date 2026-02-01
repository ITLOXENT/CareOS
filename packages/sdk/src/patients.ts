export type PatientIdentifier = {
  id: number;
  kind: string;
  value: string;
  system?: string;
  is_primary?: boolean;
};

export type PatientAddress = {
  id: number;
  address_type?: string;
  line1: string;
  line2?: string;
  city?: string;
  region?: string;
  postal_code?: string;
  country?: string;
  is_primary?: boolean;
};

export type PatientContactMethod = {
  id: number;
  kind: string;
  value: string;
  notes?: string;
  is_primary?: boolean;
};

export type CareCircleMember = {
  id: number;
  person_name: string;
  relationship: string;
  contact?: string;
  notes?: string;
  created_at: string;
};

export type PatientConsent = {
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

export type Patient = {
  id: number;
  given_name: string;
  family_name: string;
  date_of_birth: string | null;
  nhs_number: string | null;
  phone: string;
  email: string;
  address_line1?: string;
  address_line2?: string;
  city?: string;
  region?: string;
  postal_code?: string;
  country?: string;
  identifiers?: PatientIdentifier[];
  addresses?: PatientAddress[];
  contacts?: PatientContactMethod[];
  restricted?: boolean;
  created_at: string;
  updated_at: string;
};

export type PatientListResponse = {
  results: Patient[];
  count: number;
  page: number;
  page_size: number;
};

export type PatientsClientOptions = {
  baseUrl: string;
  fetch?: typeof fetch;
};

export function createPatientsClient(options: PatientsClientOptions) {
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
    listPatients: (filters: {
      search?: string;
      page?: number;
      page_size?: number;
    } = {}) => request<PatientListResponse>(`/patients/${buildQuery(filters)}`),
    searchPatients: (filters: {
      q?: string;
      page?: number;
      page_size?: number;
    } = {}) => request<PatientListResponse>(`/patients/search/${buildQuery(filters)}`),
    createPatient: (payload: {
      given_name: string;
      family_name: string;
      date_of_birth?: string | null;
      nhs_number?: string | null;
      phone?: string;
      email?: string;
      address_line1?: string;
      address_line2?: string;
      city?: string;
      region?: string;
      postal_code?: string;
      country?: string;
      restricted?: boolean;
      identifiers?: Omit<PatientIdentifier, "id">[];
      addresses?: Omit<PatientAddress, "id">[];
      contacts?: Omit<PatientContactMethod, "id">[];
    }) =>
      request<Patient>("/patients/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      }),
    getPatient: (patientId: number) => request<Patient>(`/patients/${patientId}/`),
    updatePatient: (patientId: number, payload: {
      given_name?: string;
      family_name?: string;
      date_of_birth?: string | null;
      nhs_number?: string | null;
      phone?: string;
      email?: string;
      address_line1?: string;
      address_line2?: string;
      city?: string;
      region?: string;
      postal_code?: string;
      country?: string;
      restricted?: boolean;
      identifiers?: Omit<PatientIdentifier, "id">[];
      addresses?: Omit<PatientAddress, "id">[];
      contacts?: Omit<PatientContactMethod, "id">[];
    }) =>
      request<Patient>(`/patients/${patientId}/`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      }),
    listPatientEpisodes: (patientId: number) =>
      request<{ results: { id: number; title: string; status: string; created_at: string; updated_at: string }[] }>(
        `/patients/${patientId}/episodes/`
      ),
    listCareCircle: (patientId: number) =>
      request<{ results: CareCircleMember[] }>(`/patients/${patientId}/care-circle/`),
    createCareCircleMember: (patientId: number, payload: {
      person_name: string;
      relationship: string;
      contact?: string;
      notes?: string;
    }) =>
      request<CareCircleMember>(`/patients/${patientId}/care-circle/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      }),
    updateCareCircleMember: (patientId: number, memberId: number, payload: {
      person_name?: string;
      relationship?: string;
      contact?: string;
      notes?: string;
    }) =>
      request<CareCircleMember>(`/patients/${patientId}/care-circle/${memberId}/`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      }),
    deleteCareCircleMember: (patientId: number, memberId: number) =>
      request<{ status: string }>(`/patients/${patientId}/care-circle/${memberId}/`, {
        method: "DELETE"
      }),
    listConsents: (patientId: number) =>
      request<{ results: PatientConsent[] }>(`/patients/${patientId}/consents/`),
    createConsent: (patientId: number, payload: {
      scope: string;
      lawful_basis: string;
      granted_by: string;
      expires_at?: string | null;
      policy_version?: string;
      channel?: string;
      metadata?: Record<string, unknown>;
    }) =>
      request<PatientConsent>(`/patients/${patientId}/consents/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      }),
    revokeConsent: (patientId: number, consentId: number) =>
      request<PatientConsent>(`/patients/${patientId}/consents/${consentId}/revoke/`, {
        method: "POST"
      }),
    mergePatient: (patientId: number, sourceId: number) =>
      request<{ id: number; merged_source_id: number }>(`/patients/${patientId}/merge/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ source_id: sourceId })
      })
  };
}
