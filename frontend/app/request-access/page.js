"use client";

import { useState } from "react";
import Link from "next/link";
import API_BASE_URL from "../lib/api";

export default function RequestAccessPage() {
  const [formData, setFormData] = useState({
    company_name: "",
    email: "",
    organization_type: "enterprise",
    sector: "",
    notes: ""
  });
  const [status, setStatus] = useState({ loading: false, msg: "", isError: false });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setStatus({ loading: true, msg: "", isError: false });

    try {
      const res = await fetch(`${API_BASE_URL}/request-access`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });
      const data = await res.json();
      
      if (data.success) {
        setStatus({ loading: false, msg: data.message, isError: false });
        setFormData({ company_name: "", email: "", organization_type: "enterprise", sector: "", notes: "" });
      } else {
        setStatus({ loading: false, msg: data.message || "Failed to submit request.", isError: true });
      }
    } catch {
      setStatus({ loading: false, msg: "Server error. Please try again later.", isError: true });
    }
  };

  return (
    <div style={{ flex: 1, display: "flex", flexDirection: "column", background: "var(--bg-main)" }}>
      <div style={{ padding: "4rem 2.5rem", maxWidth: "800px", margin: "0 auto", width: "100%" }}>
        
        <div style={{ textAlign: "center", marginBottom: "3rem" }}>
          <h1 style={{ fontSize: "2.5rem", fontWeight: 800, color: "var(--text-main)", letterSpacing: "-0.03em", marginBottom: "1rem" }}>
            Unlock Enterprise GRC
          </h1>
          <p style={{ fontSize: "1.1rem", color: "var(--text-muted)", lineHeight: "1.6", maxWidth: "600px", margin: "0 auto" }}>
            Request access to the SmartISMS intelligence platform. Our team will review your organization's alignment to set up a dedicated enterprise environment.
          </p>
        </div>

        <div className="card" style={{ padding: "2.5rem" }}>
          {status.msg && !status.isError ? (
             <div style={{ textAlign: "center", padding: "2rem" }}>
               <div style={{ display: "inline-flex", width: "64px", height: "64px", borderRadius: "50%", background: "rgba(16, 185, 129, 0.1)", color: "#10B981", alignItems: "center", justifyContent: "center", marginBottom: "1.5rem" }}>
                 <svg width="32" height="32" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
               </div>
               <h3 style={{ fontSize: "1.5rem", fontWeight: 700, color: "var(--text-main)" }}>Request Received</h3>
               <p style={{ color: "var(--text-muted)", marginTop: "0.5rem" }}>{status.msg}</p>
               <div style={{ marginTop: "2rem" }}>
                 <Link href="/" className="btn-primary" style={{ textDecoration: "none", display: "inline-block" }}>Return to Home</Link>
               </div>
             </div>
          ) : (
             <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
               <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1.5rem" }}>
                 <div>
                   <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600, color: "var(--text-main)", marginBottom: "0.5rem" }}>Registered Company Name</label>
                   <input type="text" className="input-field" required value={formData.company_name} onChange={e => setFormData({...formData, company_name: e.target.value})} placeholder="Acme Corp" />
                 </div>
                 <div>
                   <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600, color: "var(--text-main)", marginBottom: "0.5rem" }}>Work Email Address</label>
                   <input type="email" className="input-field" required value={formData.email} onChange={e => setFormData({...formData, email: e.target.value})} placeholder="admin@acme.com" />
                 </div>
               </div>
               
               <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1.5rem" }}>
                  <div>
                   <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600, color: "var(--text-main)", marginBottom: "0.5rem" }}>Organization Structure</label>
                   <select className="input-field" value={formData.organization_type} onChange={e => setFormData({...formData, organization_type: e.target.value})}>
                     <option value="enterprise">Enterprise</option>
                     <option value="bank">Financial Institution / Bank</option>
                     <option value="hospital">Healthcare / Hospital</option>
                     <option value="government">Government Agency</option>
                   </select>
                 </div>
                 <div>
                   <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600, color: "var(--text-main)", marginBottom: "0.5rem" }}>Industry Sector</label>
                   <input type="text" className="input-field" value={formData.sector} onChange={e => setFormData({...formData, sector: e.target.value})} placeholder="e.g. Technology, Finance" />
                 </div>
               </div>

               <div>
                 <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600, color: "var(--text-main)", marginBottom: "0.5rem" }}>Additional Notes / Requirements</label>
                 <textarea className="input-field" rows={4} value={formData.notes} onChange={e => setFormData({...formData, notes: e.target.value})} placeholder="Briefly describe your compliance goals..."></textarea>
               </div>

               {status.isError && (
                 <div style={{ padding: "1rem", background: "rgba(239, 68, 68, 0.1)", color: "#EF4444", borderRadius: "6px", fontSize: "0.9rem" }}>
                   {status.msg}
                 </div>
               )}

               <div style={{ marginTop: "1rem", borderTop: "1px solid var(--border-color)", paddingTop: "1.5rem", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                 <Link href="/" style={{ color: "var(--text-muted)", fontSize: "0.9rem", textDecoration: "none", fontWeight: 500 }}>
                   ← Back to Home
                 </Link>
                 <button type="submit" className="btn-primary" disabled={status.loading} style={{ padding: "0.75rem 2rem", fontSize: "1rem" }}>
                   {status.loading ? "Submitting..." : "Submit Access Request"}
                 </button>
               </div>
             </form>
          )}
        </div>
      </div>
    </div>
  );
}
