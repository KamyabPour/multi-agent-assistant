"use client";

import { useRef, useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api/v1";

const AGENTS = [
  {
    name: "Planner",
    route: "planner",
    color: "#d7613c",
    purpose: "Breaks goals into milestones, plans, and practical next actions.",
    example: "Plan my top 3 priorities for this week.",
  },
  {
    name: "Calendar",
    route: "calendar",
    color: "#0f7b6c",
    purpose: "Helps with scheduling, meetings, and time blocks.",
    example: "Rework my schedule so I protect 2 focus blocks tomorrow.",
  },
  {
    name: "Finance",
    route: "finance",
    color: "#c18d1f",
    purpose: "Suggests budget, savings, and spending actions.",
    example: "Help me review my top spending categories this month.",
  },
  {
    name: "Wellness",
    route: "wellness",
    color: "#4474c5",
    purpose: "Supports sleep, stress, exercise, and sustainable routines.",
    example: "Create a low-stress end-of-day routine for me.",
  },
  {
    name: "Compliance",
    route: "compliance",
    color: "#7a52bf",
    purpose: "Reads a shared folder, collects compliance sources, and writes a report.",
    example: "Run a compliance review for my cross-border business.",
  },
  {
    name: "General",
    route: "general",
    color: "#5f6470",
    purpose: "Fallback assistant for requests outside the specialist routes.",
    example: "Help me summarize what I should focus on today.",
  },
];

const JOURNEY = [
  "Tell the assistant what you need in plain language.",
  "The coordinator routes your message to the best specialist agent.",
  "The selected agent uses GitHub Models when configured, or a safe fallback.",
  "You receive a short summary plus concrete actions.",
];

const COMPLIANCE_STEPS = [
  "Upload your business profile folder or files (.md/.txt plus optional legal docs).",
  "Choose your business file (.md or .txt) from the uploaded files.",
  "Optionally add compliance source URLs, or the agent will use official sources automatically.",
  "Reports are saved in the same folder as your business context file, plus a compliance_downloads subfolder.",
];

export default function HomePage() {
  const [message, setMessage] = useState("Help me plan my top 3 goals this week.");
  const [userId, setUserId] = useState("desktop-user");
  const [sharedFolder, setSharedFolder] = useState("");
  const [businessFile, setBusinessFile] = useState("business_context.md");
  const [sourceUrls, setSourceUrls] = useState("");
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [uploadedBusinessFile, setUploadedBusinessFile] = useState("");
  const [selectedAgentRoute, setSelectedAgentRoute] = useState("planner");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const fileInputRef = useRef(null);
  const folderInputRef = useRef(null);

  const selectedAgent = AGENTS.find((agent) => agent.route === selectedAgentRoute) || AGENTS[0];
  const downloadActions = (result?.result?.actions || []).filter((item) => item.download_url);
  const reportDownload = downloadActions.find(
    (item) => item.title?.toLowerCase().includes("report") && !item.title?.toLowerCase().includes("pdf")
  );
  const pdfDownload = downloadActions.find((item) => item.title?.toLowerCase().includes("pdf"));
  const resourcesDownload = downloadActions.find((item) =>
    item.title?.toLowerCase().includes("resource")
  );

  async function submitPrompt(event) {
    event.preventDefault();
    setLoading(true);
    setError("");

    const isCompliance = selectedAgentRoute === "compliance";
    if (isCompliance && uploadedFiles.length === 0) {
      setError("Compliance requires uploading at least one file (.md or .txt).");
      setLoading(false);
      return;
    }

    const context = {};
    if (sourceUrls.trim()) {
      context.source_urls = sourceUrls
        .split(/\r?\n|,/) 
        .map((item) => item.trim())
        .filter(Boolean);
    }

    try {
      const hasUploads = selectedAgentRoute === "compliance" && uploadedFiles.length > 0;
      let response;

      if (hasUploads) {
        const formData = new FormData();
        formData.append("user_id", userId);
        formData.append("message", message);
        if (uploadedBusinessFile) {
          formData.append("business_file", uploadedBusinessFile);
        }
        if (sourceUrls.trim()) {
          formData.append("source_urls", sourceUrls.trim());
        }

        const lightweightContext = {};
        if (sharedFolder.trim()) {
          lightweightContext.shared_folder_hint = sharedFolder.trim();
        }
        formData.append("context_json", JSON.stringify(lightweightContext));

        for (const f of uploadedFiles) {
          formData.append("files", f);
        }

        response = await fetch(`${API_BASE}/chat/upload`, {
          method: "POST",
          body: formData,
        });
      } else {
        response = await fetch(`${API_BASE}/chat`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ user_id: userId, message, context }),
        });
      }

      if (!response.ok) {
        let detail = "";
        try {
          const errPayload = await response.json();
          if (typeof errPayload?.detail === "string" && errPayload.detail.trim()) {
            detail = errPayload.detail.trim();
          }
        } catch {
          // Ignore parse failures and fall back to status.
        }
        throw new Error(detail || `Request failed: ${response.status}`);
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message || "Unknown error");
    } finally {
      setLoading(false);
    }
  }

  function applyExample(prompt) {
    setMessage(prompt);
  }

  function addFilesFromSelection(fileList) {
    const incoming = Array.from(fileList || []);
    if (!incoming.length) {
      return;
    }

    setUploadedFiles((prev) => {
      const next = [...prev];
      for (const file of incoming) {
        const exists = next.some((x) => x.name === file.name && x.size === file.size);
        if (!exists) {
          next.push(file);
        }
      }
      return next;
    });
  }

  function clearUploadedFiles() {
    setUploadedFiles([]);
    setUploadedBusinessFile("");
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
    if (folderInputRef.current) {
      folderInputRef.current.value = "";
    }
  }

  function selectAgent(agent) {
    setSelectedAgentRoute(agent.route);
    setMessage(agent.example);
  }

  return (
    <main
      style={{
        minHeight: "100vh",
        background:
          "radial-gradient(circle at top left, #fff6e7 0, #f4f2eb 38%, #e6edf3 100%)",
        color: "#18212b",
        fontFamily: 'Aptos, "Segoe UI", "Trebuchet MS", sans-serif',
        padding: "32px 20px 56px",
      }}
    >
      <section
        style={{
          maxWidth: 1240,
          margin: "0 auto",
          display: "grid",
          gap: 24,
        }}
      >
        <header
          style={{
            display: "grid",
            gridTemplateColumns: "1.4fr 1fr",
            gap: 24,
            alignItems: "stretch",
          }}
        >
          <div
            style={{
              padding: 28,
              borderRadius: 28,
              background: "rgba(255,255,255,0.76)",
              border: "1px solid rgba(24,33,43,0.08)",
              boxShadow: "0 24px 80px rgba(35, 47, 62, 0.12)",
            }}
          >
            <div
              style={{
                display: "inline-block",
                padding: "8px 14px",
                borderRadius: 999,
                background: "#18212b",
                color: "#f9f1db",
                fontSize: 13,
                letterSpacing: "0.08em",
                textTransform: "uppercase",
              }}
            >
              Multi-Agent Desktop Console
            </div>
            <h1 style={{ fontSize: 52, lineHeight: 1.02, margin: "18px 0 14px" }}>
              See what the assistant can do before you start chatting.
            </h1>
            <p style={{ fontSize: 18, lineHeight: 1.6, maxWidth: 720, margin: 0 }}>
              This app is not just one chatbot. It is an orchestrated assistant with specialist
              services for planning, scheduling, finance, wellness, compliance, and general help.
            </p>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(4, minmax(0, 1fr))",
                gap: 12,
                marginTop: 24,
              }}
            >
              {JOURNEY.map((step, index) => (
                <div
                  key={step}
                  style={{
                    padding: 14,
                    borderRadius: 18,
                    background: index === 0 ? "#fff2d1" : "rgba(24,33,43,0.05)",
                    border: "1px solid rgba(24,33,43,0.08)",
                  }}
                >
                  <div style={{ fontSize: 12, letterSpacing: "0.08em", textTransform: "uppercase" }}>
                    Step {index + 1}
                  </div>
                  <div style={{ marginTop: 8, fontSize: 14, lineHeight: 1.5 }}>{step}</div>
                </div>
              ))}
            </div>
          </div>

          <div
            style={{
              padding: 24,
              borderRadius: 28,
              background: "#18212b",
              color: "#f7f4ed",
              boxShadow: "0 24px 80px rgba(24, 33, 43, 0.22)",
            }}
          >
            <div style={{ fontSize: 13, letterSpacing: "0.08em", textTransform: "uppercase", color: "#f6c56e" }}>
              Service Graph
            </div>
            <div style={{ marginTop: 18, display: "grid", gap: 12 }}>
              <ServiceBox title="User" subtitle="Desktop or web operator" tone="#f6c56e" />
              <Connector />
              <ServiceBox title="Web Frontend" subtitle="Guided dashboard + prompt workspace" tone="#96d4c5" />
              <Connector />
              <ServiceBox title="FastAPI Orchestrator" subtitle="Routes requests to the best agent" tone="#88a9ff" />
              <Connector />
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(3, minmax(0, 1fr))",
                  gap: 10,
                }}
              >
                {AGENTS.map((agent) => (
                  <ServiceBox
                    key={agent.route}
                    title={agent.name}
                    subtitle={agent.route}
                    tone={agent.color}
                    compact
                    interactive
                    active={selectedAgentRoute === agent.route}
                    onClick={() => selectAgent(agent)}
                  />
                ))}
              </div>
              <Connector />
              <ServiceBox title="Integrations + Files" subtitle="GitHub Models, Gmail, profiles, shared folders" tone="#e087b7" />
            </div>
          </div>
        </header>

        <section
          style={{
            borderRadius: 28,
            background: "rgba(255,255,255,0.72)",
            border: "1px solid rgba(24,33,43,0.08)",
            boxShadow: "0 16px 40px rgba(35, 47, 62, 0.08)",
            padding: 20,
            display: "grid",
            gap: 18,
          }}
        >
          <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
            {AGENTS.map((agent) => {
              const active = selectedAgentRoute === agent.route;
              return (
                <button
                  key={agent.route}
                  type="button"
                  onClick={() => selectAgent(agent)}
                  style={{
                    borderRadius: 999,
                    border: `1px solid ${active ? agent.color : "rgba(24,33,43,0.12)"}`,
                    background: active ? agent.color : "rgba(255,255,255,0.68)",
                    color: active ? "#fff" : "#18212b",
                    padding: "10px 16px",
                    fontWeight: 700,
                    cursor: "pointer",
                  }}
                >
                  {agent.name}
                </button>
              );
            })}
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "0.9fr 1.1fr",
              gap: 18,
              alignItems: "stretch",
            }}
          >
            <article
              style={{
                borderRadius: 24,
                background: "#fff",
                border: "1px solid rgba(24,33,43,0.08)",
                padding: 22,
              }}
            >
              <div
                style={{
                  width: 18,
                  height: 18,
                  borderRadius: 999,
                  background: selectedAgent.color,
                  boxShadow: `0 0 0 6px ${selectedAgent.color}22`,
                }}
              />
              <h2 style={{ margin: "14px 0 8px", fontSize: 28 }}>{selectedAgent.name}</h2>
              <p style={{ margin: 0, lineHeight: 1.65 }}>{selectedAgent.purpose}</p>
              <div
                style={{
                  marginTop: 18,
                  borderRadius: 18,
                  background: "#f6f7f9",
                  padding: 14,
                  border: "1px solid rgba(24,33,43,0.07)",
                }}
              >
                <div style={{ fontSize: 12, letterSpacing: "0.08em", textTransform: "uppercase", color: "#59616f" }}>
                  Best Prompt Style
                </div>
                <div style={{ marginTop: 8, lineHeight: 1.6 }}>{selectedAgent.example}</div>
              </div>
              <button
                type="button"
                onClick={() => applyExample(selectedAgent.example)}
                style={{
                  marginTop: 16,
                  border: 0,
                  borderRadius: 999,
                  background: selectedAgent.color,
                  color: "white",
                  padding: "10px 14px",
                  cursor: "pointer",
                  fontWeight: 600,
                }}
              >
                Load This Agent Example
              </button>
            </article>

            <article
              style={{
                borderRadius: 24,
                background: "#18212b",
                color: "#f7f4ed",
                padding: 22,
              }}
            >
              <div style={{ fontSize: 13, letterSpacing: "0.08em", textTransform: "uppercase", color: "#f6c56e" }}>
                What This Service Needs
              </div>
              <ul style={{ margin: "14px 0 0", paddingLeft: 18, lineHeight: 1.75 }}>
                <li>User ID so the app can load profile context.</li>
                <li>A clear outcome, not just a topic.</li>
                <li>Relevant constraints, dates, or priorities inside your prompt.</li>
                <li>
                  For compliance only: shared folder path, business markdown file, and optional extra source URLs.
                </li>
              </ul>
              <div
                style={{
                  marginTop: 18,
                  borderRadius: 18,
                  background: "rgba(255,255,255,0.08)",
                  padding: 14,
                  border: `1px solid ${selectedAgent.color}55`,
                }}
              >
                <strong>Selected route:</strong> {selectedAgent.route}
                <div style={{ marginTop: 8, color: "rgba(247,244,237,0.82)", lineHeight: 1.6 }}>
                  Clicking an agent in the graph or tabs loads its example into the workspace so the user understands how to talk to it.
                </div>
              </div>
            </article>
          </div>
        </section>

        <section
          style={{
            display: "grid",
            gridTemplateColumns: "1.2fr 0.8fr",
            gap: 24,
            alignItems: "start",
          }}
        >
          <form
            onSubmit={submitPrompt}
            style={{
              borderRadius: 28,
              background: "rgba(255,255,255,0.88)",
              border: "1px solid rgba(24,33,43,0.08)",
              padding: 24,
              boxShadow: "0 18px 48px rgba(35, 47, 62, 0.09)",
              display: "grid",
              gap: 18,
            }}
          >
            <div>
              <div style={{ fontSize: 13, letterSpacing: "0.08em", textTransform: "uppercase", color: "#59616f" }}>
                Prompt Workspace
              </div>
              <h2 style={{ margin: "8px 0 0", fontSize: 32 }}>Tell the assistant what outcome you want.</h2>
            </div>

            <label style={{ display: "grid", gap: 8 }}>
              <span style={{ fontWeight: 700 }}>User ID</span>
              <input
                value={userId}
                onChange={(e) => setUserId(e.target.value)}
                style={inputStyle}
                placeholder="desktop-user"
              />
            </label>

            <label style={{ display: "grid", gap: 8 }}>
              <span style={{ fontWeight: 700 }}>Message</span>
              <textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                rows={6}
                style={{ ...inputStyle, resize: "vertical", minHeight: 150 }}
                placeholder="Describe what you want the assistant to do."
              />
            </label>

            <div
              style={{
                borderRadius: 22,
                background: "#f8f3e6",
                border: "1px solid rgba(24,33,43,0.08)",
                padding: 18,
                display: "grid",
                gap: 14,
              }}
            >
              <div style={{ fontWeight: 800, fontSize: 20 }}>Compliance Inputs</div>
              <div style={{ color: "#5b4d2d", lineHeight: 1.6 }}>
                Only needed when selected route is Compliance.
              </div>
              {selectedAgentRoute !== "compliance" ? (
                <div style={{ color: "#5b4d2d", fontSize: 14 }}>
                  Switch to Compliance route to enable these fields.
                </div>
              ) : (
                <>
                  <div
                    style={{
                      borderRadius: 16,
                      background: "#fff",
                      border: "1px solid rgba(24,33,43,0.12)",
                      padding: 12,
                      display: "grid",
                      gap: 10,
                    }}
                  >
                    <div style={{ fontWeight: 700 }}>Upload Business Profile & Legal Docs</div>
                    <div style={{ color: "#5b4d2d", fontSize: 14, lineHeight: 1.5 }}>
                      Upload .md/.txt business context and optional legal documents (.pdf/.docx/.txt).
                    </div>
                    <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
                      <button
                        type="button"
                        onClick={() => fileInputRef.current?.click()}
                        style={secondaryButtonStyle}
                      >
                        Choose Files
                      </button>
                      <button
                        type="button"
                        onClick={() => folderInputRef.current?.click()}
                        style={secondaryButtonStyle}
                      >
                        Choose Folder
                      </button>
                      <button type="button" onClick={clearUploadedFiles} style={secondaryButtonStyle}>
                        Clear Uploads
                      </button>
                    </div>
                    <input
                      ref={fileInputRef}
                      type="file"
                      multiple
                      accept=".md,.txt,.pdf,.doc,.docx,.html"
                      onChange={(e) => addFilesFromSelection(e.target.files)}
                      style={{ display: "none" }}
                    />
                    <input
                      ref={folderInputRef}
                      type="file"
                      multiple
                      webkitdirectory=""
                      directory=""
                      onChange={(e) => addFilesFromSelection(e.target.files)}
                      style={{ display: "none" }}
                    />
                    {uploadedFiles.length > 0 && (
                      <>
                        <div style={{ fontSize: 14 }}>
                          Uploaded files ready: <strong>{uploadedFiles.length}</strong>
                        </div>
                        <div style={{ fontSize: 12, color: "#5f6470" }}>
                          {uploadedFiles.slice(0, 5).map((f) => f.name).join(", ")}
                          {uploadedFiles.length > 5 ? " ..." : ""}
                        </div>
                        <label style={{ display: "grid", gap: 8 }}>
                          <span>Business context file from uploads (.md or .txt)</span>
                          <select
                            value={uploadedBusinessFile}
                            onChange={(e) => setUploadedBusinessFile(e.target.value)}
                            style={inputStyle}
                          >
                            <option value="">Auto-pick first .md/.txt</option>
                            {uploadedFiles
                              .filter((f) => /\.(md|txt)$/i.test(f.name))
                              .map((f) => (
                                <option key={f.name} value={f.name}>
                                  {f.name}
                                </option>
                              ))}
                          </select>
                        </label>
                      </>
                    )}
                    <div style={{ color: "#5b4d2d", fontSize: 13 }}>
                      Reports are saved in the same folder as your selected business context file.
                    </div>
                  </div>

                  <label style={{ display: "grid", gap: 8 }}>
                    <span>Legal/Compliance URLs (optional, one per line or comma separated)</span>
                    <textarea
                      value={sourceUrls}
                      onChange={(e) => setSourceUrls(e.target.value)}
                      rows={4}
                      style={{ ...inputStyle, resize: "vertical" }}
                      placeholder="https://example.gov/regulation-page"
                    />
                  </label>
                  <div style={{ color: "#5b4d2d", fontSize: 13 }}>
                    If no URLs are provided, the agent automatically uses official internet sources.
                  </div>
                </>
              )}
            </div>

            <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
              <button type="submit" disabled={loading} style={primaryButtonStyle}>
                {loading ? "Running assistant..." : "Run Assistant"}
              </button>
              <button
                type="button"
                onClick={() => {
                  setMessage("Run a compliance review for my cross-border business.");
                }}
                style={secondaryButtonStyle}
              >
                Load Compliance Example
              </button>
            </div>

            {error && <p style={{ color: "crimson", margin: 0 }}>Error: {error}</p>}
          </form>

          <div style={{ display: "grid", gap: 20 }}>
            <aside
              style={{
                borderRadius: 28,
                background: "#18212b",
                color: "#f7f4ed",
                padding: 24,
                boxShadow: "0 20px 44px rgba(24, 33, 43, 0.2)",
              }}
            >
              <div style={{ fontSize: 13, letterSpacing: "0.08em", textTransform: "uppercase", color: "#f6c56e" }}>
                Compliance Workflow
              </div>
              <ol style={{ margin: "14px 0 0", paddingLeft: 20, lineHeight: 1.7 }}>
                {COMPLIANCE_STEPS.map((step) => (
                  <li key={step} style={{ marginBottom: 10 }}>
                    {step}
                  </li>
                ))}
              </ol>
            </aside>

            <section
              style={{
                borderRadius: 28,
                background: "rgba(255,255,255,0.88)",
                border: "1px solid rgba(24,33,43,0.08)",
                padding: 24,
                minHeight: 340,
                boxShadow: "0 18px 48px rgba(35, 47, 62, 0.09)",
              }}
            >
              <div style={{ fontSize: 13, letterSpacing: "0.08em", textTransform: "uppercase", color: "#59616f" }}>
                Response Panel
              </div>
              {!result ? (
                <div style={{ marginTop: 18, color: "#59616f", lineHeight: 1.7 }}>
                  Send a message to see:
                  <ul>
                    <li>Which agent the coordinator selected</li>
                    <li>A concise summary</li>
                    <li>Action items with priorities</li>
                  </ul>
                </div>
              ) : (
                <div style={{ marginTop: 16, display: "grid", gap: 14 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                    <span style={{ fontWeight: 800, fontSize: 24 }}>{result.route}</span>
                    <span
                      style={{
                        padding: "6px 12px",
                        borderRadius: 999,
                        background: "#18212b",
                        color: "#f7f4ed",
                        fontSize: 13,
                        textTransform: "uppercase",
                        letterSpacing: "0.06em",
                      }}
                    >
                      selected route
                    </span>
                  </div>
                  <p style={{ margin: 0, fontSize: 17, lineHeight: 1.7 }}>{result.result.summary}</p>
                  {downloadActions.length > 0 && (
                    <div
                      style={{
                        borderRadius: 18,
                        padding: 14,
                        background: "#eef4fb",
                        border: "1px solid rgba(24,33,43,0.1)",
                        display: "grid",
                        gap: 10,
                      }}
                    >
                      <div
                        style={{
                          fontSize: 12,
                          letterSpacing: "0.08em",
                          textTransform: "uppercase",
                          color: "#2f4661",
                          fontWeight: 700,
                        }}
                      >
                        Downloads
                      </div>
                      <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                        {reportDownload?.download_url && (
                          <a
                            href={reportDownload.download_url}
                            target="_blank"
                            rel="noreferrer"
                            style={downloadBadgeStyle}
                          >
                            Report (.md)
                          </a>
                        )}
                        {pdfDownload?.download_url && (
                          <a
                            href={pdfDownload.download_url}
                            target="_blank"
                            rel="noreferrer"
                            style={downloadBadgeStyle}
                          >
                            Report PDF
                          </a>
                        )}
                        {resourcesDownload?.download_url && (
                          <a
                            href={resourcesDownload.download_url}
                            target="_blank"
                            rel="noreferrer"
                            style={downloadBadgeStyle}
                          >
                            Resources (.zip)
                          </a>
                        )}
                      </div>
                    </div>
                  )}
                  <div style={{ display: "grid", gap: 10 }}>
                    {result.result.actions.map((item, idx) => (
                      <div
                        key={`${item.title}-${idx}`}
                        style={{
                          borderRadius: 18,
                          padding: 14,
                          background: "#f6f7f9",
                          border: "1px solid rgba(24,33,43,0.07)",
                        }}
                      >
                        <div style={{ display: "flex", justifyContent: "space-between", gap: 12 }}>
                          <strong>{item.title}</strong>
                          <span style={{ textTransform: "uppercase", fontSize: 12, color: "#5f6470" }}>
                            {item.priority}
                          </span>
                        </div>
                        <div style={{ marginTop: 8, lineHeight: 1.55 }}>{item.details}</div>
                        {item.download_url && (
                          <a
                            href={item.download_url}
                            target="_blank"
                            rel="noreferrer"
                            style={{
                              display: "inline-block",
                              marginTop: 10,
                              borderRadius: 999,
                              background: "#18212b",
                              color: "#f7f4ed",
                              padding: "8px 12px",
                              textDecoration: "none",
                              fontSize: 13,
                              fontWeight: 700,
                            }}
                          >
                            Download
                          </a>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </section>
          </div>
        </section>
      </section>
    </main>
  );
}

const downloadBadgeStyle = {
  borderRadius: 999,
  background: "#18212b",
  color: "#f7f4ed",
  padding: "8px 12px",
  textDecoration: "none",
  fontSize: 13,
  fontWeight: 700,
};

function ServiceBox({ title, subtitle, tone, compact = false, interactive = false, active = false, onClick }) {
  return (
    <div
      onClick={onClick}
      style={{
        borderRadius: compact ? 16 : 18,
        padding: compact ? "10px 12px" : "14px 16px",
        background: active ? "rgba(255,255,255,0.18)" : "rgba(255,255,255,0.08)",
        border: `1px solid ${active ? tone : `${tone}55`}`,
        cursor: interactive ? "pointer" : "default",
        transform: active ? "translateY(-1px)" : "none",
        boxShadow: active ? `0 0 0 1px ${tone}55 inset` : "none",
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
        <span
          style={{
            width: 12,
            height: 12,
            borderRadius: 999,
            background: tone,
            boxShadow: `0 0 0 4px ${tone}30`,
            flexShrink: 0,
          }}
        />
        <strong style={{ fontSize: compact ? 14 : 16 }}>{title}</strong>
      </div>
      <div style={{ marginTop: 8, fontSize: compact ? 12 : 13, color: "rgba(247,244,237,0.82)" }}>{subtitle}</div>
    </div>
  );
}

function Connector() {
  return <div style={{ height: 18, width: 2, background: "linear-gradient(180deg, #f6c56e, #88a9ff)", justifySelf: "center" }} />;
}

const inputStyle = {
  width: "100%",
  borderRadius: 16,
  border: "1px solid rgba(24,33,43,0.14)",
  background: "#fff",
  padding: "13px 14px",
  fontSize: 15,
  color: "#18212b",
  boxSizing: "border-box",
};

const primaryButtonStyle = {
  border: 0,
  borderRadius: 999,
  background: "#18212b",
  color: "#f7f4ed",
  padding: "12px 18px",
  fontWeight: 700,
  cursor: "pointer",
};

const secondaryButtonStyle = {
  border: "1px solid rgba(24,33,43,0.16)",
  borderRadius: 999,
  background: "rgba(24,33,43,0.04)",
  color: "#18212b",
  padding: "12px 18px",
  fontWeight: 700,
  cursor: "pointer",
};
