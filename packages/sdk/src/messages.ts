export type ConversationParticipant = {
  id: number;
  email: string | null;
  username: string;
};

export type Conversation = {
  id: number;
  episode_id: number | null;
  participants: ConversationParticipant[];
  created_at: string;
};

export type Message = {
  id: number;
  sender_id: number | null;
  body: string;
  created_at: string;
  read?: boolean;
};

export type ConversationDetail = Conversation & {
  messages: Message[];
};

export type ConversationListResponse = {
  results: Conversation[];
};

export type MessagesClientOptions = {
  baseUrl: string;
  fetch?: typeof fetch;
};

export function createMessagesClient(options: MessagesClientOptions) {
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
    listConversations: (filters: { episode_id?: string | number } = {}) =>
      request<ConversationListResponse>(`/conversations/${buildQuery(filters)}`),
    createConversation: (payload: { episode_id?: number; participants?: number[] }) =>
      request<Conversation>("/conversations/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      }),
    getConversation: (conversationId: number) =>
      request<ConversationDetail>(`/conversations/${conversationId}/`),
    sendMessage: (conversationId: number, payload: { body: string }) =>
      request<Message>(`/conversations/${conversationId}/messages/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      }),
    markMessageRead: (messageId: number) =>
      request<{ id: number; read_at: string }>(`/messages/${messageId}/read/`, {
        method: "POST"
      })
  };
}
