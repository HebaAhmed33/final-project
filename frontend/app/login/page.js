"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import API_BASE_URL from "../lib/api";
import "./login.css";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const res = await fetch(`${API_BASE_URL}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const data = await res.json();

      if (data.success) {
        localStorage.setItem("smartisms_user", JSON.stringify(data.user));
        router.push("/upload");
      } else {
        setError(data.message || "Invalid credentials");
      }
    } catch {
      setError("Unable to connect to server");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-card">
        {/* Logo / Brand */}
        <div className="login-brand">
          <div className="login-logo">
            <svg width="28" height="28" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
          </div>
          <h1 className="login-title">SmartISMS</h1>
          <p className="login-subtitle">Sign in to your account</p>
        </div>

        {/* Error banner */}
        {error && (
          <div className="login-error">
            <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            {error}
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleLogin} className="login-form">
          <div className="login-field">
            <label htmlFor="login-email">Email</label>
            <input
              id="login-email"
              className="input-field"
              type="email"
              placeholder="demo@smartisms.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoFocus
            />
          </div>

          <div className="login-field">
            <label htmlFor="login-password">Password</label>
            <input
              id="login-password"
              className="input-field"
              type="password"
              placeholder="demo123"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <button type="submit" className="btn-primary login-btn" disabled={loading}>
            {loading ? (
              <span className="login-spinner-wrap">
                <span className="login-spinner" />
                Signing in…
              </span>
            ) : (
              "Sign In"
            )}
          </button>
        </form>

        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: "1.5rem", fontSize: "0.9rem" }}>
          <p className="login-hint" style={{ margin: 0 }}>
            Demo: <strong>demo@smartisms.com</strong> / <strong>demo123</strong>
          </p>
          <Link href="/request-access" style={{ color: "var(--primary)", fontWeight: 600, textDecoration: "none" }}>
            Request Access
          </Link>
        </div>
      </div>
    </div>
  );
}
