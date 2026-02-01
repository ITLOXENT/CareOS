export type Notification = {
  id: number;
  kind?: string;
  title: string;
  body: string;
  url: string;
  unread: boolean;
  read_at: string | null;
  created_at: string;
};

export type NotificationListResponse = {
  results: Notification[];
  count?: number;
  page?: number;
  page_size?: number;
};

export type NotificationsClientOptions = {
  baseUrl: string;
  fetch?: typeof fetch;
};

export function createNotificationsClient(options: NotificationsClientOptions) {
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

  function buildQuery(params: Record<string, string | number | boolean | undefined>): string {
    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== "" && value !== false) {
        searchParams.set(key, String(value));
      }
    });
    const query = searchParams.toString();
    return query ? `?${query}` : "";
  }

  return {
    listNotifications: (
      unreadOnlyOrOptions:
        | boolean
        | { unread_only?: boolean; page?: number; page_size?: number; limit?: number } = false
    ) => {
      const options =
        typeof unreadOnlyOrOptions === "boolean"
          ? { unread_only: unreadOnlyOrOptions }
          : unreadOnlyOrOptions;
      return request<NotificationListResponse>(
        `/notifications/${buildQuery(options)}`
      );
    },
    markRead: (notificationId: number) =>
      request<{ id: number; unread: boolean; read_at: string | null }>(
        `/notifications/${notificationId}/read/`,
        { method: "POST" }
      )
  };
}
