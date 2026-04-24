"use client";

import { useState, useEffect } from "react";
import PageContainer from "../components/PageContainer";
import ComplianceScoreGauge from "../components/ComplianceScoreGauge";
import { useRouter } from "next/navigation";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip as RechartsTooltip, ResponsiveContainer
} from "recharts";

export default function AssessmentResultsPage() {
  const router = useRouter();
  const [uploadData, setUploadData] = useState(null);
  const [ad, setAd] = useState(null);
  const [activeTab, setActiveTab] = useState("overview");

  useEffect(() => {
    if (typeof window !== "undefined") {
      const storedUpload = sessionStorage.getItem("latest_assessment_results");
      const storedAd = sessionStorage.getItem("assessment_framework_output");
      if (storedUpload) setUploadData(JSON.parse(storedUpload));
      if (storedAd) setAd(JSON.parse(storedAd));
    }
  }, []);

  if (!uploadData || !ad) {
    return (
      <PageContainer>
        <div style={{ textAlign: "center", padding: "4rem" }}>
          <h2>No Assessment Data Found</h2>
          <button onClick={() => router.push('/upload')} className="btn-primary" style={{ marginTop: "1rem" }}>
            Go to Upload
          </button>
        </div>
      </PageContainer>
    );
  }

  const sev = ad?.severity_summary || {};
  const severityChartData = [
    { name: "High", Compliant: sev.high?.compliant || 0, Missing: sev.high?.missing || 0, Partial: sev.high?.partial || 0 },
    { name: "Medium", Compliant: sev.medium?.compliant || 0, Missing: sev.medium?.missing || 0, Partial: sev.medium?.partial || 0 },
    { name: "Low", Compliant: sev.low?.compliant || 0, Missing: sev.low?.missing || 0, Partial: sev.low?.partial || 0 },
  ];

  const getBadgeClass = (s) => {
    if (!s) return "badge badge-blue";
    const v = s.toLowerCase();
    if (["compliant", "pass", "low", "true", "fully implemented"].includes(v)) return "badge badge-green";
    if (["missing", "fail", "high", "false", "not implemented"].includes(v)) return "badge badge-red";
    if (["partial", "medium", "partially implemented"].includes(v)) return "badge badge-yellow";
    return "badge badge-blue";
  };

  const tabs = [
    { id: "overview", label: "Overview" },
    { id: "high_risk", label: "High Risk" },
    { id: "risk_register", label: "Risk Register" },
    { id: "treatment_plan", label: "Treatment Plan" },
    { id: "soa", label: "SOA" },
    { id: "compliance_matrix", label: "Compliance Matrix" },
    { id: "vendor", label: "Vendor Checklist" },
    { id: "training", label: "Training Matrix" },
    { id: "governance", label: "Governance Calendar" }
  ];

  // High Risk Logic
  const highRiskRows = [];
  const seenIds = new Set();
  if (ad.cross_framework_mapping && ad.cross_framework_mapping.length > 0) {
    ad.cross_framework_mapping.forEach((r) => {
      const id = r.risk_id || `HR-${highRiskRows.length + 1}`;
      if (!seenIds.has(id)) {
        seenIds.add(id);
        highRiskRows.push({
          risk_id: id,
          risk_statement: r.risk_statement || "—",
          controls: (r.iso_controls || []).join(", ") || "—",
          rationale: r.rationale || "Mapped from uploaded High-Risk sheet.",
        });
      }
    });
  }
  if (ad.top_missing_high_risk && ad.top_missing_high_risk.length > 0) {
    ad.top_missing_high_risk.forEach((r) => {
      const id = r.rule_id || `GAP-${highRiskRows.length + 1}`;
      if (!seenIds.has(id)) {
        seenIds.add(id);
        highRiskRows.push({
          risk_id: id,
          risk_statement: r.name || "—",
          controls: r.rule_id || "—",
          rationale: r.reason || `High-severity ${r.status || "missing"} control in ${r.domain || r.section_key || "framework"}.`,
        });
      }
    });
  }
  if (ad.risk_register) {
    const entries = [
      ...(ad.risk_register.findings || []),
      ...(ad.risk_register.generated_risk_entries || []),
    ];
    entries.forEach((r) => {
      const level = (r.risk_level || r.level || "").toLowerCase();
      if (level === "high" || level === "critical") {
        const id = r.risk_id || r.rule_id || `RR-${highRiskRows.length + 1}`;
        if (!seenIds.has(id)) {
          seenIds.add(id);
          highRiskRows.push({
            risk_id: id,
            risk_statement: r.risk_name || r.risk_statement || r.name || "—",
            controls: (r.iso_controls || []).join(", ") || r.rule_id || "—",
            rationale: r.rationale || r.reason || `${level.charAt(0).toUpperCase() + level.slice(1)}-level risk from risk register.`,
          });
        }
      }
    });
  }

  return (
    <PageContainer>
      <div style={{ padding: "0 0 2rem" }}>
        <button onClick={() => router.push('/upload')} style={{ background: "none", border: "none", color: "var(--primary)", cursor: "pointer", display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "1rem" }}>
          <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7"/></svg>
          Back to Upload
        </button>
        <h1 style={{ fontSize: "2.25rem", fontWeight: 800, letterSpacing: "-0.04em", marginBottom: "0.75rem", color: "var(--text-main)" }}>
          Assessment Results Dashboard
        </h1>
        <p style={{ color: "var(--text-secondary)", fontSize: "1rem", maxWidth: "800px" }}>
          Comprehensive view of your parsed and analyzed compliance posture, derived directly from your uploaded {uploadData?.detected_sheets || 0} sheets.
        </p>
      </div>

      <div style={{
        padding: "1.25rem 1.5rem", borderRadius: "8px", marginBottom: "1.5rem",
        background: "linear-gradient(135deg, rgba(16,185,129,0.08), rgba(37,99,235,0.05))",
        border: "1px solid #10B981", display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "0.5rem"
      }}>
        <div>
          <h2 style={{ fontSize: "1.5rem", fontWeight: 800, margin: "0 0 0.25rem 0", color: "var(--text-main)" }}>{ad.framework} Output</h2>
        </div>
      </div>

      {/* Tabs */}
      <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem", marginBottom: "2rem", borderBottom: "2px solid var(--border-color)", paddingBottom: "1rem" }}>
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            style={{
              padding: "0.5rem 1rem",
              background: activeTab === tab.id ? "var(--primary)" : "var(--bg-main)",
              color: activeTab === tab.id ? "#fff" : "var(--text-main)",
              border: `1px solid ${activeTab === tab.id ? "var(--primary)" : "var(--border-color)"}`,
              borderRadius: "6px",
              cursor: "pointer",
              fontWeight: activeTab === tab.id ? 600 : 500,
              transition: "all 0.2s"
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* TAB CONTENT */}
      <div>
        
        {/* OVERVIEW TAB */}
        {activeTab === "overview" && (
          <div style={{ animation: "fadeIn 0.3s ease" }}>
            <h3 style={{ fontSize: "1.5rem", fontWeight: 800, color: "var(--text-main)", marginBottom: "1rem" }}>Compliance Score</h3>
            <div style={{ marginBottom: "2rem" }}>
              <ComplianceScoreGauge 
                score={uploadData.compliance_score || Math.round(ad.compliance_score || 0)}
                totalControls={ad.total_controls || 0}
                compliantControls={ad.compliant_controls || 0}
                partialControls={ad.partial_controls || 0}
                missingControls={ad.missing_controls || 0}
                frameworkName={ad.framework || ""}
              />
            </div>

            <h3 style={{ fontSize: "1.5rem", fontWeight: 800, color: "var(--text-main)" }}>Risk Assessment Summary</h3>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(380px, 1fr))", gap: "1.5rem", marginBottom: "2.5rem", marginTop: "1rem" }}>
              <div className="card" style={{ padding: "1.5rem" }}>
                <h3 style={{ fontSize: "1.1rem", fontWeight: 700, marginBottom: "0.75rem", color: "var(--text-main)" }}>Severity Distribution</h3>
                <div style={{ height: "200px" }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={severityChartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border-color)" />
                      <XAxis dataKey="name" tick={{ fill: "var(--text-muted)", fontSize: 12 }} axisLine={false} tickLine={false} />
                      <YAxis tick={{ fill: "var(--text-muted)", fontSize: 12 }} axisLine={false} tickLine={false} />
                      <RechartsTooltip cursor={{ fill: "var(--bg-main)" }} contentStyle={{ borderRadius: "8px", border: "1px solid var(--border-color)", background: "var(--bg-card)" }} />
                      <Bar dataKey="Compliant" stackId="a" fill="#10B981" maxBarSize={50} />
                      <Bar dataKey="Partial" stackId="a" fill="#F59E0B" maxBarSize={50} />
                      <Bar dataKey="Missing" stackId="a" fill="#EF4444" radius={[4, 4, 0, 0]} maxBarSize={50} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              <div className="card" style={{ padding: "1.25rem", border: "1px solid rgba(239,68,68,0.3)", background: "rgba(239,68,68,0.02)" }}>
                <h3 style={{ fontSize: "1.1rem", fontWeight: 700, marginBottom: "0.75rem", color: "#EF4444" }}>Critical Gaps</h3>
                <div style={{ display: "flex", flexDirection: "column", gap: "0.4rem" }}>
                  {(ad.top_missing_high_risk?.length > 0) ? ad.top_missing_high_risk.map((r, i) => (
                    <div key={i} style={{ display: "flex", justifyContent: "space-between", padding: "0.6rem 0.75rem", background: "var(--bg-card)", borderRadius: "6px", border: "1px solid rgba(239,68,68,0.15)" }}>
                      <div><span style={{ fontSize: "0.8rem", fontWeight: 600, color: "#EF4444", marginRight: "0.5rem" }}>{r.rule_id}</span><span style={{ fontSize: "0.82rem", color: "var(--text-main)" }}>{r.name}</span></div>
                      <span style={{ fontSize: "0.78rem", color: "var(--text-muted)" }}>{r.section_key}</span>
                    </div>
                  )) : <p style={{color: "var(--text-muted)", fontSize:"0.9rem"}}>No critical gaps derived.</p>}
                </div>
              </div>
            </div>
            
            {ad.insights?.length > 0 && (
              <div className="card" style={{ padding: "1.5rem" }}>
                <h3 style={{ fontSize: "1.1rem", fontWeight: 700, marginBottom: "1rem", color: "var(--text-main)", display: "flex", alignItems: "center", gap: "0.5rem" }}>
                  <svg style={{ width: "18px", height: "18px", color: "var(--primary)" }} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
                  Actionable Insights
                </h3>
                <ul style={{ margin: 0, padding: 0, listStyle: "none", display: "flex", flexDirection: "column", gap: "0.6rem" }}>
                  {ad.insights.map((ins, i) => (
                    <li key={i} style={{ padding: "0.75rem 1rem", background: "var(--bg-main)", borderRadius: "6px", fontSize: "0.88rem", color: "var(--text-main)", borderLeft: "3px solid var(--primary)", lineHeight: "1.45" }}>{ins}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {/* HIGH RISK TAB */}
        {activeTab === "high_risk" && (
          <div style={{ animation: "fadeIn 0.3s ease" }}>
            <h3 style={{ fontSize: "1.5rem", fontWeight: 800, color: "var(--text-main)", marginBottom: "1rem" }}>High Risk</h3>
            {highRiskRows.length > 0 ? (
              <div className="card" style={{ padding: 0, overflow: "hidden" }}>
                <div className="table-container" style={{ margin: 0, borderRadius: 0, border: "none" }}>
                  <table className="modern-table" style={{ margin: 0 }}>
                    <thead>
                      <tr>
                        <th>Risk ID</th>
                        <th>Risk Statement</th>
                        <th>Control(s)</th>
                        <th>Rationale</th>
                      </tr>
                    </thead>
                    <tbody>
                      {highRiskRows.map((row, i) => (
                        <tr key={i}>
                          <td style={{ fontWeight: 600, color: "#EF4444", whiteSpace: "nowrap" }}>{row.risk_id}</td>
                          <td style={{ color: "var(--text-main)" }}>{row.risk_statement}</td>
                          <td style={{ color: "var(--text-secondary)", whiteSpace: "nowrap" }}>{row.controls}</td>
                          <td style={{ color: "var(--text-muted)", fontSize: "0.88rem" }}>{row.rationale}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            ) : (
              <div className="card" style={{ padding: "2rem", textAlign: "center" }}>
                <p style={{ color: "var(--text-muted)", fontSize: "0.95rem", margin: 0 }}>No high risks found.</p>
              </div>
            )}
          </div>
        )}

        {/* RISK REGISTER TAB */}
        {activeTab === "risk_register" && (
          <div style={{ animation: "fadeIn 0.3s ease" }}>
            <h3 style={{ fontSize: "1.5rem", fontWeight: 800, color: "var(--text-main)" }}>Risk Register</h3>
            {ad.risk_register ? (
              <>
                <p style={{ color: "var(--text-muted)", fontSize: "0.95rem", marginBottom: "1.5rem" }}>Compiled from your uploaded risk data context.</p>
                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", gap: "1.25rem", marginBottom: "1.5rem" }}>
                  {[
                    { label: "Total Risks", value: ad.risk_register.total_risks, color: "var(--primary)" },
                    { label: "High / Critical", value: ad.risk_register.high_risks || 0, color: "#EF4444" },
                    { label: "Untreated", value: ad.risk_register.untreated_count || 0, color: "#7C3AED" },
                  ].map((m) => (
                    <div key={m.label} className="card" style={{ padding: "1.25rem", borderLeft: `4px solid ${m.color}` }}>
                      <div style={{ fontSize: "0.72rem", color: "var(--text-muted)", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: "0.4rem" }}>{m.label}</div>
                      <div style={{ fontSize: "1.75rem", fontWeight: 800, color: m.color, lineHeight: "1" }}>{m.value}</div>
                    </div>
                  ))}
                </div>
              </>
            ) : (
              <div className="card" style={{ padding: "2rem", textAlign: "center" }}><p style={{ color: "var(--text-muted)", fontSize: "0.95rem", margin: 0 }}>No risk register data found.</p></div>
            )}
          </div>
        )}
        
        {/* TREATMENT PLAN TAB */}
        {activeTab === "treatment_plan" && (
          <div style={{ animation: "fadeIn 0.3s ease" }}>
            <h3 style={{ fontSize: "1.5rem", fontWeight: 800, color: "var(--text-main)", marginBottom: "1rem" }}>Treatment Plan</h3>
            <div className="card" style={{ padding: "2rem", textAlign: "center" }}>
              <p style={{ color: "var(--text-muted)", fontSize: "0.95rem", margin: 0 }}>Treatment plan details will appear here based on risk register configuration.</p>
            </div>
          </div>
        )}

        {/* SOA TAB */}
        {activeTab === "soa" && (() => {
          // Build SOA rows from the existing evaluated controls in ad.sections
          // NO scoring/logic changes — display-only mapping
          const soaRows = [];
          let rowId = 1;
          (ad.sections || []).forEach((section) => {
            (section.controls || []).forEach((ctrl) => {
              const status = (ctrl.status || "").toLowerCase();

              // Col 5: Applicable — all evaluated controls = "Yes"
              const applicable = "Yes";

              // Col 6: Remarks — "N/A" when applicable (per spec)
              const remarks = "N/A";

              // Col 7: Implemented — map from existing status
              let implemented = "Control is not implemented; no supporting evidence found";
              if (status === "compliant") implemented = "Control is implemented and supported by available evidence";
              else if (status === "partial") implemented = "Control is partially implemented; improvements required";

              // Col 8: Reference — mapped from ISO Annex A section (A5/A6/A7/A8) + vendor/missing fallback
              // Display-only — no scoring or inference changes
              const domainHint = (ctrl.domain || section.section_name || section.section_key || "").toLowerCase();
              const ruleHint = (ctrl.rule_id || "").toLowerCase();
              let reference = "System Inference Engine";
              if (status === "missing" && !ctrl.has_evidence) {
                reference = "System Inference Engine / No supporting evidence";
              } else if (domainHint.includes("vendor") || domainHint.includes("supplier") || ruleHint.includes("vendor")) {
                reference = "Vendor Records / Third-Party Data";
              } else if (domainHint.includes("people") || domainHint.includes("a6") || ruleHint.startsWith("iso-a6")) {
                reference = "HR / Employee Data; Training Matrix";
              } else if (domainHint.includes("physical") || domainHint.includes("a7") || ruleHint.startsWith("iso-a7")) {
                reference = "Asset Inventory / Facilities Data";
              } else if (domainHint.includes("technological") || domainHint.includes("a8") || ruleHint.startsWith("iso-a8")) {
                reference = "Network Rules / Configurations / Systems";
              } else if (domainHint.includes("organizational") || domainHint.includes("a5") || ruleHint.startsWith("iso-a5")) {
                reference = "Policies / Governance / Risk Register";
              } else if (ctrl.has_evidence) {
                reference = "System Inference Engine";
              }

              soaRows.push({
                id: rowId++,
                section: section.section_name || section.section_key || "—",
                // Normalise raw rule_id: "ISO-A6.1-01" → "A.6.1"
                control_no: (() => {
                  const raw = ctrl.rule_id || "";
                  // Match the annex letter + dotted number part: A6.1, A7.10, A8.24
                  const m = raw.match(/[Aa](\d+\.\d+)/);
                  return m ? `A.${m[1]}` : (raw || "—");
                })(),
                control_title: ctrl.name || "—",
                applicable,
                remarks,
                implemented,
                reference,
                status,
              });
            });
          });

          return (
            <div>
              {soaRows.length > 0 ? (
                <div className="card" style={{ padding: 0, overflow: "hidden" }}>
                  <div className="table-container" style={{ margin: 0, borderRadius: 0, border: "none", width: "100%" }}>
                    <table className="modern-table" style={{ margin: 0, width: "100%", tableLayout: "auto" }}>
                      <thead>
                        <tr>
                          <th style={{ width: "40px" }}>ID</th>
                          <th style={{ width: "10%" }}>Section</th>
                          <th style={{ width: "80px" }}>Control No.</th>
                          <th style={{ width: "22%" }}>Control Title</th>
                          <th style={{ width: "80px" }}>Applicable</th>
                          <th style={{ width: "10%" }}>Remarks</th>
                          <th style={{ width: "90px" }}>Status</th>
                          <th style={{ width: "26%" }}>Implementation Overview</th>
                          <th style={{ width: "18%" }}>Reference</th>
                        </tr>
                      </thead>
                      <tbody>
                        {soaRows.map((row) => (
                          <tr key={row.id}>
                            <td style={{ fontWeight: 600, color: "var(--text-muted)", textAlign: "center" }}>{row.id}</td>
                            <td style={{ fontSize: "0.82rem", color: "var(--text-muted)", whiteSpace: "normal", wordWrap: "break-word" }}>{row.section}</td>
                            <td style={{ fontWeight: 600, color: "var(--primary)", fontSize: "0.85rem" }}>{row.control_no}</td>
                            <td style={{ fontWeight: 500, color: "var(--text-main)", fontSize: "0.88rem", whiteSpace: "normal", wordWrap: "break-word" }}>{row.control_title}</td>
                            <td style={{ textAlign: "center" }}>
                              <span className="badge badge-green">{row.applicable}</span>
                            </td>
                            <td style={{ fontSize: "0.82rem", color: "var(--text-muted)", whiteSpace: "normal", wordWrap: "break-word" }}>{row.remarks}</td>
                            <td>
                              <span className={getBadgeClass(row.status)} style={{ display: "inline-block", fontSize: "0.72rem" }}>{(row.status || "").toUpperCase()}</span>
                            </td>
                            <td style={{ fontSize: "0.82rem", color: "var(--text-main)", lineHeight: "1.4", whiteSpace: "normal", wordWrap: "break-word" }}>{row.implemented}</td>
                            <td style={{ fontSize: "0.82rem", color: "var(--text-secondary)", whiteSpace: "normal", wordWrap: "break-word" }}>{row.reference}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                  <div style={{ padding: "0.6rem 1rem", background: "var(--bg-main)", fontSize: "0.8rem", color: "var(--text-muted)", borderTop: "1px solid var(--border-color)" }}>
                    {soaRows.length} control{soaRows.length !== 1 ? "s" : ""} — all evaluated controls included
                  </div>
                </div>
              ) : (
                <div className="card" style={{ padding: "2rem", textAlign: "center" }}>
                  <p style={{ color: "var(--text-muted)", fontSize: "0.95rem", margin: 0 }}>No SOA data found. Upload an assessment to generate the Statement of Applicability.</p>
                </div>
              )}
            </div>
          );
        })()}

        {/* COMPLIANCE MATRIX TAB */}
        {activeTab === "compliance_matrix" && (
          <div style={{ animation: "fadeIn 0.3s ease" }}>
            <h3 style={{ fontSize: "1.5rem", fontWeight: 800, color: "var(--text-main)", marginBottom: "1rem" }}>Compliance Matrix</h3>
            {ad.sections ? (
              <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
                {ad.sections.map((sec, idx) => (
                  <div key={idx} className="card" style={{padding: "1rem", display: "flex", justifyContent: "space-between", alignItems: "center"}}>
                    <div>
                      <h4 style={{margin:0, fontSize:"1.05rem"}}>{sec.section_key} {sec.section_name}</h4>
                      <span style={{fontSize:"0.8rem", color:"var(--text-muted)"}}>Reqs: {sec.controls_count} | Pass: {sec.compliant_controls} | Partial: {sec.partial_controls} | Fail: {sec.missing_controls}</span>
                    </div>
                    <div style={{fontSize:"1.25rem", fontWeight:"bold", color: sec.compliance_score >= 80 ? "#10B981" : sec.compliance_score >= 50 ? "#F59E0B" : "#EF4444"}}>{sec.compliance_score}%</div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="card" style={{ padding: "2rem", textAlign: "center" }}><p style={{ color: "var(--text-muted)", fontSize: "0.95rem", margin: 0 }}>No compliance matrix data found.</p></div>
            )}
          </div>
        )}

        {/* VENDOR CHECKLIST TAB */}
        {activeTab === "vendor" && (
          <div style={{ animation: "fadeIn 0.3s ease" }}>
            <h3 style={{ fontSize: "1.5rem", fontWeight: 800, color: "var(--text-main)", marginBottom: "1rem" }}>Vendor Security Checklist</h3>
            {ad.vendor_checklist && ad.vendor_checklist.length > 0 ? (
              <div className="card" style={{ padding: 0, overflow: "hidden" }}>
                <div className="table-container" style={{ margin: 0, borderRadius: 0, border: "none" }}>
                  <table className="modern-table" style={{ margin: 0 }}>
                    <thead><tr><th>Vendor Name</th><th>Service Provided</th><th>Compliance Status</th><th>Action Required</th></tr></thead>
                    <tbody>
                      {ad.vendor_checklist.map((vendor, i) => (
                        <tr key={i}>
                          <td style={{fontWeight:500}}>{vendor.vendor_name}</td>
                          <td>{vendor.service_provided}</td>
                          <td><span className={getBadgeClass(vendor.compliance_status)}>{vendor.compliance_status}</span></td>
                          <td style={{color: "var(--primary)", fontWeight:500}}>{vendor.action_required}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            ) : (
              <div className="card" style={{ padding: "2rem", textAlign: "center" }}><p style={{ color: "var(--text-muted)", fontSize: "0.95rem", margin: 0 }}>No vendor checklist data found.</p></div>
            )}
          </div>
        )}

        {/* TRAINING MATRIX TAB */}
        {activeTab === "training" && (
          <div style={{ animation: "fadeIn 0.3s ease" }}>
            <h3 style={{ fontSize: "1.5rem", fontWeight: 800, color: "var(--text-main)", marginBottom: "1rem" }}>Training Matrix</h3>
            {ad.training_matrix && ad.training_matrix.length > 0 ? (
              <div className="card" style={{ padding: 0, overflow: "hidden" }}>
                <div className="table-container" style={{ margin: 0, borderRadius: 0, border: "none" }}>
                  <table className="modern-table" style={{ margin: 0 }}>
                    <thead><tr><th>Employee Role</th><th>Employee Name</th><th>Training Status</th><th>Required Modules</th></tr></thead>
                    <tbody>
                      {ad.training_matrix.map((row, i) => (
                        <tr key={i}>
                          <td style={{fontWeight:500}}>{row.role}</td>
                          <td>{row.employee}</td>
                          <td><span className={getBadgeClass(row.training_status)}>{row.training_status}</span></td>
                          <td style={{color: "var(--text-secondary)"}}>{row.required_modules}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            ) : (
              <div className="card" style={{ padding: "2rem", textAlign: "center" }}><p style={{ color: "var(--text-muted)", fontSize: "0.95rem", margin: 0 }}>No training matrix data found.</p></div>
            )}
          </div>
        )}

        {/* GOVERNANCE CALENDAR TAB */}
        {activeTab === "governance" && (
          <div style={{ animation: "fadeIn 0.3s ease" }}>
            <h3 style={{ fontSize: "1.5rem", fontWeight: 800, color: "var(--text-main)", marginBottom: "1rem" }}>Governance Calendar</h3>
            {ad.governance_calendar && ad.governance_calendar.length > 0 ? (
              <div className="card" style={{ padding: 0, overflow: "hidden" }}>
                <div className="table-container" style={{ margin: 0, borderRadius: 0, border: "none" }}>
                  <table className="modern-table" style={{ margin: 0 }}>
                    <thead><tr><th>Recurring Activity</th><th>Cadence</th><th>Responsible Party</th><th>Status</th></tr></thead>
                    <tbody>
                      {ad.governance_calendar.map((row, i) => (
                        <tr key={i}>
                          <td style={{fontWeight:500}}>{row.activity}</td>
                          <td>{row.cadence}</td>
                          <td>{row.responsible}</td>
                          <td><span className={getBadgeClass(row.status)}>{row.status}</span></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            ) : (
              <div className="card" style={{ padding: "2rem", textAlign: "center" }}><p style={{ color: "var(--text-muted)", fontSize: "0.95rem", margin: 0 }}>No governance calendar data found.</p></div>
            )}
          </div>
        )}

      </div>
    </PageContainer>
  );
}
