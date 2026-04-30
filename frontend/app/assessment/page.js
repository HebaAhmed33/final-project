"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import PageContainer from "../components/PageContainer";
import API_BASE_URL from "../lib/api";

export default function AssessmentPage() {
  const router = useRouter();

  // Company info
  const [companyName, setCompanyName] = useState("");
  const [companyType, setCompanyType] = useState("Company");

  // Assessment fields
  const [assessmentFile, setAssessmentFile] = useState(null);
  const [assessmentName, setAssessmentName] = useState("");
  const [framework, setFramework] = useState("");

  // Status
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [uploadResult, setUploadResult] = useState(null);
  const [assessmentResult, setAssessmentResult] = useState(null);

  // Refs
  const assessmentFileRef = useRef(null);

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

    try {
      // 1) Upload
      const uploadRes = await fetch(`http://localhost:8000/upload/assessment`, {
        method: "POST",
        body: formData,
      });
      if (uploadRes.headers.get("content-type")?.includes("text/html")) {
        throw new Error("API returned HTML instead of JSON");
      }
      if (!uploadRes.ok) {
        throw new Error("API request failed");
      }
      const uploadData = await uploadRes.json();
      setUploadResult(uploadData);

      // 2) The upload endpoint now runs the full GRC intelligence inference pipeline
      // and returns the enriched assessment inside framework_assessment
      if (uploadData.framework_assessment && uploadData.framework_assessment.compliance_score !== undefined) {
        setAssessmentResult(uploadData.framework_assessment);
        sessionStorage.setItem("assessment_result", JSON.stringify({ upload: uploadData, framework: uploadData.framework_assessment }));
      } else if (isEnrichedFramework) {
        // Fallback for legacy mode just in case
        const assessRes = await fetch(`http://localhost:8000/assess/${framework}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            assessment_name: assessmentName,
            use_uploaded_evidence: true,
          }),
        });
        if (assessRes.headers.get("content-type")?.includes("text/html")) {
          throw new Error("API returned HTML instead of JSON");
        }
        if (!assessRes.ok) {
          throw new Error("API request failed");
        }
        if (assessRes.ok) {
          const assessData = await assessRes.json();
          setAssessmentResult(assessData);
          sessionStorage.setItem("assessment_result", JSON.stringify({ upload: uploadData, framework: assessData }));
        }
      }

      // Clear form
      setAssessmentFile(null);
      setAssessmentName("");
      setFramework("");
      if (assessmentFileRef.current) assessmentFileRef.current.value = "";
      
      // Redirect to results
      setTimeout(() => {
        router.push("/assessment-results");
      }, 1500);
    } catch (err) {
      if (err instanceof TypeError && err.message === "Failed to fetch") {
        setError(`Cannot connect to backend at ${API_BASE_URL}. Make sure the backend server is running.`);
      } else {
        setError(err.message || "An unexpected error occurred.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <PageContainer>
      {/* Page Header */}
      <div style={{ padding: "0 0 2rem" }}>
        <h1 style={{ fontSize: "2.5rem", fontWeight: 800, letterSpacing: "-0.04em", marginBottom: "0.5rem", color: "var(--text-main)" }}>
          Compliance Assessment
        </h1>
        <p style={{ color: "var(--text-main)", fontSize: "1.1rem", fontWeight: 600, maxWidth: "700px", lineHeight: "1.6", margin: "0 0 0.25rem 0" }}>
          Upload your compliance evidence for intelligent mapping.
        </p>
        <p style={{ color: "var(--text-muted)", fontSize: "0.95rem", maxWidth: "700px", lineHeight: "1.6", margin: 0 }}>
          Evaluates your organization against ISO 27001, HIPAA, and PCI DSS.
        </p>
      </div>

      {/* ──────────── ERROR ──────────── */}
      {error && (
        <div style={{ padding: "1rem", marginBottom: "1.5rem", background: "rgba(239,68,68,0.05)", border: "1px solid #EF4444", color: "#EF4444", borderRadius: "0.5rem", display: "flex", alignItems: "center", gap: "0.75rem" }}>
          <svg style={{ width: "20px", height: "20px", flexShrink: 0 }} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
          <span style={{ fontSize: "0.95rem" }}>{error}</span>
        </div>
      )}

      {/* ──────────── ASSESSMENT FORM ──────────── */}
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
                  <option value="" disabled>Choose standard</option>
                  <option value="iso27001">ISO 27001</option>
                  <option value="hipaa">HIPAA</option>
                  <option value="pci_dss">PCI DSS</option>
                </select>
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

      {/* ──────────── UPLOAD SUCCESS (Just in case rendering is needed before redirect) ──────────── */}
      {uploadResult && (
        <div className="card" style={{ marginTop: "1.5rem", padding: "1.25rem", background: "rgba(16,185,129,0.05)", border: "1px solid #10B981" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", marginBottom: "0.75rem" }}>
            <svg style={{ width: "22px", height: "22px", color: "#10B981" }} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
            <strong style={{ color: "#065F46", fontSize: "1rem" }}>{uploadResult.message || "Upload Successful"}</strong>
          </div>
        </div>
      )}

    </PageContainer>
  );
}
