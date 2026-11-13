import { useState } from "react";
import { askQuestion } from "../services/api";
import type { ChatMessage } from "../types/chat";

export default function Chat() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSend() {
    const text = question.trim();

    if (!text || loading) return;

    setMessages((prev) => [
      ...prev,
      { role: "user", content: text },
    ]);

    setQuestion("");
    setError("");
    setLoading(true);

    try {
      const response = await askQuestion(text);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: response.answer,
          sources: response.sources,
        },
      ]);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Something went wrong"
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="chat">
      <div className="messages">
        {messages.length === 0 && !loading && (
          <p className="empty-chat">
            Ask a question about your uploaded documents.
          </p>
        )}

        {messages.map((message, index) => (
          <div
            className={`message message-${message.role}`}
            key={index}
          >
            <strong className="message-role">
              {message.role === "user"
                ? "You"
                : "ContextForge"}
            </strong>

            <p>{message.content}</p>

            {message.role === "assistant" &&
              message.sources &&
              message.sources.length > 0 && (
                <div className="sources">
                  <h4>Sources</h4>

                  {message.sources.map((source, sourceIndex) => (
                    <div className="source" key={sourceIndex}>
                      {source.filename} · chunk {source.chunk_index} ·{" "}
                      {source.similarity.toFixed(3)}
                    </div>
                  ))}
                </div>
              )}
          </div>
        ))}
      </div>

      {loading && <p className="muted">Generating answer...</p>}

      {error && <p className="alert" role="alert">{error}</p>}

      <form
        className="composer"
        onSubmit={(event) => {
          event.preventDefault();
          void handleSend();
        }}
      >
        <input
          type="text"
          value={question}
          onChange={(event) =>
            setQuestion(event.target.value)
          }
          placeholder="Ask a question..."
          disabled={loading}
        />

        <button
          className="btn btn-primary"
          type="submit"
          disabled={loading || !question.trim()}
        >
          Send
        </button>
      </form>
    </div>
  );
}
