export type ApiSuccess<T> = {
  success: true;
  request_id: string;
  data: T;
};

export type ApiErrorEnvelope = {
  success: false;
  request_id: string;
  error: {
    code: string;
    message: string;
    details?: unknown;
  };
};

export type ChatRequest = {
  query: string;
};

export type ChatData = {
  type?: "information" | "action";
  answer?: string;
  [key: string]: unknown;
};

export type UploadData = {
  status: "success";
  message: string;
  filename: string;
};
