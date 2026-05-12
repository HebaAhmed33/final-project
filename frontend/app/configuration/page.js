"use client";

import { useRouter } from "next/navigation";
import PageContainer from "../components/PageContainer";

export default function ConfigurationPage() {
  const router = useRouter();

  const cardStyle = {
    flex: 1, padding: "2.5rem 2rem", borderRadius: "1rem", cursor: "pointer",
    border: "2px solid var(--border-color)", background: "var(--bg-card)",
    transition: "all 0.3s ease", display: "flex", flexDirection: "column",
    alignItems: "center", justifyContent: "center", textAlign: "center",
    minHeight: "280px"
  };

  const handleMouseEnter = (e) => {
    e.currentTarget.style.borderColor = "var(--primary)";
    e.currentTarget.style.transform = "translateY(-4px)";
    e.currentTarget.style.boxShadow = "0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1)";
  };

  const handleMouseLeave = (e) => {
    e.currentTarget.style.borderColor = "var(--border-color)";
    e.currentTarget.style.transform = "translateY(0)";
    e.currentTarget.style.boxShadow = "none";
  };

  return (
    <PageContainer>
      {/* Page Header */}
      <div style={{ padding: "0 0 2rem", textAlign: "center", marginBottom: "2rem" }}>
        <h1 style={{ fontSize: "2.5rem", fontWeight: 800, letterSpacing: "-0.04em", marginBottom: "0.5rem", color: "var(--text-main)" }}>
          Technical Configuration
        </h1>
        <p style={{ color: "var(--text-main)", fontSize: "1.1rem", fontWeight: 600, maxWidth: "700px", lineHeight: "1.6", margin: "0 auto 0.25rem auto" }}>
          Analyze technical configurations for compliance.
        </p>
        <p style={{ color: "var(--text-muted)", fontSize: "0.95rem", maxWidth: "700px", lineHeight: "1.6", margin: "0 auto" }}>
          Upload configuration files or perform a live SSH-based scan to map against security frameworks.
        </p>
      </div>

      {/* ── Mode Selection Cards ──────────────────────────────────────────────── */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "2rem", maxWidth: "900px", margin: "0 auto" }}>
        
        <div 
          onClick={() => router.push("/configuration/upload")}
          style={cardStyle}
          onMouseEnter={handleMouseEnter}
          onMouseLeave={handleMouseLeave}
        >
          <div style={{ 
            width: "64px", height: "64px", borderRadius: "50%", 
            background: "rgba(37, 99, 235, 0.1)", color: "var(--primary)",
            display: "flex", alignItems: "center", justifyContent: "center",
            marginBottom: "1.5rem"
          }}>
            <svg style={{ width: "32px", height: "32px" }} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" /></svg>
          </div>
          <h2 style={{ fontSize: "1.5rem", fontWeight: 700, color: "var(--text-main)", margin: "0 0 0.5rem 0" }}>
            Upload Configuration Files
          </h2>
          <p style={{ fontSize: "0.95rem", color: "var(--text-muted)", margin: 0, lineHeight: "1.5" }}>
            Upload JSON, YAML, ENV, or raw config files for analysis against selected frameworks
          </p>
        </div>

        <div 
          onClick={() => router.push("/configuration/live")}
          style={cardStyle}
          onMouseEnter={handleMouseEnter}
          onMouseLeave={handleMouseLeave}
        >
          <div style={{ 
            width: "64px", height: "64px", borderRadius: "50%", 
            background: "rgba(37, 99, 235, 0.1)", color: "var(--primary)",
            display: "flex", alignItems: "center", justifyContent: "center",
            marginBottom: "1.5rem"
          }}>
            <svg style={{ width: "32px", height: "32px" }} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>
          </div>
          <h2 style={{ fontSize: "1.5rem", fontWeight: 700, color: "var(--text-main)", margin: "0 0 0.5rem 0" }}>
            Live Configuration Scan
          </h2>
          <p style={{ fontSize: "0.95rem", color: "var(--text-muted)", margin: 0, lineHeight: "1.5" }}>
            SSH into a server and scan its live configuration remotely
          </p>
        </div>
      </div>
    </PageContainer>
  );
}
