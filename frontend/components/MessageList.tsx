"use client";

import React from "react";

export type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  text: string;
};

type MessageListProps = {
  messages: ChatMessage[];
  isAssistantTyping?: boolean;
};

export default function MessageList({ messages, isAssistantTyping = false }: MessageListProps) {
  const bottomRef = React.useRef<HTMLDivElement | null>(null);

  React.useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, isAssistantTyping]);

  if (messages.length === 0 && !isAssistantTyping) {
    return <p className="help">No messages yet.</p>;
  }

  return (
    <div className="messages" aria-live="polite">
      {messages.map((message) => (
        <div key={message.id} className={`message ${message.role}`}>
          <strong>{message.role === "user" ? "You" : "Assistant"}</strong>
          <div>{message.text}</div>
        </div>
      ))}

      {isAssistantTyping ? (
        <div className="message assistant typing" aria-label="Assistant is typing">
          <strong>Assistant</strong>
          <div className="typing-dots">
            <span />
            <span />
            <span />
          </div>
        </div>
      ) : null}

      <div ref={bottomRef} />
    </div>
  );
}
