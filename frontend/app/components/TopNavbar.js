"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export default function TopNavbar() {
  const pathname = usePathname();

  return (
    <header style={{
      height: "68px",
      background: "#F7F8FC",
      borderBottom: "1px solid #E5E7EB",
      position: "sticky",
      top: 0,
      zIndex: 100,
      display: "flex",
      alignItems: "center",
      justifyContent: "center"
    }}>
      <div style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        width: "100%",
        maxWidth: "1060px",
        padding: "0 20px"
      }}>
        {/* Logo — Aegis.One */}
        <Link href="/" style={{ textDecoration: "none", display: "flex", alignItems: "center", gap: "0.6rem", marginLeft: "-10px" }}>
          <div style={{ background: "#151B3A", borderRadius: "50%", width: "28px", height: "28px", display: "flex", alignItems: "center", justifyContent: "center" }}>
            <svg width="16" height="16" fill="none" stroke="#fce69a" strokeWidth="2.5" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
          </div>
          <span style={{ fontSize: "1.25rem", fontWeight: 800, color: "#151B3A", letterSpacing: "-0.02em" }}>
            Aegis.One
          </span>
        </Link>

        {/* Nav Links: Home | Explore */}
        <nav style={{ display: "flex", alignItems: "center", gap: "2rem", position: "absolute", left: "50%", transform: "translateX(-50%)" }}>
          <Link
            href="/"
            style={{
              textDecoration: "none",
              color: pathname === "/" ? "#151B3A" : "#64748b",
              fontWeight: pathname === "/" ? 700 : 500,
              fontSize: "0.9rem"
            }}
          >
            Home
          </Link>
          <Link
            href="/about"
            style={{
              textDecoration: "none",
              color: pathname === "/about" ? "#151B3A" : "#64748b",
              fontWeight: pathname === "/about" ? 700 : 500,
              fontSize: "0.9rem"
            }}
          >
            About
          </Link>
        </nav>

        {/* CTA: Get Started only */}
        <div>
          <Link href="/onboarding" style={{ textDecoration: "none" }}>
            <button style={{
              background: "#151B3A",
              color: "#ffffff",
              border: "none",
              padding: "0.5rem 1.25rem",
              borderRadius: "8px",
              fontSize: "0.85rem",
              fontWeight: 600,
              cursor: "pointer",
              transition: "opacity 0.2s"
            }}
            onMouseOver={(e) => e.currentTarget.style.opacity = "0.9"}
            onMouseOut={(e) => e.currentTarget.style.opacity = "1"}
            >
              Get Started
            </button>
          </Link>
        </div>
      </div>
    </header>
  );
}
