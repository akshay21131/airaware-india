import { useState } from "react";
import { api } from "../api";

const SUGGESTIONS = [
  "Is it safe to exercise outdoors right now?",
  "What precautions should children take today?",
  "Should I keep my windows open?",
  "I have asthma - what should I do?",
];

export default function AdvisoryChat({ stationId, stationName }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  async function ask(question) {
    if (!question.trim() || !stationId) return;
    const userMsg = { role: "user", text: question };
    setMessages((m) => [...m, userMsg]);
    setInput("");
    setLoading(true);
    try {
      const res = await api.chat(stationId, question);
      setMessages((m) => [...m, { role: "bot", text: res.advisory }]);
    } catch {
      setMessages((m) => [
        ...m,
        { role: "bot", text: "Sorry, I couldn't reach the advisory service. Is the backend running?" },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="card reveal">
      <div className="section-label">AI Health Advisor · Gemini</div>
      <h2 className="h-title" style={{ marginBottom: 4 }}>Ask about air quality</h2>
      <p style={{ color: "var(--text-muted)", fontSize: 13, marginTop: 0, marginBottom: 18 }}>
        Grounded in the live reading{stationName ? ` for ${stationName}` : ""}. Not a substitute
        for professional medical advice.
      </p>

      <div
        style={{
          display: "grid",
          gap: 12,
          marginBottom: 16,
          maxHeight: 340,
          overflowY: "auto",
        }}
      >
        {messages.length === 0 && (
          <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
            {SUGGESTIONS.map((s) => (
              <button key={s} onClick={() => ask(s)} className="btn-ghost" style={{ fontSize: 13 }}>
                {s}
              </button>
            ))}
          </div>
        )}
        {messages.map((m, i) => (
          <div
            key={i}
            style={{
              justifySelf: m.role === "user" ? "end" : "start",
              maxWidth: "85%",
              padding: "10px 14px",
              borderRadius: 12,
              fontSize: 14,
              lineHeight: 1.5,
              whiteSpace: "pre-wrap",
              background: m.role === "user" ? "var(--accent-teal-dim)" : "var(--bg-elevated)",
              border: `1px solid ${m.role === "user" ? "var(--accent-teal)" : "var(--border)"}`,
              color: "var(--text-primary)",
            }}
          >
            {m.text}
          </div>
        ))}
        {loading && (
          <div style={{ justifySelf: "start", color: "var(--text-faint)", fontSize: 13 }}>
            Thinking...
          </div>
        )}
      </div>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          ask(input);
        }}
        style={{ display: "flex", gap: 10 }}
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your question…"
          style={{
            flex: 1,
            background: "var(--bg-elevated)",
            color: "var(--text-primary)",
            border: "1px solid var(--border)",
            borderRadius: 999,
            padding: "11px 18px",
            fontSize: 14,
            fontFamily: "var(--font-body)",
          }}
        />
        <button type="submit" disabled={loading || !input.trim()} className="btn-primary" style={{ padding: "11px 24px" }}>
          Ask
        </button>
      </form>
    </div>
  );
}
