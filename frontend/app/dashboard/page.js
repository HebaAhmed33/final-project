"use client";

import Link from "next/link";
import PageContainer from "../components/PageContainer";

const SYSTEM_METRICS = [
  {
    label: "Active Frameworks",
    value: "6",
    trend: "+2 this quarter",
    color: "rgba(16, 185, 129, 0.1)", // Green
    iconColor: "#10B981",
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
      </svg>
    ),
  },
  {
    label: "Configuration Nodes",
    value: "142",
    trend: "fully audited",
    color: "rgba(59, 130, 246, 0.1)", // Blue
    iconColor: "#3B82F6",
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
      </svg>
    ),
  },
  {
    label: "Historical Reports",
    value: "24",
    trend: "ready for export",
    color: "rgba(139, 92, 246, 0.1)", // Purple
    iconColor: "#8B5CF6",
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
    ),
  },
  {
    label: "Latest Intelligence",
    value: "live",
    trend: "threat feeds active",
    color: "rgba(245, 158, 11, 0.1)", // Yellow
    iconColor: "#F59E0B",
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
         <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
      </svg>
    ),
  }
];

const CARDS = [
  {
    href: "/assessment",
    title: "Assessment Workflow",
    desc: "Execute full cross-framework compliance evaluations against ISO 27001, NIST, and HIPAA standards.",
    btnLabel: "Start Assessment",
    icon: (
      <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
      </svg>
    )
  },
  {
    href: "/config-analysis",
    title: "Configuration Analysis",
    desc: "Scan infrastructure blueprints and detect deep operational drift against rigid technical baselines.",
    btnLabel: "Analyze Config",
    icon: (
      <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
      </svg>
    )
  },
  {
    href: "/reports",
    title: "Executive Report Center",
    desc: "Access chronological audit trails, risk registers, and generate polished C-level PDF specifications.",
    btnLabel: "View Reports",
    icon: (
      <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
    )
  },
  {
    href: "/news",
    title: "Live Intelligence Feed",
    desc: "Monitor aggregated GRC updates, global breach disclosures, and emerging cybersecurity threats.",
    btnLabel: "Access Intelligence",
    icon: (
      <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
      </svg>
    )
  }
];

export default function Home() {
  return (
    <PageContainer>
      {/* Hero Header Area */}
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
          Welcome to <span style={{ color: "var(--primary)" }}>SmartISMS</span>
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
          Your unified Information Security Management System platform. Streamline complex compliance architectures, 
          manage global risk vectors, and synchronize actionable threat intelligence directly from this unified command center.
        </p>
      </div>

      {/* Summary / Metric Strip */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "1.25rem", marginBottom: "3.5rem" }}>
        {SYSTEM_METRICS.map((metric, idx) => (
          <div key={idx} className="card" style={{ display: "flex", flexDirection: "column", padding: "1.5rem", position: "relative", overflow: "hidden" }}>
            <div style={{ position: "absolute", top: "-1rem", right: "-1rem", opacity: 0.05, color: metric.iconColor, transform: "scale(3)" }}>
              {metric.icon}
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.5rem" }}>
               <div style={{ width: "24px", height: "24px", color: metric.iconColor, background: metric.color, borderRadius: "6px", display: "flex", alignItems: "center", justifyContent: "center" }}>
                 {metric.icon}
               </div>
               <h3 style={{ fontSize: "0.85rem", fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.05em", margin: 0 }}>
                 {metric.label}
               </h3>
            </div>
            <div style={{ fontSize: "2rem", fontWeight: 800, color: "var(--text-main)", margin: "0.5rem 0 0.25rem 0", lineHeight: "1" }}>
              {metric.value}
            </div>
            <div style={{ fontSize: "0.8rem", color: "var(--text-muted)", fontWeight: 500 }}>
              {metric.trend}
            </div>
          </div>
        ))}
      </div>

      {/* Quick Actions (Navigation Grid) */}
      <div style={{ marginBottom: "3rem" }}>
        <h2 style={{ fontSize: "1.25rem", fontWeight: 700, color: "var(--text-main)", marginBottom: "1.25rem" }}>
          Workspace Modules
        </h2>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: "1.5rem" }}>
          {CARDS.map((card) => (
            <Link key={card.href} href={card.href} style={{ display: "block", textDecoration: "none" }}>
              <div 
                className="card" 
                style={{ 
                  display: "flex", 
                  flexDirection: "column", 
                  height: "100%", 
                  cursor: "pointer",
                  position: "relative",
                  border: "1px solid var(--border-color)",
                }}
              >
                <div style={{ display: "flex", alignItems: "flex-start", gap: "1.25rem", marginBottom: "1.5rem" }}>
                  <div style={{ color: "var(--primary)", padding: "0.6rem", background: "rgba(37, 99, 235, 0.08)", borderRadius: "10px" }}>
                    {card.icon}
                  </div>
                  <div>
                    <h3 style={{ fontSize: "1.15rem", fontWeight: 700, marginBottom: "0.35rem", color: "var(--text-main)", letterSpacing: "-0.01em" }}>
                      {card.title}
                    </h3>
                    <p style={{ color: "var(--text-muted)", fontSize: "0.9rem", margin: 0, lineHeight: "1.5" }}>
                      {card.desc}
                    </p>
                  </div>
                </div>
                
                <div style={{ marginTop: "auto", display: "flex", justifyContent: "flex-end", alignItems: "center", borderTop: "1px solid var(--border-color)", paddingTop: "1rem" }}>
                  <span 
                    style={{ 
                      fontSize: "0.85rem", 
                      fontWeight: 600, 
                      color: "var(--primary)", 
                      display: "flex", 
                      alignItems: "center", 
                      gap: "0.35rem" 
                    }}
                  >
                    {card.btnLabel}
                    <svg style={{ width: "16px", height: "16px" }} fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                    </svg>
                  </span>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </PageContainer>
  );
}
