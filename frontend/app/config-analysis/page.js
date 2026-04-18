"use client";

import { useState } from "react";
import PageContainer from "../components/PageContainer";
import API_BASE_URL from "../lib/api";
import { PieChart, Pie, Cell, Tooltip as RechartsTooltip, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';

const CONFIG_FIELDS = [
  { key: "firewall_rules_defined",       label: "Firewall Rules Defined" },
  { key: "logging_enabled",              label: "Logging Enabled" },
  { key: "backup_configured",            label: "Backup Configured" },
  { key: "network_segmentation_enabled", label: "Network Segmentation Enabled" },
  { key: "remote_access_restricted",     label: "Remote Access Restricted" },
];

const labelStyle = { display: "flex", alignItems: "center", justifyContent: "space-between", padding: "0.75rem 0", fontSize: "0.95rem", color: "var(--text-main)", borderBottom: "1px dashed var(--border-color)" };
const headingStyle = { fontSize: "1.15rem", fontWeight: 700, marginBottom: "0.25rem", color: "var(--text-main)", letterSpacing: "-0.01em" };
const descStyle = { fontSize: "0.9rem", color: "var(--text-muted)", marginBottom: "1.5rem", lineHeight: "1.5" };

export default function ConfigAnalysisPage() {
  const [configData, setConfigData] = useState(
    Object.fromEntries(CONFIG_FIELDS.map((f) => [f.key, false]))
  );

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  function toggle(key) { setConfigData((prev) => ({ ...prev, [key]: !prev[key] })); }

  async function runAnalysis() {
    setLoading(true);
    setError(null);
    setResult(null);

    const body = {
      raw_config_data: configData,
      config_standard_file: "backend/standards/config_baseline.json",
    };

    try {
      const res = await fetch(`${API_BASE_URL}/run-config-analysis`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!res.ok) throw new Error(`Server responded with ${res.status}`);
      const data = await res.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  const summary = result?.summary;
  const findings = result?.findings;
  const risks = result?.risks;

  const getBadgeClass = (status) => {
    if (!status) return "";
    const s = status.toLowerCase();
    if (s === "pass" || s === "low" || s === "true") return "badge badge-green";
    if (s === "fail" || s === "high" || s === "false") return "badge badge-red";
    if (s === "medium") return "badge badge-yellow";
    return "badge badge-blue";
  };

  // Visual Analytics Processing
  const complianceData = summary ? [
    { name: "Passed Scans", value: summary.passed_checks, color: "#10B981" },
    { name: "Failed Drifts", value: summary.failed_checks, color: "#EF4444" }
  ] : [];

  const riskCounts = risks ? risks.reduce((acc, r) => {
    const level = (r.level || "low").toLowerCase();
    acc[level] = (acc[level] || 0) + 1;
    return acc;
  }, { high: 0, medium: 0, low: 0 }) : { high: 0, medium: 0, low: 0 };

  const riskData = [
    { name: "High", count: riskCounts.high, fill: "#EF4444" },
    { name: "Medium", count: riskCounts.medium, fill: "#F59E0B" },
    { name: "Low", count: riskCounts.low, fill: "#10B981" }
  ];

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
          Diagnostic Validation Console
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
          Analyze root infrastructure layer configurations detecting unauthorized deployment drifts strictly mapping defined operational baselines.
        </p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr", gap: "2rem", marginBottom: "2.5rem" }}>
        
        {/* Input Scope */}
        <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
          <div style={{ borderBottom: "2px solid var(--border-color)", paddingBottom: "1rem" }}>
            <h2 style={{ fontSize: "1.25rem", fontWeight: 700, color: "var(--text-main)", marginBottom: "0.25rem", display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <span style={{ display: "flex", alignItems: "center", justifyContent: "center", width: "24px", height: "24px", borderRadius: "50%", background: "var(--primary)", color: "#fff", fontSize: "0.85rem" }}>1</span>
              Evaluate Technical Posture
            </h2>
            <p style={{ fontSize: "0.95rem", color: "var(--text-muted)", margin: 0 }}>
              Audit active configuration states from exposed internal systems manually simulating node endpoints.
            </p>
          </div>

          <div className="card" style={{ maxWidth: "700px", background: "var(--bg-main)" }}>
             <h3 style={headingStyle}>System Settings Baseline Execution</h3>
             <p style={descStyle}>Identify whether explicit boundary conditions pass engineering requirements.</p>
             <div style={{ display: "flex", flexDirection: "column" }}>
               {CONFIG_FIELDS.map((f, idx) => (
                 <div key={f.key} style={{ ...labelStyle, borderBottom: idx === CONFIG_FIELDS.length - 1 ? "none" : labelStyle.borderBottom, paddingBottom: idx === CONFIG_FIELDS.length - 1 ? "0" : labelStyle.padding }}>
                   <span style={{ fontWeight: 600 }}>{f.label}</span>
                   <input type="checkbox" checked={configData[f.key]} onChange={() => toggle(f.key)} style={{ width: "22px", height: "22px", cursor: "pointer", accentColor: "var(--primary)" }} />
                 </div>
               ))}
             </div>
          </div>
        </div>
      </div>

      {/* Action Bar */}
      <div className="card" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "3rem", background: "var(--bg-card)", border: "2px solid var(--border-color)", position: "relative", overflow: "hidden" }}>
        
        {/* Background visual artifact */}
        <div style={{ position: "absolute", top: "-50%", left: "-5%", width: "150px", height: "150px", background: "var(--primary)", opacity: 0.05, borderRadius: "50%", pointerEvents: "none" }} />

        <div style={{ position: "relative", zIndex: 1 }}>
          <h3 style={{ fontSize: "1.2rem", fontWeight: 800, color: "var(--text-main)", margin: "0 0 0.3rem 0" }}>Run Technical Scan</h3>
          <p style={{ color: "var(--text-muted)", fontSize: "0.95rem", margin: 0 }}>
            Evaluate your explicit configurations for architectural drifts and vulnerabilities.
          </p>
        </div>
        
        <button 
          className="btn-primary" 
          onClick={runAnalysis} 
          disabled={loading} 
          style={{ padding: "0.85rem 2rem", fontSize: "1rem", display: "flex", alignItems: "center", gap: "0.5rem", position: "relative", zIndex: 1 }}
        >
          {loading ? (
            <>
              <svg style={{ width: "18px", height: "18px", animation: "spin 1s infinite linear" }} fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Scanning Configuration...
            </>
          ) : (
             "Run Analysis"
          )}
        </button>
      </div>

      {/* Error */}
      {error && (
        <div className="card" style={{ display: "flex", gap: "1rem", alignItems: "center", background: "rgba(239,68,68,0.05)", border: "1px solid #EF4444", color: "#EF4444", marginBottom: "2rem" }}>
          <svg style={{ width: "24px", height: "24px", flexShrink: 0 }} fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
             <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <strong style={{ display: "block", fontWeight: 700, marginBottom: "0.2rem" }}>Diagnostic Protocol Failure</strong>
            <span style={{ fontSize: "0.9rem" }}>{error}</span>
          </div>
        </div>
      )}

      {/* Idle / Empty State (Pre-Execution Graphic) */}
      {!result && !loading && !error && (
        <div style={{ padding: "4rem 2rem", textAlign: "center", border: "2px dashed var(--border-color)", borderRadius: "12px", background: "var(--bg-main)" }}>
          <div style={{ display: "inline-flex", alignItems: "center", justifyContent: "center", width: "64px", height: "64px", borderRadius: "50%", background: "rgba(37, 99, 235, 0.1)", color: "var(--primary)", marginBottom: "1.5rem" }}>
            <svg style={{ width: "32px", height: "32px" }} fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
          <h3 style={{ fontSize: "1.25rem", fontWeight: 700, color: "var(--text-main)", marginBottom: "0.5rem" }}>Ready for Configuration Scan</h3>
          <p style={{ color: "var(--text-muted)", fontSize: "0.95rem", maxWidth: "450px", margin: "0 auto", lineHeight: "1.6" }}>
            Select your infrastructure settings above to execute an isolated technical vulnerability scan.
          </p>
        </div>
      )}

      {/* Results Workspace */}
      {result && (
        <div style={{ marginTop: "3rem", borderTop: "2px solid var(--border-color)", paddingTop: "3rem" }}>
          <div style={{ marginBottom: "2.5rem" }}>
             <h2 style={{ fontSize: "2rem", fontWeight: 800, marginBottom: "0.5rem", color: "var(--text-main)", letterSpacing: "-0.03em" }}>
               Validation Output Trace
             </h2>
             <p style={{ color: "var(--text-muted)", fontSize: "1.05rem" }}>
               Analyzed boolean conditions and measured vulnerabilities against core architectures.
             </p>
          </div>

          {/* Metric Cards */}
          {summary && (
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: "1.25rem", marginBottom: "2.5rem" }}>
              {[
                { label: "Active Vectors", value: summary.total_checks, color: "var(--primary)" },
                { label: "Verification Pass", value: summary.passed_checks, color: "#10B981" },
                { label: "Drift Nodes Found", value: summary.failed_checks, color: "#EF4444" },
                { label: "Measured Risks", value: risks?.length || 0, color: risks?.length > 0 ? "#F59E0B" : "var(--text-muted)" },
              ].map((m) => (
                <div key={m.label} className="card" style={{ display: "flex", flexDirection: "column", padding: "1.5rem", borderLeft: `4px solid ${m.color}` }}>
                  <div style={{ fontSize: "0.85rem", color: "var(--text-muted)", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: "0.5rem" }}>
                    {m.label}
                  </div>
                  <div style={{ fontSize: "2.5rem", fontWeight: 800, color: m.color, lineHeight: "1" }}>
                    {m.value}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Visual Analytics Array */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: "1.5rem", marginBottom: "2.5rem" }}>
            
            {/* Donut Chart - Diagnostics */}
            {complianceData.length > 0 && (
              <div className="card" style={{ minHeight: "350px", display: "flex", flexDirection: "column" }}>
                <h3 style={headingStyle}>Scan Pass vs Fail Status</h3>
                <p style={descStyle}>Ratio of stable operational checks.</p>
                <div style={{ flex: 1, position: "relative", minHeight: "250px" }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={complianceData}
                        cx="50%"
                        cy="50%"
                        innerRadius={65}
                        outerRadius={95}
                        paddingAngle={5}
                        dataKey="value"
                      >
                        {complianceData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <RechartsTooltip contentStyle={{ borderRadius: "8px", border: "1px solid var(--border-color)", background: "var(--bg-card)" }} />
                    </PieChart>
                  </ResponsiveContainer>
                  {/* Center Text */}
                  <div style={{ position: "absolute", top: "50%", left: "50%", transform: "translate(-50%, -50%)", textAlign: "center" }}>
                    <span style={{ fontSize: "1.5rem", fontWeight: 800, color: "var(--text-main)", display: "block" }}>{summary.passed_checks}/{summary.total_checks}</span>
                  </div>
                </div>
              </div>
            )}

            {/* Bar Chart - Risk Distribution */}
            {risks && risks.length > 0 && (
              <div className="card" style={{ minHeight: "350px", display: "flex", flexDirection: "column" }}>
                <h3 style={headingStyle}>Configuration Risk Mapping</h3>
                <p style={descStyle}>Volume of immediate technical drift threats.</p>
                <div style={{ flex: 1, minHeight: "250px" }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={riskData} margin={{ top: 20, right: 30, left: -20, bottom: 5 }}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border-color)" />
                      <XAxis dataKey="name" tick={{ fill: "var(--text-muted)", fontSize: 12 }} axisLine={false} tickLine={false} />
                      <YAxis tick={{ fill: "var(--text-muted)", fontSize: 12 }} axisLine={false} tickLine={false} allowDecimals={false} />
                      <RechartsTooltip cursor={{ fill: "var(--bg-main)" }} contentStyle={{ borderRadius: "8px", border: "1px solid var(--border-color)", background: "var(--bg-card)" }} />
                      <Bar dataKey="count" radius={[4, 4, 0, 0]} maxBarSize={60} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            )}
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr", gap: "2.5rem" }}>
            
            {/* Findings Table */}
            {findings && findings.length > 0 && (
              <div className="card">
                <h3 style={headingStyle}>Configuration Finding Details</h3>
                <p style={descStyle}>Explicit boolean verification mapping inputs dynamically to target conditions.</p>
                <div className="table-container">
                  <table className="modern-table">
                    <thead>
                      <tr><th>Reference ID</th><th>Mapped System Node</th><th>Evaluated Trace</th><th>Expected Environment Array</th><th>Actual Measured State</th></tr>
                    </thead>
                    <tbody>
                      {findings.map((f) => {
                        const isDrift = String(f.actual) !== String(f.expected);
                        return (
                          <tr key={f.id}>
                            <td style={{ color: "var(--text-muted)", width: "160px", fontWeight: 600 }}>{f.id}</td>
                            <td style={{ fontWeight: 600, color: "var(--text-main)" }}>{f.name}</td>
                            <td><span className={getBadgeClass(f.status)}>{f.status}</span></td>
                            <td style={{ color: "var(--text-muted)", fontWeight: 600 }}>{String(f.expected).toUpperCase()}</td>
                            <td style={{ color: isDrift ? "#EF4444" : "var(--text-main)", fontWeight: 700, letterSpacing: isDrift ? "0.05em" : "0" }}>
                              {String(f.actual).toUpperCase()}
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Risks Table */}
            {risks && risks.length > 0 && (
              <div className="card">
                <h3 style={headingStyle}>Identified Technical Vulnerabilities</h3>
                <p style={descStyle}>Immediate risk calculations derived intrinsically via mapped failure parameters.</p>
                <div className="table-container">
                  <table className="modern-table">
                    <thead>
                      <tr><th>Risk ID</th><th>Vulnerability Type Constraint</th><th>Likelihood</th><th>Impact</th><th>Sum Score</th><th>Evaluated Severity</th></tr>
                    </thead>
                    <tbody>
                      {risks.map((r) => (
                        <tr key={r.id}>
                          <td style={{ color: "var(--text-muted)", width: "160px", fontWeight: 600 }}>{r.id}</td>
                          <td style={{ fontWeight: 500, color: "var(--text-main)" }}>{r.name}</td>
                          <td style={{ color: "var(--text-muted)" }}>{r.likelihood}</td>
                          <td style={{ color: "var(--text-muted)" }}>{r.impact}</td>
                          <td style={{ fontWeight: 800, fontSize: "1.1rem" }}>{r.score}</td>
                          <td><span className={getBadgeClass(r.level)}>{r.level}</span></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Success State */}
            {risks && risks.length === 0 && (
              <div className="card" style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: "4rem 2rem", textAlign: "center", background: "var(--bg-main)", border: "2px solid #10B981" }}>
                <div style={{ display: "flex", alignItems: "center", justifyContent: "center", width: "64px", height: "64px", background: "rgba(16, 185, 129, 0.1)", borderRadius: "50%", marginBottom: "1.5rem" }}>
                   <svg style={{ width: "32px", height: "32px", color: "#10B981" }} fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                     <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                   </svg>
                </div>
                <h3 style={{ fontSize: "1.5rem", fontWeight: 800, color: "#10B981", marginBottom: "0.5rem", letterSpacing: "-0.02em" }}>Operational Baseline Secure</h3>
                <p style={{ fontSize: "1.05rem", color: "var(--text-muted)", maxWidth: "500px", margin: 0, lineHeight: "1.6" }}>
                   All configuration parameters correctly validate against the strict security logic framework. No external or structural drift variables were discovered.
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </PageContainer>
  );
}
