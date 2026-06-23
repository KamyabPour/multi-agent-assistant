"use client";

import { useMemo, useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api/v1";

export default function HomePage() {
  const [message, setMessage] = useState("Help me plan my top 3 goals this week.");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const routeLabel = useMemo(() => result?.route || "-", [result]);

  async function submitPrompt(event) {
    event.preventDefault();
    setLoading(true);
    setError("");

    try {
      const response = await fetch(`${API_BASE}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: "desktop-user", message, context: {} }),
      });

      if (!response.ok) {
        throw new Error(`Request failed: ${response.status}`);
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message || "Unknown error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main style={{ maxWidth: 860, margin: "40px auto", padding: 20, fontFamily: "Segoe UI, sans-serif" }}>
      <h1>Multi-Agent Life Assistant (Desktop)</h1>
      <p>One orchestration API, specialist agents, and action-oriented responses.</p>

      <form onSubmit={submitPrompt}>
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          rows={5}
          style={{ width: "100%", padding: 10, fontSize: 16 }}
        />
        <button type="submit" disabled={loading} style={{ marginTop: 12, padding: "10px 16px" }}>
          {loading ? "Thinking..." : "Send"}
        </button>
      </form>

      {error && <p style={{ color: "crimson" }}>Error: {error}</p>}

      {result && (
        <section style={{ marginTop: 24, border: "1px solid #ddd", borderRadius: 8, padding: 16 }}>
          <h2>Route: {routeLabel}</h2>
          <p>{result.result.summary}</p>
          <ul>
            {result.result.actions.map((item, idx) => (
              <li key={`${item.title}-${idx}`}>
                <strong>{item.title}</strong>: {item.details} ({item.priority})
              </li>
            ))}
          </ul>
        </section>
      )}
    </main>
  );
}
