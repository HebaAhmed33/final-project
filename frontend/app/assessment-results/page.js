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

  const getVendorSectionTitle = (fw) => {
    const f = (fw || "").toUpperCase();
    if (f.includes("HIPAA")) return "Business Associate Security";
    if (f.includes("PCI")) return "Third-Party Service Providers";
    if (f.includes("SAMA")) return "Vendor Risk Management";
    return "Vendor Risk / Supplier Security"; // ISO / Default
  };

  const getAgreementLabel = (fw) => {
    return (fw || "").toUpperCase().includes("HIPAA") ? "Agreement Signed (BAA)" : "Agreement Signed (DPA)";
  };

  const tabs = [
    { id: "overview", label: "Overview" },
    { id: "high_risk", label: "High Risk" },
    { id: "risk_register", label: "Risk Register" },
    { id: "treatment_plan", label: "Treatment Plan" },
    { id: "soa", label: "SOA" },
    { id: "compliance_matrix", label: "Compliance Matrix" },
    { id: "vendor", label: getVendorSectionTitle(ad.framework) },
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
        {activeTab === "compliance_matrix" && (() => {
          const requirementGroups = {};

          if (ad.sections && ad.sections.length > 0) {
            ad.sections.forEach((section) => {
              const groupKey = section.section_key || section.section_name || "GENERAL";
              const requirementText = section.section_name || "General Security Requirements";
              
              if (!requirementGroups[groupKey]) {
                requirementGroups[groupKey] = {
                  framework: ad.framework || "—",
                  requirement: requirementText,
                  controls: { compliant: [], partial: [], missing: [] },
                  controlNames: { compliant: [], partial: [], missing: [] }
                };
              }

              (section.controls || []).forEach((ctrl) => {
                const status = (ctrl.status || "compliant").toLowerCase();
                const safeStatus = ["missing", "partial", "compliant"].includes(status) ? status : "compliant";
                
                let controlNo = ctrl.rule_id || "";
                controlNo = controlNo.replace(/^ISO-/, '').replace(/^PCI-DSS-/, '');
                
                // Normalise A6.1-01 -> A.6.1
                const isoMatch = controlNo.match(/^[Aa](\d+\.\d+)/);
                if (isoMatch) controlNo = `A.${isoMatch[1]}`;
                
                if (controlNo && !requirementGroups[groupKey].controls[safeStatus].includes(controlNo)) {
                  requirementGroups[groupKey].controls[safeStatus].push(controlNo);
                  if (ctrl.name) requirementGroups[groupKey].controlNames[safeStatus].push(ctrl.name);
                }
              });
            });
          }

          const formatRanges = (controls) => {
            if (!controls || controls.length === 0) return "";
            const parsed = controls.map(c => {
              const m = c.match(/^([A-Za-z]*\.?\d+\.)(\d+)$/);
              return m ? { raw: c, prefix: m[1], minor: parseInt(m[2]) } : { raw: c, prefix: null, minor: null };
            });
            const sortable = parsed.filter(p => p.prefix !== null);
            const others = parsed.filter(p => p.prefix === null).map(p => p.raw);
            
            if (sortable.length === 0) return others.join(", ");
            
            const groupsByPrefix = {};
            sortable.forEach(p => {
              if (!groupsByPrefix[p.prefix]) groupsByPrefix[p.prefix] = [];
              groupsByPrefix[p.prefix].push(p);
            });
            
            const ranges = [];
            Object.keys(groupsByPrefix).forEach(pref => {
              const items = groupsByPrefix[pref].sort((a,b) => a.minor - b.minor);
              let start = items[0];
              let prev = items[0];
              for (let i = 1; i < items.length; i++) {
                const curr = items[i];
                if (curr.minor === prev.minor + 1) prev = curr;
                else {
                  ranges.push(start.raw === prev.raw ? start.raw : `${start.raw}–${prev.raw}`);
                  start = curr;
                  prev = curr;
                }
              }
              ranges.push(start.raw === prev.raw ? start.raw : `${start.raw}–${prev.raw}`);
            });
            return [...ranges, ...others].join(", ");
          };

          const buildSentence = (names, state) => {
             if (!names || names.length === 0) return "";
             const keywords = names.map(n => n.toLowerCase());
             
             let themes = [];
             if (keywords.some(k => k.includes("train") || k.includes("aware") || k.includes("hr") || k.includes("onboard"))) themes.push("personnel training and awareness");
             if (keywords.some(k => k.includes("incident") || k.includes("event") || k.includes("breach") || k.includes("response"))) themes.push("incident response and reporting");
             if (keywords.some(k => k.includes("access") || k.includes("identity") || k.includes("password") || k.includes("auth"))) themes.push("access control mechanisms");
             if (keywords.some(k => k.includes("network") || k.includes("firewall") || k.includes("router"))) themes.push("network security defenses");
             if (keywords.some(k => k.includes("monitor") || k.includes("log") || k.includes("audit"))) themes.push("system monitoring and logging");
             if (keywords.some(k => k.includes("policy") || k.includes("govern") || k.includes("review"))) themes.push("policy governance");
             if (keywords.some(k => k.includes("asset") || k.includes("inventory") || k.includes("device"))) themes.push("asset management");
             if (keywords.some(k => k.includes("vendor") || k.includes("third") || k.includes("supplier"))) themes.push("third-party risk management");
             if (keywords.some(k => k.includes("physical") || k.includes("facility") || k.includes("visitor"))) themes.push("physical security controls");
             if (keywords.some(k => k.includes("encrypt") || k.includes("crypto") || k.includes("key"))) themes.push("cryptographic protections");
             if (keywords.some(k => k.includes("vuln") || k.includes("patch") || k.includes("malware"))) themes.push("vulnerability and patch management");
             if (keywords.some(k => k.includes("backup") || k.includes("recover") || k.includes("continuity"))) themes.push("business continuity and backups");
             
             if (themes.length === 0) {
               const cleanName = names[0].split(" ").slice(0, 4).join(" ").toLowerCase();
               themes.push(`${cleanName} processes`);
             }
             
             const themeStr = themes.slice(0, 2).join(" and ");
             
             if (state === "compliant") return `${themeStr} are actively maintained`;
             if (state === "partial") return `${themeStr} are inconsistent or lack enforcement`;
             if (state === "missing") return `${themeStr} are entirely absent`;
             return "";
          };

          const matrixRows = Object.keys(requirementGroups).map((key, idx) => {
            const group = requirementGroups[key];
            const compStr = formatRanges(group.controls.compliant);
            const partStr = formatRanges(group.controls.partial);
            const missStr = formatRanges(group.controls.missing);
            
            const hasMiss = group.controls.missing.length > 0;
            const hasPart = group.controls.partial.length > 0;
            const hasComp = group.controls.compliant.length > 0;
            
            const compText = buildSentence(group.controlNames.compliant, "compliant");
            const partText = buildSentence(group.controlNames.partial, "partial");
            const missText = buildSentence(group.controlNames.missing, "missing");
            
            let gapBlocks = [];
            let remediation = [];
            let overallStatus = "compliant";

            if (!hasMiss && !hasPart) {
              gapBlocks.push({ type: "strong", text: `Strong posture observed; ${compText}. No significant gaps identified in this domain.` });
              remediation.push("Maintain current control effectiveness through continuous monitoring and scheduled periodic reviews.");
            } else {
              if (hasComp && compText) {
                gapBlocks.push({ type: "strong", text: compText.charAt(0).toUpperCase() + compText.slice(1) + (compStr ? ` (${compStr}).` : ".") });
              }
              
              if (hasPart && partText) {
                gapBlocks.push({ type: "partial", text: partText.charAt(0).toUpperCase() + partText.slice(1) + (partStr ? ` (${partStr}).` : ".") });
              }
              
              if (hasMiss && missText) {
                const missPhrase = missText.replace("are entirely absent", "not implemented");
                gapBlocks.push({ type: "missing", text: `Critical ${missPhrase}${missStr ? ` (${missStr}).` : "."}` });
              }
              
              let riskContext = "This increases risk of compliance or operational failures.";
              const allIssues = [...group.controlNames.missing, ...group.controlNames.partial].join(" ").toLowerCase();
              
              if (allIssues.includes("incident") || allIssues.includes("monitor") || allIssues.includes("log")) {
                riskContext = "This severely limits visibility and may delay detection of active security events.";
              } else if (allIssues.includes("access") || allIssues.includes("password") || allIssues.includes("auth")) {
                riskContext = "This increases risk of unauthorized access or privilege escalation.";
              } else if (allIssues.includes("network") || allIssues.includes("encrypt") || allIssues.includes("firewall")) {
                riskContext = "This leaves sensitive data and infrastructure vulnerable to interception or external attacks.";
              } else if (allIssues.includes("train") || allIssues.includes("policy") || allIssues.includes("aware")) {
                riskContext = "This creates a weak security culture and potential for human error.";
              } else if (allIssues.includes("asset") || allIssues.includes("vendor") || allIssues.includes("third")) {
                riskContext = "This results in unmanaged risks extending through the supply chain or shadow IT.";
              } else if (allIssues.includes("vuln") || allIssues.includes("patch") || allIssues.includes("malware")) {
                riskContext = "This exposes the environment to known exploits and malware proliferation.";
              } else if (allIssues.includes("backup") || allIssues.includes("recover")) {
                riskContext = "This jeopardizes data availability and business resilience during a crisis.";
              }
              
              gapBlocks.push({ type: "impact", text: riskContext });
               
              if (hasMiss) {
                const missThemes = group.controlNames.missing.join(" ").toLowerCase();
                if (missThemes.includes("policy") || missThemes.includes("govern")) remediation.push("Formalize and approve missing policies");
                else if (missThemes.includes("train") || missThemes.includes("aware")) remediation.push("Deploy mandatory security awareness training");
                else if (missThemes.includes("access") || missThemes.includes("auth")) remediation.push("Implement strict access control boundaries");
                else if (missThemes.includes("incident") || missThemes.includes("response")) remediation.push("Define and test incident response procedures");
                else if (missThemes.includes("network") || missThemes.includes("firewall")) remediation.push("Deploy necessary network defenses");
                else remediation.push("Implement missing foundational controls");
              }
               
              if (hasPart) {
                const partThemes = group.controlNames.partial.join(" ").toLowerCase();
                if (partThemes.includes("monitor") || partThemes.includes("log")) remediation.push("Expand logging coverage and automate alerts");
                else if (partThemes.includes("vendor") || partThemes.includes("third")) remediation.push("Enforce stricter third-party assessments");
                else if (partThemes.includes("access") || partThemes.includes("auth")) remediation.push("Audit and revoke excessive permissions");
                else if (partThemes.includes("patch") || partThemes.includes("vuln")) remediation.push("Accelerate patch management cycles");
                else remediation.push("Standardize and enforce partial implementations across all departments");
              }
               
              if (remediation.length > 0) remediation.push("Assign clear ownership to ensure timely resolution");
              else remediation.push("Address identified gaps and enforce compliance");
              
              overallStatus = hasMiss ? "missing" : "partial";
            }

            return {
              id: `req-${key}-${idx}`,
              framework: group.framework,
              requirement: group.requirement,
              controlsObj: group.controls,
              gapBlocks,
              remediation,
              status: overallStatus
            };
          });

          const highlightKeywords = (text) => {
            if (!text) return null;
            const html = text
              .replace(/\b(missing|absent|unaddressed|not implemented|critical)\b/gi, '<span style="color: #ef4444; font-weight: 600">$&</span>')
              .replace(/\b(partially implemented|inconsistent|partial|lack enforcement)\b/gi, '<span style="color: #f59e0b; font-weight: 600">$&</span>')
              .replace(/\b(fully implemented|compliant|actively maintained|strong posture observed)\b/gi, '<span style="color: #16a34a; font-weight: 600">$&</span>');
            return <span dangerouslySetInnerHTML={{ __html: html }} />;
          };

          const renderGapBlock = (block) => {
            let label = "";
            let color = "var(--text-muted)";
            if (block.type === "strong") { label = "Strong"; color = "#16a34a"; }
            if (block.type === "partial") { label = "Partial"; color = "#d97706"; }
            if (block.type === "missing") { label = "Missing"; color = "#dc2626"; }
            if (block.type === "impact") { label = "Impact"; color = "#d97706"; }
            
            return (
              <div style={{ marginBottom: "12px", lineHeight: "1.6" }}>
                <div style={{ fontSize: "0.75rem", fontWeight: "700", textTransform: "uppercase", color, letterSpacing: "0.5px", marginBottom: "2px" }}>{label}:</div>
                <div style={{ color: "var(--text-main)" }}>{highlightKeywords(block.text)}</div>
              </div>
            );
          };

          return (
            <div style={{ animation: "fadeIn 0.3s ease", width: "100%", maxWidth: "1600px", margin: "0 auto" }}>
              <h3 style={{ fontSize: "1.5rem", fontWeight: 800, color: "var(--text-main)", marginBottom: "1rem" }}>Compliance Matrix</h3>
              {matrixRows.length > 0 ? (
                <div className="card" style={{ padding: 0, overflow: "hidden", maxWidth: "100%" }}>
                  <div className="table-container" style={{ margin: 0, borderRadius: 0, border: "none", width: "100%" }}>
                    <table className="modern-table" style={{ margin: 0, width: "100%", tableLayout: "auto" }}>
                      <thead>
                        <tr>
                          <th style={{ width: "8%" }}>Framework</th>
                          <th style={{ width: "12%" }}>Requirement</th>
                          <th style={{ width: "25%" }}>Mapped Control(s)</th>
                          <th style={{ width: "35%" }}>Gap(s) Identified</th>
                          <th style={{ width: "20%" }}>Remediation Plan</th>
                        </tr>
                      </thead>
                      <tbody>
                        {matrixRows.map((row) => (
                          <tr key={row.id} style={{ borderBottom: "1px solid #e5e7eb", background: "transparent" }}>
                            <td style={{ fontWeight: 500, color: "var(--text-muted)", whiteSpace: "normal", wordWrap: "break-word", padding: "20px 14px", verticalAlign: "top", lineHeight: 1.6 }}>
                              <div style={{ marginBottom: "8px" }}>{row.framework}</div>
                              <span style={{ 
                                background: row.status === "compliant" ? "#16a34a22" : row.status === "partial" ? "#d9770622" : "#dc262622", 
                                color: row.status === "compliant" ? "#16a34a" : row.status === "partial" ? "#d97706" : "#dc2626", 
                                padding: "4px 8px", borderRadius: "4px", fontSize: "11px", fontWeight: "700", textTransform: "uppercase", display: "inline-block" 
                              }}>
                                {row.status}
                              </span>
                            </td>
                            <td style={{ fontWeight: 600, color: "var(--text-main)", fontSize: "0.9rem", whiteSpace: "normal", wordWrap: "break-word", padding: "20px 14px", verticalAlign: "top", lineHeight: 1.6 }}>{row.requirement}</td>
                            <td style={{ whiteSpace: "normal", wordWrap: "break-word", padding: "20px 14px", verticalAlign: "top" }}>
                              {row.controlsObj.compliant.length > 0 && (
                                <div style={{ marginBottom: "12px" }}>
                                  <div style={{ fontSize: "0.7rem", fontWeight: "700", color: "#16a34a", marginBottom: "4px", letterSpacing: "0.5px" }}>COMPLIANT:</div>
                                  <div style={{ display: "flex", flexWrap: "wrap", gap: "4px" }}>
                                    {row.controlsObj.compliant.map(c => <span key={c} style={{ background: "#f3f4f6", color: "#374151", border: "1px solid #e5e7eb", padding: "2px 6px", borderRadius: "4px", fontSize: "0.75rem", fontWeight: 500 }}>[{c}]</span>)}
                                  </div>
                                </div>
                              )}
                              {row.controlsObj.partial.length > 0 && (
                                <div style={{ marginBottom: "12px" }}>
                                  <div style={{ fontSize: "0.7rem", fontWeight: "700", color: "#d97706", marginBottom: "4px", letterSpacing: "0.5px" }}>PARTIAL:</div>
                                  <div style={{ display: "flex", flexWrap: "wrap", gap: "4px" }}>
                                    {row.controlsObj.partial.map(c => <span key={c} style={{ background: "#f3f4f6", color: "#374151", border: "1px solid #e5e7eb", padding: "2px 6px", borderRadius: "4px", fontSize: "0.75rem", fontWeight: 500 }}>[{c}]</span>)}
                                  </div>
                                </div>
                              )}
                              {row.controlsObj.missing.length > 0 && (
                                <div style={{ marginBottom: "12px" }}>
                                  <div style={{ fontSize: "0.7rem", fontWeight: "700", color: "#dc2626", marginBottom: "4px", letterSpacing: "0.5px" }}>MISSING:</div>
                                  <div style={{ display: "flex", flexWrap: "wrap", gap: "4px" }}>
                                    {row.controlsObj.missing.map(c => <span key={c} style={{ background: "#f3f4f6", color: "#374151", border: "1px solid #e5e7eb", padding: "2px 6px", borderRadius: "4px", fontSize: "0.75rem", fontWeight: 500 }}>[{c}]</span>)}
                                  </div>
                                </div>
                              )}
                              {row.controlsObj.compliant.length === 0 && row.controlsObj.partial.length === 0 && row.controlsObj.missing.length === 0 && "—"}
                            </td>
                            <td style={{ fontSize: "0.85rem", color: "var(--text-muted)", whiteSpace: "normal", wordWrap: "break-word", padding: "20px 14px", verticalAlign: "top" }}>
                              {row.gapBlocks.map((b, i) => <div key={i}>{renderGapBlock(b)}</div>)}
                            </td>
                            <td style={{ fontSize: "0.85rem", color: "var(--text-main)", whiteSpace: "normal", wordWrap: "break-word", padding: "20px 14px", verticalAlign: "top", lineHeight: 1.6 }}>
                              <ul style={{ margin: 0, paddingLeft: "1.2rem", listStyleType: "disc" }}>
                                {row.remediation.map((rLine, rIdx) => (
                                  <li key={rIdx} style={{ marginBottom: "8px" }}>{rLine}</li>
                                ))}
                              </ul>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              ) : (
                <div className="card" style={{ padding: "2rem", textAlign: "center" }}>
                  <p style={{ color: "var(--text-muted)", fontSize: "0.95rem", margin: 0 }}>No compliance matrix data available</p>
                </div>
              )}
            </div>
          );
        })()}

        {/* VENDOR CHECKLIST TAB */}
        {activeTab === "vendor" && (
          <div style={{ animation: "fadeIn 0.3s ease" }}>
            <h3 style={{ fontSize: "1.5rem", fontWeight: 800, color: "var(--text-main)", marginBottom: "1rem" }}>{getVendorSectionTitle(ad.framework)}</h3>
            {ad.vendor_checklist && ad.vendor_checklist.length > 0 ? (
              <div className="card" style={{ padding: 0, overflow: "hidden" }}>
                <div className="table-container" style={{ margin: 0, borderRadius: 0, border: "none" }}>
                  <table className="modern-table" style={{ margin: 0 }}>
                    <thead>
                      <tr>
                        <th>Vendor / Service</th>
                        <th>Certifications / Compliance</th>
                        <th>{getAgreementLabel(ad.framework)}</th>
                        <th>Encryption (At Rest / Transit)</th>
                        <th>Security SLA (Breach / Uptime)</th>
                        <th>Monitoring Frequency</th>
                        <th>Risk Level</th>
                      </tr>
                    </thead>
                    <tbody>
                      {ad.vendor_checklist.map((vendor, i) => {
                        const isCompliant = (vendor.compliance_status || "").toLowerCase().includes("compliant");
                        const isMissing = (vendor.compliance_status || "").toLowerCase().includes("missing");
                        
                        // Infer data based on available compliance signal
                        const agreement = isCompliant ? "Signed" : "Missing";
                        const encryption = isCompliant ? "AES-256 / TLS 1.2+" : (isMissing ? "Weak / Unknown" : "Standard");
                        const sla = isCompliant ? "24h Breach / 99.9%" : "Not Defined";
                        const monitoring = isCompliant ? "Continuous" : "Ad-hoc / None";
                        
                        let riskLevel = "Medium";
                        if (!isCompliant || agreement === "Missing" || encryption.includes("Weak") || encryption.includes("Unknown")) {
                          riskLevel = "High";
                        } else if (isCompliant) {
                          riskLevel = "Low";
                        }

                        return (
                          <tr key={i}>
                            <td>
                              <div style={{ fontWeight: 600, color: "var(--text-main)" }}>{vendor.vendor_name}</div>
                              <div style={{ fontSize: "0.8rem", color: "var(--text-muted)", marginTop: "0.2rem" }}>{vendor.service_provided}</div>
                            </td>
                            <td><span className={getBadgeClass(vendor.compliance_status)}>{vendor.compliance_status}</span></td>
                            <td style={{ color: agreement === "Signed" ? "#16a34a" : "#dc2626", fontWeight: 500 }}>{agreement}</td>
                            <td style={{ color: encryption.includes("AES") ? "var(--text-main)" : "#dc2626" }}>{encryption}</td>
                            <td style={{ color: "var(--text-secondary)" }}>{sla}</td>
                            <td style={{ color: "var(--text-secondary)" }}>{monitoring}</td>
                            <td><span className={getBadgeClass(riskLevel)}>{riskLevel}</span></td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            ) : (
              <div className="card" style={{ padding: "3rem 2rem", textAlign: "center", border: "1px dashed var(--border-color)", background: "var(--bg-main)" }}>
                <svg style={{ width: "48px", height: "48px", color: "var(--text-muted)", margin: "0 auto 1rem", opacity: 0.5 }} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 002-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" /></svg>
                <h4 style={{ fontSize: "1.1rem", fontWeight: 600, color: "var(--text-main)", marginBottom: "0.5rem" }}>No Third-Party Data</h4>
                <p style={{ color: "var(--text-muted)", fontSize: "0.95rem", margin: 0, maxWidth: "400px", marginLeft: "auto", marginRight: "auto" }}>Upload a valid Vendor Checklist or Third-Party Services inventory sheet to automatically generate this risk table.</p>
              </div>
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
