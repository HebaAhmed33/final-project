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
            Gain full visibility into your assets, access requests, and security controls. Automate compliance processes and track risks with a centralized GRC dashboard.
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

      {/* SECURITY OVERVIEW (DASHBOARD PREVIEW) */}
      <section id="overview" className="relative z-10 max-w-5xl mx-auto px-4 mt-20 mb-32">
        <div className="bg-white rounded-xl shadow-[0_20px_50px_rgba(0,0,0,0.1)] border border-slate-200 overflow-visible relative">
          {/* Mac window header */}
          <div className="bg-[#333333] px-4 py-3 flex items-center gap-2 rounded-t-xl">
            <div className="w-3 h-3 rounded-full bg-[#ff5f56]"></div>
            <div className="w-3 h-3 rounded-full bg-[#ffbd2e]"></div>
            <div className="w-3 h-3 rounded-full bg-[#27c93f]"></div>
          </div>
          
          <div className="p-8 md:p-14 flex flex-col md:flex-row gap-16 bg-white rounded-b-xl">
            {/* Left side: Bars */}
            <div className="flex-1 space-y-10">
              <div>
                <div className="bg-gradient-to-r from-[#8ca8a0] to-[#59698d] text-white rounded-md px-5 py-3 font-semibold mb-6 shadow-sm">
                  Security Score
                </div>
                <div className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-8">
                  Risk Assessment: APR 2025 – APR 2026
                </div>

                {/* Network Security Bar */}
                <div className="mb-10">
                  <div className="flex items-center gap-2 font-bold text-[#1a2340] mb-3 text-[15px]">
                    <svg className="w-3 h-3 text-slate-600" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" /></svg>
                    Network Security
                  </div>
                  <div className="flex items-baseline gap-3 mb-3 border-l-2 border-slate-200 pl-4 ml-1">
                    <span className="text-[2.5rem] font-extrabold text-[#1a2340] leading-none">95</span>
                    <span className="text-[#649e73] font-bold text-xl">Good</span>
                  </div>
                  <div className="flex h-2.5 gap-1.5 rounded-full overflow-hidden mt-4">
                    <div className="flex-1 bg-[#cc4f4f] rounded-l-full"></div>
                    <div className="flex-1 bg-[#eebb66]"></div>
                    <div className="flex-1 bg-[#f4d03f]"></div>
                    <div className="flex-1 bg-[#2c3e50]"></div>
                    <div className="flex-1 bg-[#649e73] rounded-r-full"></div>
                  </div>
                  <div className="flex justify-between text-[9px] text-slate-400 mt-2 font-bold uppercase tracking-wider">
                    <span className="w-1/5 text-center leading-tight">Below 50<br/>(Poor)</span>
                    <span className="w-1/5 text-center leading-tight">50-69<br/>(Average)</span>
                    <span className="w-1/5 text-center leading-tight text-[#f4d03f]">70-89<br/>(Good)</span>
                    <span className="w-1/5 text-center leading-tight">90-99<br/>(Very Good)</span>
                    <span className="w-1/5 text-center leading-tight">100<br/>(Excellent)</span>
                  </div>
                </div>

                {/* Access Compliance Bar */}
                <div>
                  <div className="flex items-center gap-2 font-bold text-[#1a2340] mb-3 text-[15px]">
                    <svg className="w-3 h-3 text-slate-600" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" /></svg>
                    Access Compliance
                  </div>
                  <div className="flex items-baseline gap-3 mb-3 border-l-2 border-slate-200 pl-4 ml-1">
                    <span className="text-[2.5rem] font-extrabold text-[#1a2340] leading-none">100</span>
                    <span className="text-[#649e73] font-bold text-xl">Excellent</span>
                  </div>
                  <div className="flex h-2.5 gap-1.5 rounded-full overflow-hidden mt-4">
                    <div className="flex-1 bg-[#cc4f4f] rounded-l-full"></div>
                    <div className="flex-1 bg-[#eebb66]"></div>
                    <div className="flex-1 bg-[#f4d03f]"></div>
                    <div className="flex-1 bg-[#2c3e50]"></div>
                    <div className="flex-1 bg-[#649e73] rounded-r-full"></div>
                  </div>
                </div>
              </div>
            </div>

            {/* Right side: Gauge Chart */}
            <div className="flex-1 flex flex-col items-center justify-center relative mt-8 md:mt-0">
              <h3 className="text-3xl font-bold text-[#1a2340] mb-8 tracking-wide" style={{ fontFamily: "Georgia, serif", transform: "rotate(-10deg) translateY(10px)" }}>
                Security Risk analysis
              </h3>
              
              {/* Complex Gauge Recreation */}
              <div className="relative w-[300px] h-[150px] overflow-hidden mb-8">
                {/* Gauge segments using SVG for exact matching */}
                <svg viewBox="0 0 200 100" className="w-full h-full">
                  {/* Red segment */}
                  <path d="M 20 100 A 80 80 0 0 1 50 35" fill="none" stroke="#cc4f4f" strokeWidth="35" />
                  {/* Yellow segment */}
                  <path d="M 54 31 A 80 80 0 0 1 125 21" fill="none" stroke="#eebb66" strokeWidth="35" />
                  {/* Dark blue segment */}
                  <path d="M 130 22 A 80 80 0 0 1 180 100" fill="none" stroke="#2c3e50" strokeWidth="35" />
                  {/* Green segment overlapping */}
                  <path d="M 140 100 A 80 80 0 0 0 180 100" fill="none" stroke="#649e73" strokeWidth="35" />
                  
                  {/* Inner dial lines */}
                  <line x1="100" y1="100" x2="60" y2="40" stroke="#fff" strokeWidth="3" />
                  <line x1="100" y1="100" x2="140" y2="40" stroke="#fff" strokeWidth="3" />
                  
                  {/* Decorative stars */}
                  <path d="M 70 70 L 73 78 L 81 78 L 75 83 L 77 91 L 70 86 L 63 91 L 65 83 L 59 78 L 67 78 Z" fill="none" stroke="#f4d03f" strokeWidth="1" />
                  <path d="M 140 60 L 142 66 L 148 66 L 143 70 L 145 76 L 140 72 L 135 76 L 137 70 L 132 66 L 138 66 Z" fill="none" stroke="#f4d03f" strokeWidth="1" />
                </svg>

                {/* Score in middle */}
                <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex flex-col items-center bg-white rounded-t-full pt-4 px-8">
                  <span className="text-[4rem] font-black text-[#1a2340] leading-none tracking-tighter">95</span>
                  <span className="text-[13px] font-bold text-slate-500 mt-1">Security Score</span>
                </div>
                
                {/* Arrow pointer */}
                <div className="absolute bottom-8 right-6 w-0 h-0 border-t-[8px] border-t-transparent border-l-[12px] border-l-[#1a2340] border-b-[8px] border-b-transparent transform -rotate-12"></div>
              </div>

              {/* Floating Tooltip matching design */}
              <div className="absolute bottom-0 right-[-2rem] bg-white rounded-xl shadow-[0_10px_30px_rgba(0,0,0,0.15)] border border-slate-100 max-w-[220px] text-center z-20 translate-y-8 flex flex-col overflow-hidden">
                <div className="bg-[#4a4a4a] h-6 w-full"></div>
                <div className="p-5 flex flex-col items-center">
                  <div className="w-7 h-7 rounded-full bg-[#f4d03f] flex items-center justify-center mb-3">
                    <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={3}><path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7"/></svg>
                  </div>
                  <p className="text-[12px] font-bold text-[#1a2340] leading-snug">
                    Spot early warning indicators of security risks and compliance gaps
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
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

