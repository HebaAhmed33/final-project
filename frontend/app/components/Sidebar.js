"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";

const NAV_LINKS = [
  { 
    href: "/", 
    label: "Home",
    icon: <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" /></svg>
  },
  { 
    href: "/workspace", 
    label: "Overview",
    icon: <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" /></svg>
  },
  { 
    href: "/upload", 
    label: "Workspace",
    icon: <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" /></svg>
  },

  { 
    href: "/reports", 
    label: "Executive Reports",
    icon: <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 8v8m-4-5v5m-4-2v2m-2 4h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
  },
  { 
    href: "/access-requests", 
    label: "Access Requests",
    icon: <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" /></svg>
  },
];

export default function Sidebar({ isCollapsed = false, setIsCollapsed = () => {} }) {
  const [theme, setTheme] = useState("light");
  const pathname = usePathname();
  const router = useRouter();

  useEffect(() => {
    const saved = localStorage.getItem("theme") || "light";
    setTheme(saved);
    document.documentElement.setAttribute("data-theme", saved);
  }, []);

  const toggleTheme = () => {
    const next = theme === "light" ? "dark" : "light";
    setTheme(next);
    localStorage.setItem("theme", next);
    document.documentElement.setAttribute("data-theme", next);
  };

  const handleLogout = () => {
    localStorage.removeItem("smartisms_user");
    router.push("/login");
  };

  return (
    <div
      style={{
        width: isCollapsed ? "80px" : "260px",
        height: "100vh",
        background: "var(--bg-sidebar)",
        borderRight: "1px solid var(--border-color)",
        display: "flex",
        flexDirection: "column",
        padding: isCollapsed ? "1.5rem 0.5rem" : "1.5rem",
        position: "fixed",
        top: 0,
        left: 0,
        zIndex: 100,
        transition: "all 0.3s ease",
      }}
    >
      <div style={{ display: "flex", flexDirection: isCollapsed ? "column" : "row", alignItems: "center", justifyContent: "space-between", marginBottom: "2.5rem", paddingLeft: isCollapsed ? "0" : "0.5rem", gap: isCollapsed ? "1rem" : "0" }}>
        <Link href="/" style={{ textDecoration: "none", flex: 1, display: "flex", alignItems: "center", gap: "0.6rem", overflow: "hidden" }}>
          <div style={{ background: "#151B3A", borderRadius: "50%", width: "28px", height: "28px", minWidth: "28px", display: "flex", alignItems: "center", justifyContent: "center" }}>
            <svg width="16" height="16" fill="none" stroke="#fce69a" strokeWidth="2.5" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
          </div>
          {!isCollapsed && (
            <span style={{ fontSize: "1.25rem", fontWeight: 800, color: "#151B3A", letterSpacing: "-0.02em" }}>
              Aegis.One
            </span>
          )}
        </Link>
        
        <button 
          onClick={() => setIsCollapsed(!isCollapsed)}
          style={{ 
            background: "transparent", 
            border: "none", 
            cursor: "pointer", 
            color: "#6B7280",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: "0.25rem",
            transform: isCollapsed ? "rotate(180deg)" : "rotate(0deg)",
            transition: "all 0.3s ease"
          }}
          title={isCollapsed ? "Expand Sidebar" : "Collapse Sidebar"}
          onMouseEnter={(e) => e.currentTarget.style.color = "#111936"}
          onMouseLeave={(e) => e.currentTarget.style.color = "#6B7280"}
        >
          <svg width="22" height="22" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
          </svg>
        </button>
      </div>

      <nav style={{ flex: 1, display: "flex", flexDirection: "column", gap: "0.5rem" }}>
        {NAV_LINKS.map((link) => {
          const isActive = pathname === link.href;
          return (
            <Link
              key={link.href}
              href={link.href}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "0.75rem",
                padding: isCollapsed ? "0.75rem" : "0.75rem 1rem",
                justifyContent: isCollapsed ? "center" : "flex-start",
                borderRadius: "0.5rem",
                fontSize: "0.875rem",
                fontWeight: isActive ? 600 : 500,
                color: isActive ? "var(--primary)" : "var(--text-muted)",
                background: isActive ? "var(--icon-bg)" : "transparent",
                transition: "all 0.2s ease",
                whiteSpace: "nowrap",
                overflow: "hidden",
              }}
              title={isCollapsed ? link.label : undefined}
              onMouseEnter={(e) => {
                if (!isActive) e.currentTarget.style.background = "var(--bg-main)";
                if (!isActive) e.currentTarget.style.color = "var(--text-main)";
              }}
              onMouseLeave={(e) => {
                if (!isActive) e.currentTarget.style.background = "transparent";
                if (!isActive) e.currentTarget.style.color = "var(--text-muted)";
              }}
            >
              {link.icon}
              {!isCollapsed && <span>{link.label}</span>}
            </Link>
          );
        })}
      </nav>

      <div style={{ borderTop: "1px solid var(--border-color)", paddingTop: "1.5rem", marginTop: "auto", display: "flex", flexDirection: "column", gap: "0.5rem" }}>
        <button
          onClick={toggleTheme}
          style={{
            width: "100%",
            display: "flex",
            alignItems: "center",
            justifyContent: isCollapsed ? "center" : "space-between",
            padding: isCollapsed ? "0.5rem" : "0.5rem 0.75rem",
            background: "transparent",
            border: "1px solid var(--border-color)",
            borderRadius: "0.5rem",
            color: "var(--text-main)",
            fontSize: "0.875rem",
            fontWeight: 500,
            cursor: "pointer",
            transition: "all 0.2s ease",
          }}
          title={isCollapsed ? "Toggle Theme" : undefined}
        >
          {!isCollapsed && <span>Theme</span>}
          <span>{theme === "light" ? "🌙" : "☀️"}</span>
        </button>
        <button
          onClick={handleLogout}
          style={{
            width: "100%",
            display: "flex",
            alignItems: "center",
            justifyContent: isCollapsed ? "center" : "space-between",
            padding: isCollapsed ? "0.5rem" : "0.5rem 0.75rem",
            background: "transparent",
            border: "1px solid rgba(239, 68, 68, 0.2)",
            borderRadius: "0.5rem",
            color: "#EF4444",
            fontSize: "0.875rem",
            fontWeight: 500,
            cursor: "pointer",
            transition: "all 0.2s ease",
          }}
          title={isCollapsed ? "Logout" : undefined}
        >
          {!isCollapsed && <span>Logout</span>}
          <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
          </svg>
        </button>
      </div>
    </div>
  );
}
