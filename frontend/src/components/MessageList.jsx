export default function MessageList({ messages }) {
  return (
    <div>
      {messages.map((msg, idx) => (
        <div key={idx}>
          <strong>{msg.role === "user" ? "User" : "System"}:</strong> {msg.text}
        </div>
      ))}
    </div>
  );
}
