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

      {/* COMPLIANCE SCORE */}
      <h3 style={{ fontSize: "1.5rem", fontWeight: 800, color: "var(--text-main)", marginBottom: "1rem" }}>1. Compliance Score</h3>
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

      {/* RISK ASSESSMENT */}
      <h3 style={{ fontSize: "1.5rem", fontWeight: 800, color: "var(--text-main)" }}>2. Risk Assessment Summary</h3>
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

        {/* HIGH RISKS */}
        <div className="card" style={{ padding: "1.25rem", border: "1px solid rgba(239,68,68,0.3)", background: "rgba(239,68,68,0.02)" }}>
          <h3 style={{ fontSize: "1.1rem", fontWeight: 700, marginBottom: "0.75rem", color: "#EF4444" }}>3. High Risk Items</h3>
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

      {/* RISK REGISTER */}
      {ad.risk_register && (
        <div style={{ borderTop: "2px solid var(--border-color)", paddingTop: "2.5rem", marginTop: "2.5rem" }}>
          <h3 style={{ fontSize: "1.5rem", fontWeight: 800, color: "var(--text-main)" }}>4. Risk Register</h3>
          <p style={{ color: "var(--text-muted)", fontSize: "0.95rem", marginBottom: "1.5rem" }}>
             Compiled from your uploaded risk data context.
          </p>
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
        </div>
      )}

      {/* SOA */}
      {ad.soa && (
        <div style={{ borderTop: "2px solid var(--border-color)", paddingTop: "2.5rem", marginTop: "2.5rem" }}>
          <h3 style={{ fontSize: "1.5rem", fontWeight: 800, color: "var(--text-main)", marginBottom: "0.5rem" }}>5. Statement of Applicability (SOA)</h3>
          <div className="card" style={{ padding: 0, overflow: "hidden" }}>
             <div className="table-container" style={{ margin: 0, borderRadius: 0, border: "none" }}>
               <table className="modern-table" style={{ margin: 0 }}>
                  <thead><tr><th>Control</th><th>Applicable</th><th>Implementation</th><th>Status</th></tr></thead>
                  <tbody>
                    {ad.soa.entries.slice(0, 5).map((entry, i) => (
                       <tr key={i}>
                         <td><strong>{entry.control_no}</strong> {entry.control_title}</td>
                         <td>{entry.applicable}</td>
                         <td>{entry.implementation}</td>
                         <td><span className={getBadgeClass(entry.implementation)}>{entry.implementation}</span></td>
                       </tr>
                    ))}
                  </tbody>
               </table>
             </div>
             <div style={{padding:"0.5rem 1rem", background:"var(--bg-main)", fontSize:"0.8rem", color:"var(--text-muted)"}}>Showing 5 of {ad.soa.entries.length} SoA entries.</div>
          </div>
        </div>
      )}

      {/* COMPLIANCE MATRIX */}
      {ad.sections && (
        <div style={{ borderTop: "2px solid var(--border-color)", paddingTop: "2.5rem", marginTop: "2.5rem" }}>
          <h3 style={{ fontSize: "1.5rem", fontWeight: 800, color: "var(--text-main)", marginBottom: "0.5rem" }}>6. Compliance Matrix</h3>
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
        </div>
      )}

      {/* VENDOR CHECKLIST */}
      {ad.vendor_checklist && ad.vendor_checklist.length > 0 && (
        <div style={{ borderTop: "2px solid var(--border-color)", paddingTop: "2.5rem", marginTop: "2.5rem" }}>
          <h3 style={{ fontSize: "1.5rem", fontWeight: 800, color: "var(--text-main)", marginBottom: "0.5rem" }}>7. Vendor Security Checklist</h3>
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
        </div>
      )}

      {/* TRAINING MATRIX */}
      {ad.training_matrix && ad.training_matrix.length > 0 && (
        <div style={{ borderTop: "2px solid var(--border-color)", paddingTop: "2.5rem", marginTop: "2.5rem" }}>
          <h3 style={{ fontSize: "1.5rem", fontWeight: 800, color: "var(--text-main)", marginBottom: "0.5rem" }}>8. Training Matrix</h3>
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
        </div>
      )}

      {/* GOVERNANCE CALENDAR */}
      {ad.governance_calendar && ad.governance_calendar.length > 0 && (
        <div style={{ borderTop: "2px solid var(--border-color)", paddingTop: "2.5rem", marginTop: "2.5rem", marginBottom: "4rem" }}>
          <h3 style={{ fontSize: "1.5rem", fontWeight: 800, color: "var(--text-main)", marginBottom: "0.5rem" }}>9. Governance Calendar</h3>
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
        </div>
      )}
      
    </PageContainer>
  );
}
