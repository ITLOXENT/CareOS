export type BillingPlan = {
  code: string;
  name: string;
  seats: number;
};

export type BillingPlanListResponse = {
  results: BillingPlan[];
};

export type BillingSubscription = {
  plan_code?: string;
  status: string;
  current_period_end?: string | null;
  seat_limit?: number;
};

export type BillingClientOptions = {
  baseUrl: string;
  fetch?: typeof fetch;
};

export function createBillingClient(options: BillingClientOptions) {
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
    listPlans: () => request<BillingPlanListResponse>("/billing/plans/"),
    createCheckoutSession: (payload: {
      plan_code: string;
      success_url: string;
      cancel_url: string;
    }) =>
      request<{ id: string; url: string }>("/billing/checkout-session/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      }),
    getSubscription: () => request<BillingSubscription>("/billing/subscription/")
  };
}
