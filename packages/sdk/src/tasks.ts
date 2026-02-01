export type Task = {
  id: number;
  episode_id: number | null;
  work_item_id: number | null;
  title: string;
  status: string;
  priority: string;
  due_at: string | null;
  assigned_to: number | null;
  created_by: number | null;
  created_at: string;
  completed_at: string | null;
};

export type TaskListResponse = {
  results: Task[];
  count?: number;
  page?: number;
  page_size?: number;
};

export type TasksClientOptions = {
  baseUrl: string;
  fetch?: typeof fetch;
};

export function createTasksClient(options: TasksClientOptions) {
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
    listTasks: (filters: {
      status?: string;
      priority?: string;
      episode_id?: string | number;
      work_item_id?: string | number;
      due_before?: string;
      page?: number;
      page_size?: number;
    } = {}) => request<TaskListResponse>(`/tasks/${buildQuery(filters)}`),
    createTask: (payload: {
      episode_id?: number | null;
      work_item_id?: number | null;
      title: string;
      status?: string;
      priority?: string;
      due_at?: string | null;
    }) =>
      request<Task>("/tasks/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      }),
    assignTask: (taskId: number, assignedToId: number) =>
      request<{ id: number; status: string; assigned_to: number | null }>(
        `/tasks/${taskId}/assign/`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ assigned_to_id: assignedToId })
        }
      ),
    completeTask: (taskId: number) =>
      request<{ id: number; status: string }>(`/tasks/${taskId}/complete/`, {
        method: "POST"
      })
  };
}
