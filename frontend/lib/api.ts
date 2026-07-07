import { cookies } from "next/headers";
import { SESSION_COOKIE, verifySessionToken } from "./auth/session";
import type {
  BroadcastResponse,
  CampaignsResponse,
  DiscoveryResponse,
  IntegrationsResponse,
  LeadDetailResponse,
  LeadsResponse,
  MetaResponse,
  SettingsResponse
} from "./types";

const API_BASE_URL = process.env.LIDRAFLOW_API_BASE_URL ?? "http://127.0.0.1:8000";
const API_KEY = process.env.LIDRAFLOW_API_KEY ?? process.env.FRONTEND_API_KEY ?? "dev-local-key";

export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

type FetchOptions = Omit<RequestInit, "headers"> & {
  headers?: HeadersInit;
};

async function readError(response: Response): Promise<string> {
  try {
    const data = (await response.json()) as { detail?: string | { msg?: string }[] };
    if (typeof data.detail === "string") return data.detail;
    if (Array.isArray(data.detail)) return data.detail.map((item) => item.msg ?? "Ошибка валидации").join("; ");
    return JSON.stringify(data);
  } catch {
    return response.statusText || "Ошибка API";
  }
}

export async function apiFetch<T>(path: string, options: FetchOptions = {}): Promise<T> {
  const headers = new Headers(options.headers);
  headers.set("X-LidraFlow-Key", API_KEY);

  try {
    const sessionCookie = cookies().get(SESSION_COOKIE)?.value;
    const session = verifySessionToken(sessionCookie);
    if (session?.backend_token && !headers.has("X-LidraFlow-Session")) {
      headers.set("X-LidraFlow-Session", session.backend_token);
    }
  } catch {
  }

  if (options.body && !(options.body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
    cache: "no-store"
  });

  if (!response.ok) {
    throw new ApiError(response.status, await readError(response));
  }

  return (await response.json()) as T;
}

export function getMeta() {
  return apiFetch<MetaResponse>("/api/meta");
}

export function getLeads(params: {
  q?: string;
  status_filter?: string;
  consent_filter?: string;
  city_filter?: string;
  region_filter?: string;
  district_filter?: string;
  niche_filter?: string;
  channel_filter?: string;
}) {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value) search.set(key, value);
  });
  const suffix = search.toString() ? `?${search.toString()}` : "";
  return apiFetch<LeadsResponse>(`/api/leads${suffix}`);
}

export function getLead(id: number) {
  return apiFetch<LeadDetailResponse>(`/api/leads/${id}`);
}

export function getSettings() {
  return apiFetch<SettingsResponse>("/api/settings");
}

export function getIntegrations() {
  return apiFetch<IntegrationsResponse>("/api/integrations");
}

export function getCampaigns() {
  return apiFetch<CampaignsResponse>("/api/campaigns");
}

export function runDiscovery(payload: Record<string, unknown>) {
  return apiFetch<DiscoveryResponse>("/api/discovery/search", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function runBroadcast(payload: Record<string, unknown>) {
  return apiFetch<BroadcastResponse>("/api/broadcast", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}
