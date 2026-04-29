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
    if (["compliant", "pass", "low", "true", "fully implemented", "completed (on time)"].includes(v)) return "badge badge-green";
    if (["missing", "fail", "high", "false", "not implemented", "overdue"].includes(v)) return "badge badge-red";
    if (["partial", "medium", "partially implemented", "pending"].includes(v)) return "badge badge-yellow";
    return "badge badge-blue";
  };

  const formatStatusLabel = (s) => {
    if (!s) return "";
    const v = s.toLowerCase();
    if (v === "completed (on time)") return "Completed (On Time)";
    if (v === "overdue") return "Overdue";
    if (v === "pending") return "Pending";
    return s.split(" ").map(w => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase()).join(" ");
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
  if (ad.risk_register) {
    const entries = [
      ...(ad.risk_register.generated_risk_entries || []),
      ...(ad.risk_register.uploaded_risk_entries || []),
    ];
    entries.forEach((r) => {
      let rawL = parseFloat(r.likelihood);
      let rawI = parseFloat(r.impact);
      let level = (r.risk_level || r.level || "").toLowerCase();

      let riskScore = 0;
      if (!isNaN(rawL) && !isNaN(rawI)) {
        riskScore = rawL * rawI;
      }

      if (riskScore >= 12) {
        const id = String(r.risk_id || r.id || `HR-${highRiskRows.length + 1}`);

        // Exclude placeholder IDs
        if (id.startsWith("RSK-")) {
            return;
        }

        // Exclude status-based controls
        const rawControl = String(r.control || r.control_id || r.mitigation || "").toLowerCase();
        if (rawControl.includes("in progress") || rawControl.includes("planned") || rawControl.includes("not started")) {
            return;
        }

        // Exclude non-real risks (lacking threat context)
        const rThreat = (r.threat || "").toLowerCase();
        if (!rThreat || rThreat === "unspecified threat" || rThreat === "identified risk" || rThreat === "placeholder") {
            return;
        }

        if (!seenIds.has(id)) {
          seenIds.add(id);
          const rStatement = r.risk_statement || r.description || r.title || r.name || r.risk_name || "—";
          const rThreatSafe = (r.threat || r.vulnerability || r.rule_id || rStatement || "").toLowerCase();
          
          let controlsArr = r.control_id;
          if (!controlsArr && r.iso_controls) controlsArr = r.iso_controls;
          if (!controlsArr && r.control) controlsArr = [r.control];
          if (!Array.isArray(controlsArr)) {
             if (typeof controlsArr === "string") controlsArr = controlsArr.split(",").map(c => c.trim()).filter(Boolean);
             else controlsArr = [];
          }

          let controls = controlsArr.join("; ");
          
          if (!controls || controls === "—") {
             if (rThreatSafe.includes("sql injection") || rStatement.toLowerCase().includes("sql injection")) controls = "A.8.28";
             else if (rThreatSafe.includes("api abuse") || rThreatSafe.includes("api") || rStatement.toLowerCase().includes("api")) controls = "A.8.23; A.8.28";
             else if (rThreatSafe.includes("default") || rThreatSafe.includes("misconfiguration") || rStatement.toLowerCase().includes("misconfiguration")) controls = "A.8.9";
             else if (rThreatSafe.includes("unpatched") || rThreatSafe.includes("vuln") || rThreatSafe.includes("remote code execution") || rThreatSafe.includes("patch") || rThreatSafe.includes("exploit") || rThreatSafe.includes("cve") || rStatement.toLowerCase().includes("unpatched") || rStatement.toLowerCase().includes("vulnerability") || rStatement.toLowerCase().includes("remote code execution")) controls = "A.8.8";
             else if (rThreatSafe.includes("vendor") || rThreatSafe.includes("third") || rThreatSafe.includes("supply") || rThreatSafe.includes("supplier") || rThreatSafe.includes("compliance gap") || rThreatSafe.includes("review pending") || rStatement.toLowerCase().includes("vendor") || rStatement.toLowerCase().includes("supply chain")) controls = "A.5.19; A.5.20";
             else if (rThreatSafe.includes("shadow it") || rThreatSafe.includes("unmanaged") || rStatement.toLowerCase().includes("shadow it") || rStatement.toLowerCase().includes("unmanaged")) controls = "A.5.9";
             else if (rThreatSafe.includes("policy gap") || rThreatSafe.includes("policy") || rStatement.toLowerCase().includes("policy")) controls = "A.5.1";
             else if (rThreatSafe.includes("data exfiltration") || (rThreatSafe.includes("data") && (rThreatSafe.includes("loss") || rThreatSafe.includes("leak") || rThreatSafe.includes("breach") || rThreatSafe.includes("exfil"))) || rStatement.toLowerCase().includes("data exfiltration")) controls = "A.8.12";
             else if (rThreatSafe.includes("access") || rThreatSafe.includes("auth") || rThreatSafe.includes("credential") || rStatement.toLowerCase().includes("access")) controls = "A.8.3";
             else if (rThreatSafe.includes("phish") || rThreatSafe.includes("social") || rThreatSafe.includes("train")) controls = "A.6.3";
             else if (rThreatSafe.includes("malware") || rThreatSafe.includes("ransomware") || rThreatSafe.includes("virus")) controls = "A.8.7";
             else if (rThreatSafe.includes("network") || rThreatSafe.includes("firewall") || rThreatSafe.includes("ddos") || rThreatSafe.includes("attack")) controls = "A.8.20";
             else if (rThreatSafe.includes("physical") || rThreatSafe.includes("theft") || rThreatSafe.includes("unauthorized entry")) controls = "A.7.1; A.7.2";
             else if (rThreatSafe.includes("backup") || rThreatSafe.includes("disaster") || rThreatSafe.includes("recover") || rThreatSafe.includes("business continuity") || rStatement.toLowerCase().includes("business continuity")) controls = "A.5.30";
             else controls = "A.5.1; A.5.2";
          }

          const isHipaa = ad.framework_id === "hipaa" || String(ad.framework).toLowerCase() === "hipaa";
          if (isHipaa) {
             if (rThreatSafe.includes("sql injection") || rStatement.toLowerCase().includes("sql injection")) controls = "§164.312(c)";
             else if (rThreatSafe.includes("api abuse") || rThreatSafe.includes("api") || rStatement.toLowerCase().includes("api")) controls = "§164.312(c); §164.312(e)";
             else if (rThreatSafe.includes("default") || rThreatSafe.includes("misconfiguration") || rStatement.toLowerCase().includes("misconfiguration")) controls = "§164.312(c); §164.308(a)(1)";
             else if (rThreatSafe.includes("unpatched") || rThreatSafe.includes("vuln") || rThreatSafe.includes("remote code execution") || rThreatSafe.includes("patch") || rThreatSafe.includes("exploit") || rThreatSafe.includes("cve") || rStatement.toLowerCase().includes("unpatched") || rStatement.toLowerCase().includes("vulnerability") || rStatement.toLowerCase().includes("remote code execution")) controls = "§164.308(a)(1)";
             else if (rThreatSafe.includes("vendor") || rThreatSafe.includes("third") || rThreatSafe.includes("supply") || rThreatSafe.includes("supplier") || rThreatSafe.includes("compliance gap") || rThreatSafe.includes("review pending") || rStatement.toLowerCase().includes("vendor") || rStatement.toLowerCase().includes("supply chain")) controls = "§164.308(b)(1)";
             else if (rThreatSafe.includes("shadow it") || rThreatSafe.includes("unmanaged") || rStatement.toLowerCase().includes("shadow it") || rStatement.toLowerCase().includes("unmanaged")) controls = "§164.312(a)(1)";
             else if (rThreatSafe.includes("policy gap") || rThreatSafe.includes("policy") || rStatement.toLowerCase().includes("policy") || rThreatSafe.includes("governance control gap") || rStatement.toLowerCase().includes("governance control gap")) controls = "§164.308(a)(1)";
             else if (rThreatSafe.includes("data exfiltration") || (rThreatSafe.includes("data") && (rThreatSafe.includes("loss") || rThreatSafe.includes("leak") || rThreatSafe.includes("breach") || rThreatSafe.includes("exfil"))) || rStatement.toLowerCase().includes("data exfiltration")) controls = "§164.312(e)";
             else if (rThreatSafe.includes("access") || rThreatSafe.includes("auth") || rThreatSafe.includes("credential") || rStatement.toLowerCase().includes("access")) controls = "§164.312(a)(1); §164.312(d)";
             else if (rThreatSafe.includes("phish") || rThreatSafe.includes("social") || rThreatSafe.includes("train")) controls = "§164.308(a)(5)";
             else if (rThreatSafe.includes("malware") || rThreatSafe.includes("ransomware") || rThreatSafe.includes("virus")) controls = "§164.308(a)(6)";
             else if (rThreatSafe.includes("network") || rThreatSafe.includes("firewall") || rThreatSafe.includes("ddos") || rThreatSafe.includes("attack")) controls = "§164.312(e)";
             else if (rThreatSafe.includes("physical") || rThreatSafe.includes("theft") || rThreatSafe.includes("unauthorized entry")) controls = "§164.310(a)(1)";
             else if (rThreatSafe.includes("backup") || rThreatSafe.includes("disaster") || rThreatSafe.includes("recover") || rThreatSafe.includes("business continuity") || rStatement.toLowerCase().includes("business continuity")) controls = "§164.308(a)(7)";
             else if (controls.includes("A.")) {
                controls = controls.replace(/A\.8\.3/g, "§164.312(a)(1)")
                                   .replace(/A\.8\.12/g, "§164.312(e)")
                                   .replace(/A\.8\.28/g, "§164.312(c)")
                                   .replace(/A\.8\.7/g, "§164.308(a)(6)")
                                   .replace(/A\.8\.9/g, "§164.312(c); §164.308(a)(1)")
                                   .replace(/A\.8\.20/g, "§164.312(e)")
                                   .replace(/A\.5\.19/g, "§164.308(b)(1)")
                                   .replace(/A\.5\.20/g, "§164.308(b)(1)")
                                   .replace(/A\.5\.1/g, "§164.308(a)(1)")
                                   .replace(/A\.5\.30/g, "§164.308(a)(7)")
                                   .replace(/A\.\d+\.\d+/g, "§164.308(a)(1)");
                
                controls = Array.from(new Set(controls.split("; ").map(s=>s.trim()))).join("; ");
             }
             if (!controls || controls === "—") controls = "§164.308(a)(1)";
          }

          let rationale = "";
          if (rThreatSafe.includes("sql injection") || rStatement.toLowerCase().includes("sql injection")) rationale = "Secure coding/input validation prevents injection attacks.";
          else if (rThreatSafe.includes("api abuse") || rThreatSafe.includes("api") || rStatement.toLowerCase().includes("api")) rationale = "API security and secure coding reduce endpoint abuse.";
          else if (rThreatSafe.includes("unpatched") || rThreatSafe.includes("vuln") || rThreatSafe.includes("remote code execution") || rThreatSafe.includes("patch") || rThreatSafe.includes("exploit") || rThreatSafe.includes("cve") || rStatement.toLowerCase().includes("unpatched") || rStatement.toLowerCase().includes("vulnerability") || rStatement.toLowerCase().includes("remote code execution")) rationale = "Vulnerability management reduces exposure to known exploits through timely remediation.";
          else if (rThreatSafe.includes("default") || rThreatSafe.includes("misconfiguration") || rStatement.toLowerCase().includes("misconfiguration")) rationale = "Configuration management reduces insecure settings and prevents misuse of default accounts.";
          else if (rThreatSafe.includes("shadow it") || rThreatSafe.includes("unmanaged") || rStatement.toLowerCase().includes("shadow it") || rStatement.toLowerCase().includes("unmanaged")) rationale = "Asset inventory controls reduce unmanaged systems and improve visibility over the attack surface.";
          else if (rThreatSafe.includes("policy gap") || rThreatSafe.includes("policy") || rStatement.toLowerCase().includes("policy")) rationale = "Security policies define ownership, requirements, and governance for managing this risk.";
          else if (rThreatSafe.includes("broken access control") || rThreatSafe.includes("access") || rStatement.toLowerCase().includes("access")) rationale = "RBAC and access reviews reduce unauthorized access.";
          else if (rThreatSafe.includes("supply chain") || rThreatSafe.includes("vendor") || rThreatSafe.includes("supplier") || rThreatSafe.includes("third-party") || rThreatSafe.includes("compliance gap") || rThreatSafe.includes("review pending") || rStatement.toLowerCase().includes("supply chain") || rStatement.toLowerCase().includes("vendor")) rationale = "Supplier security controls ensure third parties meet required security and compliance obligations.";
          else if (rThreatSafe.includes("data exfiltration") || rThreatSafe.includes("leak") || rThreatSafe.includes("loss") || rStatement.toLowerCase().includes("data exfiltration")) rationale = "DLP and monitoring reduce leakage risk.";
          else if (rThreatSafe.includes("business continuity") || rThreatSafe.includes("disaster") || rThreatSafe.includes("backup") || rThreatSafe.includes("outage") || rStatement.toLowerCase().includes("business continuity")) rationale = "DR and backup controls reduce outage impact.";
          else rationale = "Relevant controls reduce likelihood or impact of this risk.";

          highRiskRows.push({
            risk_id: id,
            risk_statement: rStatement,
            controls: controls,
            rationale: rationale,
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
                        <th>{ad.framework_id === "hipaa" || String(ad.framework).toLowerCase() === "hipaa" ? "HIPAA Security Rule" : "Annex A:2022 Control(s)"}</th>
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
                {/* Risk Register Table & Metrics */}
                {(() => {
                  const entries = [
                    ...(ad.risk_register.generated_risk_entries || []),
                    ...(ad.risk_register.uploaded_risk_entries || []),
                  ];

                  if (entries.length === 0) return null;

                  let highCriticalCount = 0;
                  let untreatedCount = 0;

                  entries.forEach((risk) => {
                    let rawL = parseFloat(risk.likelihood);
                    let rawI = parseFloat(risk.impact);

                    if (isNaN(rawL) || isNaN(rawI)) {
                      const level = (risk.risk_level || risk.level || "Medium").toLowerCase();
                      if (level === "low") { rawL = 2; rawI = 2; }
                      else if (level === "high") { rawL = 4; rawI = 3; }
                      else if (level === "critical" || level === "extreme") { rawL = 5; rawI = 5; }
                      else { rawL = 3; rawI = 3; }
                    }

                    const lScore = Math.max(1, Math.min(5, Math.round(rawL)));
                    const iScore = Math.max(1, Math.min(5, Math.round(rawI)));
                    
                    if (lScore * iScore >= 12) {
                      highCriticalCount++;
                    }

                    let rControl = "—";
                    if (risk.iso_controls && risk.iso_controls.length > 0) {
                      rControl = risk.iso_controls.join(", ");
                    } else if (risk.rule_id) {
                      rControl = risk.rule_id;
                    } else if (risk.controls) {
                      rControl = risk.controls;
                    } else if (ad.framework) {
                      rControl = `Mapped via ${ad.framework}`;
                    }

                    if (!rControl || rControl === "—" || rControl.toLowerCase() === "pending mitigation") {
                      untreatedCount++;
                    }
                  });

                  const getScoreColorBg = (val) => {
                    if (val === 1) return "#14532d";
                    if (val === 2) return "#166534";
                    if (val === 3) return "#854d0e";
                    if (val === 4) return "#9a3412";
                    return "#7f1d1d";
                  };
                  const getScoreColorText = (val) => {
                    return "#ffffff";
                  };

                  const getRiskLevelScore = (likelihood, impact) => likelihood * impact;

                  const getRiskLevelLabelAndColor = (score) => {
                    if (score <= 5) return { label: "Low", bg: "#166534", text: "#ffffff" };
                    if (score <= 10) return { label: "Medium", bg: "#854d0e", text: "#ffffff" };
                    if (score <= 15) return { label: "High", bg: "#9a3412", text: "#ffffff" };
                    return { label: "Extreme", bg: "#7f1d1d", text: "#ffffff" };
                  };

                  const inferOwner = (assetType) => {
                    if (!assetType) return "IT Team";
                    const t = assetType.toLowerCase();
                    if (t.includes("server") || t.includes("infrastructure") || t.includes("host")) return "IT Team";
                    if (t.includes("auth") || t.includes("identity") || t.includes("access") || t.includes("iam")) return "IT Security";
                    if (t.includes("db") || t.includes("database") || t.includes("storage")) return "DBA";
                    if (t.includes("network") || t.includes("firewall") || t.includes("router")) return "DevOps";
                    if (t.includes("vendor") || t.includes("third-party") || t.includes("supplier")) return "IT Security";
                    return "IT Team";
                  };

                  return (
                    <>
                      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", gap: "1.25rem", marginBottom: "1.5rem" }}>
                        {[
                          { label: "Total Risks", value: entries.length, color: "var(--primary)" },
                          { label: "High / Critical", value: highCriticalCount, color: "#EF4444" },
                          { label: "Untreated", value: untreatedCount, color: "#7C3AED" },
                        ].map((m) => (
                          <div key={m.label} className="card" style={{ padding: "1.25rem", borderLeft: `4px solid ${m.color}` }}>
                            <div style={{ fontSize: "0.72rem", color: "var(--text-muted)", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: "0.4rem" }}>{m.label}</div>
                            <div style={{ fontSize: "1.75rem", fontWeight: 800, color: m.color, lineHeight: "1" }}>{m.value}</div>
                          </div>
                        ))}
                      </div>

                      <div className="w-full rounded-xl overflow-hidden border border-slate-200 bg-white dark:bg-slate-950 dark:border-slate-800">
                      <div className="table-container" style={{ margin: 0, borderRadius: 0, border: "none", width: "100%" }}>
                        <table style={{ margin: 0, width: "100%", tableLayout: "fixed", borderCollapse: "collapse" }}>
                          <thead style={{ position: "sticky", top: 0, zIndex: 10 }}>
                            <tr className="bg-slate-100 text-slate-900 dark:bg-slate-900 dark:text-white">
                              <th className="px-4 py-3 text-sm font-semibold border-b border-slate-200 dark:border-slate-800" style={{ textAlign: "left", wordBreak: "break-word", whiteSpace: "normal" }}>Risk ID</th>
                              <th className="px-4 py-3 text-sm font-semibold border-b border-slate-200 dark:border-slate-800" style={{ textAlign: "left", maxWidth: "250px", wordBreak: "break-word", whiteSpace: "normal" }}>Risk Statement</th>
                              <th className="px-4 py-3 text-sm font-semibold border-b border-slate-200 dark:border-slate-800" style={{ textAlign: "left", wordBreak: "break-word", whiteSpace: "normal" }}>Asset</th>
                              <th className="px-4 py-3 text-sm font-semibold border-b border-slate-200 dark:border-slate-800" style={{ textAlign: "left", wordBreak: "break-word", whiteSpace: "normal" }}>Threat</th>
                              <th className="px-4 py-3 text-sm font-semibold border-b border-slate-200 dark:border-slate-800" style={{ textAlign: "center", wordBreak: "break-word", whiteSpace: "normal" }}>Likelihood</th>
                              <th className="px-4 py-3 text-sm font-semibold border-b border-slate-200 dark:border-slate-800" style={{ textAlign: "center", wordBreak: "break-word", whiteSpace: "normal" }}>Impact</th>
                              <th className="px-4 py-3 text-sm font-semibold border-b border-slate-200 dark:border-slate-800" style={{ textAlign: "center", wordBreak: "break-word", whiteSpace: "normal" }}>Risk Level</th>
                              <th className="px-4 py-3 text-sm font-semibold border-b border-slate-200 dark:border-slate-800" style={{ textAlign: "left", maxWidth: "300px", wordBreak: "break-word", whiteSpace: "normal" }}>Control</th>
                              <th className="px-4 py-3 text-sm font-semibold border-b border-slate-200 dark:border-slate-800" style={{ textAlign: "left", wordBreak: "break-word", whiteSpace: "normal" }}>Owner</th>
                            </tr>
                          </thead>
                          <tbody>
                            {entries.map((risk, idx) => {
                              const rId = risk.risk_id || risk.id || `R${idx + 1}`;
                              const rStatement = risk.risk_statement || risk.description || risk.title || risk.name || risk.risk_name || "—";
                              const rAsset = risk.asset || risk.asset_type || "System";
                              const rThreat = risk.threat || risk.vulnerability || risk.rule_id || "Unspecified Threat";
                              
                              let rawL = parseFloat(risk.likelihood);
                              let rawI = parseFloat(risk.impact);

                              if (isNaN(rawL) || isNaN(rawI)) {
                                const level = (risk.risk_level || risk.level || "Medium").toLowerCase();
                                if (level === "low") { rawL = 2; rawI = 2; }
                                else if (level === "high") { rawL = 4; rawI = 3; }
                                else if (level === "critical" || level === "extreme") { rawL = 5; rawI = 5; }
                                else { rawL = 3; rawI = 3; }
                              }

                              const lScore = Math.max(1, Math.min(5, Math.round(rawL)));
                              const iScore = Math.max(1, Math.min(5, Math.round(rawI)));
                              const riskScore = getRiskLevelScore(lScore, iScore);
                              const riskLevelMeta = getRiskLevelLabelAndColor(riskScore);
                              
                              let rControl = "—";
                              if (risk.iso_controls && risk.iso_controls.length > 0) {
                                rControl = risk.iso_controls.join(", ");
                              } else if (risk.rule_id) {
                                rControl = risk.rule_id;
                              } else if (risk.controls) {
                                rControl = risk.controls;
                              } else if (ad.framework) {
                                rControl = `Mapped via ${ad.framework}`;
                              }
                              
                              const rOwner = risk.owner || inferOwner(rAsset);

                              return (
                                <tr key={`${rId || risk.id || "risk"}-${idx}`} className="bg-white text-slate-800 border-slate-200 hover:bg-slate-50 dark:bg-slate-950 dark:text-slate-100 dark:border-slate-800 dark:hover:bg-slate-900">
                                  <td className="px-4 py-3 text-sm border-slate-200 dark:border-slate-800" style={{ fontWeight: 600, wordBreak: "break-word", whiteSpace: "normal" }}>{rId}</td>
                                  <td className="px-4 py-3 text-sm border-slate-200 dark:border-slate-800" style={{ maxWidth: "250px", wordBreak: "break-word", whiteSpace: "normal" }}>{rStatement}</td>
                                  <td className="px-4 py-3 text-sm border-slate-200 dark:border-slate-800" style={{ wordBreak: "break-word", whiteSpace: "normal" }}>{rAsset}</td>
                                  <td className="px-4 py-3 text-sm border-slate-200 dark:border-slate-800" style={{ wordBreak: "break-word", whiteSpace: "normal" }}>{rThreat}</td>
                                  
                                  <td className="px-4 py-3 text-sm border-slate-200 dark:border-slate-800" style={{ textAlign: "center", wordBreak: "break-word", whiteSpace: "normal" }}>
                                    <span style={{ display: "inline-block", padding: "4px 10px", borderRadius: "4px", fontSize: "0.85rem", fontWeight: 700, background: getScoreColorBg(lScore), color: getScoreColorText(lScore) }}>
                                      {lScore}
                                    </span>
                                  </td>
                                  <td className="px-4 py-3 text-sm border-slate-200 dark:border-slate-800" style={{ textAlign: "center", wordBreak: "break-word", whiteSpace: "normal" }}>
                                    <span style={{ display: "inline-block", padding: "4px 10px", borderRadius: "4px", fontSize: "0.85rem", fontWeight: 700, background: getScoreColorBg(iScore), color: getScoreColorText(iScore) }}>
                                      {iScore}
                                    </span>
                                  </td>
                                  
                                  <td className="px-4 py-3 text-sm border-slate-200 dark:border-slate-800" style={{ textAlign: "center", wordBreak: "break-word", whiteSpace: "normal" }}>
                                    <span style={{ display: "inline-flex", alignItems: "center", justifyContent: "center", width: "100%", padding: "6px 12px", borderRadius: "6px", fontSize: "0.85rem", fontWeight: 700, background: riskLevelMeta.bg, color: riskLevelMeta.text, border: `1px solid ${riskLevelMeta.bg}` }}>
                                      {riskScore} {riskLevelMeta.label}
                                    </span>
                                  </td>
                                  
                                  <td className="px-4 py-3 text-sm border-slate-200 dark:border-slate-800" style={{ fontWeight: 500, maxWidth: "300px", wordBreak: "break-word", whiteSpace: "normal" }}>{rControl}</td>
                                  <td className="px-4 py-3 text-sm border-slate-200 dark:border-slate-800" style={{ wordBreak: "break-word", whiteSpace: "normal" }}>{rOwner}</td>
                                </tr>
                              );
                            })}
                          </tbody>
                        </table>
                      </div>
                      </div>
                    </>
                  );
                })()}
              </>
            ) : (
              <div className="card" style={{ padding: "2rem", textAlign: "center" }}><p style={{ color: "var(--text-muted)", fontSize: "0.95rem", margin: 0 }}>No risk register data found.</p></div>
            )}
          </div>
        )}
        
        {/* TREATMENT PLAN TAB */}
        {activeTab === "treatment_plan" && (() => {
          /* ---- Framework-specific treatment mappings ---- */
          const TREATMENT_MAP_ISO27001 = {
            application_security: "Mitigate: Implement parameterized queries, secure coding reviews, WAF protection, and regular DAST/SAST testing aligned with ISO 27001 application security controls.",
            vulnerability_management: "Mitigate: Implement automated patch management, monthly vulnerability scanning, emergency patch SLAs for critical CVEs, and documented remediation tracking.",
            identity_access: "Mitigate: Enforce MFA, strong password policy, privileged access reviews, and conditional access controls.",
            encryption: "Mitigate: Enforce TLS, certificate lifecycle management, encryption at rest, key rotation, and cryptographic policy reviews.",
            vendor_risk: "Mitigate: Perform vendor security assessments, review DPAs/SLAs, require security evidence, and monitor supplier compliance.",
            default: "Mitigate: Apply relevant ISO 27001 controls, assign ownership, define remediation steps, and track closure evidence.",
          };
          const TREATMENT_MAP_HIPAA = {
            identity_access: "Mitigate: Enforce unique user identification, MFA, role-based access, and periodic access reviews for systems handling ePHI.",
            audit_logging: "Mitigate: Enable audit controls, log access to ePHI, monitor suspicious activity, and retain logs according to policy.",
            encryption: "Mitigate: Protect ePHI using encryption in transit and at rest, enforce secure transmission controls, and review key management.",
            resilience: "Mitigate: Maintain backup procedures, disaster recovery plans, emergency mode operations, and periodic restoration testing.",
            vendor_risk: "Mitigate: Review Business Associate Agreements, validate security responsibilities, and monitor third-party handling of ePHI.",
            default: "Mitigate: Apply relevant HIPAA Security Rule safeguards, assign responsibility, document remediation, and verify protection of ePHI.",
          };
          const TREATMENT_MAP_PCI_DSS = {
            application_security: "Mitigate: Remediate injection weaknesses using secure coding, parameterized queries, code review, WAF rules, and PCI DSS application security testing.",
            vulnerability_management: "Mitigate: Apply security patches, maintain vulnerability scans, remediate critical findings within SLA, and document evidence.",
            identity_access: "Mitigate: Enforce MFA for administrative and cardholder data access, strong authentication, least privilege, and access reviews.",
            network_security: "Mitigate: Review firewall rules, segment the cardholder data environment, restrict inbound/outbound traffic, and validate rule ownership.",
            encryption: "Mitigate: Encrypt cardholder data in transit and at rest, manage keys securely, and validate cryptographic controls.",
            default: "Mitigate: Apply relevant PCI DSS requirements, define remediation ownership, collect evidence, and validate closure.",
          };

          /* ---- Detect framework ---- */
          const normaliseFramework = (raw) => {
            if (!raw) return "iso27001";
            const f = raw.toLowerCase().replace(/[^a-z0-9]/g, "");
            if (f.includes("hipaa")) return "hipaa";
            if (f.includes("pci")) return "pci_dss";
            return "iso27001";
          };
          const fwKey = normaliseFramework(ad.framework);
          const treatmentMap = fwKey === "hipaa" ? TREATMENT_MAP_HIPAA
            : fwKey === "pci_dss" ? TREATMENT_MAP_PCI_DSS
            : TREATMENT_MAP_ISO27001;

          /* ---- Risk category detection ---- */
          const CATEGORY_KEYWORDS = {
            application_security: ["sql", "injection", "input validation", "xss", "cross-site", "secure coding", "sast", "dast"],
            vulnerability_management: ["patch", "vulnerability", "cve", "unpatched", "exploit", "remote code execution", "outdated"],
            identity_access: ["mfa", "password", "authentication", "access", "credential", "privilege", "identity", "iam", "auth"],
            encryption: ["encryption", "tls", "certificate", "crypto", "ssl", "key management", "cipher", "cryptographic"],
            vendor_risk: ["vendor", "supplier", "third party", "third-party", "dpa", "baa", "supply chain", "service provider"],
            network_security: ["firewall", "network", "segmentation", "dmz", "ids", "ips", "router", "traffic", "perimeter"],
            audit_logging: ["audit", "logging", "log", "monitor", "siem", "detection", "event", "alerting"],
            resilience: ["backup", "recovery", "availability", "disaster", "continuity", "restoration", "failover"],
          };
          const detectCategory = (risk) => {
            const text = [
              risk.risk_statement, risk.description, risk.title,
              risk.threat, risk.vulnerability, risk.asset,
              risk.asset_type, risk.control, risk.rule_id,
              risk.name, risk.risk_name,
            ].filter(Boolean).join(" ").toLowerCase();
            for (const [cat, keywords] of Object.entries(CATEGORY_KEYWORDS)) {
              for (const kw of keywords) {
                if (text.includes(kw)) return cat;
              }
            }
            return "default";
          };

          /* ---- Risk score & due date ---- */
          const computeScore = (risk) => {
            let rawL = parseFloat(risk.likelihood);
            let rawI = parseFloat(risk.impact);
            if (!isNaN(rawL) && !isNaN(rawI) && rawL > 0 && rawI > 0) {
              return Math.max(1, Math.min(5, Math.round(rawL))) * Math.max(1, Math.min(5, Math.round(rawI)));
            }
            const level = (risk.risk_level || risk.level || "medium").toLowerCase();
            if (level === "critical" || level === "extreme") return 25;
            if (level === "high") return 12;
            if (level === "low") return 4;
            return 9;
          };
          const calcDueDate = (score) => {
            const now = new Date();
            let days = 90;
            if (score >= 15) days = 30;
            else if (score >= 8) days = 60;
            const due = new Date(now.getTime() + days * 86400000);
            const dd = String(due.getDate()).padStart(2, "0");
            const mm = String(due.getMonth() + 1).padStart(2, "0");
            const yyyy = due.getFullYear();
            return `${dd}/${mm}/${yyyy}`;
          };

          /* ---- Build treatment rows: prefer backend, fallback to client ---- */
          let treatmentRows = [];

          // Prefer backend-generated risk_treatment_plan
          const backendPlan = ad.risk_treatment_plan;
          if (backendPlan && Array.isArray(backendPlan) && backendPlan.length > 0) {
            treatmentRows = backendPlan.map((row) => ({
              risk_id: String(row.risk_id || "—"),
              treatment: row.treatment || "—",
              due_date: (row.due_date || "").includes("/")
                ? row.due_date
                : (() => { // Convert YYYY-MM-DD → DD/MM/YYYY
                    const p = (row.due_date || "").split("-");
                    return p.length === 3 ? `${p[2]}/${p[1]}/${p[0]}` : row.due_date || "—";
                  })(),
            }));
          } else {
            // Fallback: generate client-side from risk register
            const entries = ad.risk_register ? [
              ...(ad.risk_register.generated_risk_entries || []),
              ...(ad.risk_register.uploaded_risk_entries || []),
            ] : [];

            treatmentRows = entries.map((risk, idx) => {
              const riskId = String(risk.risk_id || risk.id || `R${idx + 1}`);
              const category = detectCategory(risk);
              const treatment = treatmentMap[category] || treatmentMap.default;
              const score = computeScore(risk);
              const dueDate = calcDueDate(score);
              return { risk_id: riskId, treatment, due_date: dueDate };
            });
          }

          /* ---- Due date badge color ---- */
          const getDueBadge = (dueDateStr) => {
            const parts = dueDateStr.split("/");
            const dueMs = new Date(`${parts[2]}-${parts[1]}-${parts[0]}`).getTime();
            const nowMs = Date.now();
            const daysLeft = Math.round((dueMs - nowMs) / 86400000);
            if (daysLeft <= 30) return { bg: "#7f1d1d", text: "#ffffff" };
            if (daysLeft <= 60) return { bg: "#854d0e", text: "#ffffff" };
            return { bg: "#166534", text: "#ffffff" };
          };

          return (
            <div style={{ animation: "fadeIn 0.3s ease" }}>
              <h3 style={{ fontSize: "1.5rem", fontWeight: 800, color: "var(--text-main)", marginBottom: "0.25rem" }}>Treatment Plan</h3>
              <p style={{ color: "var(--text-muted)", fontSize: "0.95rem", marginBottom: "1.5rem" }}>
                One treatment action per risk, mapped to {ad.framework || "the selected framework"}.
              </p>

              {treatmentRows.length > 0 ? (
                <div className="w-full rounded-xl overflow-hidden border border-slate-200 bg-white dark:bg-slate-950 dark:border-slate-800">
                  <div className="table-container" style={{ margin: 0, borderRadius: 0, border: "none", width: "100%" }}>
                    <table style={{ margin: 0, width: "100%", tableLayout: "fixed", borderCollapse: "collapse" }}>
                      <thead style={{ position: "sticky", top: 0, zIndex: 10 }}>
                        <tr className="bg-slate-100 text-slate-900 dark:bg-slate-900 dark:text-white">
                          <th className="px-4 py-3 text-sm font-semibold border-b border-slate-200 dark:border-slate-800" style={{ textAlign: "left", width: "100px" }}>Risk ID</th>
                          <th className="px-4 py-3 text-sm font-semibold border-b border-slate-200 dark:border-slate-800" style={{ textAlign: "left" }}>Treatment</th>
                          <th className="px-4 py-3 text-sm font-semibold border-b border-slate-200 dark:border-slate-800" style={{ textAlign: "center", width: "130px" }}>Due Date</th>
                        </tr>
                      </thead>
                      <tbody>
                        {treatmentRows.map((row, i) => {
                          const badge = getDueBadge(row.due_date);
                          return (
                            <tr key={row.risk_id + "-" + i} className="bg-white text-slate-800 border-slate-200 hover:bg-slate-50 dark:bg-slate-950 dark:text-slate-100 dark:border-slate-800 dark:hover:bg-slate-900">
                              <td className="px-4 py-3 text-sm border-b border-slate-200 dark:border-slate-800" style={{ fontWeight: 600, wordBreak: "break-word", whiteSpace: "normal" }}>{row.risk_id}</td>
                              <td className="px-4 py-3 text-sm border-b border-slate-200 dark:border-slate-800" style={{ wordBreak: "break-word", whiteSpace: "normal", lineHeight: "1.5" }}>{row.treatment}</td>
                              <td className="px-4 py-3 text-sm border-b border-slate-200 dark:border-slate-800" style={{ textAlign: "center" }}>
                                <span style={{ display: "inline-block", padding: "4px 12px", borderRadius: "6px", fontSize: "0.85rem", fontWeight: 700, background: badge.bg, color: badge.text }}>
                                  {row.due_date}
                                </span>
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                  <div style={{ padding: "0.6rem 1rem", fontSize: "0.8rem", color: "var(--text-muted)", borderTop: "1px solid var(--border-color)" }}>
                    {treatmentRows.length} treatment action{treatmentRows.length !== 1 ? "s" : ""} generated for {ad.framework || "the selected framework"}
                  </div>
                </div>
              ) : (
                <div className="card" style={{ padding: "2rem", textAlign: "center" }}>
                  <p style={{ color: "var(--text-muted)", fontSize: "0.95rem", margin: 0 }}>No risks found in the Risk Register. Upload an assessment to generate treatment actions.</p>
                </div>
              )}
            </div>
          );
        })()}

        {/* SOA TAB */}
        {activeTab === "soa" && (() => {
          let soaRows = [];
          const isHipaa = ad.framework && ad.framework.toLowerCase() === "hipaa";
          
          if (isHipaa && ad.soa && ad.soa.entries && ad.soa.entries.length > 0) {
            soaRows = ad.soa.entries.map((entry, idx) => ({
              id: idx + 1,
              section: entry.section || "—",
              control_no: (() => {
                const raw = entry.control_no || "";
                const m = raw.match(/[Aa](\d+\.\d+)/);
                return m ? `A.${m[1]}` : (raw || "—");
              })(),
              control_title: entry.control_title || "—",
              applicable: entry.applicable || "Yes",
              remarks: entry.remarks || "N/A",
              implemented: entry.implementation || "Not Implemented",
              reference: entry.reference || "—",
              status: entry.status || "missing",
            }));
          } else {
            // Build SOA rows from the existing evaluated controls in ad.sections
            // NO scoring/logic changes — display-only mapping
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
          }

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
          const matrixRows = Array.isArray(ad.compliance_matrix) 
            ? ad.compliance_matrix 
            : (ad.compliance_matrix?.entries || []);

          return (
            <div style={{ animation: "fadeIn 0.3s ease", width: "100%", maxWidth: "1600px", margin: "0 auto" }}>
              <h3 style={{ fontSize: "1.5rem", fontWeight: 800, color: "var(--text-main)", marginBottom: "1rem" }}>Compliance Matrix</h3>
              {matrixRows.length > 0 ? (
                <div className="card" style={{ padding: 0, overflow: "hidden", maxWidth: "100%" }}>
                  <div className="table-container" style={{ margin: 0, borderRadius: 0, border: "none", width: "100%" }}>
                    <table className="modern-table" style={{ margin: 0, width: "100%", tableLayout: "auto" }}>
                      <thead>
                        <tr>
                          <th style={{ width: "10%" }}>Framework</th>
                          <th style={{ width: "15%" }}>Requirement</th>
                          <th style={{ width: "20%" }}>Mapped Controls</th>
                          <th style={{ width: "30%" }}>Gaps Identified</th>
                          <th style={{ width: "25%" }}>Remediation Plan</th>
                        </tr>
                      </thead>
                      <tbody>
                        {matrixRows.map((row, idx) => {
                          const status = row.Status || "Unknown";
                          const statusLower = status.toLowerCase();
                          
                          let statusBg = "#16a34a22";
                          let statusColor = "#16a34a";
                          if (statusLower === "partial") { statusBg = "#d9770622"; statusColor = "#d97706"; }
                          else if (statusLower === "missing") { statusBg = "#dc262622"; statusColor = "#dc2626"; }

                          const mappedControlsLines = (row["Mapped Controls"] || "—").split("\n").filter(Boolean);
                          const remLines = (row["Remediation Plan"] || "").split(/(?<=\.)\s+/).filter(Boolean);

                          return (
                            <tr key={`cm-${idx}`} style={{ borderBottom: "1px solid #e5e7eb", background: "transparent" }}>
                              <td style={{ fontWeight: 500, color: "var(--text-muted)", whiteSpace: "normal", wordWrap: "break-word", padding: "20px 14px", verticalAlign: "top", lineHeight: 1.6 }}>
                                <div style={{ marginBottom: "8px" }}>{row.Framework}</div>
                                <span style={{ 
                                  background: statusBg, 
                                  color: statusColor, 
                                  padding: "4px 8px", borderRadius: "4px", fontSize: "11px", fontWeight: "700", textTransform: "uppercase", display: "inline-block" 
                                }}>
                                  {status}
                                </span>
                              </td>
                              <td style={{ fontWeight: 600, color: "var(--text-main)", fontSize: "0.9rem", whiteSpace: "normal", wordWrap: "break-word", padding: "20px 14px", verticalAlign: "top", lineHeight: 1.6 }}>
                                {row.Requirement}
                              </td>
                              <td style={{ whiteSpace: "normal", wordWrap: "break-word", padding: "20px 14px", verticalAlign: "top" }}>
                                {mappedControlsLines.length > 0 ? mappedControlsLines.map((line, i) => {
                                  if (line.startsWith("COMPLIANT:")) {
                                    const value = line.replace("COMPLIANT:", "").trim();
                                    return (
                                      <div key={i} style={{ marginBottom: value ? "12px" : "4px" }}>
                                        <div style={{ fontSize: "0.7rem", fontWeight: "700", color: "#16a34a", marginBottom: value ? "4px" : "0", letterSpacing: "0.5px" }}>COMPLIANT:</div>
                                        {value && <div style={{ color: "#374151", fontSize: "0.8rem", background: "#f3f4f6", border: "1px solid #e5e7eb", padding: "4px 8px", borderRadius: "4px", display: "inline-block", fontWeight: 500 }}>{value}</div>}
                                      </div>
                                    );
                                  } else if (line.startsWith("PARTIAL:")) {
                                    const value = line.replace("PARTIAL:", "").trim();
                                    return (
                                      <div key={i} style={{ marginBottom: value ? "12px" : "4px" }}>
                                        <div style={{ fontSize: "0.7rem", fontWeight: "700", color: "#d97706", marginBottom: value ? "4px" : "0", letterSpacing: "0.5px" }}>PARTIAL:</div>
                                        {value && <div style={{ color: "#374151", fontSize: "0.8rem", background: "#f3f4f6", border: "1px solid #e5e7eb", padding: "4px 8px", borderRadius: "4px", display: "inline-block", fontWeight: 500 }}>{value}</div>}
                                      </div>
                                    );
                                  } else if (line.startsWith("MISSING:")) {
                                    const value = line.replace("MISSING:", "").trim();
                                    return (
                                      <div key={i} style={{ marginBottom: value ? "12px" : "4px" }}>
                                        <div style={{ fontSize: "0.7rem", fontWeight: "700", color: "#dc2626", marginBottom: value ? "4px" : "0", letterSpacing: "0.5px" }}>MISSING:</div>
                                        {value && <div style={{ color: "#374151", fontSize: "0.8rem", background: "#f3f4f6", border: "1px solid #e5e7eb", padding: "4px 8px", borderRadius: "4px", display: "inline-block", fontWeight: 500 }}>{value}</div>}
                                      </div>
                                    );
                                  }
                                  return <div key={i} style={{ color: "var(--text-main)", fontSize: "0.85rem" }}>{line}</div>;
                                }) : <span style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>—</span>}
                              </td>
                              <td style={{ fontSize: "0.85rem", color: "var(--text-main)", whiteSpace: "normal", wordWrap: "break-word", padding: "20px 14px", verticalAlign: "top", lineHeight: 1.6 }}>
                                {row["Gaps Identified"] ? row["Gaps Identified"].split(" • ").map((gap, gIdx) => (
                                  <div key={gIdx} style={{ marginBottom: "6px" }}>• {gap}</div>
                                )) : "—"}
                              </td>
                              <td style={{ fontSize: "0.85rem", color: "var(--text-main)", whiteSpace: "normal", wordWrap: "break-word", padding: "20px 14px", verticalAlign: "top", lineHeight: 1.6 }}>
                                <ul style={{ margin: 0, paddingLeft: "1.2rem", listStyleType: "disc" }}>
                                  {remLines.map((rLine, rIdx) => (
                                    <li key={rIdx} style={{ marginBottom: "8px" }}>{rLine}</li>
                                  ))}
                                </ul>
                              </td>
                            </tr>
                          );
                        })}
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
                        const agreement  = vendor.agreement || vendor.agreement_signed || vendor.baa_status || vendor.baa_signed || "—";
                        const encryption = vendor.encryption || vendor.encryption_status || vendor.encryption_at_rest_transit || "—";
                        const sla        = vendor.sla || vendor.security_sla || vendor.breach_uptime_sla || "—";
                        const monitoring = vendor.monitoring || vendor.monitoring_frequency || "—";
                        const riskLevel  = vendor.risk_level || vendor.riskLevel || "Unknown";
                        const certs      = vendor.certifications || vendor.compliance_status || vendor.certifications_compliance || "—";

                        return (
                          <tr key={i}>
                            <td>
                              <div style={{ fontWeight: 600, color: "var(--text-main)" }}>{vendor.vendor_name}</div>
                              <div style={{ fontSize: "0.8rem", color: "var(--text-muted)", marginTop: "0.2rem" }}>{vendor.service_provided}</div>
                            </td>
                            <td><span className={getBadgeClass(certs)}>{certs}</span></td>
                            <td style={{ color: agreement === "Signed" ? "#16a34a" : agreement === "Under Review" ? "#d97706" : "#dc2626", fontWeight: 500 }}>{agreement}</td>
                            <td style={{ color: encryption.includes("AES") || encryption.includes("TLS 1.3") ? "var(--text-main)" : encryption.includes("Weak") || encryption.includes("Unknown") ? "#dc2626" : "#d97706" }}>{encryption}</td>
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
        {activeTab === "training" && (() => {
          /* ── Prefer backend-generated data, fallback to client-side ──── */
          const backendData = ad.training_matrix_generated;
          const hasBackend = backendData && backendData.role_based_matrix && backendData.role_based_matrix.length > 0;

          /* ── Role-Based Matrix ── */
          let roleBasedMatrix;
          if (hasBackend) {
            roleBasedMatrix = backendData.role_based_matrix;
          } else {
            // Client-side fallback
            const defaultRoleBasedMatrix = [
              { role: "All Employees", content: "Security Awareness, Phishing & Data Privacy", frequency: "Annually", driver: "Social Engineering, Data Handling" },
              { role: "IT & Operations", content: "Privileged Access, Incident Response, Cloud Security", frequency: "Bi-Annually", driver: "Privilege Escalation, Infrastructure Misconfigurations" },
              { role: "Developers / Engineering", content: "Secure Coding, OWASP Top 10, API Security", frequency: "Annually", driver: "Application Vulnerabilities, Injection Attacks" },
              { role: "HR & Finance", content: "BEC Prevention, Privacy (GDPR/HIPAA), Fraud Detection", frequency: "Annually", driver: "Business Email Compromise, Data Leakage" },
              { role: "Executive Management", content: "Cyber Crisis Management, Executive Briefing", frequency: "Annually", driver: "Ransomware, Targeted Whaling Attacks" }
            ];

            const fallbackEmployees = ad.training_matrix || [];
            if (fallbackEmployees.length > 0) {
              const rolesSet = new Set(fallbackEmployees.map(r => r.role).filter(Boolean));
              const uniqueRoles = Array.from(rolesSet);
              const risks = ad.risk_register ? [
                ...(ad.risk_register.generated_risk_entries || []),
                ...(ad.risk_register.uploaded_risk_entries || [])
              ] : [];
              const riskText = risks.map(r => [r.threat, r.risk_statement, r.description].filter(Boolean).join(" ").toLowerCase()).join(" ");

              roleBasedMatrix = uniqueRoles.map(role => {
                const r = role.toLowerCase();
                let content = "Security Awareness & General Data Privacy";
                let frequency = "Annually";
                let driver = "General Security Posture, Data Handling";
                if (r.includes("it") || r.includes("admin") || r.includes("ops")) {
                  content = "Privileged Access, Incident Response, Cloud Security"; frequency = "Bi-Annually";
                  driver = "Privilege Escalation, System Misconfigurations";
                  if (riskText.includes("ransomware") || riskText.includes("malware")) driver += ", Ransomware Threats";
                } else if (r.includes("dev") || r.includes("eng")) {
                  content = "Secure Coding, OWASP Top 10, API Security";
                  driver = "Application Vulnerabilities, Injection Attacks";
                  if (riskText.includes("sql") || riskText.includes("xss") || riskText.includes("api")) driver += ", API Abuse, Web Exploits";
                } else if (r.includes("hr") || r.includes("fin") || r.includes("account") || r.includes("legal")) {
                  content = "BEC Prevention, Data Privacy, Fraud Detection";
                  driver = "Business Email Compromise, Data Leakage";
                  if (riskText.includes("phish") || riskText.includes("social")) driver += ", Social Engineering";
                } else if (r.includes("exec") || r.includes("dir") || r.includes("vp") || r.includes("chief") || r.includes("c-suite")) {
                  content = "Cyber Crisis Management, Executive Briefing";
                  driver = "Targeted Whaling Attacks, Reputational Risk";
                } else {
                  if (riskText.includes("phish") || riskText.includes("social")) driver += ", Social Engineering";
                  if (riskText.includes("loss") || riskText.includes("leak") || riskText.includes("data exfiltration")) driver += ", Data Leakage";
                }
                return { role, content, frequency, driver };
              });
              if (roleBasedMatrix.length === 0) roleBasedMatrix = defaultRoleBasedMatrix;
            } else {
              roleBasedMatrix = defaultRoleBasedMatrix;
            }
          }

          /* ── Employee Tracker: backend first, then raw training_matrix ── */
          const backendTraining = ad.training_matrix_generated || {};
          const trackerData = backendTraining.employee_tracker || backendTraining.employee_training_tracker || [];

          return (
            <div style={{ animation: "fadeIn 0.3s ease", display: "flex", flexDirection: "column", gap: "2rem" }}>
              <div>
                <h3 style={{ fontSize: "1.5rem", fontWeight: 800, color: "var(--text-main)", marginBottom: "0.5rem" }}>Training Matrix</h3>
                <p style={{ color: "var(--text-muted)", fontSize: "0.95rem", marginBottom: "1.25rem" }}>
                  {hasBackend
                    ? `Framework-aware training requirements generated for ${backendData.framework?.toUpperCase() || ad.framework || "the selected framework"}.`
                    : "Standardized security training requirements mapped to organizational roles and risk drivers."}
                </p>
                <div className="card" style={{ padding: 0, overflow: "hidden" }}>
                  <div className="table-container" style={{ margin: 0, borderRadius: 0, border: "none" }}>
                    <table className="modern-table" style={{ margin: 0 }}>
                      <thead>
                        <tr>
                          <th>Role / Group</th>
                          <th>Training Content</th>
                          <th>Frequency</th>
                          <th>Risk / Incident Driver</th>
                        </tr>
                      </thead>
                      <tbody>
                        {roleBasedMatrix.map((row, i) => (
                          <tr key={i}>
                            <td style={{ fontWeight: 600, color: "var(--text-main)" }}>{row.role}</td>
                            <td style={{ color: "var(--text-main)" }}>{row.content}</td>
                            <td style={{ color: "var(--text-secondary)", whiteSpace: "nowrap" }}>{row.frequency}</td>
                            <td style={{ color: "var(--text-secondary)" }}>{row.driver}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>

              <div>
                <h3 style={{ fontSize: "1.5rem", fontWeight: 800, color: "var(--text-main)", marginBottom: "0.5rem" }}>Employee Training Tracker</h3>
                <p style={{ color: "var(--text-muted)", fontSize: "0.95rem", marginBottom: "1.25rem" }}>Current compliance status for individual employee training requirements.</p>
                {trackerData.length > 0 ? (
                  <div className="card" style={{ padding: 0, overflow: "hidden" }}>
                    <div className="table-container" style={{ margin: 0, borderRadius: 0, border: "none" }}>
                      <table className="modern-table" style={{ margin: 0 }}>
                        <thead>
                          <tr>
                            <th>Employee Name</th>
                            <th>Role</th>
                            <th>Assigned Training</th>
                            <th>Status</th>
                            <th>Last Training Date</th>
                            <th>Next Due Date</th>
                          </tr>
                        </thead>
                        <tbody>
                          {trackerData.map((row, i) => {
                            const statusVal = row.status || row.training_status || "Pending";
                            const isOverdue = statusVal.toLowerCase() === "overdue";

                            // Format YYYY-MM-DD → DD/MM/YYYY for display
                            const fmtDate = (raw) => {
                              if (!raw || raw === "Not Available") return "—";
                              const p = raw.split("-");
                              if (p.length === 3 && p[0].length === 4) return `${p[2]}/${p[1]}/${p[0]}`;
                              return raw;
                            };

                            return (
                              <tr key={i}>
                                <td style={{ fontWeight: 500, color: "var(--text-main)" }}>{row.employee || row.employee_name || row.name || "Unknown"}</td>
                                <td style={{ color: "var(--text-secondary)" }}>{row.role || "Employee"}</td>
                                <td style={{ color: "var(--text-main)" }}>{row.assigned_training || row.required_modules || "Security Awareness"}</td>
                                <td>
                                  <span
                                    className={getBadgeClass(statusVal)}
                                    style={{
                                      ...(isOverdue ? { background: "#7f1d1d", color: "#ffffff", fontWeight: 700 } : {}),
                                      textTransform: "none"
                                    }}
                                  >
                                    {formatStatusLabel(statusVal)}
                                  </span>
                                </td>
                                <td style={{ color: "var(--text-secondary)" }}>{fmtDate(row.last_training_date)}</td>
                                <td>
                                  {/* Flex row: date | PAST DUE badge — never concatenated */}
                                  <div className="inline-flex items-center gap-2 whitespace-nowrap">
                                    <span style={isOverdue ? { color: "#dc2626", fontWeight: 600 } : { color: "var(--text-secondary)" }}>
                                      {fmtDate(row.next_due_date)}
                                    </span>
                                    {isOverdue && (
                                      <>
                                        <span style={{ color: "var(--text-muted)", fontSize: "0.8rem", userSelect: "none" }}>|</span>
                                        <span style={{
                                          fontSize: "0.68rem",
                                          fontWeight: 800,
                                          letterSpacing: "0.04em",
                                          textTransform: "uppercase",
                                          background: "#7f1d1d",
                                          color: "#ffffff",
                                          padding: "2px 7px",
                                          borderRadius: "4px",
                                        }}>
                                          PAST DUE
                                        </span>
                                      </>
                                    )}
                                  </div>
                                </td>
                              </tr>
                            );
                          })}
                        </tbody>
                      </table>
                    </div>
                  </div>
                ) : (
                  <div className="card" style={{ padding: "3rem 2rem", textAlign: "center", border: "1px dashed var(--border-color)", background: "var(--bg-main)" }}>
                    <svg style={{ width: "48px", height: "48px", color: "var(--text-muted)", margin: "0 auto 1rem", opacity: 0.5 }} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" /></svg>
                    <h4 style={{ fontSize: "1.1rem", fontWeight: 600, color: "var(--text-main)", marginBottom: "0.5rem" }}>No Employee Data Found</h4>
                    <p style={{ color: "var(--text-muted)", fontSize: "0.95rem", margin: 0, maxWidth: "400px", marginLeft: "auto", marginRight: "auto" }}>Upload HR records or a training matrix spreadsheet to populate employee tracking.</p>
                  </div>
                )}
              </div>
            </div>
          );
        })()}

        {/* GOVERNANCE CALENDAR TAB */}
        {activeTab === "governance" && (() => {
          const generatedCal = ad.governance_calendar_generated;
          const hasGenerated = Array.isArray(generatedCal) && generatedCal.length > 0;

          const legacyCal = ad.governance_calendar;
          const hasLegacy = Array.isArray(legacyCal) && legacyCal.length > 0;

          const calendarRows =
            hasGenerated
              ? generatedCal
              : hasLegacy
                ? legacyCal.map((row, i) => ({
                    month: `Month ${i + 1}`,
                    governance_activity: row.activity || row.governance_activity || "—",
                  }))
                : [];

          return (
            <div style={{ animation: "fadeIn 0.3s ease" }}>
              <h3 style={{ fontSize: "1.5rem", fontWeight: 800, color: "var(--text-main)", marginBottom: "0.5rem" }}>Governance Calendar</h3>
              <p style={{ color: "var(--text-muted)", fontSize: "0.95rem", marginBottom: "1.25rem" }}>
                {hasGenerated
                  ? `Framework-aware governance activities generated for ${ad.framework || "the selected framework"}.`
                  : "Governance activities schedule for recurring compliance and security reviews."}
                {!hasGenerated && hasLegacy && (
                  <span style={{ color: "orange", marginLeft: "0.5rem" }}>(Using legacy governance calendar)</span>
                )}
              </p>
              {calendarRows.length > 0 ? (
                <div className="card" style={{ padding: 0, overflow: "hidden" }}>
                  <div className="table-container" style={{ margin: 0, borderRadius: 0, border: "none" }}>
                    <table className="modern-table" style={{ margin: 0 }}>
                      <thead>
                        <tr>
                          <th>Month</th>
                          <th>Governance Activity</th>
                        </tr>
                      </thead>
                      <tbody>
                        {calendarRows.map((row, i) => (
                          <tr key={i}>
                            <td style={{ fontWeight: 600, color: "var(--text-main)", whiteSpace: "nowrap" }}>{row.month}</td>
                            <td style={{ color: "var(--text-main)" }}>{row.governance_activity}</td>
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
          );
        })()}

      </div>
    </PageContainer>
  );
}
