"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";

const NAV_LINKS = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/upload", label: "Data Initialization" },
  { href: "/config-analysis", label: "Technical Analysis" },
  { href: "/reports", label: "Executive Reports" },
  { href: "/news", label: "Intelligence Feed" },
  { href: "/access-requests", label: "Access Requests" },
];

export default function Sidebar() {
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
        width: "260px",
        height: "100vh",
        background: "var(--bg-sidebar)",
        borderRight: "1px solid var(--border-color)",
        display: "flex",
        flexDirection: "column",
        padding: "1.5rem",
        position: "fixed",
        top: 0,
        left: 0,
        zIndex: 100,
      }}
    >
      <div style={{ marginBottom: "2.5rem", paddingLeft: "0.5rem" }}>
        <h1
          style={{
            fontSize: "1.25rem",
            fontWeight: 800,
            letterSpacing: "-0.03em",
            color: "var(--text-main)",
          }}
        >
          Smart<span style={{ color: "var(--primary)" }}>ISMS</span>
        </h1>
        <p style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginTop: "0.25rem" }}>
          GRC & Security Intelligence
        </p>
      </div>

      <nav style={{ flex: 1, display: "flex", flexDirection: "column", gap: "0.5rem" }}>
        {NAV_LINKS.map((link) => {
          const isActive = pathname === link.href;
          return (
            <Link
              key={link.href}
              href={link.href}
              style={{
                padding: "0.75rem 1rem",
                borderRadius: "0.5rem",
                fontSize: "0.875rem",
                fontWeight: isActive ? 600 : 500,
                color: isActive ? "var(--primary)" : "var(--text-muted)",
                background: isActive ? "rgba(37, 99, 235, 0.08)" : "transparent",
                transition: "all 0.2s ease",
              }}
              onMouseEnter={(e) => {
                if (!isActive) e.currentTarget.style.color = "var(--text-main)";
              }}
              onMouseLeave={(e) => {
                if (!isActive) e.currentTarget.style.color = "var(--text-muted)";
              }}
            >
              {link.label}
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
            justifyContent: "space-between",
            padding: "0.5rem 0.75rem",
            background: "transparent",
            border: "1px solid var(--border-color)",
            borderRadius: "0.5rem",
            color: "var(--text-main)",
            fontSize: "0.875rem",
            fontWeight: 500,
            cursor: "pointer",
            transition: "all 0.2s ease",
          }}
        >
          <span>Theme</span>
          <span>{theme === "light" ? "🌙" : "☀️"}</span>
        </button>
        <button
          onClick={handleLogout}
          style={{
            width: "100%",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            padding: "0.5rem 0.75rem",
            background: "transparent",
            border: "1px solid var(--border-color)",
            borderRadius: "0.5rem",
            color: "#EF4444",
            fontSize: "0.875rem",
            fontWeight: 500,
            cursor: "pointer",
            transition: "all 0.2s ease",
          }}
        >
          <span>Logout</span>
          <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
          </svg>
        </button>
      </div>
    </div>
  );
}
