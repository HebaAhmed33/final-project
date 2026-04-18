"use client";

import { useState, useEffect } from "react";
import PageContainer from "../components/PageContainer";
import API_BASE_URL from "../lib/api";

export default function ReportsPage() {
  const [reports, setReports] = useState([]);
  const [totalReports, setTotalReports] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [exporting, setExporting] = useState(false);
  const [exportMsg, setExportMsg] = useState(null);

  const loggedInUser = typeof window !== "undefined"
    ? JSON.parse(localStorage.getItem("smartisms_user") || "null")
    : null;
  const companyId = loggedInUser?.company_id || "C001";

  useEffect(() => {
    fetchReports();
  }, []);

  async function fetchReports() {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE_URL}/reports/${companyId}`);
      if (!res.ok) throw new Error(`Server responded with HTTP ${res.status}`);
      const data = await res.json();
      setReports(data.reports || []);
      setTotalReports(data.total_reports || 0);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleExport() {
    setExporting(true);
    setExportMsg(null);
    try {
      const res = await fetch(`${API_BASE_URL}/export-latest-report`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ company_id: companyId }),
      });
      if (!res.ok) throw new Error(`Server responded with HTTP ${res.status}`);
      const data = await res.json();
      if (data.status === "success") {
        setExportMsg(`Success! Report saved to: ${data.output_path.split(/[/\\]/).pop()}`);
      } else {
        setExportMsg(data.message || "Export failed. Please check backend logs.");
      }
    } catch (err) {
      setExportMsg(`Export Error: ${err.message}`);
    } finally {
      setExporting(false);
    }
  }

  const getComplianceClass = (percentage) => {
    if (percentage >= 80) return "badge badge-green";
    if (percentage >= 50) return "badge badge-yellow";
    return "badge badge-red";
  };

  // Derived metrics for summary strip
  const latestReport = reports.length > 0 ? reports[0] : null;
  const latestCompliance = latestReport?.assessment_output?.assessment_summary?.compliance_percentage;
  const latestStandard = latestReport?.standard_file?.split(/[/\\]/)?.pop()?.replace(".json", "")?.toUpperCase() || "—";
  
  return (
    <PageContainer>
      <div style={{ padding: "0 0 2.5rem" }}>
        <h1
          style={{
            fontSize: "2.5rem",
            fontWeight: 800,
            letterSpacing: "-0.04em",
            marginBottom: "0.5rem",
            color: "var(--text-main)",
            lineHeight: "1.2"
          }}
        >
          Executive Report Center
        </h1>
        <p
          style={{
            color: "var(--text-muted)",
            fontSize: "1.05rem",
            maxWidth: "700px",
            lineHeight: "1.6",
            margin: 0
          }}
        >
          Access chronological audit trails, risk registers, and generate polished C-level PDF specifications. Manage the complete artifact history for tracking ID: <strong style={{color: "var(--text-main)"}}>{companyId}</strong>.
        </p>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: "2.5rem" }}>
        
        {/* Dynamic Executive Metrics Strip */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "1.25rem", marginBottom: "1rem" }}>
          
          <div className="card" style={{ padding: "1.5rem", display: "flex", flexDirection: "column", borderLeft: "4px solid var(--primary)" }}>
            <span style={{ fontSize: "0.85rem", color: "var(--text-muted)", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: "0.5rem" }}>
               Total Assessments
            </span>
            <span style={{ fontSize: "2rem", fontWeight: 800, color: "var(--text-main)", lineHeight: "1" }}>
              {loading ? "..." : totalReports}
            </span>
          </div>

          <div className="card" style={{ padding: "1.5rem", display: "flex", flexDirection: "column", borderLeft: "4px solid #8B5CF6" }}>
            <span style={{ fontSize: "0.85rem", color: "var(--text-muted)", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: "0.5rem" }}>
               Latest Baseline
            </span>
            <span style={{ fontSize: "2rem", fontWeight: 800, color: "var(--text-main)", lineHeight: "1" }}>
              {loading ? "..." : latestStandard}
            </span>
          </div>

          <div className="card" style={{ padding: "1.5rem", display: "flex", flexDirection: "column", borderLeft: `4px solid ${latestCompliance >= 80 ? "#10B981" : latestCompliance >= 50 ? "#F59E0B" : "#EF4444"}` }}>
            <span style={{ fontSize: "0.85rem", color: "var(--text-muted)", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: "0.5rem" }}>
               Recent Coverage
            </span>
            <span style={{ fontSize: "2rem", fontWeight: 800, color: latestCompliance >= 80 ? "#10B981" : latestCompliance >= 50 ? "#F59E0B" : "#EF4444", lineHeight: "1" }}>
              {loading ? "..." : latestCompliance != null ? `${latestCompliance}%` : "—"}
            </span>
          </div>

          <div className="card" style={{ padding: "1.5rem", display: "flex", flexDirection: "column", borderLeft: "4px solid var(--text-muted)" }}>
            <span style={{ fontSize: "0.85rem", color: "var(--text-muted)", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: "0.5rem" }}>
               Export Engine
            </span>
            <span style={{ fontSize: "1.2rem", fontWeight: 700, color: reports.length > 0 ? "#10B981" : "var(--text-muted)", marginTop: "auto", paddingBottom: "0.25rem" }}>
              {loading ? "..." : reports.length > 0 ? "Ready for Download" : "No Data Available"}
            </span>
          </div>
          
        </div>

        {/* Assessment History Data Block */}
        <div className="card">
          <div style={{ marginBottom: "1.5rem" }}>
            <h2 style={{ fontSize: "1.25rem", fontWeight: 700, color: "var(--text-main)", marginBottom: "0.25rem", letterSpacing: "-0.01em" }}>
              Assessment History Ledger
            </h2>
            <p style={{ color: "var(--text-muted)", fontSize: "0.9rem", margin: 0 }}>
              Complete chronological audit trail for the active organization constraints.
            </p>
          </div>

          {/* Loading State Workspace */}
          {loading && (
            <div style={{ padding: "4rem 2rem", textAlign: "center", border: "1px dashed var(--border-color)", borderRadius: "8px" }}>
              <div style={{ display: "inline-block", width: "32px", height: "32px", border: "3px solid var(--border-color)", borderTopColor: "var(--primary)", borderRadius: "50%", animation: "spin 1s infinite linear", marginBottom: "1rem" }} />
              <p style={{ color: "var(--text-muted)", fontSize: "0.95rem", fontWeight: 500, margin: 0 }}>Fetching history...</p>
              <style>{`@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }`}</style>
            </div>
          )}

          {/* Error Workspace */}
          {error && (
            <div style={{ padding: "1.5rem", background: "rgba(239, 68, 68, 0.05)", border: "1px solid #EF4444", borderRadius: "8px", color: "#EF4444", display: "flex", alignItems: "center", gap: "1rem" }}>
              <svg style={{ width: "24px", height: "24px", flexShrink: 0 }} fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <strong style={{ display: "block", fontWeight: 600, fontSize: "0.95rem", marginBottom: "0.2rem" }}>Failed to Fetch History</strong>
                <span style={{ fontSize: "0.85rem" }}>{error}. Ensure the secure backend service is reachable.</span>
              </div>
            </div>
          )}

          {/* Empty Records Workspace */}
          {!loading && !error && reports.length === 0 && (
            <div style={{ padding: "4rem 2rem", background: "var(--bg-main)", border: "1px dashed var(--border-color)", borderRadius: "8px", textAlign: "center", display: "flex", flexDirection: "column", alignItems: "center" }}>
              <svg style={{ width: "48px", height: "48px", color: "var(--text-muted)", marginBottom: "1rem", opacity: 0.5 }} fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <h3 style={{ fontSize: "1.1rem", fontWeight: 600, color: "var(--text-main)", marginBottom: "0.25rem" }}>No Historical Records</h3>
              <p style={{ color: "var(--text-muted)", fontSize: "0.9rem", margin: 0, maxWidth: "340px" }}>
                No reports have been generated for your organization yet. Head over to the Assessment Workspace to run your first evaluation.
              </p>
            </div>
          )}

          {/* Successful Payload Workspace */}
          {!loading && !error && reports.length > 0 && (
            <div className="table-container" style={{ border: "1px solid var(--border-color)", borderRadius: "8px", overflow: "hidden" }}>
              <table className="modern-table" style={{ margin: 0 }}>
                <thead style={{ background: "var(--bg-main)" }}>
                  <tr>
                    <th style={{ width: "60px", textAlign: "center" }}>#</th>
                    <th>Target Entity</th>
                    <th>Core Framework</th>
                    <th>Compliance Vector</th>
                    <th>Processed Timestamp</th>
                  </tr>
                </thead>
                <tbody>
                  {reports.map((report, index) => {
                    const summary = report.assessment_output?.assessment_summary || {};
                    const standardFile = report.standard_file || "—";
                    const standardName = standardFile.split(/[/\\]/).pop()?.replace(".json", "").toUpperCase() || "—";
                    
                    return (
                      <tr key={index}>
                        <td style={{ color: "var(--text-muted)", textAlign: "center", fontWeight: 600 }}>{index + 1}</td>
                        <td style={{ fontWeight: 600, color: "var(--text-main)" }}>{report.company_name || report.company_id}</td>
                        <td style={{ color: "var(--text-muted)", fontWeight: 500 }}>{standardName}</td>
                        <td>
                          {summary.compliance_percentage != null ? (
                            <span className={getComplianceClass(summary.compliance_percentage)} style={{ fontSize: "0.80rem", padding: "0.25rem 0.75rem", fontWeight: 700 }}>
                              {summary.compliance_percentage}% COVERAGE
                            </span>
                          ) : <span style={{ color: "var(--text-muted)" }}>—</span>}
                        </td>
                        <td style={{ color: "var(--text-muted)", fontSize: "0.85rem", letterSpacing: "0.02em", whiteSpace: "nowrap" }}>
                          {report.created_at ? new Date(report.created_at).toLocaleString() : "—"}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Global Export Engine Block */}
        <div className="card" style={{ background: "var(--bg-card)", border: "2px solid var(--border-color)", position: "relative", overflow: "hidden" }}>
          
          {/* Decorative background circle */}
          <div style={{ position: "absolute", top: "-50%", right: "-10%", width: "300px", height: "300px", background: "var(--primary)", opacity: 0.05, borderRadius: "50%", pointerEvents: "none" }} />
          
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "1.5rem", position: "relative", zIndex: 1 }}>
            <div style={{ display: "flex", gap: "1.25rem", alignItems: "flex-start" }}>
              <div style={{ width: "48px", height: "48px", background: "rgba(37, 99, 235, 0.08)", borderRadius: "10px", display: "flex", alignItems: "center", justifyContent: "center", color: "var(--primary)", flexShrink: 0 }}>
                <svg style={{ width: "24px", height: "24px" }} fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 10v6m0 0l-3-3m3 3l3-3M3 17V7a2 2 0 012-2h6l2 2h6a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2z" />
                </svg>
              </div>
              <div>
                <h2 style={{ fontSize: "1.2rem", fontWeight: 800, color: "var(--text-main)", marginBottom: "0.25rem" }}>
                  Download Executive Report
                </h2>
                <p style={{ color: "var(--text-muted)", fontSize: "0.95rem", margin: 0, maxWidth: "450px", lineHeight: 1.5 }}>
                  Generate a polished, shareable PDF specification report detailing your latest audit findings.
                </p>
              </div>
            </div>
            
            <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end" }}>
              <button 
                className="btn-primary" 
                onClick={handleExport} 
                disabled={exporting || reports.length === 0}
                style={{ padding: "0.85rem 1.5rem", fontSize: "1rem", display: "flex", alignItems: "center", gap: "0.5rem" }}
              >
                {exporting ? (
                  <>
                    <svg style={{ width: "18px", height: "18px", animation: "spin 1s infinite linear" }} fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                    Generating PDF...
                  </>
                ) : (
                  <>
                    Download Report (PDF)
                    <svg style={{ width: "18px", height: "18px" }} fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                    </svg>
                  </>
                )}
              </button>
              
              {exportMsg && (
                <span style={{ 
                  display: "block", 
                  marginTop: "0.75rem", 
                  fontSize: "0.85rem", 
                  color: exportMsg.includes("Error") || exportMsg.includes("failed") ? "#EF4444" : "#10B981", 
                  fontWeight: 600 
                }}>
                  {exportMsg}
                </span>
              )}
            </div>
          </div>
        </div>
        
      </div>
    </PageContainer>
  );
}
