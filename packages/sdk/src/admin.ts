export type OrgMember = {
  id: number;
  user_id: number;
  email: string;
  username: string;
  role: string;
  is_active: boolean;
};

export type OrgMemberListResponse = {
  results: OrgMember[];
};

export type OrgInvite = {
  id: number;
  email: string;
  role: string;
  expires_at: string;
  created_at: string;
};

export type OrgInviteListResponse = {
  results: OrgInvite[];
};

export type AdminClientOptions = {
  baseUrl: string;
  fetch?: typeof fetch;
};

export function createAdminClient(options: AdminClientOptions) {
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
    getOrgProfile: () => request<{ id: number; name: string; slug: string }>("/orgs/current/"),
    updateOrgProfile: (payload: { name: string }) =>
      request<{ id: number; name: string; slug: string }>("/orgs/current/", {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      }),
    listMembers: () => request<OrgMemberListResponse>("/orgs/members/"),
    changeMemberRole: (memberId: number, role: string) =>
      request<{ id: number; role: string }>(`/orgs/members/${memberId}/role/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ role })
      }),
    deactivateMember: (memberId: number) =>
      request<{ id: number; is_active: boolean }>(
        `/orgs/members/${memberId}/deactivate/`,
        { method: "POST" }
      ),
    listInvites: () => request<OrgInviteListResponse>("/orgs/invites/"),
    createInvite: (payload: { email: string; role: string; expires_in_hours?: number }) =>
      request<{ id: number; email: string; role: string; expires_at: string; token: string }>(
        "/orgs/invites/",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        }
      )
  };
}
