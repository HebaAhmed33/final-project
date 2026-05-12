"use client";

import { useState, useRef } from "react";
import { useRouter } from "next/navigation";
import PageContainer from "../../components/PageContainer";
import API_BASE_URL from "../../lib/api";

export default function ConfigurationLivePage() {
  const router = useRouter();

  // ── NEW Live Scan state (ISOLATED) ─────────────────────────────────────
  const [scanHost, setScanHost] = useState("");
  const [scanPort, setScanPort] = useState("22");
  const [scanUsername, setScanUsername] = useState("");
  const [scanKeyFile, setScanKeyFile] = useState(null);
  const [scanFramework, setScanFramework] = useState("cis");
  const [scanLoading, setScanLoading] = useState(false);
  const [scanError, setScanError] = useState(null);
  const [scanProgress, setScanProgress] = useState([]);
  const scanKeyRef = useRef(null);

  const handleLiveScan = async (e) => {
    e.preventDefault();
    setScanError(null);
    setScanProgress([]);

    if (!scanHost.trim()) { setScanError("Target IP / Hostname is required."); return; }
    if (!scanUsername.trim()) { setScanError("Username is required."); return; }
    if (!scanKeyFile) { setScanError("SSH Private Key file is required."); return; }

    setScanLoading(true);
    setScanProgress([{ message: "Reading SSH key...", status: "running" }]);

    try {
      // Read key file content as UTF-8 text
      const keyContent = await scanKeyFile.text();
      const validHeaders = ["BEGIN OPENSSH PRIVATE KEY", "BEGIN RSA PRIVATE KEY", "BEGIN EC PRIVATE KEY", "BEGIN DSA PRIVATE KEY", "BEGIN PRIVATE KEY"];
      const hasValidHeader = validHeaders.some(h => keyContent.includes(h));
      if (!hasValidHeader) {
        setScanError("Invalid SSH private key format. The file must contain a valid private key (OpenSSH, RSA, EC, or PEM format).");
        setScanLoading(false);
        return;
      }

      setScanProgress(prev => [...prev, { message: "Sending scan request...", status: "running" }]);

      const res = await fetch(`http://localhost:8000/live-scan/start`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          host: scanHost.trim(),
          port: parseInt(scanPort) || 22,
          username: scanUsername.trim(),
          private_key: keyContent,
          framework: scanFramework,
        }),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || "Scan request failed");
      }

      const data = await res.json();

      if (data.progress) {
        setScanProgress(data.progress);
      }

      if (data.success) {
        // Store result and redirect to results page
        if (typeof window !== "undefined") {
          sessionStorage.setItem("config_result", JSON.stringify(data));
        }
        router.push("/configuration-results");
      } else {
        setScanError(data.error || "Scan failed. Check the target host and credentials.");
        setScanLoading(false);
      }
    } catch (err) {
      if (err instanceof TypeError && err.message === "Failed to fetch") {
        setScanError(`Cannot connect to backend at ${API_BASE_URL}. Make sure the backend server is running.`);
      } else {
        setScanError(err.message || "An unexpected error occurred.");
      }
      setScanLoading(false);
    }
  };

  const fwBtnStyle = (active) => ({
    padding: "1rem", borderRadius: "0.5rem", cursor: "pointer",
    border: `2px solid ${active ? "var(--primary)" : "var(--border-color)"}`,
    background: active ? "rgba(37, 99, 235, 0.06)" : "var(--bg-main)",
    color: active ? "var(--primary)" : "var(--text-main)",
    fontWeight: active ? 700 : 500, transition: "all 0.2s ease",
    display: "flex", flexDirection: "column", gap: "0.25rem", alignItems: "center",
  });

  const inputStyle = {
    width: "100%", padding: "0.75rem 1rem", borderRadius: "0.5rem",
    border: "1px solid var(--border-color)", background: "var(--bg-main)",
    color: "var(--text-main)", fontSize: "0.95rem", outline: "none",
    transition: "border-color 0.2s",
  };

  const labelStyle = {
    display: "block", fontSize: "0.85rem", fontWeight: 600,
    color: "var(--text-main)", marginBottom: "0.4rem",
  };

  return (
    <PageContainer>
      {/* Page Header */}
      <div style={{ padding: "0 0 2rem", display: "flex", alignItems: "center", gap: "1rem" }}>
        <button 
          onClick={() => router.push("/configuration")}
          style={{ 
            display: "flex", alignItems: "center", gap: "0.5rem", 
            padding: "0.5rem 1rem", borderRadius: "0.5rem", 
            border: "1px solid var(--border-color)", 
            background: "transparent", color: "var(--text-main)", 
            cursor: "pointer", fontSize: "0.9rem", fontWeight: 600
          }}
        >
          <svg style={{ width: "16px", height: "16px" }} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" /></svg>
          Back
        </button>
        <div>
          <h1 style={{ fontSize: "2.5rem", fontWeight: 800, letterSpacing: "-0.04em", marginBottom: "0.5rem", color: "var(--text-main)" }}>
            Live Configuration Scan
          </h1>
          <p style={{ color: "var(--text-muted)", fontSize: "0.95rem", maxWidth: "700px", lineHeight: "1.6", margin: 0 }}>
            SSH into a server and scan its live configuration remotely
          </p>
        </div>
      </div>

      {/* ──────────── ERROR ──────────── */}
      {scanError && (
        <div style={{ padding: "1rem", marginBottom: "1.5rem", background: "rgba(239,68,68,0.05)", border: "1px solid #EF4444", color: "#EF4444", borderRadius: "0.5rem", display: "flex", alignItems: "center", gap: "0.75rem" }}>
          <svg style={{ width: "20px", height: "20px", flexShrink: 0 }} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
          <span style={{ fontSize: "0.95rem" }}>{scanError}</span>
        </div>
      )}

      <form onSubmit={handleLiveScan}>
        <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
          {/* Framework Selection for Live Scan */}
          <div className="card" style={{ padding: "1.5rem" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "1rem" }}>
              <span style={{ display: "flex", alignItems: "center", justifyContent: "center", width: "24px", height: "24px", borderRadius: "50%", background: "var(--primary)", color: "#fff", fontSize: "0.8rem", fontWeight: 700 }}>1</span>
              <h3 style={{ fontSize: "1.1rem", fontWeight: 700, color: "var(--text-main)", margin: 0 }}>Compliance Framework</h3>
            </div>
            <p style={{ color: "var(--text-muted)", fontSize: "0.9rem", marginBottom: "1rem" }}>Select a framework to evaluate the live configuration against.</p>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: "0.75rem" }}>
              {[
                { key: "cis", label: "CIS Controls", desc: "Center for Internet Security" },
                { key: "nist", label: "NIST 800-53", desc: "National Institute of Standards" },
              ].map((fw) => (
                <button key={fw.key} type="button" onClick={() => setScanFramework(fw.key)} style={fwBtnStyle(scanFramework === fw.key)}>
                  <span style={{ fontSize: "1rem" }}>{fw.label}</span>
                  <span style={{ fontSize: "0.75rem", color: "var(--text-muted)", fontWeight: 400 }}>{fw.desc}</span>
                </button>
              ))}
            </div>
          </div>

          {/* SSH Connection Details */}
          <div className="card" style={{ padding: "1.5rem" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "1rem" }}>
              <span style={{ display: "flex", alignItems: "center", justifyContent: "center", width: "24px", height: "24px", borderRadius: "50%", background: "var(--primary)", color: "#fff", fontSize: "0.8rem", fontWeight: 700 }}>2</span>
              <h3 style={{ fontSize: "1.1rem", fontWeight: 700, color: "var(--text-main)", margin: 0 }}>SSH Connection Details</h3>
            </div>
            <p style={{ color: "var(--text-muted)", fontSize: "0.9rem", marginBottom: "1.25rem" }}>
              Provide credentials for a read-only SSH connection. Your private key is used in-memory only and is never stored.
            </p>

            <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: "1rem", marginBottom: "1rem" }}>
              <div>
                <label style={labelStyle}>Target IP / Hostname *</label>
                <input type="text" value={scanHost} onChange={(e) => setScanHost(e.target.value)} placeholder="e.g. 192.168.1.100" required style={inputStyle} />
              </div>
              <div>
                <label style={labelStyle}>SSH Port</label>
                <input type="number" value={scanPort} onChange={(e) => setScanPort(e.target.value)} placeholder="22" min="1" max="65535" style={inputStyle} />
              </div>
            </div>

            <div style={{ marginBottom: "1rem" }}>
              <label style={labelStyle}>Username *</label>
              <input type="text" value={scanUsername} onChange={(e) => setScanUsername(e.target.value)} placeholder="e.g. root" required style={inputStyle} />
            </div>

            <div>
              <label style={labelStyle}>SSH Private Key (.pem / id_rsa) *</label>
              <div style={{ border: "2px dashed var(--border-color)", borderRadius: "0.5rem", padding: "1.25rem", textAlign: "center", background: "var(--bg-main)" }}>
                <svg style={{ width: "32px", height: "32px", color: "var(--primary)", margin: "0 auto 0.5rem" }} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" /></svg>
                <input type="file" onChange={(e) => setScanKeyFile(e.target.files?.[0] || null)} ref={scanKeyRef} required id="scan-key-input" style={{ display: "none" }} />
                <label htmlFor="scan-key-input" className="btn-primary" style={{ display: "inline-block", cursor: "pointer", marginBottom: "0.5rem", padding: "0.5rem 1.25rem", fontSize: "0.9rem" }}>Select Key File</label>
                <div style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>
                  {scanKeyFile ? <span style={{ color: "var(--primary)", fontWeight: 600 }}>{scanKeyFile.name}</span> : "Accepts any SSH private key file (.pem, id_rsa, id_ed25519, id_ecdsa)"}
                </div>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginTop: "0.75rem", padding: "0.6rem 0.75rem", background: "rgba(37, 99, 235, 0.04)", borderRadius: "0.5rem", border: "1px solid rgba(37, 99, 235, 0.1)" }}>
                <svg style={{ width: "16px", height: "16px", color: "var(--primary)", flexShrink: 0 }} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" /></svg>
                <span style={{ fontSize: "0.78rem", color: "var(--text-muted)" }}>Your private key is used in-memory only and is never stored, logged, or persisted.</span>
              </div>
            </div>
          </div>

          {/* Scan Progress */}
          {scanProgress.length > 0 && (
            <div className="card" style={{ padding: "1.5rem" }}>
              <h3 style={{ fontSize: "1rem", fontWeight: 700, color: "var(--text-main)", margin: "0 0 1rem 0" }}>Scan Progress</h3>
              <div style={{ display: "flex", flexDirection: "column", gap: "0.4rem" }}>
                {scanProgress.map((step, i) => (
                  <div key={i} style={{ display: "flex", alignItems: "center", gap: "0.5rem", fontSize: "0.85rem", padding: "0.35rem 0" }}>
                    {step.status === "success" ? (
                      <svg style={{ width: "16px", height: "16px", color: "#10B981", flexShrink: 0 }} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
                    ) : step.status === "error" ? (
                      <svg style={{ width: "16px", height: "16px", color: "#EF4444", flexShrink: 0 }} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
                    ) : step.status === "warning" ? (
                      <svg style={{ width: "16px", height: "16px", color: "#F59E0B", flexShrink: 0 }} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.27 16.5c-.77.833.192 2.5 1.732 2.5z" /></svg>
                    ) : (
                      <span style={{ width: "16px", height: "16px", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                        <span style={{ width: "8px", height: "8px", borderRadius: "50%", background: "var(--primary)", animation: "pulse 1.5s infinite" }}></span>
                      </span>
                    )}
                    <span style={{ color: step.status === "error" ? "#EF4444" : step.status === "warning" ? "#F59E0B" : "var(--text-main)" }}>{step.message}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Submit Button */}
          <div className="card" style={{ padding: "1.5rem", border: "2px solid var(--primary)", background: "rgba(37, 99, 235, 0.02)" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "1rem" }}>
              <span style={{ display: "flex", alignItems: "center", justifyContent: "center", width: "24px", height: "24px", borderRadius: "50%", background: "var(--primary)", color: "#fff", fontSize: "0.8rem", fontWeight: 700 }}>3</span>
              <h3 style={{ fontSize: "1.1rem", fontWeight: 700, color: "var(--text-main)", margin: 0 }}>Start Scan</h3>
            </div>
            <p style={{ color: "var(--text-muted)", fontSize: "0.9rem", marginBottom: "1rem" }}>
              The scanner will connect via SSH, fetch configurations using read-only commands, and evaluate them against the selected framework.
            </p>
            <div style={{ display: "flex", justifyContent: "flex-end" }}>
              <button type="submit" className="btn-primary" disabled={scanLoading} style={{ minWidth: "200px", padding: "0.85rem 1.5rem", fontSize: "1rem", display: "flex", alignItems: "center", justifyContent: "center", gap: "0.5rem" }}>
                {scanLoading ? (
                  <>
                    <span style={{ width: "16px", height: "16px", border: "2px solid rgba(255,255,255,0.3)", borderTop: "2px solid #fff", borderRadius: "50%", animation: "spin 1s linear infinite", display: "inline-block" }}></span>
                    Scanning...
                  </>
                ) : "Start Live Scan"}
              </button>
            </div>
          </div>
        </div>
      </form>

      <style jsx>{`
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }
        @keyframes spin { to { transform: rotate(360deg); } }
      `}</style>
    </PageContainer>
  );
}
