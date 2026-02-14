import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { sendChat } from "../api/client";
import MessageList from "./MessageList";

export default function ChatPanel() {
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState([]);

  const chatMutation = useMutation({
    mutationFn: sendChat,
    onSuccess: (data) => {
      const text = data.answer || data.action || "";
      setMessages((prev) => [...prev, { role: "system", text: String(text) }]);
    },
  });

  const handleSend = () => {
    const trimmed = query.trim();
    if (!trimmed) return;

    setMessages((prev) => [...prev, { role: "user", text: trimmed }]);
    setQuery("");
    chatMutation.mutate(trimmed);
  };

  return (
    <section>
      <h2>Chat</h2>
      <MessageList messages={messages} />

      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Ask a question..."
      />
      <button onClick={handleSend} disabled={chatMutation.isPending}>
        {chatMutation.isPending ? "Sending..." : "Send"}
      </button>
    </section>
  );
}
