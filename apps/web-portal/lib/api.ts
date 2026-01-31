import { createClient } from "@careos/sdk";

const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export const apiClient = createClient({ baseUrl });
