"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

const NAV_LINKS = [
  { href: "/", label: "Home" },
  { href: "/assessment", label: "Assessment" },
];

export default function Navbar() {
  const [theme, setTheme] = useState("light");

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

  return (
    <nav
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "0.75rem 1.5rem",
        borderBottom: "1px solid var(--border)",
        background: "var(--bg-card)",
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: "2rem" }}>
        <span
          style={{
            fontWeight: 700,
            fontSize: "1.1rem",
            color: "var(--accent)",
            letterSpacing: "-0.02em",
          }}
        >
          SmartISMS
        </span>
        {NAV_LINKS.map((link) => (
          <Link
            key={link.href}
            href={link.href}
            style={{
              fontSize: "0.9rem",
              color: "var(--text-muted)",
              transition: "color 0.15s",
            }}
          >
            {link.label}
          </Link>
        ))}
      </div>
      <button
        onClick={toggleTheme}
        style={{
          background: "none",
          border: "1px solid var(--border)",
          borderRadius: "6px",
          padding: "0.35rem 0.75rem",
          cursor: "pointer",
          fontSize: "0.85rem",
          color: "var(--text-muted)",
        }}
      >
        {theme === "light" ? "🌙 Dark" : "☀️ Light"}
      </button>
    </nav>
  );
}
