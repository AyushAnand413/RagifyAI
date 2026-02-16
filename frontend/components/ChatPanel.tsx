"use client";

import React from "react";
import MessageList, { type ChatMessage } from "./MessageList";

type ChatPanelProps = {
  enabled: boolean;
  isLoading: boolean;
  messages: ChatMessage[];
  onSend: (query: string) => Promise<void>;
};

export default function ChatPanel({ enabled, isLoading, messages, onSend }: ChatPanelProps) {
  const [query, setQuery] = React.useState("");

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    const trimmed = query.trim();
    if (!trimmed || !enabled || isLoading) {
      return;
    }

    setQuery("");
    await onSend(trimmed);
  };

  return (
    <section className="card">
      <h2>2) Chat</h2>
      <MessageList messages={messages} isAssistantTyping={isLoading && enabled} />
      <form onSubmit={handleSubmit}>
        <textarea
          className="textarea"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={enabled ? "Ask a question about the uploaded PDF..." : "Upload a PDF first"}
          disabled={!enabled || isLoading}
        />
        <div className="row" style={{ marginTop: 10 }}>
          <button className="button" type="submit" disabled={!enabled || isLoading || !query.trim()}>
            {isLoading ? "Thinking..." : "Send"}
          </button>
        </div>
      </form>
      {!enabled ? <p className="help">Chat is disabled until upload succeeds.</p> : null}
    </section>
  );
}
