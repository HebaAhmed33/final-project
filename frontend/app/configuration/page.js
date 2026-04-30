"use client";

import { useState, useRef } from "react";
import { useRouter } from "next/navigation";
import PageContainer from "../components/PageContainer";
import API_BASE_URL from "../lib/api";

export default function ConfigurationPage() {
  const router = useRouter();
  
  // Config fields
  const [configFile, setConfigFile] = useState(null);
  const [configFramework, setConfigFramework] = useState("cis");

  // Status
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Refs
  const configFileRef = useRef(null);

  const resetStatus = () => { setError(null); };

  // ── Config submit ──────────────────────────────────────────────────────
  const handleConfigSubmit = async (e) => {
    e.preventDefault();
    if (!configFile) { setError("Please select a configuration file."); return; }

    setLoading(true);
    resetStatus();

    const formData = new FormData();
    formData.append("file", configFile);
    formData.append("framework", configFramework);

    try {
      const res = await fetch(`http://localhost:8000/upload/configuration`, {
        method: "POST",
        body: formData,
      });
      if (res.headers.get("content-type")?.includes("text/html")) {
        throw new Error("API returned HTML instead of JSON");
      }
      if (!res.ok) {
        throw new Error("API request failed");
      }
      const data = await res.json();
      
      // Store result and redirect
      if (typeof window !== "undefined") {
        sessionStorage.setItem("config_result", JSON.stringify(data));
      }
      
      setConfigFile(null);
      if (configFileRef.current) configFileRef.current.value = "";
      
      router.push("/configuration-results");
    } catch (err) {
      if (err instanceof TypeError && err.message === "Failed to fetch") {
        setError(`Cannot connect to backend at ${API_BASE_URL}. Make sure the backend server is running.`);
      } else {
        setError(err.message || "An unexpected error occurred.");
      }
      setLoading(false);
    }
  };

  return (
    <PageContainer>
      {/* Page Header */}
      <div style={{ padding: "0 0 2rem" }}>
        <h1 style={{ fontSize: "2.5rem", fontWeight: 800, letterSpacing: "-0.04em", marginBottom: "0.5rem", color: "var(--text-main)" }}>
          Technical Configuration
        </h1>
        <p style={{ color: "var(--text-main)", fontSize: "1.1rem", fontWeight: 600, maxWidth: "700px", lineHeight: "1.6", margin: "0 0 0.25rem 0" }}>
          Analyze technical configurations for compliance.
        </p>
        <p style={{ color: "var(--text-muted)", fontSize: "0.95rem", maxWidth: "700px", lineHeight: "1.6", margin: 0 }}>
          Upload JSON, YAML, ENV, or raw files to map against CIS, NIST, or ISO 27001.
        </p>
      </div>

      {/* ──────────── ERROR ──────────── */}
      {error && (
        <div style={{ padding: "1rem", marginBottom: "1.5rem", background: "rgba(239,68,68,0.05)", border: "1px solid #EF4444", color: "#EF4444", borderRadius: "0.5rem", display: "flex", alignItems: "center", gap: "0.75rem" }}>
          <svg style={{ width: "20px", height: "20px", flexShrink: 0 }} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
          <span style={{ fontSize: "0.95rem" }}>{error}</span>
        </div>
      )}

      {/* ──────────── CONFIGURATION FORM ──────────── */}
      <form onSubmit={handleConfigSubmit}>
        <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
          {/* Framework Selection */}
          <div className="card" style={{ padding: "1.5rem" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "1rem" }}>
              <span style={{ display: "flex", alignItems: "center", justifyContent: "center", width: "24px", height: "24px", borderRadius: "50%", background: "var(--primary)", color: "#fff", fontSize: "0.8rem", fontWeight: 700 }}>1</span>
              <h3 style={{ fontSize: "1.1rem", fontWeight: 700, color: "var(--text-main)", margin: 0 }}>Compliance Framework</h3>
            </div>
            <p style={{ color: "var(--text-muted)", fontSize: "0.9rem", marginBottom: "1rem" }}>Select a framework to map configuration findings against.</p>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "0.75rem" }}>
              {[
                { key: "cis", label: "CIS Controls", desc: "Center for Internet Security" },
                { key: "nist", label: "NIST 800-53", desc: "National Institute of Standards" },
                { key: "iso27001", label: "ISO 27001", desc: "Information Security Management" },
              ].map((fw) => (
                <button key={fw.key} type="button" onClick={() => setConfigFramework(fw.key)}
                  style={{
                    padding: "1rem", borderRadius: "0.5rem", cursor: "pointer",
                    border: `2px solid ${configFramework === fw.key ? "var(--primary)" : "var(--border-color)"}`,
                    background: configFramework === fw.key ? "rgba(37, 99, 235, 0.06)" : "var(--bg-main)",
                    color: configFramework === fw.key ? "var(--primary)" : "var(--text-main)",
                    fontWeight: configFramework === fw.key ? 700 : 500, transition: "all 0.2s ease",
                    display: "flex", flexDirection: "column", gap: "0.25rem", alignItems: "center",
                  }}>
                  <span style={{ fontSize: "1rem" }}>{fw.label}</span>
                  <span style={{ fontSize: "0.75rem", color: "var(--text-muted)", fontWeight: 400 }}>{fw.desc}</span>
                </button>
              ))}
            </div>
          </div>

          {/* File Upload */}
          <div className="card" style={{ padding: "1.5rem", border: "2px solid var(--primary)", background: "rgba(37, 99, 235, 0.02)" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "1rem" }}>
              <span style={{ display: "flex", alignItems: "center", justifyContent: "center", width: "24px", height: "24px", borderRadius: "50%", background: "var(--primary)", color: "#fff", fontSize: "0.8rem", fontWeight: 700 }}>2</span>
              <h3 style={{ fontSize: "1.1rem", fontWeight: 700, color: "var(--text-main)", margin: 0 }}>Upload Configuration File</h3>
            </div>
            <div style={{ border: "2px dashed var(--border-color)", borderRadius: "0.5rem", padding: "2rem", textAlign: "center", background: "var(--bg-main)" }}>
              <svg style={{ width: "40px", height: "40px", color: "var(--primary)", margin: "0 auto 0.75rem" }} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" /></svg>
              <input type="file" accept=".json,.yaml,.yml,.env,.sh,.conf,.log,.txt,.fw" onChange={(e) => setConfigFile(e.target.files?.[0] || null)} ref={configFileRef} required id="config-file-input" style={{ display: "none" }} />
              <label htmlFor="config-file-input" className="btn-primary" style={{ display: "inline-block", cursor: "pointer", marginBottom: "0.75rem", padding: "0.6rem 1.5rem" }}>Select File</label>
              <div style={{ fontSize: "0.85rem", color: "var(--text-muted)" }}>
                {configFile ? <span style={{ color: "var(--primary)", fontWeight: 600 }}>{configFile.name}</span> : "Accepts .json, .yaml, .env, .sh, .conf, .log, .txt, .fw"}
              </div>
            </div>
            <div style={{ display: "flex", justifyContent: "flex-end", marginTop: "1.25rem" }}>
              <button type="submit" className="btn-primary" disabled={loading} style={{ minWidth: "200px", padding: "0.85rem 1.5rem", fontSize: "1rem" }}>
                {loading ? "Analyzing..." : "Upload & Analyze"}
              </button>
            </div>
          </div>
        </div>
      </form>

    </PageContainer>
  );
}
