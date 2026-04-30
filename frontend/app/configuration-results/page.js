"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import PageContainer from "../components/PageContainer";

export default function ConfigurationResultsPage() {
  const router = useRouter();
  const [uploadResult, setUploadResult] = useState(null);

  useEffect(() => {
    if (typeof window !== "undefined") {
      const stored = sessionStorage.getItem("config_result");
      if (stored) {
        try {
          setUploadResult(JSON.parse(stored));
        } catch (e) {
          console.error("Failed to parse stored config data");
        }
      }
    }
  }, []);

  const getBadgeClass = (s) => {
    if (!s) return "badge badge-blue";
    const v = s.toLowerCase();
    if (["compliant", "pass", "low", "true"].includes(v)) return "badge badge-green";
    if (["missing", "fail", "high", "false"].includes(v)) return "badge badge-red";
    if (["partial", "medium"].includes(v)) return "badge badge-yellow";
    return "badge badge-blue";
  };

  if (!uploadResult) {
    return (
      <PageContainer>
        <div style={{ textAlign: "center", padding: "4rem" }}>
          <h2>No Configuration Data Found</h2>
          <button onClick={() => router.push('/configuration')} className="btn-primary" style={{ marginTop: "1rem" }}>
            Start New Configuration Analysis
          </button>
        </div>
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      <div style={{ padding: "0 0 2rem", display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "1rem" }}>
        <div>
          <button onClick={() => { sessionStorage.removeItem('config_result'); router.push('/configuration'); }} style={{ background: "none", border: "none", color: "var(--primary)", cursor: "pointer", display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "1rem", padding: 0 }}>
            <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7"/></svg>
            Start New Configuration Analysis
          </button>
          <h1 style={{ fontSize: "2.25rem", fontWeight: 800, letterSpacing: "-0.04em", marginBottom: "0.75rem", color: "var(--text-main)" }}>
            Configuration Analysis Results
          </h1>
          <p style={{ color: "var(--text-secondary)", fontSize: "1rem", maxWidth: "800px", margin: 0 }}>
            Review the findings and compliance score for your uploaded configuration.
          </p>
        </div>
        <button onClick={() => router.push('/exports')} className="btn-primary" style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <svg width="18" height="18" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
          Download Configuration Report
        </button>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
        {/* Compliance Score Card */}
        {uploadResult.config_compliance && !uploadResult.config_compliance.error && (() => {
          const score = uploadResult.config_compliance.compliance?.compliance_score ?? 0;
          const frameworkName = uploadResult.config_compliance.framework_label || "Framework";
          let riskLevel = "High Risk";
          let color = "#EF4444";
          if (score >= 80) {
            riskLevel = "Low Risk";
            color = "#10B981";
          } else if (score >= 60) {
            riskLevel = "Medium Risk";
            color = "#F59E0B";
          }
          
          const radius = 50;
          const circumference = 2 * Math.PI * radius;
          const offset = circumference - (score / 100) * circumference;

          return (
            <div className="card" style={{ padding: "2rem", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
              <div style={{ position: "relative", width: "120px", height: "120px", marginBottom: "1rem" }}>
                <svg width="120" height="120" viewBox="0 0 120 120">
                  <circle
                    cx="60" cy="60" r={radius}
                    fill="none" stroke="var(--border-color)" strokeWidth="10"
                  />
                  <circle
                    cx="60" cy="60" r={radius}
                    fill="none" stroke={color} strokeWidth="10"
                    strokeLinecap="round"
                    strokeDasharray={circumference}
                    strokeDashoffset={offset}
                    style={{ transition: "stroke-dashoffset 1s ease-in-out" }}
                    transform="rotate(-90 60 60)"
                  />
                </svg>
                <div style={{ position: "absolute", top: 0, left: 0, width: "100%", height: "100%", display: "flex", alignItems: "center", justifyContent: "center", flexDirection: "column" }}>
                  <span style={{ fontSize: "1.75rem", fontWeight: 800, color: "var(--text-main)", lineHeight: 1 }}>{score}%</span>
                </div>
              </div>
              <h3 style={{ fontSize: "1.25rem", fontWeight: 700, margin: "0 0 0.5rem 0", color: "var(--text-main)", textAlign: "center" }}>
                {frameworkName} Compliance
              </h3>
              <span style={{ 
                backgroundColor: `${color}15`, 
                color: color, 
                fontSize: "0.95rem", 
                padding: "0.4rem 1rem", 
                borderRadius: "20px",
                fontWeight: 600 
              }}>
                {riskLevel}
              </span>
            </div>
          );
        })()}

        {/* Analysis Details */}
        <div className="card" style={{ padding: "1.5rem" }}>
          <h2 style={{ fontSize: "1.25rem", fontWeight: 700, margin: "0 0 1rem 0", color: "var(--text-main)" }}>Configuration Review</h2>
          {uploadResult.config_analysis ? (
            <>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "1rem", marginBottom: "1.5rem" }}>
                <div style={{ padding: "1rem", background: "var(--bg-main)", borderRadius: "0.5rem", border: "1px solid var(--border-color)" }}>
                  <div style={{ fontSize: "0.8rem", color: "var(--text-muted)", marginBottom: "0.25rem" }}>Config Type</div>
                  <div style={{ fontSize: "1.1rem", fontWeight: 600, color: "var(--text-main)" }}>{uploadResult.config_analysis.summary?.config_type?.replace(/_/g, ' ').toUpperCase() || "N/A"}</div>
                </div>
                <div style={{ padding: "1rem", background: "var(--bg-main)", borderRadius: "0.5rem", border: "1px solid var(--border-color)" }}>
                  <div style={{ fontSize: "0.8rem", color: "var(--text-muted)", marginBottom: "0.25rem" }}>Overall Risk</div>
                  <div style={{ fontSize: "1.1rem", fontWeight: 600, color: uploadResult.config_analysis.summary?.overall_risk === "High" ? "#EF4444" : uploadResult.config_analysis.summary?.overall_risk === "Medium" ? "#F59E0B" : "#10B981" }}>{uploadResult.config_analysis.summary?.overall_risk || "Low"}</div>
                </div>
                <div style={{ padding: "1rem", background: "var(--bg-main)", borderRadius: "0.5rem", border: "1px solid var(--border-color)" }}>
                  <div style={{ fontSize: "0.8rem", color: "var(--text-muted)", marginBottom: "0.25rem" }}>Findings Summary</div>
                  <div style={{ display: "flex", gap: "0.75rem", fontSize: "0.9rem", fontWeight: 600 }}>
                    <span style={{ color: "#EF4444" }}>High: {uploadResult.config_analysis.summary?.high || 0}</span>
                    <span style={{ color: "#F59E0B" }}>Med: {uploadResult.config_analysis.summary?.medium || 0}</span>
                    <span style={{ color: "#10B981" }}>Low: {uploadResult.config_analysis.summary?.low || 0}</span>
                  </div>
                </div>
              </div>
              {uploadResult.config_analysis.components && uploadResult.config_analysis.components.length > 0 && (
                <div style={{ marginBottom: "1.5rem" }}>
                  <h3 style={{ fontSize: "1rem", fontWeight: 600, color: "var(--text-main)", marginBottom: "0.5rem" }}>Detected Components</h3>
                  <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
                    {uploadResult.config_analysis.components.map((comp, i) => (
                      <span key={i} className="badge badge-blue" style={{ fontSize: "0.8rem" }}>
                        <strong>{comp.type}:</strong> {comp.value}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              {uploadResult.config_compliance?.findings && uploadResult.config_compliance.findings.length > 0 && (
                <div>
                  <h3 style={{ fontSize: "1rem", fontWeight: 600, color: "var(--text-main)", marginBottom: "0.5rem" }}>Detailed Findings</h3>
                  <div style={{ overflowX: "auto" }}>
                    <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.9rem" }}>
                      <thead>
                        <tr style={{ background: "rgba(0,0,0,0.02)", borderBottom: "2px solid var(--border-color)", textAlign: "left" }}>
                          <th style={{ padding: "0.75rem 1rem", color: "var(--text-muted)", fontWeight: 600 }}>ID</th>
                          <th style={{ padding: "0.75rem 1rem", color: "var(--text-muted)", fontWeight: 600 }}>Title</th>
                          <th style={{ padding: "0.75rem 1rem", color: "var(--text-muted)", fontWeight: 600 }}>Severity</th>
                          <th style={{ padding: "0.75rem 1rem", color: "var(--text-muted)", fontWeight: 600 }}>Description</th>
                          <th style={{ padding: "0.75rem 1rem", color: "var(--text-muted)", fontWeight: 600 }}>Framework Control</th>
                          <th style={{ padding: "0.75rem 1rem", color: "var(--text-muted)", fontWeight: 600 }}>Recommendation</th>
                        </tr>
                      </thead>
                      <tbody>
                        {uploadResult.config_compliance.findings.map((f, i) => (
                          <tr key={i} style={{ borderBottom: "1px solid var(--border-color)" }}>
                            <td style={{ padding: "0.75rem 1rem", color: "var(--text-main)", fontWeight: 500, whiteSpace: "nowrap" }}>{f.id}</td>
                            <td style={{ padding: "0.75rem 1rem", color: "var(--text-main)", fontWeight: 500 }}>{f.title}</td>
                            <td style={{ padding: "0.75rem 1rem" }}><span className={getBadgeClass(f.severity)}>{f.severity}</span></td>
                            <td style={{ padding: "0.75rem 1rem", color: "var(--text-muted)" }}>{f.description}</td>
                            <td style={{ padding: "0.75rem 1rem", color: "var(--text-main)", fontSize: "0.85rem" }}>{f.framework_control}</td>
                            <td style={{ padding: "0.75rem 1rem", color: "var(--text-main)" }}>{f.recommendation}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Risk Register */}
              {uploadResult.config_compliance?.risk_register && uploadResult.config_compliance.risk_register.length > 0 && (
                <div style={{ marginTop: "2rem" }}>
                  <h3 style={{ fontSize: "1rem", fontWeight: 600, color: "var(--text-main)", marginBottom: "0.5rem" }}>Risk Register</h3>
                  <div style={{ overflowX: "auto" }}>
                    <table style={{ width: "100%", tableLayout: "auto", borderCollapse: "collapse", fontSize: "0.9rem" }}>
                      <thead>
                        <tr style={{ background: "rgba(0,0,0,0.02)", borderBottom: "2px solid var(--border-color)", textAlign: "left" }}>
                          <th style={{ padding: "16px", verticalAlign: "top", lineHeight: 1.625, whiteSpace: "normal", wordBreak: "break-word", color: "var(--text-muted)", fontWeight: 600, width: "90px", borderRight: "1px solid var(--border-color)" }}>Risk ID</th>
                          <th style={{ padding: "16px", verticalAlign: "top", lineHeight: 1.625, whiteSpace: "normal", wordBreak: "break-word", color: "var(--text-muted)", fontWeight: 600, width: "28%", borderRight: "1px solid var(--border-color)" }}>Risk Statement</th>
                          <th style={{ padding: "16px", verticalAlign: "top", lineHeight: 1.625, whiteSpace: "normal", wordBreak: "break-word", color: "var(--text-muted)", fontWeight: 600, textAlign: "center", width: "80px", borderRight: "1px solid var(--border-color)" }}>Impact</th>
                          <th style={{ padding: "16px", verticalAlign: "top", lineHeight: 1.625, whiteSpace: "normal", wordBreak: "break-word", color: "var(--text-muted)", fontWeight: 600, textAlign: "center", width: "80px", borderRight: "1px solid var(--border-color)" }}>Likelihood</th>
                          <th style={{ padding: "16px", verticalAlign: "top", lineHeight: 1.625, whiteSpace: "normal", wordBreak: "break-word", color: "var(--text-muted)", fontWeight: 600, textAlign: "center", width: "120px", borderRight: "1px solid var(--border-color)" }}>Risk Level</th>
                          <th style={{ padding: "16px", verticalAlign: "top", lineHeight: 1.625, whiteSpace: "normal", wordBreak: "break-word", color: "var(--text-muted)", fontWeight: 600, width: "20%", borderRight: "1px solid var(--border-color)" }}>Treatment</th>
                          <th style={{ padding: "16px", verticalAlign: "top", lineHeight: 1.625, whiteSpace: "normal", wordBreak: "break-word", color: "var(--text-muted)", fontWeight: 600 }}>Recommendation</th>
                        </tr>
                      </thead>
                      <tbody>
                        {uploadResult.config_compliance.risk_register.map((r, i) => {
                          let rTitle = r.risk_statement || "—";
                          let rDesc = "";
                          const splitIdx = rTitle.indexOf(":") !== -1 ? rTitle.indexOf(":") : rTitle.indexOf(".");
                          if (splitIdx !== -1 && splitIdx < 100) {
                            rTitle = rTitle.substring(0, splitIdx + (rTitle[splitIdx] === '.' ? 1 : 0)).trim();
                            rDesc = (r.risk_statement || "").substring(splitIdx + 1).trim();
                          }
                          
                          const riskScoreNum = parseInt(r.risk_score) || 0;
                          let rlBg = "#166534";
                          let rlText = "#ffffff";
                          let rlLabel = "Low";
                          if (riskScoreNum >= 15) { rlBg = "#7f1d1d"; rlLabel = "Extreme"; }
                          else if (riskScoreNum >= 10) { rlBg = "#9a3412"; rlLabel = "High"; }
                          else if (riskScoreNum >= 5) { rlBg = "#854d0e"; rlLabel = "Medium"; }

                          return (
                          <tr key={i} style={{ borderBottom: "1px solid var(--border-color)" }}>
                            <td style={{ padding: "16px", verticalAlign: "top", lineHeight: 1.625, whiteSpace: "normal", wordBreak: "break-word", color: "var(--text-main)", fontWeight: 600, borderRight: "1px solid var(--border-color)" }}>{r.risk_id}</td>
                            <td style={{ padding: "16px", verticalAlign: "top", lineHeight: 1.625, whiteSpace: "normal", wordBreak: "break-word", borderRight: "1px solid var(--border-color)" }}>
                              <div style={{ fontWeight: 600, color: "var(--text-main)", marginBottom: rDesc ? "0.4rem" : "0" }}>{rTitle}</div>
                              {rDesc && <div style={{ fontSize: "0.85rem", color: "var(--text-muted)" }}>{rDesc}</div>}
                            </td>
                            <td style={{ padding: "16px", verticalAlign: "top", lineHeight: 1.625, whiteSpace: "normal", wordBreak: "break-word", textAlign: "center", borderRight: "1px solid var(--border-color)" }}>
                              <span className={getBadgeClass(r.impact)} style={{ display: "inline-block", padding: "4px 10px", borderRadius: "4px", fontSize: "0.85rem", fontWeight: 700 }}>{r.impact}</span>
                            </td>
                            <td style={{ padding: "16px", verticalAlign: "top", lineHeight: 1.625, whiteSpace: "normal", wordBreak: "break-word", textAlign: "center", borderRight: "1px solid var(--border-color)" }}>
                              <span className={getBadgeClass(r.likelihood)} style={{ display: "inline-block", padding: "4px 10px", borderRadius: "4px", fontSize: "0.85rem", fontWeight: 700 }}>{r.likelihood}</span>
                            </td>
                            <td style={{ padding: "16px", verticalAlign: "top", lineHeight: 1.625, whiteSpace: "normal", wordBreak: "break-word", textAlign: "center", borderRight: "1px solid var(--border-color)" }}>
                              <span style={{ display: "inline-flex", alignItems: "center", justifyContent: "center", width: "100%", padding: "6px 12px", borderRadius: "6px", fontSize: "0.85rem", fontWeight: 700, background: rlBg, color: rlText, border: `1px solid ${rlBg}` }}>
                                {r.risk_score} {rlLabel}
                              </span>
                            </td>
                            <td style={{ padding: "16px", verticalAlign: "top", lineHeight: 1.625, whiteSpace: "normal", wordBreak: "break-word", color: "var(--text-main)", fontWeight: 500, borderRight: "1px solid var(--border-color)" }}>{r.treatment}</td>
                            <td style={{ padding: "16px", verticalAlign: "top", lineHeight: 1.625, whiteSpace: "normal", wordBreak: "break-word", color: "var(--text-muted)", fontSize: "0.85rem" }}>{r.recommendation}</td>
                          </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Best Practices */}
              {uploadResult.config_compliance?.best_practices && uploadResult.config_compliance.best_practices.length > 0 && (
                <div style={{ marginTop: "2rem" }}>
                  <h3 style={{ fontSize: "1rem", fontWeight: 600, color: "var(--text-main)", marginBottom: "0.75rem" }}>Recommended Best Practices</h3>
                  <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: "1rem" }}>
                    {uploadResult.config_compliance.best_practices.map((bp, i) => (
                      <div key={i} style={{ padding: "1rem", background: "var(--bg-main)", borderRadius: "0.5rem", border: "1px solid var(--border-color)" }}>
                        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "0.5rem" }}>
                          <div style={{ fontWeight: 600, color: "var(--text-main)" }}>{bp.title}</div>
                          <span className="badge badge-blue" style={{ fontSize: "0.75rem" }}>{bp.category}</span>
                        </div>
                        <p style={{ margin: 0, fontSize: "0.85rem", color: "var(--text-muted)", lineHeight: "1.5" }}>{bp.description}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          ) : (
            <div style={{ padding: "1rem", background: "rgba(0,0,0,0.02)", borderRadius: "0.5rem", border: "1px solid var(--border-color)" }}>
              <p style={{ color: "var(--text-muted)", fontSize: "0.95rem", margin: 0, display: "flex", alignItems: "center", gap: "0.5rem" }}>
                <svg style={{ width: "20px", height: "20px" }} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                No configuration review findings were generated for this file.
              </p>
            </div>
          )}
        </div>
      </div>
    </PageContainer>
  );
}
