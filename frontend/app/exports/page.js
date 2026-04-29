"use client";

import { useState, useEffect } from "react";
import PageContainer from "../components/PageContainer";

const API_BASE_URL =
  typeof window !== "undefined"
    ? process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000"
    : "http://localhost:8000";

export default function ExportsPage() {
  const [hasData, setHasData] = useState(null); // null = loading
  const [downloading, setDownloading] = useState({ excel: false, pdf: false });
  const [error, setError] = useState({ excel: "", pdf: "" });

  useEffect(() => {
    async function checkData() {
      try {
        const res = await fetch(`${API_BASE_URL}/assess/history`);
        if (res.ok) {
          const data = await res.json();
          const history = data.history || [];
          setHasData(history.length > 0);
        } else {
          setHasData(false);
        }
      } catch {
        setHasData(false);
      }
    }
    checkData();
  }, []);

  const handleDownload = async (type) => {
    setDownloading((prev) => ({ ...prev, [type]: true }));
    setError((prev) => ({ ...prev, [type]: "" }));
    try {
      const res = await fetch(`${API_BASE_URL}/export/latest/${type}`);
      if (!res.ok) {
        const body = await res.json().catch(() => null);
        throw new Error(
          body?.detail || `Export failed (${res.status})`
        );
      }
      const blob = await res.blob();
      const disposition = res.headers.get("content-disposition") || "";
      const match = disposition.match(/filename="?([^"]+)"?/);
      const filename =
        match?.[1] ||
        (type === "excel"
          ? "assessment_export.xlsx"
          : "assessment_report.pdf");

      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch (err) {
      setError((prev) => ({ ...prev, [type]: err.message }));
    } finally {
      setDownloading((prev) => ({ ...prev, [type]: false }));
    }
  };

  return (
    <PageContainer>
      <div style={{ padding: "0 0 2rem" }}>
        <h1
          style={{
            fontSize: "2.25rem",
            fontWeight: 800,
            letterSpacing: "-0.04em",
            marginBottom: "0.5rem",
            color: "var(--text-main)",
          }}
        >
          Assessment Export Center
        </h1>
        <p
          style={{
            color: "var(--text-secondary)",
            fontSize: "1rem",
            maxWidth: "700px",
          }}
        >
          Download your latest assessment results as an Excel workbook or a PDF
          report.
        </p>
      </div>

      {/* Loading state */}
      {hasData === null && (
        <div
          className="card"
          style={{
            padding: "3rem",
            textAlign: "center",
            color: "var(--text-muted)",
          }}
        >
          <div
            style={{
              width: "36px",
              height: "36px",
              border: "3px solid var(--border-color)",
              borderTop: "3px solid var(--primary)",
              borderRadius: "50%",
              animation: "spin 0.8s linear infinite",
              margin: "0 auto 1rem",
            }}
          />
          <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
          Checking for assessment data…
        </div>
      )}

      {/* Empty state */}
      {hasData === false && (
        <div
          className="card"
          style={{
            padding: "3rem 2rem",
            textAlign: "center",
            maxWidth: "560px",
          }}
        >
          <div
            style={{
              width: "56px",
              height: "56px",
              borderRadius: "50%",
              background: "var(--icon-bg)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              margin: "0 auto 1.25rem",
            }}
          >
            <svg
              width="28"
              height="28"
              fill="none"
              stroke="var(--text-muted)"
              strokeWidth={1.5}
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2h7"
              />
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M16 19h6m-3-3v6"
              />
            </svg>
          </div>
          <h3
            style={{
              fontSize: "1.1rem",
              fontWeight: 700,
              color: "var(--text-main)",
              marginBottom: "0.5rem",
            }}
          >
            No Assessment Data Available
          </h3>
          <p
            style={{
              color: "var(--text-muted)",
              fontSize: "0.92rem",
              lineHeight: 1.6,
              margin: 0,
            }}
          >
            No assessment results available for export yet. Run an assessment
            first.
          </p>
        </div>
      )}

      {/* Export cards */}
      {hasData === true && (
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))",
            gap: "1.5rem",
            maxWidth: "780px",
          }}
        >
          {/* Excel Card */}
          <div
            className="card"
            style={{
              padding: "2rem 1.75rem",
              display: "flex",
              flexDirection: "column",
              alignItems: "flex-start",
              gap: "1rem",
            }}
          >
            <div
              style={{
                width: "48px",
                height: "48px",
                borderRadius: "12px",
                background: "rgba(16, 185, 129, 0.1)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                flexShrink: 0,
              }}
            >
              <svg
                width="24"
                height="24"
                fill="none"
                stroke="#10B981"
                strokeWidth={2}
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
            </div>
            <div>
              <h3
                style={{
                  fontSize: "1.1rem",
                  fontWeight: 700,
                  color: "var(--text-main)",
                  marginBottom: "0.35rem",
                }}
              >
                Excel Workbook
              </h3>
              <p
                style={{
                  color: "var(--text-muted)",
                  fontSize: "0.85rem",
                  lineHeight: 1.55,
                  margin: 0,
                }}
              >
                Multi-sheet workbook with Summary, SoA, Compliance Matrix, Risk
                Register, Treatment Plan, Vendor Checklist, Training Matrix, and
                Governance Calendar.
              </p>
            </div>
            <button
              id="export-excel-btn"
              className="btn-primary"
              disabled={downloading.excel}
              onClick={() => handleDownload("excel")}
              style={{
                marginTop: "auto",
                display: "flex",
                alignItems: "center",
                gap: "0.5rem",
                width: "100%",
                justifyContent: "center",
                padding: "0.7rem 1.25rem",
              }}
            >
              {downloading.excel ? (
                <>
                  <span
                    style={{
                      width: "16px",
                      height: "16px",
                      border: "2px solid rgba(255,255,255,0.3)",
                      borderTop: "2px solid #fff",
                      borderRadius: "50%",
                      animation: "spin 0.8s linear infinite",
                      display: "inline-block",
                    }}
                  />
                  Generating…
                </>
              ) : (
                <>
                  <svg
                    width="16"
                    height="16"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth={2}
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
                    />
                  </svg>
                  Download Excel Workbook
                </>
              )}
            </button>
            {error.excel && (
              <p
                style={{
                  color: "#EF4444",
                  fontSize: "0.82rem",
                  margin: "0.25rem 0 0",
                }}
              >
                {error.excel}
              </p>
            )}
          </div>

          {/* PDF Card */}
          <div
            className="card"
            style={{
              padding: "2rem 1.75rem",
              display: "flex",
              flexDirection: "column",
              alignItems: "flex-start",
              gap: "1rem",
            }}
          >
            <div
              style={{
                width: "48px",
                height: "48px",
                borderRadius: "12px",
                background: "rgba(239, 68, 68, 0.08)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                flexShrink: 0,
              }}
            >
              <svg
                width="24"
                height="24"
                fill="none"
                stroke="#EF4444"
                strokeWidth={2}
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"
                />
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M9 13h6m-6 3h4"
                />
              </svg>
            </div>
            <div>
              <h3
                style={{
                  fontSize: "1.1rem",
                  fontWeight: 700,
                  color: "var(--text-main)",
                  marginBottom: "0.35rem",
                }}
              >
                PDF Report
              </h3>
              <p
                style={{
                  color: "var(--text-muted)",
                  fontSize: "0.85rem",
                  lineHeight: 1.55,
                  margin: 0,
                }}
              >
                Executive summary with compliance score, key findings, high
                risks, treatment plan, governance calendar, training matrix, and
                vendor checklist highlights.
              </p>
            </div>
            <button
              id="export-pdf-btn"
              className="btn-primary"
              disabled={downloading.pdf}
              onClick={() => handleDownload("pdf")}
              style={{
                marginTop: "auto",
                display: "flex",
                alignItems: "center",
                gap: "0.5rem",
                width: "100%",
                justifyContent: "center",
                padding: "0.7rem 1.25rem",
              }}
            >
              {downloading.pdf ? (
                <>
                  <span
                    style={{
                      width: "16px",
                      height: "16px",
                      border: "2px solid rgba(255,255,255,0.3)",
                      borderTop: "2px solid #fff",
                      borderRadius: "50%",
                      animation: "spin 0.8s linear infinite",
                      display: "inline-block",
                    }}
                  />
                  Generating…
                </>
              ) : (
                <>
                  <svg
                    width="16"
                    height="16"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth={2}
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
                    />
                  </svg>
                  Download PDF Report
                </>
              )}
            </button>
            {error.pdf && (
              <p
                style={{
                  color: "#EF4444",
                  fontSize: "0.82rem",
                  margin: "0.25rem 0 0",
                }}
              >
                {error.pdf}
              </p>
            )}
          </div>
        </div>
      )}
    </PageContainer>
  );
}
