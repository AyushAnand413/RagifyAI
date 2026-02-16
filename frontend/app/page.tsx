"use client";

import React from "react";
import ChatPanel from "@/components/ChatPanel";
import type { ChatMessage } from "@/components/MessageList";
import StatusBanner from "@/components/StatusBanner";
import UploadPanel from "@/components/UploadPanel";
import { sendChat, uploadPdf } from "@/lib/api/client";
import { getApiBaseUrlError } from "@/lib/api/config";
import { isNormalizedApiError, type NormalizedApiError } from "@/lib/api/errors";

function makeId(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function toAssistantText(data: Record<string, unknown>): string {
  const answer = data.answer;
  if (typeof answer === "string" && answer.trim()) {
    return answer;
  }

  const action = data.action;
  if (typeof action === "string" && action.trim()) {
    return JSON.stringify(data, null, 2);
  }

  return "Received response from backend.";
}

type BannerStatus = {
  type: "error" | "success" | "loading";
  message: string;
};

export default function HomePage() {
  const configError = getApiBaseUrlError();

  const [messages, setMessages] = React.useState<ChatMessage[]>([]);
  const [uploadedFilename, setUploadedFilename] = React.useState<string | null>(null);
  const [uploadLoading, setUploadLoading] = React.useState(false);
  const [chatLoading, setChatLoading] = React.useState(false);
  const [uploadState, setUploadState] = React.useState<"idle" | "loading" | "success" | "error">("idle");
  const [status, setStatus] = React.useState<BannerStatus | null>(null);
  const [lastError, setLastError] = React.useState<NormalizedApiError | null>(null);
  const [lastRequestId, setLastRequestId] = React.useState<string | null>(null);

  const handleUpload = async (file: File) => {
    if (configError) {
      setStatus({ type: "error", message: configError.message });
      setLastError(configError);
      setLastRequestId(configError.requestId || null);
      return;
    }

    setUploadLoading(true);
    setUploadState("loading");
    setStatus({ type: "loading", message: "Uploading and indexing document..." });
    setLastError(null);

    try {
      const response = await uploadPdf(file);
      setUploadedFilename(response.data.filename);
      setLastRequestId(response.request_id || null);
      setUploadState("success");
      setStatus({ type: "success", message: response.data.message });
    } catch (error) {
      const normalized = isNormalizedApiError(error)
        ? error
        : { code: "UNKNOWN_ERROR", message: "Upload failed.", requestId: "" };
      setLastError(normalized);
      setLastRequestId(normalized.requestId || null);
      setUploadState("error");
      setStatus({ type: "error", message: normalized.message });
    } finally {
      setUploadLoading(false);
    }
  };

  const handleSend = async (query: string) => {
    if (configError) {
      setStatus({ type: "error", message: configError.message });
      setLastError(configError);
      setLastRequestId(configError.requestId || null);
      return;
    }

    const userMessage: ChatMessage = { id: makeId(), role: "user", text: query };
    setMessages((prev) => [...prev, userMessage]);
    setChatLoading(true);
    setStatus({ type: "loading", message: "Assistant is thinking..." });
    setLastError(null);

    try {
      const response = await sendChat({ query });
      const data = (response.data ?? {}) as Record<string, unknown>;
      const assistantText = toAssistantText(data);

      setMessages((prev) => [...prev, { id: makeId(), role: "assistant", text: assistantText }]);
      setLastRequestId(response.request_id || null);
      setStatus(null);
    } catch (error) {
      const normalized = isNormalizedApiError(error)
        ? error
        : { code: "UNKNOWN_ERROR", message: "Request failed.", requestId: "" };
      setLastError(normalized);
      setLastRequestId(normalized.requestId || null);
      setStatus({ type: "error", message: normalized.message });
    } finally {
      setChatLoading(false);
    }
  };

  return (
    <main className="page">
      <header className="header">
        <h1 className="title">Corporate RAG Assistant</h1>
        <p className="subtitle">Upload a PDF, then ask questions through your HF backend API.</p>
      </header>

      <div className="grid">
        {configError ? (
          <StatusBanner
            type="error"
            message={configError.message}
            error={configError}
            requestId={configError.requestId || null}
          />
        ) : null}

        {status ? <StatusBanner type={status.type} message={status.message} error={lastError} requestId={lastRequestId} /> : null}

        <UploadPanel
          onUpload={handleUpload}
          isLoading={uploadLoading}
          uploadedFilename={uploadedFilename}
          status={uploadState}
          errorMessage={uploadState === "error" ? status?.message || null : null}
        />

        <ChatPanel enabled={Boolean(uploadedFilename)} isLoading={chatLoading} messages={messages} onSend={handleSend} />
      </div>
    </main>
  );
}
