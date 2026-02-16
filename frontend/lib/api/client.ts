import { getApiBaseUrl, getApiBaseUrlError } from "./config";
import { isNormalizedApiError, type NormalizedApiError } from "./errors";
import type { ApiErrorEnvelope, ApiSuccess, ChatData, ChatRequest, UploadData } from "./types";

type ApiFetchOptions = {
  method?: "GET" | "POST";
  headers?: Record<string, string>;
  body?: BodyInit | null;
  timeoutMs?: number;
};

const DEFAULT_TIMEOUT_MS = 25000;
const CHAT_TIMEOUT_MS = 25000;
const UPLOAD_TIMEOUT_MS = 180000;

function safeParseJson(text: string): unknown | null {
  if (!text) {
    return null;
  }

  try {
    return JSON.parse(text);
  } catch {
    return null;
  }
}

function makeError(input: {
  code: string;
  message: string;
  status?: number;
  requestId?: string;
  details?: unknown;
}): NormalizedApiError {
  return {
    code: input.code,
    message: input.message,
    requestId: input.requestId || "",
    status: input.status,
    details: input.details,
  };
}

function normalizeApiError(input: {
  status: number;
  fallbackMessage: string;
  body: unknown;
  requestId?: string;
}): NormalizedApiError {
  const { status, fallbackMessage, body, requestId } = input;

  if (body && typeof body === "object") {
    const maybe = body as Partial<ApiErrorEnvelope>;
    if (maybe.success === false && maybe.error?.message) {
      return makeError({
        code: maybe.error.code || "BACKEND_ERROR",
        message: maybe.error.message,
        status,
        requestId: maybe.request_id || requestId,
        details: maybe.error.details,
      });
    }
  }

  return makeError({
    code: "BACKEND_ERROR",
    message: fallbackMessage,
    status,
    requestId,
  });
}

export async function apiFetch<T>(path: string, options: ApiFetchOptions = {}): Promise<ApiSuccess<T>> {
  const configError = getApiBaseUrlError();
  if (configError) {
    throw configError;
  }

  const baseUrl = getApiBaseUrl();
  if (!baseUrl) {
    throw makeError({
      code: "CONFIG_ERROR",
      message: "Backend API base URL is not configured.",
      status: 500,
    });
  }

  const controller = new AbortController();
  const timeoutMs = options.timeoutMs ?? DEFAULT_TIMEOUT_MS;
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(`${baseUrl}${path}`, {
      method: options.method ?? "GET",
      headers: {
        Accept: "application/json",
        ...(options.headers ?? {}),
      },
      body: options.body ?? null,
      signal: controller.signal,
      cache: "no-store",
    });

    const responseText = await response.text();
    const responseJson = safeParseJson(responseText);
    const headerRequestId = response.headers.get("X-Request-ID") || "";

    if (response.ok) {
      if (responseJson && typeof responseJson === "object") {
        const maybe = responseJson as Partial<ApiSuccess<T>>;
        if (maybe.success === true && maybe.data !== undefined) {
          return {
            success: true,
            request_id: maybe.request_id || headerRequestId,
            data: maybe.data,
          };
        }
      }

      return {
        success: true,
        request_id: headerRequestId,
        data: (responseJson as T) ?? ({} as T),
      };
    }

    throw normalizeApiError({
      status: response.status,
      fallbackMessage: `Request failed with status ${response.status}.`,
      body: responseJson,
      requestId: headerRequestId,
    });
  } catch (error) {
    if ((error as Error)?.name === "AbortError") {
      throw makeError({
        code: "TIMEOUT",
        message: "Request timed out. Please try again.",
        status: 408,
      });
    }

    if (isNormalizedApiError(error)) {
      throw error;
    }

    throw makeError({
      code: "NETWORK_ERROR",
      message: "Could not reach backend API.",
      status: 0,
    });
  } finally {
    clearTimeout(timeoutId);
  }
}

export async function uploadPdf(file: File) {
  const formData = new FormData();
  formData.append("file", file);

  return apiFetch<UploadData>("/api/v1/upload", {
    method: "POST",
    body: formData,
    timeoutMs: UPLOAD_TIMEOUT_MS,
  });
}

export async function sendChat(payload: ChatRequest) {
  return apiFetch<ChatData>("/api/v1/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
    timeoutMs: CHAT_TIMEOUT_MS,
  });
}
