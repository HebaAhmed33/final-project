"use client";

import Link from "next/link";
import { useState, useEffect } from "react";

export default function MarketingHomePage() {
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchNewsPreview() {
      try {
        const res = await fetch("/api/news");
        const data = await res.json();
        // /api/news returns an array directly (up to 4 items already)
        if (Array.isArray(data)) {
          setNews(data.slice(0, 4));
        }
      } catch (err) {
        console.error("Failed to fetch news preview:", err);
      } finally {
        setLoading(false);
      }
    }
    fetchNewsPreview();
  }, []);

  return (
    <div style={{ flex: 1, display: "flex", flexDirection: "column", background: "#ffffff", minHeight: "100vh" }}>

      {/* Hero Section */}
      <section style={{
        padding: "6rem 2.5rem 4rem",
        textAlign: "center",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        background: "linear-gradient(180deg, #f8fafc 0%, #ffffff 100%)"
      }}>
        <p style={{
          fontSize: "1.05rem",
          color: "#64748b",
          lineHeight: 1.6,
          marginBottom: "3rem",
          maxWidth: "800px"
        }}>
          Gain full visibility into your assets, access requests, and security controls. Automate compliance
          processes and track risks with a centralized GRC dashboard.
        </p>

        <Link href="/onboarding" style={{ textDecoration: "none" }}>
          <button style={{
            background: "#1a2340",
            color: "#ffffff",
            border: "none",
            padding: "1rem 2.5rem",
            borderRadius: "99px",
            fontSize: "1.05rem",
            fontWeight: 600,
            cursor: "pointer",
            boxShadow: "0 10px 15px -3px rgba(0, 0, 0, 0.1)"
          }}>
            Get Started Now
          </button>
        </Link>

        {/* Dashboard Mockup Image */}
        <div style={{
          marginTop: "4rem",
          width: "100%",
          maxWidth: "1000px",
          borderRadius: "16px",
          overflow: "hidden",
          boxShadow: "0 40px 80px -20px rgba(0,0,0,0.2), 0 0 0 1px rgba(0,0,0,0.06)",
          background: "#ffffff"
        }}>
          <img
            src="/isms-image.png"
            alt="Aegis.One Security Dashboard"
            style={{ width: "100%", height: "auto", display: "block" }}
            onError={(e) => { e.target.onerror = null; e.target.src = "/isms-new.jpg"; }}
          />
        </div>

        <div style={{
          marginTop: "3rem",
          color: "#94a3b8",
          fontSize: "0.75rem",
          fontWeight: 700,
          letterSpacing: "0.1em",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: "0.5rem",
          textTransform: "uppercase"
        }}>
          SCROLL TO EXPLORE
          <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
          </svg>
        </div>
      </section>

      {/* Decorative Wave */}
      <div style={{ width: "100%", overflow: "hidden", lineHeight: 0 }}>
        <svg viewBox="0 0 1440 320" width="100%" height="auto" preserveAspectRatio="none" style={{ display: "block" }}>
          <path fill="#f8fafc" fillOpacity="1" d="M0,256L48,250.7C96,245,192,235,288,213.3C384,192,480,160,576,144C672,128,768,128,864,154.7C960,181,1056,235,1152,245.3C1248,256,1344,224,1392,208L1440,192L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"></path>
        </svg>
      </div>

      {/* Cybersecurity News & Trends Section */}
      <section style={{ padding: "5rem 2.5rem", background: "#ffffff" }}>
        <div style={{ maxWidth: "1200px", margin: "0 auto" }}>

          <div style={{ textAlign: "center", marginBottom: "3rem" }}>
            <h2 style={{ fontSize: "2rem", fontWeight: 800, color: "#1a2340", letterSpacing: "-0.03em", marginBottom: "1rem" }}>
              Cybersecurity News &amp; Trends
            </h2>
            <div style={{ width: "48px", height: "3px", background: "#f5c842", borderRadius: "2px", margin: "0 auto 1rem" }}></div>
            <p style={{ color: "#64748b", fontSize: "1rem", margin: 0 }}>
              Stay updated with the latest GRC, compliance, and risk management insights.
            </p>
          </div>

          {loading ? (
            <div style={{ textAlign: "center", padding: "3rem", color: "#64748b" }}>Loading...</div>
          ) : (
            <div style={{
              display: "grid",
              gridTemplateColumns: "repeat(2, 1fr)",
              gap: "1.5rem",
              maxWidth: "900px",
              margin: "0 auto"
            }}>
              {news.length > 0 ? news.map((item, idx) => (
                <a
                  key={idx}
                  href={item.link}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{ textDecoration: "none", color: "inherit" }}
                >
                  <div style={{
                    background: "#ffffff",
                    padding: "1.5rem",
                    borderRadius: "12px",
                    border: "1px solid #e2e8f0",
                    boxShadow: "0 2px 8px rgba(0,0,0,0.06)",
                    transition: "box-shadow 0.2s",
                    height: "100%",
                    display: "flex",
                    flexDirection: "column",
                    gap: "0.75rem"
                  }}
                    onMouseEnter={e => e.currentTarget.style.boxShadow = "0 8px 24px rgba(0,0,0,0.12)"}
                    onMouseLeave={e => e.currentTarget.style.boxShadow = "0 2px 8px rgba(0,0,0,0.06)"}
                  >
                    {/* Title */}
                    <h3 style={{
                      fontSize: "0.95rem",
                      fontWeight: 700,
                      color: idx === 0 ? "#b7791f" : "#1a2340",
                      lineHeight: 1.4,
                      margin: 0,
                      flex: 1
                    }}>
                      {item.title}
                    </h3>

                    {/* Source + Date row */}
                    <div style={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                      fontSize: "0.8rem",
                      color: "#94a3b8"
                    }}>
                      <div style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}>
                        {/* Newspaper icon */}
                        <svg width="13" height="13" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
                        </svg>
                        <span>{item.source || "The Hacker News"}</span>
                      </div>
                      <span>
                        {item.date
                          ? new Date(item.date).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })
                          : ""}
                      </span>
                    </div>
                  </div>
                </a>
              )) : (
                /* Fallback static cards if feed is empty */
                [
                  { title: "Google Blocks 8.3B Policy-Violating Ads in 2025, Launches Android 17 Privacy Overhaul", source: "The Hacker News", date: "Apr 17, 2026" },
                  { title: "NIST Limits CVE Enrichment After 263% Surge in Vulnerability Submissions", source: "The Hacker News", date: "Apr 17, 2026" },
                  { title: "Deterministic + Agentic AI: The Architecture Exposure Validation Requires", source: "The Hacker News", date: "Apr 15, 2026" },
                  { title: "Google Adds Rust-Based DNS Parser into Pixel 10 Modem to Enhance Security", source: "The Hacker News", date: "Apr 14, 2026" },
                ].map((item, idx) => (
                  <div key={idx} style={{
                    background: "#ffffff",
                    padding: "1.5rem",
                    borderRadius: "12px",
                    border: "1px solid #e2e8f0",
                    boxShadow: "0 2px 8px rgba(0,0,0,0.06)",
                    display: "flex",
                    flexDirection: "column",
                    gap: "0.75rem"
                  }}>
                    <h3 style={{
                      fontSize: "0.95rem",
                      fontWeight: 700,
                      color: idx === 0 ? "#b7791f" : "#1a2340",
                      lineHeight: 1.4,
                      margin: 0,
                      flex: 1
                    }}>
                      {item.title}
                    </h3>
                    <div style={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                      fontSize: "0.8rem",
                      color: "#94a3b8"
                    }}>
                      <div style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}>
                        <svg width="13" height="13" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
                        </svg>
                        <span>{item.source}</span>
                      </div>
                      <span>{item.date}</span>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}
        </div>
      </section>

      {/* Footer */}
      <footer style={{ padding: "3rem 2.5rem", textAlign: "center", borderTop: "1px solid #f1f5f9", background: "#ffffff", color: "#94a3b8", fontSize: "0.95rem", fontWeight: 500 }}>
        © {new Date().getFullYear()} Aegis.One by SmartISMS. Enterprise GRC &amp; Security Intelligence. All rights reserved.
      </footer>
    </div>
  );
}
