"use client";

import Link from "next/link";
import { useState, useEffect } from "react";

export default function MarketingHomePage() {
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newsError, setNewsError] = useState("");

  useEffect(() => {
    async function fetchNewsPreview() {
      try {
        const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
        const res = await fetch(`${API_BASE_URL}/news`);
        if (res.headers.get("content-type")?.includes("text/html")) {
          throw new Error("API returned HTML instead of JSON");
        }
        if (!res.ok) {
          throw new Error("News API request failed");
        }
        const data = await res.json();
        const articles = data.articles || [];
        if (Array.isArray(articles) && articles.length > 0) {
          setNews(articles.slice(0, 6));
          setNewsError("");
        } else {
          setNews([]);
          setNewsError(data.error || "No articles available right now.");
        }
      } catch (err) {
        console.error("Failed to fetch news:", err);
        setNews([]);
        setNewsError("Unable to load live news right now. Please try again later.");
      } finally {
        setLoading(false);
      }
    }
    fetchNewsPreview();
  }, []);

  return (
    <div className="bg-[#F7F8FC] font-sans text-slate-900 relative">
      {/* HERO SECTION */}
      <section className="relative flex flex-col items-center justify-start w-full z-10 overflow-hidden" style={{ height: "calc(100vh - 68px)", minHeight: "600px", paddingTop: "115px" }}>
        
        {/* WAVE BACKGROUND */}
        <div className="absolute bottom-0 left-0 w-full z-0 pointer-events-none" style={{ height: "180px", color: "#EEF0F6" }}>
          <style>{`
            @keyframes waveDrift {
              0% { transform: translateX(0); }
              50% { transform: translateX(-2%); }
              100% { transform: translateX(0); }
            }
          `}</style>
          <svg viewBox="0 0 1440 180" preserveAspectRatio="none" style={{ width: "110%", height: "100%", animation: "waveDrift 15s ease-in-out infinite", marginLeft: "-5%" }}>
            <path fill="currentColor" d="M0,180L0,80C400,160,600,0,1000,40C1200,60,1350,140,1440,140L1440,180Z" />
          </svg>
        </div>

        <div className="relative flex flex-col items-center w-full max-w-[1060px] mx-auto text-center px-4 z-10">
          {/* 1) Main Title */}
          <h1 className="whitespace-normal md:whitespace-nowrap text-[#111936] dark:text-slate-100" style={{
            fontSize: "48px",
            fontWeight: 900,
            letterSpacing: "-0.02em",
            lineHeight: 1.1,
            margin: 0
          }}>
            <span className="text-[#111936]" style={{
              backgroundColor: "#F8E98F",
              padding: "6px 8px",
              borderRadius: "4px",
              marginRight: "10px",
              display: "inline-block",
              lineHeight: 1
            }}>ISMS Compliance</span>
            Platform
          </h1>
          
          {/* 2) Subtitle */}
          <h2 className="text-[#303545] dark:text-slate-300" style={{
            fontSize: "23px",
            fontWeight: 600,
            marginTop: "26px",
            marginBottom: 0
          }}>
            to manage security, risk, and governance in one place
          </h2>
          
          {/* 3) Description */}
          <p className="text-[#777B8A] dark:text-slate-400" style={{
            fontSize: "15.5px",
            marginTop: "28px",
            maxWidth: "650px",
            lineHeight: 1.7,
            marginBottom: 0
          }}>
            Gain full visibility into your assets, access requests, and security controls. Automate compliance<br className="hidden md:block" /> processes and track risks with a centralized GRC dashboard.
          </p>
          
          {/* 4) Button */}
          <Link href="/onboarding" style={{ marginTop: "38px" }}>
            <button style={{
              background: "#151B3A",
              color: "#ffffff",
              border: "none",
              borderRadius: "999px",
              width: "185px",
              height: "52px",
              fontWeight: 700,
              fontSize: "15px",
              cursor: "pointer",
              boxShadow: "0 6px 15px rgba(21, 27, 58, 0.15)",
              transition: "transform 0.2s"
            }}
            onMouseOver={(e) => e.currentTarget.style.transform = "scale(1.02)"}
            onMouseOut={(e) => e.currentTarget.style.transform = "scale(1)"}
            >
              Get Started Now
            </button>
          </Link>
        </div>

        {/* Scroll indicator */}
        <div style={{ marginTop: "85px", display: "flex", flexDirection: "column", alignItems: "center", gap: "6px", zIndex: 10 }}>
          <style>{`
            @keyframes bounceSmall {
              0%, 100% { transform: translateY(0); }
              50% { transform: translateY(4px); }
            }
          `}</style>
          <span className="text-[#AEB3C2] dark:text-slate-400" style={{
            fontSize: "9px",
            fontWeight: 700,
            letterSpacing: "0.25em",
            textTransform: "uppercase"
          }}>
            SCROLL TO EXPLORE
          </span>
          <svg width="12" height="12" fill="none" className="stroke-[#AEB3C2] dark:stroke-slate-400" strokeWidth="2" viewBox="0 0 24 24" style={{ animation: "bounceSmall 2s infinite" }}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M19 14l-7 7m0 0l-7-7m7 7V3" />
          </svg>
        </div>
      </section>

      {/* DASHBOARD PREVIEW SECTION */}
      <section className="relative z-10 w-full flex justify-center px-4 pb-24" style={{ paddingTop: '80px' }}>
        <style>{`
          @keyframes browserFadeUp {
            0% { opacity: 0; transform: translateY(40px); }
            100% { opacity: 1; transform: translateY(0); }
          }
          @keyframes floatCard {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
          }
          @keyframes pulseStar {
            0%, 100% { transform: scale(1); opacity: 0.5; }
            50% { transform: scale(1.15); opacity: 1; }
          }
          @keyframes gaugeDraw {
            0% { opacity: 0; transform: scale(0.9); }
            100% { opacity: 1; transform: scale(1); }
          }
        `}</style>
        
        <div 
          className="w-full max-w-[900px] bg-white rounded-[10px] shadow-[0_25px_70px_-15px_rgba(0,0,0,0.12)] overflow-hidden flex flex-col"
          style={{ height: '560px', animation: 'browserFadeUp 1s ease-out forwards' }}
        >
          {/* Browser Top Bar */}
          <div className="h-[34px] bg-[#33363D] flex items-center px-4 gap-[8px] flex-shrink-0">
            <div className="w-[11px] h-[11px] rounded-full bg-[#FF5F56]"></div>
            <div className="w-[11px] h-[11px] rounded-full bg-[#FFBD2E]"></div>
            <div className="w-[11px] h-[11px] rounded-full bg-[#27C93F]"></div>
          </div>

          {/* Browser Content */}
          <div className="flex w-full h-full" style={{ padding: '46px 42px' }}>
            
            {/* Left Column: Scores (48%) */}
            <div style={{ width: '48%' }} className="flex flex-col pr-4">
              {/* Gradient Label Bar */}
              <div 
                className="bg-gradient-to-r from-[#88B097] to-[#60729A] text-white font-medium rounded-[6px] shadow-sm flex items-center"
                style={{ width: '410px', height: '44px', paddingLeft: '20px', fontSize: '15px' }}
              >
                Security Score
              </div>
              
              <div className="text-[11px] text-[#AEB3C2] dark:text-slate-400 font-semibold tracking-wide uppercase" style={{ marginTop: '22px', marginBottom: '32px' }}>
                Risk Assessment <span className="text-[#303545] dark:text-slate-300 font-bold ml-2">APR 2025 - APR 2026</span>
              </div>

              {/* Block 1: Network Security */}
              <div style={{ marginBottom: '36px' }}>
                <div className="flex items-center gap-2 mb-2 text-[#111936] dark:text-slate-100 font-bold text-[15px]">
                  <svg className="w-[10px] h-[10px] text-[#777B8A] dark:text-slate-400" fill="currentColor" viewBox="0 0 20 20"><path d="M5 4l10 6-10 6V4z"/></svg>
                  Network Security
                </div>
                <div className="flex items-baseline gap-3 mb-4">
                  <span className="text-[42px] font-black text-[#111936] dark:text-slate-100 leading-none tracking-tight">95</span>
                  <span className="text-[18px] font-semibold text-[#59A26A]">Good</span>
                </div>
                {/* Scale */}
                <div className="flex gap-1 h-[6px] w-full mb-3">
                  <div className="bg-[#D34D41] flex-1 rounded-l-sm"></div>
                  <div className="bg-[#E97A3B] flex-1"></div>
                  <div className="bg-[#F6C644] flex-1"></div>
                  <div className="bg-[#111936] dark:bg-slate-400 flex-1"></div>
                  <div className="bg-[#59A26A] flex-1 rounded-r-sm"></div>
                </div>
                <div className="flex justify-between text-[10px] text-[#AEB3C2] dark:text-slate-400 font-semibold leading-tight text-center px-1">
                  <span className="w-1/5 text-left">Below 50<br/>(Poor)</span>
                  <span className="w-1/5">50-69<br/>(Average)</span>
                  <span className="w-1/5">70-89<br/>(Good)</span>
                  <span className="w-1/5">90-99<br/>(Very Good)</span>
                  <span className="w-1/5 text-right">100<br/>(Excellent)</span>
                </div>
              </div>

              {/* Block 2: Access Compliance */}
              <div className="mb-4">
                <div className="flex items-center gap-2 mb-2 text-[#111936] dark:text-slate-100 font-bold text-[16px]">
                  <svg className="w-[10px] h-[10px] text-[#777B8A] dark:text-slate-400" fill="currentColor" viewBox="0 0 20 20"><path d="M5 4l10 6-10 6V4z"/></svg>
                  Access Compliance
                </div>
                <div className="flex items-baseline gap-3 mb-4">
                  <span className="text-[42px] font-black text-[#111936] dark:text-slate-100 leading-none tracking-tight">100</span>
                  <span className="text-[18px] font-semibold text-[#59A26A]">Excellent</span>
                </div>
                {/* Scale */}
                <div className="flex gap-1 h-[6px] w-full mb-3">
                  <div className="bg-[#D34D41] flex-1 rounded-l-sm"></div>
                  <div className="bg-[#E97A3B] flex-1"></div>
                  <div className="bg-[#F6C644] flex-1"></div>
                  <div className="bg-[#111936] flex-1"></div>
                  <div className="bg-[#59A26A] flex-1 rounded-r-sm"></div>
                </div>
              </div>
            </div>

            {/* Right Column: Gauge (52%) */}
            <div style={{ width: '52%' }} className="relative flex justify-center items-start pt-2">
              
              <div className="relative flex justify-center w-[360px]">
                <svg viewBox="0 0 360 220" className="w-full overflow-visible" style={{ animation: 'gaugeDraw 1.2s ease-out forwards' }}>
                  <defs>
                    <path id="curveText" d="M 40 170 A 130 130 0 0 1 320 170" fill="none" />
                  </defs>
                  
                  {/* Curved Text */}
                  <text className="fill-[#111936] dark:fill-slate-100 font-bold text-[26px]" style={{ fontFamily: 'Georgia, serif', letterSpacing: '0.02em' }}>
                    <textPath href="#curveText" startOffset="50%" textAnchor="middle">Security Risk analysis</textPath>
                  </text>

                  {/* Gauge Arcs (cx=180, cy=180, r=110) -> Circumference=691.15, Half=345.57. Dash=63, gap=1000 */}
                  <circle cx="180" cy="180" r="110" fill="none" stroke="#D34D41" strokeWidth="42" strokeDasharray="65 1000" strokeDashoffset="-345.57" />
                  <circle cx="180" cy="180" r="110" fill="none" stroke="#E97A3B" strokeWidth="42" strokeDasharray="65 1000" strokeDashoffset="-414.68" />
                  <circle cx="180" cy="180" r="110" fill="none" stroke="#F6C644" strokeWidth="42" strokeDasharray="65 1000" strokeDashoffset="-483.80" />
                  <circle cx="180" cy="180" r="110" fill="none" className="stroke-[#111936] dark:stroke-slate-400" strokeWidth="42" strokeDasharray="65 1000" strokeDashoffset="-552.92" />
                  <circle cx="180" cy="180" r="110" fill="none" stroke="#59A26A" strokeWidth="42" strokeDasharray="65 1000" strokeDashoffset="-622.03" />
                  
                  {/* Pointer Arrow on Green */}
                  <polygon points="280,170 292,175 280,180" className="fill-[#111936] dark:fill-slate-100" transform="rotate(18 286 175)" />

                  {/* Center Text */}
                  <text x="180" y="165" textAnchor="middle" className="text-[76px] font-black fill-[#111936] dark:fill-slate-100 tracking-tighter">95</text>
                  <text x="180" y="195" textAnchor="middle" className="text-[14px] font-bold fill-[#777B8A] dark:fill-slate-400">Security Score</text>

                  {/* Decorative Stars */}
                  <path style={{ animation: 'pulseStar 3s infinite ease-in-out' }} className="text-[#F6C644] fill-transparent stroke-current" strokeWidth="2" d="M125 125l3-8 3 8 8 1-6 6 2 8-8-5-8 5 2-8-6-6 8-1z" />
                  <path style={{ animation: 'pulseStar 3s infinite ease-in-out 1s' }} className="text-[#F6C644] fill-transparent stroke-current" strokeWidth="2" d="M235 135l2-5 2 5 5 1-4 4 1 5-5-3-5 3 1-5-4-4 5-1z" />
                  <path style={{ animation: 'pulseStar 3s infinite ease-in-out 2s' }} className="text-[#F6C644] fill-transparent stroke-current" strokeWidth="2" d="M140 215l2-6 2 6 6 1-4 5 1 6-6-4-6 4 1-6-4-5 6-1z" />
                  <path d="M 145 220 Q 130 270 200 270" fill="none" stroke="#F6C644" strokeWidth="2" strokeDasharray="4 4" className="opacity-60" />
                  <polygon points="200,265 210,270 200,275" fill="#F6C644" className="opacity-80" />
                </svg>

                {/* Floating Insight Card */}
                <div 
                  className="absolute right-[-40px] bottom-[-70px] bg-white pt-4 pb-5 px-5 rounded-[12px] shadow-[0_15px_35px_rgba(0,0,0,0.12)] w-[210px] z-20 flex flex-col items-center text-center border border-slate-50 dark:border-slate-800"
                  style={{ animation: 'floatCard 6s ease-in-out infinite' }}
                >
                  <div className="w-[32px] h-[32px] rounded-full bg-[#F6C644] text-white flex items-center justify-center mb-3 shadow-sm mt-[-28px] border-[3px] border-white dark:border-slate-800 relative z-10">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="4" d="M5 13l4 4L19 7"/></svg>
                  </div>
                  <div className="absolute top-0 left-0 w-full h-8 bg-[#33363D] dark:bg-[#1E293B] rounded-t-[12px]"></div>
                  <p className="text-[11px] font-bold text-[#111936] dark:text-slate-100 leading-[1.6] mt-1 relative z-10">
                    Spot early warning<br/>indicators of security risks<br/>and compliance gaps
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
            <div className="text-center py-12 text-slate-500 dark:text-slate-400 font-bold">Loading news feed...</div>
          ) : news.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto">
              {news.map((item, idx) => (
                <a
                  key={idx}
                  href={item.url || item.link || "#"}
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
                      <span>{item.published_at ? new Date(item.published_at).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" }) : ""}</span>
                    </div>
                  </div>
                </a>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <p className="text-slate-500 dark:text-slate-400 font-medium text-base">{newsError || "No articles available right now."}</p>
            </div>
          )}
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 text-center bg-white text-slate-400 text-sm font-bold tracking-wide relative">
        © {new Date().getFullYear()} Aegis.One by SmartISMS. Enterprise GRC & Security Intelligence. All rights reserved.
        <Link href="/admin-login" className="absolute bottom-4 right-4 text-slate-300 hover:text-slate-500 transition-colors text-xs font-normal">
          Admin
        </Link>
      </footer>
    </div>
  );
}

