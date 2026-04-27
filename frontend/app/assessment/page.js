"use client";

import { useState, useEffect } from "react";
import PageContainer from "../components/PageContainer";
import API_BASE_URL from "../lib/api";
import { PieChart, Pie, Cell, Tooltip as RechartsTooltip, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';

const STANDARDS = [
  { id: "iso27001", label: "ISO 27001 (Enriched)", enriched: true },
  { id: "pci_dss",  label: "PCI DSS (Legacy)",    enriched: false },
  { id: "hipaa",    label: "HIPAA (Legacy)",       enriched: false },
];

const ORG_TYPES = ["bank", "hospital", "company"];

export default function AssessmentPage() {
  const [companyName, setCompanyName] = useState("");
  const [orgType, setOrgType] = useState("company");
  const [standardId, setStandardId] = useState("iso27001");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  // Evidence detection
  const [evidenceSummary, setEvidenceSummary] = useState(null);
  const [evidenceLoading, setEvidenceLoading] = useState(true);

  // Fetch evidence status on mount
  useEffect(() => {
    async function checkEvidence() {
      try {
        const res = await fetch(`http://localhost:8000/assess/evidence-summary`);
        console.log("Content-Type:", res.headers.get("content-type"));
        if (res.headers.get("content-type")?.includes("text/html")) {
          console.error("API returned HTML instead of JSON for assess/evidence-summary");
          throw new Error("API returned HTML instead of JSON");
        }
        if (!res.ok) {
          const text = await res.text();
          console.error("API ERROR RESPONSE:", text);
          throw new Error("API request failed");
        }
        const data = await res.json();
        setEvidenceSummary(data);
      } catch {
        // Silently fail — evidence check is non-critical
      } finally {
        setEvidenceLoading(false);
      }
    }
    checkEvidence();
  }, []);

  const hasEvidence = evidenceSummary?.has_evidence === true;
  const isEnriched = STANDARDS.find(s => s.id === standardId)?.enriched;

  async function runAssessment() {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      if (isEnriched) {
        // Enriched ISO 27001 path
        const res = await fetch(`http://localhost:8000/assess/iso27001`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            assessment_name: `${companyName || "Demo Company"} Assessment`,
            scope: orgType,
            priority: "High",
            use_uploaded_evidence: true,
          }),
        });
        console.log("Content-Type:", res.headers.get("content-type"));
        if (res.headers.get("content-type")?.includes("text/html")) {
          console.error("API returned HTML instead of JSON for assess/iso27001");
          throw new Error("API returned HTML instead of JSON");
        }
        if (!res.ok) {
          const text = await res.text();
          console.error("API ERROR RESPONSE:", text);
          throw new Error("API request failed");
        }
        const data = await res.json();
        setResult({ type: "enriched", data });
      } else {
        // Legacy path
        const res = await fetch(`http://localhost:8000/run-and-save-assessment`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            company: { id: "C001", name: companyName || "Demo Company", organization_type: orgType, sector: "", country: "" },
            raw_data: {}, raw_config_data: {},
            standard_file: `backend/standards/${standardId}.json`,
            config_standard_file: "backend/standards/config_baseline.json",
          }),
        });
        console.log("Content-Type:", res.headers.get("content-type"));
        if (res.headers.get("content-type")?.includes("text/html")) {
          console.error("API returned HTML instead of JSON for run-and-save-assessment");
          throw new Error("API returned HTML instead of JSON");
        }
        if (!res.ok) {
          const text = await res.text();
          console.error("API ERROR RESPONSE:", text);
          throw new Error("API request failed");
        }
        const data = await res.json();
        setResult({ type: "legacy", data });
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  const getBadgeClass = (status) => {
    if (!status) return "badge badge-blue";
    const s = status.toLowerCase();
    if (s === "compliant" || s === "pass" || s === "low" || s === "true") return "badge badge-green";
    if (s === "missing" || s === "fail" || s === "high" || s === "false") return "badge badge-red";
    if (s === "partial" || s === "medium") return "badge badge-yellow";
    return "badge badge-blue";
  };

  const getScoreColor = (score) => {
    if (score >= 80) return "#10B981";
    if (score >= 50) return "#F59E0B";
    return "#EF4444";
  };

  // Enriched ISO data
  const enrichedData = result?.type === "enriched" ? result.data : null;

  const complianceData = enrichedData ? [
    { name: "Compliant", value: enrichedData.compliant_controls, color: "#10B981" },
    { name: "Partial", value: enrichedData.partial_controls || 0, color: "#F59E0B" },
    { name: "Missing", value: enrichedData.missing_controls, color: "#EF4444" },
  ].filter(d => d.value > 0) : [];

  const sev = enrichedData?.severity_summary || {};
  const severityChartData = [
    { name: "High", Compliant: sev.high?.compliant || 0, Missing: sev.high?.missing || 0, Partial: sev.high?.partial || 0 },
    { name: "Medium", Compliant: sev.medium?.compliant || 0, Missing: sev.medium?.missing || 0, Partial: sev.medium?.partial || 0 },
    { name: "Low", Compliant: sev.low?.compliant || 0, Missing: sev.low?.missing || 0, Partial: sev.low?.partial || 0 },
  ];

  // Legacy data
  const legacyData = result?.type === "legacy" ? result.data : null;
  const legacySummary = legacyData?.combined_output?.assessment?.assessment_summary;
  const legacyControls = legacyData?.combined_output?.assessment?.controls;

  return (
    <PageContainer>
      <div style={{ padding: "0 0 2.5rem" }}>
        <h1 style={{ fontSize: "2.5rem", fontWeight: 800, letterSpacing: "-0.04em", marginBottom: "0.5rem", color: "var(--text-main)", lineHeight: "1.2" }}>
          Compliance Assessment Workspace
        </h1>
        <p style={{ color: "var(--text-muted)", fontSize: "1.05rem", maxWidth: "700px", lineHeight: "1.6", margin: 0 }}>
          Generate structured security assessments mapped to international baselines. Features the enriched ISO 27001 engine with evidence mapping.
        </p>
      </div>

      {/* Evidence Status Banner */}
      {!evidenceLoading && isEnriched && (
        <div className="card" style={{
          padding: "1rem 1.5rem",
          marginBottom: "1.5rem",
          display: "flex",
          alignItems: "center",
          gap: "1rem",
          background: hasEvidence ? "rgba(16, 185, 129, 0.05)" : "rgba(245, 158, 11, 0.05)",
          border: `1px solid ${hasEvidence ? "#10B981" : "#F59E0B"}`,
        }}>
          <svg style={{ width: "20px", height: "20px", color: hasEvidence ? "#10B981" : "#F59E0B", flexShrink: 0 }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            {hasEvidence
              ? <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              : <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            }
          </svg>
          <div style={{ flex: 1 }}>
            {hasEvidence ? (
              <>
                <strong style={{ color: "#065F46", display: "block", fontSize: "0.95rem" }}>Evidence Available</strong>
                <span style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>
                  File: {evidenceSummary.evidence.file_name} &middot; {evidenceSummary.evidence.row_count} evidence rows &middot; Uploaded {new Date(evidenceSummary.evidence.uploaded_at).toLocaleDateString()}
                </span>
              </>
            ) : (
              <>
                <strong style={{ color: "#92400E", display: "block", fontSize: "0.95rem" }}>Baseline Mode</strong>
                <span style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>
                  No evidence uploaded. Assessment will run against the full ISO 27001 framework without evidence mapping. Upload evidence via Workspace to get mapped results.
                </span>
              </>
            )}
          </div>
          {hasEvidence && <span className="badge badge-green">Evidence-Backed</span>}
          {!hasEvidence && <span className="badge badge-yellow">Baseline Only</span>}
        </div>
      )}

      <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem", marginBottom: "2.5rem" }}>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: "1.5rem" }}>
          <div className="card" style={{ padding: "1.5rem" }}>
            <h3 style={{ fontSize: "1.15rem", fontWeight: 700, marginBottom: "0.25rem", color: "var(--text-main)" }}>Assessment Context</h3>
            <p style={{ fontSize: "0.9rem", color: "var(--text-muted)", marginBottom: "1.5rem" }}>Define the scope of the assessment audit.</p>
            <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
              <div>
                <label style={{ fontSize: "0.85rem", fontWeight: 600, color: "var(--text-main)", marginBottom: "0.5rem", display: "block" }}>Project / Entity Name</label>
                <input type="text" className="input-field" value={companyName} onChange={e => setCompanyName(e.target.value)} placeholder="e.g. Acme Enterprise" />
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
                <div>
                  <label style={{ fontSize: "0.85rem", fontWeight: 600, color: "var(--text-main)", marginBottom: "0.5rem", display: "block" }}>Industry Type</label>
                  <select className="input-field" value={orgType} onChange={e => setOrgType(e.target.value)}>
                    {ORG_TYPES.map(t => <option key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</option>)}
                  </select>
                </div>
                <div>
                  <label style={{ fontSize: "0.85rem", fontWeight: 600, color: "var(--text-main)", marginBottom: "0.5rem", display: "block" }}>Framework</label>
                  <select className="input-field" value={standardId} onChange={e => { setStandardId(e.target.value); setResult(null); setError(null); }}>
                    {STANDARDS.map(s => <option key={s.id} value={s.id}>{s.label}</option>)}
                  </select>
                </div>
              </div>
            </div>
          </div>

          <div className="card" style={{ padding: "1.5rem", display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center", border: "2px solid var(--border-color)", position: "relative", overflow: "hidden" }}>
            <div style={{ position: "absolute", top: "-50%", right: "-5%", width: "200px", height: "200px", background: "var(--primary)", opacity: 0.04, borderRadius: "50%", pointerEvents: "none" }} />
            <h3 style={{ fontSize: "1.2rem", fontWeight: 800, color: "var(--text-main)", margin: "0 0 0.5rem 0", zIndex: 1 }}>Run Full Analysis</h3>
            <p style={{ color: "var(--text-muted)", fontSize: "0.95rem", textAlign: "center", marginBottom: "1.5rem", zIndex: 1 }}>
              {isEnriched
                ? (hasEvidence ? "Will map uploaded evidence to ISO 27001 controls." : "Will generate a baseline-only framework assessment.")
                : "Will run legacy combined analysis against the selected framework."
              }
            </p>
            <button className="btn-primary" onClick={runAssessment} disabled={loading}
              style={{ width: "100%", maxWidth: "300px", padding: "1rem", fontSize: "1rem", display: "flex", justifyContent: "center", alignItems: "center", gap: "0.5rem", zIndex: 1 }}>
              {loading ? (<><svg style={{ width: "18px", height: "18px", animation: "spin 1s infinite linear" }} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg> Evaluating...</>) : "Execute Assessment"}
            </button>
          </div>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="card" style={{ padding: "1.25rem", background: "rgba(239,68,68,0.05)", border: "1px solid #EF4444", color: "#EF4444", marginBottom: "2rem", display: "flex", gap: "1rem", alignItems: "center" }}>
          <svg style={{ width: "24px", height: "24px" }} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
          <div><strong style={{ display: "block" }}>Execution Failed</strong><span style={{ fontSize: "0.9rem" }}>{error}</span></div>
        </div>
      )}

      {/* ============================================================
          ENRICHED ISO 27001 RESULTS
          Only rendered when result.type === "enriched"
          ============================================================ */}
      {enrichedData && (
        <div style={{ marginTop: "1rem", animation: "fadeIn 0.5s ease" }}>

          {/* Evidence/Baseline Banner */}
          <div style={{
            marginBottom: "2rem",
            padding: "1.25rem 1.5rem",
            borderRadius: "8px",
            background: enrichedData.evidence_backed ? "linear-gradient(135deg, rgba(16,185,129,0.08) 0%, rgba(37,99,235,0.05) 100%)" : "rgba(245,158,11,0.06)",
            border: `1px solid ${enrichedData.evidence_backed ? "#10B981" : "#F59E0B"}`,
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            flexWrap: "wrap",
            gap: "0.5rem",
          }}>
            <div>
              <h2 style={{ fontSize: "1.75rem", fontWeight: 800, margin: "0 0 0.25rem 0", color: "var(--text-main)", letterSpacing: "-0.03em" }}>
                {enrichedData.framework} Assessment
              </h2>
              <span style={{ fontSize: "0.9rem", color: "var(--text-muted)" }}>
                {enrichedData.evidence_backed
                  ? `Evidence-backed results \u2022 Source: ${enrichedData.evidence_source === "latest_upload" ? "Latest Upload" : "Direct Payload"}`
                  : "Baseline-only \u2022 No evidence mapped \u2022 Upload evidence via Workspace for compliance scoring"
                }
              </span>
            </div>
            <span className={enrichedData.evidence_backed ? "badge badge-green" : "badge badge-yellow"} style={{ fontSize: "0.85rem", padding: "0.4rem 0.75rem" }}>
              {enrichedData.evidence_backed ? "Evidence-Backed" : "Baseline Only"}
            </span>
          </div>

          {/* 1. TOP SUMMARY CARDS */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(170px, 1fr))", gap: "1.25rem", marginBottom: "2rem" }}>
            {[
              { label: "Compliance Score", value: `${enrichedData.compliance_score}%`, color: getScoreColor(enrichedData.compliance_score) },
              { label: "Total Controls", value: enrichedData.total_controls, color: "var(--primary)" },
              { label: "Compliant", value: enrichedData.compliant_controls, color: "#10B981" },
              { label: "Partial", value: enrichedData.partial_controls || 0, color: "#F59E0B" },
              { label: "Missing", value: enrichedData.missing_controls, color: "#EF4444" },
            ].map(m => (
              <div key={m.label} className="card" style={{ padding: "1.5rem", borderLeft: `4px solid ${m.color}`, display: "flex", flexDirection: "column" }}>
                <div style={{ fontSize: "0.80rem", color: "var(--text-muted)", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: "0.5rem" }}>{m.label}</div>
                <div style={{ fontSize: "2rem", fontWeight: 800, color: m.color, lineHeight: "1" }}>{m.value}</div>
              </div>
            ))}
          </div>

          {/* Evidence Mapping Summary */}
          {enrichedData.evidence_mapping && (
            <div className="card" style={{ padding: "1.25rem", marginBottom: "2rem", display: "flex", gap: "2rem", flexWrap: "wrap" }}>
              <h4 style={{ width: "100%", fontSize: "1rem", fontWeight: 700, margin: "0 0 0.5rem 0", color: "var(--text-main)" }}>Evidence Mapping Summary</h4>
              {[
                { label: "Mapped Controls", value: enrichedData.evidence_mapping.mapped_controls_count, color: "#10B981" },
                { label: "Unmapped Controls", value: enrichedData.evidence_mapping.unmapped_controls_count, color: "#EF4444" },
                { label: "Unmatched Rows", value: enrichedData.evidence_mapping.unmatched_rows_count, color: "#F59E0B" },
              ].map(m => (
                <div key={m.label} style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                  <span style={{ fontSize: "0.85rem", color: "var(--text-muted)" }}>{m.label}:</span>
                  <strong style={{ fontSize: "1.1rem", color: m.color }}>{m.value}</strong>
                </div>
              ))}
            </div>
          )}

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(400px, 1fr))", gap: "1.5rem", marginBottom: "2.5rem" }}>

            {/* 4. SMART INSIGHTS */}
            {enrichedData.insights && enrichedData.insights.length > 0 && (
              <div className="card" style={{ padding: "1.5rem" }}>
                <h3 style={{ fontSize: "1.15rem", fontWeight: 700, marginBottom: "1rem", color: "var(--text-main)", display: "flex", alignItems: "center", gap: "0.5rem" }}>
                  <svg style={{ width: "20px", height: "20px", color: "var(--primary)" }} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
                  Actionable Insights
                </h3>
                <ul style={{ margin: 0, padding: 0, listStyle: "none", display: "flex", flexDirection: "column", gap: "0.75rem" }}>
                  {enrichedData.insights.map((insight, idx) => (
                    <li key={idx} style={{ padding: "0.85rem 1rem", background: "var(--bg-main)", borderRadius: "6px", fontSize: "0.9rem", color: "var(--text-main)", borderLeft: "3px solid var(--primary)", lineHeight: "1.5" }}>
                      {insight}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* 3. SEVERITY CHART + 5. CRITICAL GAPS */}
            <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
              <div className="card" style={{ padding: "1.5rem", flex: 1 }}>
                <h3 style={{ fontSize: "1.15rem", fontWeight: 700, marginBottom: "1rem", color: "var(--text-main)" }}>Severity Distribution</h3>
                <div style={{ height: "220px", width: "100%" }}>
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

              {enrichedData.top_missing_high_risk && enrichedData.top_missing_high_risk.length > 0 && (
                <div className="card" style={{ padding: "1.5rem", border: "1px solid rgba(239, 68, 68, 0.3)", background: "rgba(239, 68, 68, 0.02)" }}>
                  <h3 style={{ fontSize: "1.15rem", fontWeight: 700, marginBottom: "1rem", color: "#EF4444", display: "flex", alignItems: "center", gap: "0.5rem" }}>
                    <svg style={{ width: "20px", height: "20px" }} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
                    Critical High-Risk Gaps
                  </h3>
                  <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
                    {enrichedData.top_missing_high_risk.map((risk, i) => (
                      <div key={i} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "0.75rem", background: "var(--bg-card)", borderRadius: "6px", border: "1px solid rgba(239, 68, 68, 0.2)" }}>
                        <div>
                          <span style={{ fontSize: "0.8rem", fontWeight: 600, color: "#EF4444", marginRight: "0.5rem" }}>{risk.rule_id}</span>
                          <span style={{ fontSize: "0.85rem", color: "var(--text-main)" }}>{risk.name}</span>
                        </div>
                        <span style={{ fontSize: "0.8rem", color: "var(--text-muted)", flexShrink: 0 }}>{risk.section_key}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* 2. SECTION SUMMARIES & CONTROLS */}
          <div style={{ borderTop: "2px solid var(--border-color)", paddingTop: "2.5rem" }}>
            <h3 style={{ fontSize: "1.5rem", fontWeight: 800, color: "var(--text-main)", marginBottom: "1.5rem" }}>Section Performance</h3>
            <div style={{ display: "flex", flexDirection: "column", gap: "2rem" }}>
              {enrichedData.sections && enrichedData.sections.map((section) => (
                <div key={section.section_key} className="card" style={{ padding: "0", overflow: "hidden" }}>
                  {/* Section header */}
                  <div style={{ padding: "1.5rem", background: "var(--bg-main)", borderBottom: "1px solid var(--border-color)", display: "flex", flexWrap: "wrap", justifyContent: "space-between", alignItems: "center", gap: "1rem" }}>
                    <div>
                      <h4 style={{ fontSize: "1.2rem", fontWeight: 700, margin: "0 0 0.25rem 0", color: "var(--text-main)" }}>{section.section_key} {section.section_name}</h4>
                      <span style={{ fontSize: "0.85rem", color: "var(--text-muted)" }}>{section.controls_count} Total Controls</span>
                    </div>
                    <div style={{ display: "flex", gap: "1.5rem", alignItems: "center" }}>
                      <div style={{ textAlign: "center" }}>
                        <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 700 }}>Score</div>
                        <div style={{ fontSize: "1.5rem", fontWeight: 800, color: getScoreColor(section.compliance_score) }}>{section.compliance_score}%</div>
                      </div>
                      <div style={{ display: "flex", gap: "0.5rem" }}>
                        <span className="badge badge-green" style={{ display: "flex", flexDirection: "column", alignItems: "center", padding: "0.2rem 0.6rem" }}>
                          <span style={{ fontSize: "0.6rem", opacity: 0.8 }}>PASS</span>
                          <strong style={{ fontSize: "1.1rem" }}>{section.compliant_controls}</strong>
                        </span>
                        <span className="badge badge-yellow" style={{ display: "flex", flexDirection: "column", alignItems: "center", padding: "0.2rem 0.6rem" }}>
                          <span style={{ fontSize: "0.6rem", opacity: 0.8 }}>PARTIAL</span>
                          <strong style={{ fontSize: "1.1rem" }}>{section.partial_controls || 0}</strong>
                        </span>
                        <span className="badge badge-red" style={{ display: "flex", flexDirection: "column", alignItems: "center", padding: "0.2rem 0.6rem" }}>
                          <span style={{ fontSize: "0.6rem", opacity: 0.8 }}>MISSING</span>
                          <strong style={{ fontSize: "1.1rem" }}>{section.missing_controls}</strong>
                        </span>
                      </div>
                    </div>
                  </div>
                  {/* Controls table */}
                  <div className="table-container" style={{ margin: 0, borderRadius: 0, border: "none" }}>
                    <table className="modern-table" style={{ margin: 0 }}>
                      <thead>
                        <tr>
                          <th>Control ID</th>
                          <th>Requirement</th>
                          <th>Severity</th>
                          <th>Evidence</th>
                          <th>Status</th>
                        </tr>
                      </thead>
                      <tbody>
                        {section.controls && section.controls.map(c => (
                          <tr key={c.rule_id}>
                            <td style={{ width: "130px", fontWeight: 600, color: "var(--text-muted)", fontSize: "0.85rem" }}>{c.rule_id}</td>
                            <td>
                              <div style={{ fontWeight: 600, color: "var(--text-main)", marginBottom: "0.15rem", fontSize: "0.95rem" }}>{c.name}</div>
                              <div style={{ fontSize: "0.82rem", color: "var(--text-muted)", lineHeight: "1.4" }}>{c.description}</div>
                            </td>
                            <td style={{ width: "100px" }}><span className={getBadgeClass(c.severity)}>{c.severity}</span></td>
                            <td style={{ width: "90px", textAlign: "center" }}>
                              {c.has_evidence
                                ? <span style={{ color: "#10B981", fontSize: "1.1rem" }}>&#10003;</span>
                                : <span style={{ color: "var(--text-muted)", fontSize: "0.8rem" }}>&mdash;</span>
                              }
                            </td>
                            <td style={{ width: "120px" }}><span className={getBadgeClass(c.status)}>{c.status?.toUpperCase()}</span></td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ============================================================
          LEGACY NON-ISO RESULTS
          Only rendered when result.type === "legacy"
          ============================================================ */}
      {legacyData && (
        <div style={{ marginTop: "2rem" }}>
          <div style={{ marginBottom: "2rem", borderBottom: "2px solid var(--border-color)", paddingBottom: "1.5rem" }}>
            <h2 style={{ fontSize: "1.75rem", fontWeight: 800, color: "var(--text-main)", marginBottom: "0.5rem" }}>Legacy Assessment Output</h2>
            <p style={{ color: "var(--text-muted)", fontSize: "0.95rem", margin: 0 }}>Results from the combined analysis pipeline. Enriched ISO features are not available for this framework.</p>
          </div>

          {legacySummary && (
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: "1.25rem", marginBottom: "2rem" }}>
              {[
                { label: "Compliance %", value: `${legacySummary.compliance_percentage}%`, color: legacySummary.compliance_percentage >= 50 ? "#10B981" : "#EF4444" },
                { label: "Total Controls", value: legacySummary.total_controls, color: "var(--primary)" },
                { label: "Passed", value: legacySummary.passed_controls, color: "#10B981" },
                { label: "Failed", value: legacySummary.failed_controls, color: "#EF4444" },
              ].map(m => (
                <div key={m.label} className="card" style={{ padding: "1.5rem", borderLeft: `4px solid ${m.color}` }}>
                  <div style={{ fontSize: "0.80rem", color: "var(--text-muted)", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: "0.5rem" }}>{m.label}</div>
                  <div style={{ fontSize: "2rem", fontWeight: 800, color: m.color, lineHeight: "1" }}>{m.value}</div>
                </div>
              ))}
            </div>
          )}

          {legacyControls && legacyControls.length > 0 && (
            <div className="card">
              <h3 style={{ fontSize: "1.15rem", fontWeight: 700, marginBottom: "1rem", color: "var(--text-main)" }}>Control Results</h3>
              <div className="table-container">
                <table className="modern-table">
                  <thead><tr><th>ID</th><th>Control</th><th>Status</th></tr></thead>
                  <tbody>
                    {legacyControls.map(c => (
                      <tr key={c.id}>
                        <td style={{ fontWeight: 600, color: "var(--text-muted)" }}>{c.id}</td>
                        <td style={{ color: "var(--text-main)" }}>{c.name}</td>
                        <td><span className={getBadgeClass(c.status)}>{c.status}</span></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}
    </PageContainer>
  );
}
