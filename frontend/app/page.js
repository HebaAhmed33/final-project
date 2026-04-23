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
    <div className="min-h-screen bg-white font-sans text-slate-900">
      {/* BACKGROUND EFFECTS */}
      <div className="absolute top-0 left-0 w-full h-[100vh] overflow-hidden -z-10 bg-gradient-to-b from-white to-[#f1f5f9]">
        <style>{`
          @keyframes slowFloat1 {
            0%, 100% { transform: translate(0, 0) scale(1); }
            50% { transform: translate(1%, 2%) scale(1.05); }
          }
          @keyframes slowFloat2 {
            0%, 100% { transform: translate(0, 0) scale(1); }
            50% { transform: translate(-1%, -1%) scale(0.95); }
          }
          @keyframes waterWave {
            0% { transform: translateX(0); }
            100% { transform: translateX(-50%); }
          }
          @keyframes waterWaveReverse {
            0% { transform: translateX(-50%); }
            100% { transform: translateX(0); }
          }
        `}</style>
        
        {/* Very subtle background gradient motion */}
        <div style={{ animation: 'slowFloat1 25s ease-in-out infinite' }} className="absolute top-[5%] left-[-10%] w-[60%] h-[70%] rounded-full bg-slate-200/30 blur-[120px] pointer-events-none" />
        <div style={{ animation: 'slowFloat2 30s ease-in-out infinite' }} className="absolute top-[10%] right-[-10%] w-[50%] h-[80%] rounded-full bg-blue-100/20 blur-[120px] pointer-events-none" />
        
        {/* Animated continuous layered water waves */}
        <div className="absolute bottom-0 left-0 w-[200%] h-[150px] md:h-[220px] origin-bottom pointer-events-none">
          <svg viewBox="0 0 2400 120" preserveAspectRatio="none" className="absolute bottom-0 w-full h-full text-[#e2e8f0]">
            <path fill="currentColor" opacity="0.5" style={{ animation: 'waterWave 30s linear infinite' }} d="M0,60 C300,120 300,0 600,60 C900,120 900,0 1200,60 C1500,120 1500,0 1800,60 C2100,120 2100,0 2400,60 L2400,120 L0,120 Z" />
            <path fill="currentColor" opacity="0.75" style={{ animation: 'waterWaveReverse 25s linear infinite' }} d="M0,50 C300,110 300,-10 600,50 C900,110 900,-10 1200,50 C1500,110 1500,-10 1800,50 C2100,110 2100,-10 2400,50 L2400,120 L0,120 Z" />
            <path fill="currentColor" opacity="1.0" style={{ animation: 'waterWave 20s linear infinite' }} d="M0,70 C300,130 300,10 600,70 C900,130 900,10 1200,70 C1500,130 1500,10 1800,70 C2100,130 2100,10 2400,70 L2400,120 L0,120 Z" />
          </svg>
        </div>
      </div>

      {/* HERO SECTION */}
      <section className="relative flex flex-col items-center justify-center text-center px-4 min-h-[85vh] pt-20 pb-10 z-10">
        
        <div className="flex flex-col items-center justify-center w-full max-w-4xl mx-auto">
          {/* 1) Main Title */}
          <h1 className="text-[2.5rem] md:text-[3.75rem] lg:text-[4.2rem] font-extrabold text-[#1a2340] tracking-tight leading-[1.2] mb-6 whitespace-nowrap">
            <span className="bg-[#fce69a] px-3 py-1 inline-block">ISMS Compliance</span> Platform
          </h1>
          
          {/* 2) Subtitle */}
          <h2 className="text-[1.1rem] md:text-[1.35rem] text-[#64748b] font-medium mb-8">
            to manage security, risk, and governance in one place
          </h2>
          
          {/* 3) Description */}
          <p className="text-[0.95rem] md:text-[1rem] text-[#94a3b8] mb-12 max-w-[650px] leading-[1.6] mx-auto font-normal">
            Gain full visibility into your assets, access requests, and security controls. Automate compliance processes and track risks with a centralized GRC platform.
          </p>
          
          {/* 4) Button */}
          <div>
            <Link href="/onboarding">
              <button className="bg-[#1a2340] hover:bg-[#111827] text-white px-9 py-4 rounded-full font-semibold text-[15px] transition-all shadow-[0_4px_10px_rgba(26,35,64,0.15)] hover:shadow-[0_6px_15px_rgba(26,35,64,0.2)]">
                Get Started Now
              </button>
            </Link>
          </div>
        </div>

        {/* Scroll indicator */}
        <button 
          onClick={() => {
            const el = document.getElementById('overview');
            if (el) el.scrollIntoView({ behavior: 'smooth' });
          }}
          className="mb-8 text-[#cbd5e1] hover:text-[#94a3b8] text-[9px] font-bold tracking-[0.25em] uppercase flex flex-col items-center gap-2 cursor-pointer transition-colors z-20 relative"
        >
          SCROLL TO EXPLORE
          <svg className="w-4 h-4 mt-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M19 14l-7 7m0 0l-7-7m7 7V3" />
          </svg>
        </button>
      </section>



      {/* Cybersecurity News & Trends Section */}
      <section className="py-20 px-6 bg-slate-50 border-t border-slate-200">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-extrabold text-[#1a2340] tracking-tight mb-5">
              Cybersecurity News & Trends
            </h2>
            <div className="w-16 h-1.5 bg-[#fce69a] rounded-full mx-auto mb-5"></div>
            <p className="text-slate-500 text-lg font-medium">
              Stay updated with the latest GRC, compliance, and risk management insights.
            </p>
          </div>

          {loading ? (
            <div className="text-center py-12 text-slate-500 font-bold">Loading news feed...</div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto">
              {news.length > 0 ? news.map((item, idx) => (
                <a
                  key={idx}
                  href={item.link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block group"
                >
                  <div className="bg-white p-7 rounded-2xl border border-slate-200 shadow-sm hover:shadow-[0_8px_30px_rgba(0,0,0,0.08)] transition-all h-full flex flex-col hover:-translate-y-1">
                    <h3 className="text-[16px] font-bold text-[#1a2340] mb-5 flex-1 leading-relaxed group-hover:text-blue-700 transition-colors">
                      {item.title}
                    </h3>
                    <div className="flex items-center justify-between text-[11px] text-slate-400 font-bold uppercase tracking-widest">
                      <div className="flex items-center gap-2">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z"/></svg>
                        {item.source || "Security Feed"}
                      </div>
                      <span>{item.date ? new Date(item.date).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" }) : ""}</span>
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
                  <div key={idx} className="bg-white p-7 rounded-2xl border border-slate-200 shadow-sm h-full flex flex-col">
                    <h3 className="text-[16px] font-bold text-[#1a2340] mb-5 flex-1 leading-relaxed">
                      {item.title}
                    </h3>
                    <div className="flex items-center justify-between text-[11px] text-slate-400 font-bold uppercase tracking-widest">
                      <div className="flex items-center gap-2">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z"/></svg>
                        {item.source}
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
      <footer className="py-12 text-center bg-white text-slate-400 text-sm font-bold tracking-wide">
        © {new Date().getFullYear()} Aegis.One by SmartISMS. Enterprise GRC & Security Intelligence. All rights reserved.
      </footer>
    </div>
  );
}

