"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export default function TopNavbar() {
  const pathname = usePathname();

  return (
    <header style={{
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      padding: "1rem 2.5rem",
      background: "#ffffff",
      borderBottom: "1px solid #f1f5f9",
      position: "sticky",
      top: 0,
      zIndex: 100
    }}>
      {/* Logo — Aegis.One */}
      <Link href="/" style={{ textDecoration: "none", display: "flex", alignItems: "center", gap: "0.5rem" }}>
        <div style={{ background: "#1a2340", borderRadius: "50%", width: "28px", height: "28px", display: "flex", alignItems: "center", justifyContent: "center" }}>
          <svg width="16" height="16" fill="none" stroke="#fef08a" strokeWidth="2.5" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
          </svg>
        </div>
        <span style={{ fontSize: "1.3rem", fontWeight: 800, color: "#1a2340", letterSpacing: "-0.03em" }}>
          Aegis.One
        </span>
      </Link>

      {/* Nav Links: Home | About */}
      <nav style={{ display: "flex", alignItems: "center", gap: "2rem" }}>
        <Link
          href="/"
          style={{
            textDecoration: "none",
            color: pathname === "/" ? "#1a2340" : "#64748b",
            fontWeight: pathname === "/" ? 700 : 500,
            fontSize: "0.95rem"
          }}
        >
          Home
        </Link>
        <Link
          href="/about"
          style={{
            textDecoration: "none",
            color: pathname === "/about" ? "#1a2340" : "#64748b",
            fontWeight: pathname === "/about" ? 700 : 500,
            fontSize: "0.95rem"
          }}
        >
          About
        </Link>
      </nav>

      {/* CTA: Get Started only */}
      <div>
        <Link href="/onboarding" style={{ textDecoration: "none" }}>
          <button style={{
            background: "#1a2340",
            color: "#ffffff",
            border: "none",
            padding: "0.65rem 1.5rem",
            borderRadius: "8px",
            fontSize: "0.9rem",
            fontWeight: 600,
            cursor: "pointer",
            boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1)"
          }}>
            Get Started
          </button>
        </Link>
      </div>
    </header>
  );
}
