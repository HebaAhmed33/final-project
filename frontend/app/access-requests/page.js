"use client";

import { useState, useEffect } from "react";
import PageContainer from "../components/PageContainer";
import API_BASE_URL from "../lib/api";

export default function AccessRequestsPage() {
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchRequests();
  }, []);

  async function fetchRequests() {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`http://localhost:8000/access-requests`);
      console.log("Content-Type:", res.headers.get("content-type"));
      if (res.headers.get("content-type")?.includes("text/html")) {
        console.error("API returned HTML instead of JSON for /access-requests");
        throw new Error("API returned HTML instead of JSON");
      }
      if (!res.ok) {
        const text = await res.text();
        console.error("API ERROR RESPONSE:", text);
        throw new Error("API request failed");
      }
      const data = await res.json();
      setRequests(data.requests || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  const getStatusBadge = (status) => {
    const s = (status || "pending").toLowerCase();
    if (s === "approved") return "badge badge-green";
    if (s === "rejected") return "badge badge-red";
    return "badge badge-yellow";
  };

  const formatDate = (iso) => {
    if (!iso) return "—";
    const d = new Date(iso);
    return d.toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const totalRequests = requests.length;
  const pendingCount = requests.filter((r) => (r.status || "pending") === "pending").length;
  const uniqueSectors = new Set(requests.map((r) => r.sector).filter(Boolean)).size;

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
            lineHeight: "1.2",
          }}
        >
          Access Requests
        </h1>
        <p
          style={{
            color: "var(--text-muted)",
            fontSize: "1.05rem",
            maxWidth: "700px",
            lineHeight: "1.6",
            margin: 0,
          }}
        >
          Review and manage incoming access requests from organizations
          seeking to use the SmartISMS platform.
        </p>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: "2.5rem" }}>
        {/* Metrics Strip */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
            gap: "1.25rem",
          }}
        >
          <div
            className="card"
            style={{
              padding: "1.5rem",
              display: "flex",
              flexDirection: "column",
              borderLeft: "4px solid var(--primary)",
            }}
          >
            <span
              style={{
                fontSize: "0.85rem",
                color: "var(--text-muted)",
                fontWeight: 700,
                textTransform: "uppercase",
                letterSpacing: "0.05em",
                marginBottom: "0.5rem",
              }}
            >
              Total Requests
            </span>
            <span
              style={{
                fontSize: "2.25rem",
                fontWeight: 800,
                color: "var(--text-main)",
                lineHeight: "1",
              }}
            >
              {loading ? "..." : totalRequests}
            </span>
          </div>

          <div
            className="card"
            style={{
              padding: "1.5rem",
              display: "flex",
              flexDirection: "column",
              borderLeft: "4px solid #F59E0B",
            }}
          >
            <span
              style={{
                fontSize: "0.85rem",
                color: "var(--text-muted)",
                fontWeight: 700,
                textTransform: "uppercase",
                letterSpacing: "0.05em",
                marginBottom: "0.5rem",
              }}
            >
              Pending Review
            </span>
            <span
              style={{
                fontSize: "2.25rem",
                fontWeight: 800,
                color: "var(--text-main)",
                lineHeight: "1",
              }}
            >
              {loading ? "..." : pendingCount}
            </span>
          </div>

          <div
            className="card"
            style={{
              padding: "1.5rem",
              display: "flex",
              flexDirection: "column",
              borderLeft: "4px solid #8B5CF6",
            }}
          >
            <span
              style={{
                fontSize: "0.85rem",
                color: "var(--text-muted)",
                fontWeight: 700,
                textTransform: "uppercase",
                letterSpacing: "0.05em",
                marginBottom: "0.5rem",
              }}
            >
              Unique Sectors
            </span>
            <span
              style={{
                fontSize: "2.25rem",
                fontWeight: 800,
                color: "var(--text-main)",
                lineHeight: "1",
              }}
            >
              {loading ? "..." : uniqueSectors}
            </span>
          </div>
        </div>

        {/* Table Area */}
        <div style={{ minHeight: "300px" }}>
          {/* Loading */}
          {loading && (
            <div
              style={{
                padding: "4rem 2rem",
                textAlign: "center",
                border: "1px dashed var(--border-color)",
                borderRadius: "8px",
              }}
            >
              <div
                style={{
                  display: "inline-block",
                  width: "40px",
                  height: "40px",
                  border: "4px solid var(--border-color)",
                  borderTopColor: "var(--primary)",
                  borderRadius: "50%",
                  animation: "spin 1s infinite linear",
                  marginBottom: "1rem",
                }}
              />
              <p
                style={{
                  color: "var(--text-main)",
                  fontSize: "1.05rem",
                  fontWeight: 700,
                  margin: "0 0 0.5rem 0",
                }}
              >
                Loading Access Requests
              </p>
              <p
                style={{
                  color: "var(--text-muted)",
                  fontSize: "0.95rem",
                  margin: 0,
                }}
              >
                Fetching submitted requests from the server…
              </p>
              <style>{`@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }`}</style>
            </div>
          )}

          {/* Error */}
          {error && (
            <div
              className="card"
              style={{
                padding: "1.5rem",
                background: "rgba(239, 68, 68, 0.05)",
                border: "1px solid #EF4444",
                color: "#EF4444",
                display: "flex",
                alignItems: "center",
                gap: "1rem",
              }}
            >
              <svg
                style={{ width: "24px", height: "24px", flexShrink: 0 }}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <div>
                <strong
                  style={{
                    display: "block",
                    fontWeight: 600,
                    fontSize: "0.95rem",
                    marginBottom: "0.25rem",
                  }}
                >
                  Failed to Load Requests
                </strong>
                <span style={{ fontSize: "0.85rem" }}>
                  {error}. Please verify the backend is running and try again.
                </span>
              </div>
            </div>
          )}

          {/* Empty */}
          {!loading && !error && requests.length === 0 && (
            <div
              style={{
                padding: "4rem 2rem",
                background: "var(--bg-main)",
                border: "1px dashed var(--border-color)",
                borderRadius: "8px",
                textAlign: "center",
              }}
            >
              <svg
                style={{
                  width: "48px",
                  height: "48px",
                  color: "var(--text-muted)",
                  marginBottom: "1rem",
                  opacity: 0.5,
                }}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
                />
              </svg>
              <h3
                style={{
                  fontSize: "1.2rem",
                  fontWeight: 700,
                  color: "var(--text-main)",
                  marginBottom: "0.5rem",
                }}
              >
                No Access Requests Yet
              </h3>
              <p
                style={{
                  color: "var(--text-muted)",
                  fontSize: "0.95rem",
                  margin: 0,
                }}
              >
                Submitted access requests will appear here once organizations
                begin registering interest.
              </p>
            </div>
          )}

          {/* Data Table */}
          {!loading && !error && requests.length > 0 && (
            <div
              className="card"
              style={{ padding: 0, overflow: "hidden" }}
            >
              <div className="table-container">
                <table className="modern-table">
                  <thead>
                    <tr>
                      <th>Company</th>
                      <th>Email</th>
                      <th>Organization Type</th>
                      <th>Sector</th>
                      <th>Status</th>
                      <th>Created At</th>
                    </tr>
                  </thead>
                  <tbody>
                    {requests.map((req) => (
                      <tr key={req.id}>
                        <td
                          style={{
                            fontWeight: 600,
                            color: "var(--text-main)",
                          }}
                        >
                          {req.company_name}
                        </td>
                        <td style={{ color: "var(--text-muted)" }}>
                          {req.email}
                        </td>
                        <td style={{ color: "var(--text-muted)" }}>
                          {req.organization_type}
                        </td>
                        <td style={{ color: "var(--text-muted)" }}>
                          {req.sector || "—"}
                        </td>
                        <td>
                          <span className={getStatusBadge(req.status)}>
                            {req.status || "pending"}
                          </span>
                        </td>
                        <td
                          style={{
                            color: "var(--text-muted)",
                            fontSize: "0.85rem",
                            whiteSpace: "nowrap",
                          }}
                        >
                          {formatDate(req.created_at)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </div>
    </PageContainer>
  );
}
