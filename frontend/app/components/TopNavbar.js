"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";

export default function TopNavbar() {
  const pathname = usePathname();
  const [dropdownOpen, setDropdownOpen] = useState(false);

  // If we are on login, we might not want the request access button or dropdown, but we will follow the prompt strictly: "Create a top navigation bar (NOT sidebar for public pages)"
  
  return (
    <header style={{
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      padding: "1rem 2.5rem",
      background: "var(--bg-main)",
      borderBottom: "1px solid var(--border-color)",
      position: "sticky",
      top: 0,
      zIndex: 100
    }}>
      {/* Logo */}
      <Link href="/" style={{ textDecoration: "none", display: "flex", alignItems: "center", gap: "0.5rem" }}>
        <svg width="24" height="24" fill="none" stroke="var(--primary)" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
        </svg>
        <span style={{ fontSize: "1.25rem", fontWeight: 800, color: "var(--text-main)", letterSpacing: "-0.03em" }}>
          Smart<span style={{ color: "var(--primary)" }}>ISMS</span>
        </span>
      </Link>

      {/* Nav Links */}
      <nav style={{ display: "flex", alignItems: "center", gap: "2rem" }}>
        <Link href="/" style={{ textDecoration: "none", color: pathname === "/" ? "var(--primary)" : "var(--text-muted)", fontWeight: pathname === "/" ? 600 : 500, fontSize: "0.95rem" }}>
          Home
        </Link>
        
        {/* Products Dropdown */}
        <div 
          style={{ position: "relative" }} 
          onMouseEnter={() => setDropdownOpen(true)} 
          onMouseLeave={() => setDropdownOpen(false)}
        >
          <span style={{ color: "var(--text-muted)", fontWeight: 500, fontSize: "0.95rem", cursor: "pointer", display: "flex", alignItems: "center", gap: "0.25rem" }}>
            Products
            <svg width="14" height="14" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" /></svg>
          </span>
          
          {dropdownOpen && (
            <div style={{ position: "absolute", top: "100%", left: "-1rem", paddingTop: "0.5rem" }}>
              <div 
                className="card"
                style={{
                  minWidth: "220px",
                  padding: "0.5rem",
                  boxShadow: "0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1)",
                  display: "flex",
                  flexDirection: "column",
                  gap: "0.25rem"
                }}
              >
                {[
                  { label: "GRC Assessment", href: "/request-access" },
                  { label: "Configuration Analysis", href: "/request-access" },
                  { label: "Risk Engine", href: "/request-access" },
                  { label: "Compliance Reporting", href: "/request-access" },
                ].map(item => (
                  <Link key={item.label} href={item.href} style={{ textDecoration: "none", padding: "0.5rem 1rem", borderRadius: "6px", color: "var(--text-main)", fontSize: "0.9rem", fontWeight: 500, transition: "background 0.2s" }} onMouseEnter={(e) => e.currentTarget.style.background = "var(--bg-main)"} onMouseLeave={(e) => e.currentTarget.style.background = "transparent"}>
                    {item.label}
                  </Link>
                ))}
              </div>
            </div>
          )}
        </div>

        <Link href="/news" style={{ textDecoration: "none", color: pathname === "/news" ? "var(--primary)" : "var(--text-muted)", fontWeight: pathname === "/news" ? 600 : 500, fontSize: "0.95rem" }}>
          Intelligence
        </Link>
        <Link href="/about" style={{ textDecoration: "none", color: pathname === "/about" ? "var(--primary)" : "var(--text-muted)", fontWeight: pathname === "/about" ? 600 : 500, fontSize: "0.95rem" }}>
          About
        </Link>
      </nav>

      {/* CTA Section */}
      <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
        <Link href="/login" style={{ textDecoration: "none", color: "var(--text-main)", fontWeight: 600, fontSize: "0.95rem" }}>
          Login
        </Link>
        <Link href="/request-access" style={{ textDecoration: "none" }}>
          <button className="btn-primary" style={{ padding: "0.6rem 1.25rem", fontSize: "0.9rem", display: "flex", alignItems: "center", gap: "0.5rem" }}>
            Request Access
            <svg width="14" height="14" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3"/></svg>
          </button>
        </Link>
      </div>
    </header>
  );
}
