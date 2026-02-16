export type NormalizedApiError = {
  code: string;
  message: string;
  requestId: string;
  status?: number;
  details?: unknown;
};

export function toUserMessage(error: NormalizedApiError): string {
  return error.message;
}

export function isNormalizedApiError(value: unknown): value is NormalizedApiError {
  if (!value || typeof value !== "object") return false;
  const maybe = value as Partial<NormalizedApiError>;
  return typeof maybe.code === "string" && typeof maybe.message === "string" && typeof maybe.requestId === "string";
}
