"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";

const NAV_LINKS = [
  { 
    href: "/upload", 
    label: "Workspace",
    icon: <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" /></svg>
  },
  { 
    href: "/config-analysis", 
    label: "Technical Analysis",
    icon: <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
  },
  { 
    href: "/reports", 
    label: "Executive Reports",
    icon: <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 8v8m-4-5v5m-4-2v2m-2 4h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
  },
  { 
    href: "/news", 
    label: "Intelligence Feed",
    icon: <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" /></svg>
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
        <Link href="/" style={{ textDecoration: "none", flex: 1, overflow: "hidden", display: "block" }}>
          <h1
            style={{
              fontSize: isCollapsed ? "1rem" : "1.25rem",
              fontWeight: 800,
              letterSpacing: "-0.03em",
              color: "var(--text-main)",
              textAlign: isCollapsed ? "center" : "left",
              transition: "all 0.3s ease",
              margin: 0,
            }}
          >
            {isCollapsed ? "A.1" : "Aegis.One"}
          </h1>
          {!isCollapsed && (
            <p style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginTop: "0.25rem", whiteSpace: "nowrap", margin: "0.25rem 0 0 0" }}>
              GRC & Security Intelligence
            </p>
          )}
        </Link>
        
        <button 
          onClick={() => setIsCollapsed(!isCollapsed)}
          style={{ 
            background: "transparent", 
            border: "none", 
            cursor: "pointer", 
            color: "var(--text-muted)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: "0.25rem",
            transform: isCollapsed ? "rotate(180deg)" : "rotate(0deg)",
            transition: "all 0.3s ease"
          }}
          title={isCollapsed ? "Expand Sidebar" : "Collapse Sidebar"}
        >
          <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
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
                background: isActive ? "rgba(37, 99, 235, 0.08)" : "transparent",
                transition: "all 0.2s ease",
                whiteSpace: "nowrap",
                overflow: "hidden",
              }}
              title={isCollapsed ? link.label : undefined}
              onMouseEnter={(e) => {
                if (!isActive) e.currentTarget.style.color = "var(--text-main)";
              }}
              onMouseLeave={(e) => {
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
            border: "1px solid var(--border-color)",
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
