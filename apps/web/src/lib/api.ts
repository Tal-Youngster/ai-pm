const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";

export interface HealthResponse {
  status: string;
  message?: string;
  [key: string]: unknown;
}

function buildUrl(path: string) {
  const base = API_BASE_URL.replace(/\/$/, "");
  if (!base) {
    return path;
  }

  return `${base}${path.startsWith("/") ? path : `/${path}`}`;
}

export async function getApiHealth(): Promise<HealthResponse> {
  const response = await fetch(buildUrl("/v1/ping"), {
    cache: "no-store",
    headers: {
      Accept: "application/json"
    }
  });

  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }

  return (await response.json()) as HealthResponse;
}

