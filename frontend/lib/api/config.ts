import type { NormalizedApiError } from "./errors";

function normalizeBaseUrl(raw?: string): string {
  if (!raw) {
    return "";
  }
  return raw.trim().replace(/\/+$/, "");
}

export const API_BASE_URL = normalizeBaseUrl(process.env.NEXT_PUBLIC_API_BASE_URL);

export function getApiBaseUrl(): string | null {
  return API_BASE_URL || null;
}

export function getApiBaseUrlError(): NormalizedApiError | null {
  if (API_BASE_URL) {
    return null;
  }

  return {
    code: "CONFIG_ERROR",
    message: "NEXT_PUBLIC_API_BASE_URL is missing. Configure it in Vercel environment variables.",
    requestId: "",
    status: 500,
  };
}
