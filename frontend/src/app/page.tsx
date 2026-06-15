"use client";

import { useState } from "react";
import styles from "./page.module.css";

export default function Home() {
  const [messages, setMessages] = useState<{ role: string; content: string }[]>([]);
  const [input, setInput] = useState("");
  const [traces, setTraces] = useState<{ step: string; details: string }[]>([]);
  const [loading, setLoading] = useState(false);
  const [provider, setProvider] = useState("groq");

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      // Connect to FastAPI backend using environment variable with a localhost fallback
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(`${API_BASE_URL}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: userMessage.content, provider }),
      });

      if (!response.ok) throw new Error("Backend offline or error");

      const data = await response.json();
      setMessages((prev) => [...prev, { role: "assistant", content: data.response }]);
      setTraces(data.trace);
    } catch (err) {
      console.error(err);
      // Fallback for demonstration when backend is not running
      setTimeout(() => {
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: "This is a fallback response. The FastAPI backend is currently offline. To see real results, start the Python backend on port 8000." },
        ]);
        setTraces([
          { step: "Received Query", details: userMessage.content },
          { step: "Router Decision", details: `Routed to Vector DB using ${provider} provider.` },
          { step: "Retrieval", details: "Retrieved 2 documents via pgvector hybrid search." },
          { step: "Generation", details: "Fallback generation executed." },
        ]);
        setLoading(false);
      }, 1000);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.sidebar}>
        <h2>Settings</h2>
        <select 
          className={styles.providerSelect}
          value={provider}
          onChange={(e) => setProvider(e.target.value)}
        >
          <option value="groq">Groq (LLaMA 3)</option>
          <option value="gemini">Gemini 1.5 Flash</option>
          <option value="openai">OpenAI (vLLM Compatible)</option>
        </select>

        <h2 style={{ marginTop: "20px" }}>Agent Trace UI</h2>
        <p style={{ fontSize: "0.8rem", color: "#94a3b8" }}>
          Live view of the routing and retrieval decisions.
        </p>
        <div className={styles.traceBox}>
          {traces.length === 0 ? (
            <p style={{ color: "#475569", textAlign: "center", marginTop: "20px" }}>Waiting for query...</p>
          ) : (
            traces.map((trace, i) => (
              <div key={i} className={styles.traceStep}>
                <strong>{trace.step}</strong>
                {trace.details}
              </div>
            ))
          )}
        </div>
      </div>

      <div className={styles.chatArea}>
        <div className={styles.messages}>
          {messages.length === 0 && (
            <div style={{ textAlign: "center", color: "#64748b", marginTop: "100px" }}>
              <h2>Advanced Agentic RAG</h2>
              <p>Ask a question about the financial reports to see the Agent in action.</p>
            </div>
          )}
          {messages.map((msg, i) => (
            <div key={i} className={`${styles.message} ${msg.role === "user" ? styles.userMessage : styles.botMessage}`}>
              {msg.content}
            </div>
          ))}
          {loading && (
            <div className={`${styles.message} ${styles.botMessage}`}>
              <span className={styles.typing}>Agent is thinking...</span>
            </div>
          )}
        </div>

        <div className={styles.inputArea}>
          <input
            type="text"
            className={styles.input}
            placeholder="Ask about revenue growth, COGS, etc..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          />
          <button className={styles.button} onClick={sendMessage} disabled={loading}>
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
