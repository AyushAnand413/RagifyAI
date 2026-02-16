"use client";

import React from "react";
import type { NormalizedApiError } from "@/lib/api/errors";

type StatusBannerProps = {
  type: "error" | "success" | "loading";
  message: string;
  error?: NormalizedApiError | null;
  requestId?: string | null;
};

export default function StatusBanner({ type, message, error, requestId }: StatusBannerProps) {
  const showRequestId = process.env.NODE_ENV !== "production";

  return (
    <div className={`banner ${type}`} role={type === "error" ? "alert" : "status"}>
      <div>{message}</div>
      {type === "error" && error?.code ? <div className="meta">Code: {error.code}</div> : null}
      {showRequestId && requestId ? <div className="meta">request_id: {requestId}</div> : null}
    </div>
  );
}
