"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import PageContainer from "../components/PageContainer";
import API_BASE_URL from "../lib/api";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip as RechartsTooltip, ResponsiveContainer,
} from "recharts";

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const COMPANY_TYPES = [
  "Company",
  "Government",
  "Healthcare",
  "Financial",
  "Education",
  "Technology",
  "Telecom",
  "Energy",
  "Retail",
  "Other",
];

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function UploadPage() {
  const router = useRouter();
  // Mode
  const [mode, setMode] = useState("assessment");

  // Company info
  const [companyName, setCompanyName] = useState("");
  const [companyType, setCompanyType] = useState("Company");

  // Assessment fields
  const [assessmentFile, setAssessmentFile] = useState(null);
  const [assessmentName, setAssessmentName] = useState("");
  const [framework, setFramework] = useState("iso27001");
  const [priority, setPriority] = useState("Medium");
  const [notes, setNotes] = useState("");

  // Config fields
  const [configFile, setConfigFile] = useState(null);

  // Status
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [uploadResult, setUploadResult] = useState(null);
  const [assessmentResult, setAssessmentResult] = useState(null);

  // Refs
  const assessmentFileRef = useRef(null);
  const configFileRef = useRef(null);

  // Fetch user data for workspace name and type
  useEffect(() => {
    const userStr = localStorage.getItem("smartisms_user");
    if (userStr) {
      try {
        const user = JSON.parse(userStr);
        if (user.companyName) {
          setCompanyName(user.companyName);
        }
        if (user.companyType) {
          setCompanyType(user.companyType);
        } else if (user.organizationType) {
          setCompanyType(user.organizationType);
        }
      } catch (e) {
        console.error("Failed to parse user data");
      }
    }
  }, []);

  const resetStatus = () => { setError(null); setUploadResult(null); setAssessmentResult(null); };

  const handleModeChange = (m) => {
    setMode(m);
    resetStatus();
  };

  // Helpers
  const getBadgeClass = (s) => {
    if (!s) return "badge badge-blue";
    const v = s.toLowerCase();
    if (["compliant", "pass", "low", "true"].includes(v)) return "badge badge-green";
    if (["missing", "fail", "high", "false"].includes(v)) return "badge badge-red";
    if (["partial", "medium"].includes(v)) return "badge badge-yellow";
    return "badge badge-blue";
  };

  const getScoreColor = (score) => {
    if (score >= 80) return "#10B981";
    if (score >= 50) return "#F59E0B";
    return "#EF4444";
  };

  const isEnrichedFramework = framework === "iso27001";
  const getFrameworkLabel = (fw) => fw === "iso27001" ? "ISO 27001" : fw === "hipaa" ? "HIPAA" : "PCI DSS";

  // ── Assessment submit ──────────────────────────────────────────────────
  const handleAssessmentSubmit = async (e) => {
    e.preventDefault();
    if (!assessmentFile) { setError("Please select an Excel file to upload."); return; }
    if (!assessmentName) { setError("Assessment name is required."); return; }
    if (!framework) { setError("Please select a framework."); return; }

    setLoading(true);
    resetStatus();

    const formData = new FormData();
    formData.append("file", assessmentFile);
    formData.append("assessment_name", assessmentName);
    formData.append("framework", getFrameworkLabel(framework));
    formData.append("priority", priority);
    formData.append("notes", notes);

    try {
      // 1) Upload
      const uploadRes = await fetch(`${API_BASE_URL}/upload/assessment`, {
        method: "POST",
        body: formData,
      });
      const uploadData = await uploadRes.json();
      if (!uploadRes.ok) throw new Error(uploadData.detail || uploadData.message || `HTTP ${uploadRes.status}`);
      setUploadResult(uploadData);

      // 2) The upload endpoint now runs the full GRC intelligence inference pipeline
      // and returns the enriched assessment inside framework_assessment
      if (uploadData.framework_assessment && uploadData.framework_assessment.compliance_score !== undefined) {
        setAssessmentResult(uploadData.framework_assessment);
        sessionStorage.setItem("latest_assessment_results", JSON.stringify(uploadData));
        sessionStorage.setItem("assessment_framework_output", JSON.stringify(uploadData.framework_assessment));
      } else if (isEnrichedFramework) {
        // Fallback for legacy mode just in case
        const assessRes = await fetch(`${API_BASE_URL}/assess/${framework}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            assessment_name: assessmentName,
            priority: priority,
            notes: notes,
            use_uploaded_evidence: true,
          }),
        });
        if (assessRes.ok) {
          const assessData = await assessRes.json();
          setAssessmentResult(assessData);
          sessionStorage.setItem("latest_assessment_results", JSON.stringify(uploadData));
          sessionStorage.setItem("assessment_framework_output", JSON.stringify(assessData));
        }
      }

      // Clear form
      setAssessmentFile(null);
      setAssessmentName("");
      setPriority("Medium");
      setNotes("");
      if (assessmentFileRef.current) assessmentFileRef.current.value = "";
      
      // Redirect to results
      setTimeout(() => {
        router.push("/assessment-results");
      }, 1500);
    } catch (err) {
      if (err instanceof TypeError && err.message === "Failed to fetch") {
        setError(`Cannot connect to backend at ${API_BASE_URL}. Make sure the backend server is running (uvicorn app:app --host 0.0.0.0 --port 8000).`);
      } else {
        setError(err.message || "An unexpected error occurred.");
      }
    } finally {
      setLoading(false);
    }
  };

  // ── Config submit ──────────────────────────────────────────────────────
  const handleConfigSubmit = async (e) => {
    e.preventDefault();
    if (!configFile) { setError("Please select a configuration file."); return; }

    setLoading(true);
    resetStatus();

    const formData = new FormData();
    formData.append("file", configFile);

    try {
      const res = await fetch(`${API_BASE_URL}/upload/configuration`, {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || data.message || `HTTP ${res.status}`);
      setUploadResult(data);
      setConfigFile(null);
      if (configFileRef.current) configFileRef.current.value = "";
    } catch (err) {
      if (err instanceof TypeError && err.message === "Failed to fetch") {
        setError(`Cannot connect to backend at ${API_BASE_URL}. Make sure the backend server is running (uvicorn app:app --host 0.0.0.0 --port 8000).`);
      } else {
        setError(err.message || "An unexpected error occurred.");
      }
    } finally {
      setLoading(false);
    }
  };

  // Enriched assessment data
  const ad = assessmentResult;
  const sev = ad?.severity_summary || {};
  const severityChartData = [
    { name: "High", Compliant: sev.high?.compliant || 0, Missing: sev.high?.missing || 0, Partial: sev.high?.partial || 0 },
    { name: "Medium", Compliant: sev.medium?.compliant || 0, Missing: sev.medium?.missing || 0, Partial: sev.medium?.partial || 0 },
    { name: "Low", Compliant: sev.low?.compliant || 0, Missing: sev.low?.missing || 0, Partial: sev.low?.partial || 0 },
  ];

  return (
    <PageContainer>
      {/* Page Header */}
      <div style={{ padding: "0 0 2rem" }}>
        <h1 style={{ fontSize: "2.5rem", fontWeight: 800, letterSpacing: "-0.04em", marginBottom: "0.5rem", color: "var(--text-main)", display: "flex", alignItems: "center", gap: "0.5rem", flexWrap: "wrap" }}>
          Welcome to <span style={{ backgroundColor: "var(--accent, #fce69a)", color: "#1a2340", borderRadius: "6px", padding: "0.2rem 0.5rem", display: "inline-block" }}>
            Aegis.One
          </span>
        </h1>
        <p style={{ color: "var(--text-muted)", fontSize: "1.05rem", maxWidth: "700px", lineHeight: "1.6", margin: 0 }}>
          Welcome{companyName ? `, ${companyName}` : ""}. Start your workspace setup to manage compliance, assessments, and configuration reviews.
        </p>
      </div>

      {/* ──────────── MODE SELECTOR ──────────── */}
      <div className="card" style={{ padding: "0.5rem", marginBottom: "1.5rem" }}>
        <div style={{ display: "flex", gap: "0.5rem" }}>
          {[
            { key: "assessment", label: "Assessment", desc: "Upload compliance evidence (Excel)" },
            { key: "configuration", label: "Configuration", desc: "Upload technical configs (JSON, YAML, ENV)" },
          ].map((m) => (
            <button key={m.key} type="button" onClick={() => handleModeChange(m.key)}
              style={{
                flex: 1, padding: "1rem", borderRadius: "0.5rem", cursor: "pointer",
                border: `2px solid ${mode === m.key ? "var(--primary)" : "transparent"}`,
                background: mode === m.key ? "rgba(37, 99, 235, 0.06)" : "var(--bg-main)",
                color: mode === m.key ? "var(--primary)" : "var(--text-main)",
                fontWeight: mode === m.key ? 700 : 500, transition: "all 0.2s ease",
                display: "flex", flexDirection: "column", gap: "0.35rem", alignItems: "center",
              }}>
              <span style={{ fontSize: "1.05rem" }}>{m.label}</span>
              <span style={{ fontSize: "0.8rem", color: "var(--text-muted)", fontWeight: 400 }}>{m.desc}</span>
            </button>
          ))}
        </div>
      </div>

      {/* ──────────── ERROR ──────────── */}
      {error && (
        <div style={{ padding: "1rem", marginBottom: "1.5rem", background: "rgba(239,68,68,0.05)", border: "1px solid #EF4444", color: "#EF4444", borderRadius: "0.5rem", display: "flex", alignItems: "center", gap: "0.75rem" }}>
          <svg style={{ width: "20px", height: "20px", flexShrink: 0 }} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
          <span style={{ fontSize: "0.95rem" }}>{error}</span>
        </div>
      )}

      {/* ──────────── ASSESSMENT MODE ──────────── */}
      {mode === "assessment" && (
        <form onSubmit={handleAssessmentSubmit}>
          <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>

            {/* Section 1: Company Info */}
            <div className="card" style={{ padding: "1.5rem" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "1rem" }}>
                <span style={{ display: "flex", alignItems: "center", justifyContent: "center", width: "24px", height: "24px", borderRadius: "50%", background: "var(--primary)", color: "#fff", fontSize: "0.8rem", fontWeight: 700 }}>1</span>
                <h3 style={{ fontSize: "1.1rem", fontWeight: 700, color: "var(--text-main)", margin: 0 }}>Company Information</h3>
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1.25rem" }}>
                <div>
                  <label style={{ display: "block", marginBottom: "0.5rem", fontWeight: 600, fontSize: "0.85rem", color: "var(--text-main)" }}>Company Name</label>
                  <div style={{ padding: "0.75rem 1rem", background: "var(--bg-main)", borderRadius: "6px", color: "var(--text-main)", fontSize: "0.95rem", border: "1px solid var(--border-color)", opacity: 0.8 }}>
                    {companyName || "Organization"}
                  </div>
                </div>
                <div>
                  <label style={{ display: "block", marginBottom: "0.5rem", fontWeight: 600, fontSize: "0.85rem", color: "var(--text-main)" }}>Company Type</label>
                  <div style={{ padding: "0.75rem 1rem", background: "var(--bg-main)", borderRadius: "6px", color: "var(--text-main)", fontSize: "0.95rem", border: "1px solid var(--border-color)", opacity: 0.8 }}>
                    {companyType || "Company"}
                  </div>
                </div>
              </div>
            </div>

            {/* Section 2: Assessment Details */}
            <div className="card" style={{ padding: "1.5rem" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "1rem" }}>
                <span style={{ display: "flex", alignItems: "center", justifyContent: "center", width: "24px", height: "24px", borderRadius: "50%", background: "var(--primary)", color: "#fff", fontSize: "0.8rem", fontWeight: 700 }}>2</span>
                <h3 style={{ fontSize: "1.1rem", fontWeight: 700, color: "var(--text-main)", margin: 0 }}>Assessment Details</h3>
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1.25rem" }}>
                <div>
                  <label style={{ display: "block", marginBottom: "0.5rem", fontWeight: 600, fontSize: "0.85rem", color: "var(--text-main)" }}>Assessment Name *</label>
                  <input type="text" className="input-field" value={assessmentName} onChange={(e) => setAssessmentName(e.target.value)} placeholder="e.g. Q3 Risk Audit" required />
                </div>
                <div>
                  <label style={{ display: "block", marginBottom: "0.5rem", fontWeight: 600, fontSize: "0.85rem", color: "var(--text-main)" }}>Standard *</label>
                  <select className="input-field" value={framework} onChange={(e) => setFramework(e.target.value)} required>
                    <option value="iso27001">ISO 27001</option>
                    <option value="hipaa">HIPAA</option>
                    <option value="pci_dss">PCI DSS</option>
                  </select>
                </div>
                <div>
                  <label style={{ display: "block", marginBottom: "0.5rem", fontWeight: 600, fontSize: "0.85rem", color: "var(--text-main)" }}>Priority</label>
                  <select className="input-field" value={priority} onChange={(e) => setPriority(e.target.value)}>
                    {["Low", "Medium", "High", "Critical"].map((p) => <option key={p} value={p}>{p}</option>)}
                  </select>
                </div>
                <div style={{ gridColumn: "1 / -1" }}>
                  <label style={{ display: "block", marginBottom: "0.5rem", fontWeight: 600, fontSize: "0.85rem", color: "var(--text-main)" }}>Notes</label>
                  <textarea className="input-field" value={notes} onChange={(e) => setNotes(e.target.value)} placeholder="Any special instructions..." rows={2} />
                </div>
              </div>
            </div>

            {/* Section 3: Upload Area */}
            <div className="card" style={{ padding: "1.5rem", border: "2px solid var(--primary)", background: "rgba(37, 99, 235, 0.02)" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "1rem" }}>
                <span style={{ display: "flex", alignItems: "center", justifyContent: "center", width: "24px", height: "24px", borderRadius: "50%", background: "var(--primary)", color: "#fff", fontSize: "0.8rem", fontWeight: 700 }}>3</span>
                <h3 style={{ fontSize: "1.1rem", fontWeight: 700, color: "var(--text-main)", margin: 0 }}>Upload Evidence File</h3>
              </div>
              <div style={{ border: "2px dashed var(--border-color)", borderRadius: "0.5rem", padding: "2rem", textAlign: "center", background: "var(--bg-main)" }}>
                <svg style={{ width: "40px", height: "40px", color: "var(--primary)", margin: "0 auto 0.75rem" }} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" /></svg>
                <input type="file" accept=".xlsx,.xls" onChange={(e) => setAssessmentFile(e.target.files?.[0] || null)} ref={assessmentFileRef} required id="assessment-file-input" style={{ display: "none" }} />
                <label htmlFor="assessment-file-input" className="btn-primary" style={{ display: "inline-block", cursor: "pointer", marginBottom: "0.75rem", padding: "0.6rem 1.5rem" }}>
                  Choose Excel File
                </label>
                <div style={{ fontSize: "0.85rem", color: "var(--text-muted)" }}>
                  {assessmentFile ? <span style={{ color: "var(--primary)", fontWeight: 600 }}>{assessmentFile.name}</span> : "Accepts .xlsx, .xls — messy headers auto-normalized"}
                </div>
              </div>
              <div style={{ display: "flex", justifyContent: "flex-end", marginTop: "1.25rem" }}>
                <button type="submit" className="btn-primary" disabled={loading} style={{ minWidth: "200px", padding: "0.85rem 1.5rem", fontSize: "1rem" }}>
                  {loading ? "Processing..." : (isEnrichedFramework ? "Upload & Assess" : "Upload Evidence")}
                </button>
              </div>
            </div>
          </div>
        </form>
      )}

      {/* ──────────── CONFIGURATION MODE ──────────── */}
      {mode === "configuration" && (
        <form onSubmit={handleConfigSubmit}>
          <div className="card" style={{ padding: "2rem" }}>
            <h2 style={{ fontSize: "1.35rem", fontWeight: 700, margin: "0 0 0.5rem 0", color: "var(--text-main)" }}>Configuration Upload</h2>
            <p style={{ color: "var(--text-muted)", fontSize: "0.95rem", marginBottom: "1.5rem" }}>Upload a JSON, YAML, or ENV file to initialize technical baseline configurations.</p>
            <div style={{ border: "2px dashed var(--border-color)", borderRadius: "0.5rem", padding: "3rem", textAlign: "center", background: "var(--bg-main)" }}>
              <svg style={{ width: "48px", height: "48px", color: "var(--text-muted)", margin: "0 auto 1rem" }} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" /></svg>
              <input type="file" accept=".json,.yaml,.yml,.env" onChange={(e) => setConfigFile(e.target.files?.[0] || null)} ref={configFileRef} required id="config-file-input" style={{ display: "none" }} />
              <label htmlFor="config-file-input" className="btn-primary" style={{ display: "inline-block", cursor: "pointer", marginBottom: "0.75rem" }}>Select File</label>
              <div style={{ fontSize: "0.85rem", color: "var(--text-muted)" }}>
                {configFile ? <span style={{ color: "var(--primary)", fontWeight: 600 }}>{configFile.name}</span> : "No file selected"}
              </div>
            </div>
            <div style={{ display: "flex", justifyContent: "flex-end", marginTop: "1.5rem" }}>
              <button type="submit" className="btn-primary" disabled={loading} style={{ minWidth: "180px" }}>
                {loading ? "Uploading..." : "Upload Configuration"}
              </button>
            </div>
          </div>
        </form>
      )}

      {/* ──────────── UPLOAD SUCCESS ──────────── */}
      {uploadResult && (
        <div className="card" style={{ marginTop: "1.5rem", padding: "1.25rem", background: "rgba(16,185,129,0.05)", border: "1px solid #10B981" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", marginBottom: "0.75rem" }}>
            <svg style={{ width: "22px", height: "22px", color: "#10B981" }} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
            <strong style={{ color: "#065F46", fontSize: "1rem" }}>{uploadResult.message || "Upload Successful"}</strong>
          </div>
          <div style={{ display: "flex", gap: "2rem", flexWrap: "wrap", fontSize: "0.9rem", color: "var(--text-main)" }}>
            <span><strong>File:</strong> {uploadResult.file_name}</span>
            {uploadResult.detected_sheets !== undefined && <span><strong>Sheets:</strong> <span className="badge badge-blue">{uploadResult.detected_sheets}</span></span>}
            {uploadResult.imported_rows !== undefined && <span><strong>Records:</strong> <span className="badge badge-green">{uploadResult.imported_rows}</span></span>}
            {uploadResult.metadata?.framework && <span><strong>Standard:</strong> {uploadResult.metadata.framework}</span>}
            {uploadResult.file_type && <span><strong>Type:</strong> <span className="badge badge-blue">{uploadResult.file_type.toUpperCase()}</span></span>}
          </div>

          {/* Detection Summary */}
          {uploadResult.detection_summary?.length > 0 && (
            <div style={{ marginTop: "0.75rem", paddingTop: "0.75rem", borderTop: "1px dashed #10B981" }}>
              <p style={{ margin: "0 0 0.4rem 0", fontWeight: 600, fontSize: "0.85rem", color: "#065F46" }}>Detected Sheets:</p>
              <div style={{ display: "flex", flexWrap: "wrap", gap: "0.4rem" }}>
                {uploadResult.detection_summary.map((line, i) => (
                  <span key={i} style={{
                    padding: "0.3rem 0.6rem",
                    borderRadius: "6px",
                    fontSize: "0.82rem",
                    fontWeight: 500,
                    background: line.startsWith("✓") ? "rgba(16,185,129,0.1)" : "rgba(245,158,11,0.1)",
                    color: line.startsWith("✓") ? "#065F46" : "#92400E",
                    border: `1px solid ${line.startsWith("✓") ? "rgba(16,185,129,0.2)" : "rgba(245,158,11,0.2)"}`,
                  }}>{line}</span>
                ))}
              </div>
            </div>
          )}

          {/* Warnings */}
          {uploadResult.warnings?.length > 0 && (
            <div style={{ marginTop: "0.75rem", paddingTop: "0.75rem", borderTop: "1px dashed #F59E0B" }}>
              <p style={{ margin: "0 0 0.4rem 0", fontWeight: 600, fontSize: "0.85rem", color: "#92400E" }}>Warnings:</p>
              <ul style={{ margin: 0, paddingLeft: "1.25rem", fontSize: "0.82rem", color: "#92400E" }}>
                {uploadResult.warnings.map((w, i) => <li key={i}>{w}</li>)}
              </ul>
            </div>
          )}

          {/* Legacy errors display */}
          {uploadResult.errors?.length > 0 && (
            <div style={{ marginTop: "0.75rem", paddingTop: "0.75rem", borderTop: "1px dashed #10B981" }}>
              <p style={{ margin: "0 0 0.4rem 0", fontWeight: 600, fontSize: "0.85rem", color: "#92400E" }}>Notes:</p>
              <ul style={{ margin: 0, paddingLeft: "1.25rem", fontSize: "0.82rem", color: "#92400E" }}>
                {uploadResult.errors.map((e, i) => <li key={i}>{e}</li>)}
              </ul>
            </div>
          )}
        </div>
      )}

    </PageContainer>
  );
}
