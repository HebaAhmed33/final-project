"use client";

import { useState, useEffect } from "react";
import PageContainer from "../components/PageContainer";
import API_BASE_URL from "../lib/api";

const CATEGORIES = ["All", "Breach", "Vulnerability", "Compliance", "Governance", "General"];

export default function NewsPage() {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [searchQuery, setSearchQuery] = useState("");
  const [activeCategory, setActiveCategory] = useState("All");

  useEffect(() => {
    fetchNews();
  }, []);

  async function fetchNews() {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE_URL}/news`);
      if (!res.ok) throw new Error(`Server responded with HTTP ${res.status}`);
      const data = await res.json();
      setArticles(data.articles || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  // Filter Logic
  const filteredArticles = articles.filter((article) => {
    const matchesCategory =
      activeCategory === "All" ||
      (article.category || "general").toLowerCase() === activeCategory.toLowerCase();

    const searchLower = searchQuery.toLowerCase();
    const matchesSearch =
      searchLower === "" ||
      (article.title || "").toLowerCase().includes(searchLower) ||
      (article.description || "").toLowerCase().includes(searchLower) ||
      (article.source || "").toLowerCase().includes(searchLower);

    return matchesCategory && matchesSearch;
  });

  const featuredArticle = filteredArticles.length > 0 ? filteredArticles[0] : null;
  const gridArticles = filteredArticles.length > 1 ? filteredArticles.slice(1) : [];

  // Summary derivations
  const totalArticles = articles.length;
  const uniqueSources = new Set(articles.map((a) => a.source)).size;
  const latestDateStr = articles.length > 0 ? new Date(articles[0].published_at).toLocaleString() : "Syncing...";

  const getCategoryBadgeClass = (cat) => {
    const c = (cat || "general").toLowerCase();
    if (c === "breach") return "badge badge-red";
    if (c === "vulnerability") return "badge badge-yellow";
    if (c === "compliance" || c === "governance") return "badge badge-blue";
    return "badge";
  };

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
          Live Intelligence Feed
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
          Aggregated continuous monitoring for global GRC, data breaches, and emerging threats. Maintain actionable intelligence vectors dynamically synced from external security networks.
        </p>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: "2.5rem" }}>
        
        {/* Dynamic Threat Metrics Strip */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "1.25rem" }}>
          
          <div className="card" style={{ padding: "1.5rem", display: "flex", flexDirection: "column", borderLeft: "4px solid var(--primary)" }}>
            <span style={{ fontSize: "0.85rem", color: "var(--text-muted)", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: "0.5rem" }}>
               Analyzed Vectors
            </span>
            <span style={{ fontSize: "2.25rem", fontWeight: 800, color: "var(--text-main)", lineHeight: "1" }}>
              {loading ? "..." : totalArticles}
            </span>
          </div>

          <div className="card" style={{ padding: "1.5rem", display: "flex", flexDirection: "column", borderLeft: "4px solid #8B5CF6" }}>
            <span style={{ fontSize: "0.85rem", color: "var(--text-muted)", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: "0.5rem" }}>
               Active Endpoints
            </span>
            <span style={{ fontSize: "2.25rem", fontWeight: 800, color: "var(--text-main)", lineHeight: "1" }}>
              {loading ? "..." : uniqueSources}
            </span>
          </div>

          <div className="card" style={{ padding: "1.5rem", display: "flex", flexDirection: "column", borderLeft: "4px solid #F59E0B" }}>
            <span style={{ fontSize: "0.85rem", color: "var(--text-muted)", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: "0.5rem" }}>
               Database Engine
            </span>
            <span style={{ fontSize: "1.2rem", fontWeight: 700, color: "#10B981", marginTop: "auto", paddingBottom: "0.25rem" }}>
               {loading ? "Establishing Link..." : "Polling Active"}
            </span>
          </div>

          <div className="card" style={{ padding: "1.5rem", display: "flex", flexDirection: "column", borderLeft: "4px solid var(--text-muted)" }}>
             <span style={{ fontSize: "0.85rem", color: "var(--text-muted)", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: "0.5rem" }}>
               Latest Sync Hook
             </span>
             <span style={{ fontSize: "1.2rem", fontWeight: 700, color: "var(--text-main)", marginTop: "auto", paddingBottom: "0.25rem" }}>
               {loading ? "..." : latestDateStr}
             </span>
          </div>
          
        </div>

        {/* Filter & Search Dashboard Array */}
        <div className="card" style={{ padding: "1.25rem 1.5rem", display: "flex", flexWrap: "wrap", justifyContent: "space-between", gap: "1.5rem", alignItems: "center", border: "2px dashed var(--border-color)", background: "var(--bg-main)" }}>
          
          <div style={{ display: "flex", gap: "0.6rem", flexWrap: "wrap" }}>
            {CATEGORIES.map((cat) => {
              const isActive = activeCategory === cat;
              return (
                <button
                  key={cat}
                  onClick={() => setActiveCategory(cat)}
                  style={{
                    padding: "0.5rem 1.25rem",
                    borderRadius: "8px",
                    fontSize: "0.85rem",
                    fontWeight: 700,
                    cursor: "pointer",
                    border: `1px solid ${isActive ? "var(--primary)" : "var(--border-color)"}`,
                    background: isActive ? "var(--primary)" : "var(--bg-card)",
                    color: isActive ? "#fff" : "var(--text-main)",
                    transition: "all 0.2s ease"
                  }}
                >
                  {cat}
                </button>
              );
            })}
          </div>

          <div style={{ flex: "1 1 300px", maxWidth: "450px", position: "relative" }}>
            <input
              type="text"
              placeholder="Query active threat signatures..."
              className="input-field"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{ paddingLeft: "3rem", padding: "0.85rem 1rem 0.85rem 3rem", fontSize: "0.95rem" }}
            />
            <svg style={{ position: "absolute", left: "1rem", top: "50%", transform: "translateY(-50%)", width: "18px", height: "18px", color: "var(--text-muted)" }} fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
        </div>

        {/* Main Feed Content Area */}
        <div style={{ minHeight: "400px" }}>
          
          {loading && (
            <div style={{ padding: "4rem 2rem", textAlign: "center", border: "1px dashed var(--border-color)", borderRadius: "8px" }}>
              <div style={{ display: "inline-block", width: "40px", height: "40px", border: "4px solid var(--border-color)", borderTopColor: "var(--primary)", borderRadius: "50%", animation: "spin 1s infinite linear", marginBottom: "1rem" }} />
              <p style={{ color: "var(--text-main)", fontSize: "1.05rem", fontWeight: 700, margin: "0 0 0.5rem 0" }}>Establishing Secure Feed Link</p>
              <p style={{ color: "var(--text-muted)", fontSize: "0.95rem", margin: 0 }}>Syncing global news parameters...</p>
              <style>{`@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }`}</style>
            </div>
          )}

          {error && (
            <div className="card" style={{ padding: "1.5rem", background: "rgba(239, 68, 68, 0.05)", border: "1px solid #EF4444", color: "#EF4444", display: "flex", alignItems: "center", gap: "1rem" }}>
              <svg style={{ width: "24px", height: "24px", flexShrink: 0 }} fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <strong style={{ display: "block", fontWeight: 600, fontSize: "0.95rem", marginBottom: "0.25rem" }}>External Connection Dropped</strong>
                <span style={{ fontSize: "0.85rem" }}>{error}. Validate outbound firewall permissions to the intelligence API node.</span>
              </div>
            </div>
          )}

          {!loading && !error && filteredArticles.length === 0 && (
             <div style={{ padding: "4rem 2rem", background: "var(--bg-main)", border: "1px dashed var(--border-color)", borderRadius: "8px", textAlign: "center" }}>
               <h3 style={{ fontSize: "1.2rem", fontWeight: 700, color: "var(--text-main)", marginBottom: "0.5rem" }}>Zero Matching Signatures</h3>
               <p style={{ color: "var(--text-muted)", fontSize: "0.95rem", margin: 0 }}>
                 Adjust the query parameters or reset categorical filtering to retrieve base payloads.
               </p>
             </div>
          )}

          {/* Featured Article Overlay Box */}
          {!loading && !error && featuredArticle && (
            <div 
              className="card" 
              style={{ 
                marginBottom: "2.5rem", 
                border: "2px solid var(--border-color)",
                borderLeft: "6px solid var(--primary)",
                display: "flex", 
                flexDirection: "column", 
                justifyContent: "space-between",
                padding: "2.5rem",
                position: "relative",
                overflow: "hidden"
              }}
            >
              <div style={{ position: "absolute", top: "-10%", right: "-5%", width: "400px", height: "400px", background: "var(--primary)", opacity: 0.03, borderRadius: "50%", pointerEvents: "none" }} />
              
              <div style={{ position: "relative", zIndex: 1, marginBottom: "2rem" }}>
                <div style={{ display: "flex", alignItems: "center", flexWrap: "wrap", gap: "0.85rem", marginBottom: "1.25rem" }}>
                  <span className={getCategoryBadgeClass(featuredArticle.category)} style={{ padding: "0.3rem 0.85rem", fontSize: "0.80rem" }}>
                    {featuredArticle.category || "General"}
                  </span>
                  <span style={{ fontSize: "0.9rem", color: "var(--text-main)", fontWeight: 700 }}>
                    {featuredArticle.source}
                  </span>
                  <span style={{ fontSize: "0.9rem", color: "var(--text-muted)", fontWeight: 500 }}>
                    {new Date(featuredArticle.published_at).toLocaleString()}
                  </span>
                </div>
                
                <h2 style={{ fontSize: "2rem", fontWeight: 800, color: "var(--text-main)", marginBottom: "1.25rem", lineHeight: 1.25, letterSpacing: "-0.02em", maxWidth: "95%" }}>
                  {featuredArticle.title}
                </h2>
                
                <p style={{ fontSize: "1.1rem", color: "var(--text-muted)", lineHeight: 1.6, margin: 0, maxWidth: "1000px" }}>
                  {featuredArticle.description}
                </p>
              </div>
              
              <div style={{ position: "relative", zIndex: 1 }}>
                <a 
                  href={featuredArticle.url} 
                  target="_blank" 
                  rel="noopener noreferrer" 
                  className="btn-primary"
                  style={{ display: "inline-flex", alignItems: "center", gap: "0.5rem", textDecoration: "none", padding: "0.85rem 1.75rem", fontSize: "1rem" }}
                >
                  Access Primary Report
                  <svg style={{ width: "18px", height: "18px" }} fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                </a>
              </div>
            </div>
          )}

          {/* Standard Grid Configuration */}
          {!loading && !error && gridArticles.length > 0 && (
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(340px, 1fr))", gap: "1.5rem" }}>
              {gridArticles.map((article, idx) => (
                <div 
                  key={idx} 
                  className="card" 
                  style={{ 
                    display: "flex", 
                    flexDirection: "column", 
                    height: "100%", 
                    padding: "1.5rem",
                    transition: "all 0.2s ease"
                  }}
                  onMouseEnter={(e) => { e.currentTarget.style.transform = "translateY(-4px)"; e.currentTarget.style.boxShadow = "var(--shadow-md)"; e.currentTarget.style.borderColor = "var(--primary)"; }}
                  onMouseLeave={(e) => { e.currentTarget.style.transform = "translateY(0)"; e.currentTarget.style.boxShadow = "var(--shadow-sm)"; e.currentTarget.style.borderColor = "var(--border-color)"; }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", marginBottom: "1.25rem", flexWrap: "wrap" }}>
                    <span className={getCategoryBadgeClass(article.category)} style={{ fontSize: "0.75rem", padding: "0.2rem 0.6rem" }}>
                      {article.category || "General"}
                    </span>
                    <span style={{ fontSize: "0.85rem", color: "var(--text-main)", fontWeight: 600, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                      {article.source}
                    </span>
                  </div>
                  
                  <h3 style={{ fontSize: "1.15rem", fontWeight: 700, color: "var(--text-main)", marginBottom: "0.85rem", lineHeight: 1.4, letterSpacing: "-0.01em" }}>
                    {article.title}
                  </h3>
                  
                  <p style={{ fontSize: "0.95rem", color: "var(--text-muted)", lineHeight: 1.5, marginBottom: "1.5rem", flex: 1 }}>
                    {article.description}
                  </p>
                  
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderTop: "1px solid var(--border-color)", paddingTop: "1.25rem", marginTop: "auto" }}>
                    <span style={{ fontSize: "0.8rem", color: "var(--text-muted)", fontWeight: 500 }}>
                      {new Date(article.published_at).toLocaleDateString()}
                    </span>
                    <a 
                      href={article.url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      style={{ fontSize: "0.9rem", fontWeight: 700, color: "var(--primary)", display: "flex", alignItems: "center", gap: "0.35rem", textDecoration: "none" }}
                    >
                      Article
                      <svg style={{ width: "14px", height: "14px" }} fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                      </svg>
                    </a>
                  </div>
                </div>
              ))}
            </div>
          )}

        </div>
      </div>
    </PageContainer>
  );
}
