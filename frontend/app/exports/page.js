"use client";

import { useState, useEffect } from "react";
import PageContainer from "../components/PageContainer";
import jsPDF from "jspdf";
import autoTable from "jspdf-autotable";

const API_BASE_URL =
  typeof window !== "undefined"
    ? process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000"
    : "http://localhost:8000";

export default function ExportsPage() {
  const [hasData, setHasData] = useState(null); // null = loading
  const [downloading, setDownloading] = useState({ excel: false, pdf: false, configPdf: false, liveScanPdf: false });
  const [error, setError] = useState({ excel: "", pdf: "" });
  const [hasLiveScan, setHasLiveScan] = useState(false);

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

  useEffect(() => {
    // Check for live scan data in session storage
    if (typeof window !== "undefined") {
      try {
        const configStr = sessionStorage.getItem("config_result");
        if (configStr) {
          const configData = JSON.parse(configStr);
          if (configData.scan_type === "live_scan") {
            setHasLiveScan(true);
          } else {
            setHasLiveScan(false);
          }
        } else {
          setHasLiveScan(false);
        }
      } catch (e) { /* ignore parse errors */ }
    }
  });

  const handleDownload = async (type) => {
    const sessionAssessment = sessionStorage.getItem("assessment_result");
    if (!sessionAssessment) {
      alert("No recent assessment or configuration data available. Please run a new analysis.");
      return;
    }

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

  const handleConfigPdfDownload = () => {
    const dataStr = sessionStorage.getItem("config_result");
    if (!dataStr) {
      alert("No recent assessment or configuration data available. Please run a new analysis.");
      return;
    }

    let raw;
    try {
      raw = JSON.parse(dataStr);
    } catch (e) {
      alert("Failed to parse configuration result data.");
      return;
    }

    const isLiveScan = raw.scan_type === "live_scan";

    const normalized = {
      framework: raw.framework_label || raw.framework || raw.config_compliance?.framework || raw.selected_framework || "Framework",
      file_name: isLiveScan ? `Live Scan — ${raw.target_host || "Unknown Host"}` : (raw.file_name || raw.filename || raw.original_filename || "Unknown File"),
      company_name: raw.company_name || raw.company?.name || "Aegis.One Client",

      compliance_score:
        raw.compliance_score ||
        raw.compliance?.compliance_score ||
        raw.config_compliance?.compliance_score ||
        raw.config_compliance?.compliance?.compliance_score || 0,

      risk_level:
        raw.risk_level ||
        raw.compliance?.risk_level ||
        raw.config_compliance?.risk_level ||
        raw.config_compliance?.compliance?.risk_level || "Unknown",

      config_analysis:
        raw.config_analysis || raw.analysis || {},

      findings:
        raw.config_compliance?.findings ||
        raw.findings ||
        raw.config_analysis?.findings ||
        raw.config_compliance?.config_analysis?.findings ||
        [],

      risk_register:
        raw.config_compliance?.risk_register ||
        raw.risk_register ||
        [],

      best_practices:
        raw.config_compliance?.best_practices ||
        raw.best_practices ||
        [],

      // Live scan specific fields
      scan_type: raw.scan_type || "upload",
      target_host: raw.target_host || "",
      scan_timestamp: raw.scan_timestamp || "",
      scan_duration_seconds: raw.scan_duration_seconds || 0,
      collected_configs: raw.collected_configs || {},
    };

    if (normalized.findings.length === 0 && normalized.risk_register.length === 0 && normalized.best_practices.length === 0) {
      alert("No configuration result data found. Please run a configuration analysis again.");
      return;
    }

    const downloadKey = isLiveScan ? "liveScanPdf" : "configPdf";
    setDownloading(prev => ({ ...prev, [downloadKey]: true }));

    const dateStr = new Date().toISOString().split("T")[0];
    const filenameOut = isLiveScan
      ? `live_scan_report_${normalized.framework.replace(/ /g, "_")}_${dateStr}.pdf`
      : `configuration_security_report_${normalized.framework.replace(/ /g, "_")}_${dateStr}.pdf`;

    const doc = new jsPDF("p", "pt", "a4");

    let currentY = 40;
    const addPage = () => {
      doc.addPage();
      currentY = 40;
    };

    // Header
    doc.setFontSize(22);
    doc.setFont("helvetica", "bold");
    doc.setTextColor(37, 99, 235);
    doc.text("Aegis.One", 40, currentY);
    currentY += 25;

    doc.setFontSize(16);
    doc.setTextColor(17, 24, 39);
    doc.text(isLiveScan ? "Live Configuration Scan Report" : "Configuration Security Analysis Report", 40, currentY);

    doc.setFontSize(10);
    doc.setFont("helvetica", "normal");
    doc.setTextColor(75, 85, 99);
    doc.text(`Framework: ${normalized.framework}`, 400, currentY - 15);
    if (isLiveScan) {
      doc.text(`Target: ${normalized.target_host}`, 400, currentY);
    } else {
      doc.text(`File: ${normalized.file_name}`, 400, currentY);
    }
    doc.text(`Generated: ${dateStr}`, 400, currentY + 15);

    currentY += 20;
    doc.text(`Company: ${normalized.company_name}`, 40, currentY);
    currentY += 25;

    // Live scan metadata block
    if (isLiveScan) {
      const scanDate = normalized.scan_timestamp ? new Date(normalized.scan_timestamp).toLocaleString() : "N/A";
      const durationMin = normalized.scan_duration_seconds ? `${Math.round(normalized.scan_duration_seconds)}s` : "N/A";
      const collectedCount = Object.values(normalized.collected_configs).filter(c => c.has_content).length;
      const totalChecks = Object.keys(normalized.collected_configs).length;

      autoTable(doc, {
        startY: currentY,
        theme: "grid",
        headStyles: { fillColor: [37, 99, 235], textColor: [255, 255, 255], fontStyle: "bold" },
        head: [["Scan Detail", "Value"]],
        body: [
          ["Scan Type", "Live SSH Configuration Scan"],
          ["Target Host", normalized.target_host],
          ["Framework", normalized.framework],
          ["Scan Timestamp", scanDate],
          ["Duration", durationMin],
          ["Configs Collected", `${collectedCount} / ${totalChecks} checks`],
        ],
        styles: { fontSize: 9, cellPadding: 5, textColor: [17, 24, 39] },
        columnStyles: { 0: { fontStyle: "bold", cellWidth: 130 } }
      });
      currentY = doc.lastAutoTable.finalY + 20;
    }

    doc.setDrawColor(229, 231, 235);
    doc.line(40, currentY, 555, currentY);
    currentY += 25;

    // Executive Summary
    doc.setFontSize(14);
    doc.setFont("helvetica", "bold");
    doc.setTextColor(17, 24, 39);
    doc.text("Executive Summary", 40, currentY);
    currentY += 20;

    autoTable(doc, {
      startY: currentY,
      theme: "grid",
      headStyles: { fillColor: [249, 250, 251], textColor: [107, 114, 128], fontStyle: "bold" },
      head: [["Compliance Score", "Risk Level", "Config Type", "Overall Risk"]],
      body: [[
        `${normalized.compliance_score}%`,
        normalized.risk_level,
        normalized.config_analysis?.summary?.config_type?.toUpperCase() || "N/A",
        normalized.config_analysis?.summary?.overall_risk || "Low"
      ]],
      styles: { halign: "center", fontSize: 10, textColor: [17, 24, 39] }
    });
    currentY = doc.lastAutoTable.finalY + 20;

    autoTable(doc, {
      startY: currentY,
      theme: "plain",
      body: [[
        `Findings Summary:   High: ${normalized.config_analysis?.summary?.high || 0}   |   Medium: ${normalized.config_analysis?.summary?.medium || 0}   |   Low: ${normalized.config_analysis?.summary?.low || 0}`
      ]],
      styles: { fillColor: [238, 242, 255], textColor: [49, 46, 129], fontStyle: "bold", fontSize: 10 }
    });
    currentY = doc.lastAutoTable.finalY + 25;

    // Detected Components
    doc.setFontSize(14);
    doc.setFont("helvetica", "bold");
    doc.setTextColor(17, 24, 39);
    doc.text("Detected Components", 40, currentY);
    currentY += 15;

    const components = normalized.config_analysis?.components || [];
    if (components.length === 0) {
      doc.setFontSize(10);
      doc.setFont("helvetica", "normal");
      doc.setTextColor(107, 114, 128);
      doc.text("No explicit components detected.", 40, currentY);
      currentY += 20;
    } else {
      const compBody = components.map(c => [`${c.type}:`, c.value]);
      autoTable(doc, {
        startY: currentY,
        theme: "plain",
        body: compBody,
        styles: { fontSize: 9, cellPadding: 2 },
        columnStyles: { 0: { fontStyle: "bold", cellWidth: 100 } }
      });
      currentY = doc.lastAutoTable.finalY + 25;
    }

    // Detailed Findings
    if (normalized.findings.length > 0) {
      if (currentY > 700) addPage();
      doc.setFontSize(14);
      doc.setFont("helvetica", "bold");
      doc.setTextColor(17, 24, 39);
      doc.text("Detailed Findings", 40, currentY);
      currentY += 15;

      const findingsBody = normalized.findings.map(f => {
        const control = f.framework_control || f.control || f.mapped_control || f.framework_mapping || "No direct mapping";
        return [
          f.id || "N/A",
          f.title || "N/A",
          f.severity || "N/A",
          f.description || "N/A",
          control,
          f.recommendation || "N/A"
        ];
      });

      autoTable(doc, {
        startY: currentY,
        head: [["ID", "Title", "Severity", "Description", "Control", "Recommendation"]],
        body: findingsBody,
        theme: "grid",
        headStyles: { fillColor: [243, 244, 246], textColor: [55, 65, 81] },
        styles: { fontSize: 9, cellPadding: 4, overflow: "linebreak" },
        columnStyles: {
          0: { cellWidth: 35 },
          1: { cellWidth: 75 },
          2: { cellWidth: 45 },
          3: { cellWidth: 110 },
          4: { cellWidth: 100 },
          5: { cellWidth: "auto" }
        }
      });
      currentY = doc.lastAutoTable.finalY + 25;
    }

    // Risk Register
    if (normalized.risk_register.length > 0) {
      if (currentY > 700) addPage();

      doc.setFontSize(14);
      doc.setFont("helvetica", "bold");
      doc.setTextColor(17, 24, 39);
      doc.text("Risk Register", 40, currentY);
      currentY += 15;

      const risksBody = normalized.risk_register.map(r => [
        r.risk_id || "N/A",
        r.risk_statement || "N/A",
        r.impact || "N/A",
        r.likelihood || "N/A",
        r.risk_score || "N/A",
        r.treatment || "N/A",
        r.recommendation || "N/A"
      ]);

      autoTable(doc, {
        startY: currentY,
        head: [["Risk ID", "Risk Statement", "Impact", "Likelihood", "Score", "Treatment", "Recommendation"]],
        body: risksBody,
        theme: "grid",
        headStyles: { fillColor: [243, 244, 246], textColor: [55, 65, 81] },
        styles: { fontSize: 8, cellPadding: 4, overflow: "linebreak" },
        columnStyles: {
          0: { cellWidth: 40 },
          1: { cellWidth: 100 },
          2: { cellWidth: 50 },
          3: { cellWidth: 50 },
          4: { cellWidth: 40 },
          5: { cellWidth: 70 },
          6: { cellWidth: "auto" }
        }
      });
      currentY = doc.lastAutoTable.finalY + 25;
    }

    // Best Practices
    if (normalized.best_practices.length > 0) {
      if (currentY > 700) addPage();

      doc.setFontSize(14);
      doc.setFont("helvetica", "bold");
      doc.setTextColor(17, 24, 39);
      doc.text("Recommended Best Practices", 40, currentY);
      currentY += 15;

      const practicesBody = normalized.best_practices.map(bp => [
        bp.title || "Best Practice",
        bp.category || "General",
        bp.description || "N/A"
      ]);

      autoTable(doc, {
        startY: currentY,
        head: [["Title", "Category", "Description"]],
        body: practicesBody,
        theme: "grid",
        headStyles: { fillColor: [243, 244, 246], textColor: [55, 65, 81] },
        styles: { fontSize: 9, cellPadding: 5, overflow: "linebreak" },
        columnStyles: {
          0: { cellWidth: 120, fontStyle: "bold" },
          1: { cellWidth: 70 },
          2: { cellWidth: "auto" }
        }
      });
    }

    // Collected configs summary (live scan only)
    if (isLiveScan && Object.keys(normalized.collected_configs).length > 0) {
      if (currentY > 700) addPage();

      doc.setFontSize(14);
      doc.setFont("helvetica", "bold");
      doc.setTextColor(17, 24, 39);
      doc.text("Collected Configuration Sources", 40, currentY);
      currentY += 15;

      const configRows = Object.entries(normalized.collected_configs).map(([id, info]) => [
        info.label || id,
        info.has_content ? "Collected" : "Not Available",
        info.has_content ? `${info.output_length} bytes` : "—",
      ]);

      autoTable(doc, {
        startY: currentY,
        head: [["Configuration Source", "Status", "Size"]],
        body: configRows,
        theme: "grid",
        headStyles: { fillColor: [243, 244, 246], textColor: [55, 65, 81] },
        styles: { fontSize: 9, cellPadding: 4 },
        columnStyles: {
          0: { cellWidth: 200, fontStyle: "bold" },
          1: { cellWidth: 100, halign: "center" },
          2: { cellWidth: "auto", halign: "center" },
        },
        didParseCell: function(data) {
          if (data.section === "body" && data.column.index === 1) {
            if (data.cell.raw === "Collected") {
              data.cell.styles.textColor = [16, 185, 129];
              data.cell.styles.fontStyle = "bold";
            } else {
              data.cell.styles.textColor = [156, 163, 175];
            }
          }
        }
      });
    }

    try {
      doc.save(filenameOut);
    } catch (e) {
      console.error(e);
      alert("Failed to generate PDF");
    }
    const doneKey = isLiveScan ? "liveScanPdf" : "configPdf";
    setDownloading(prev => ({ ...prev, [doneKey]: false }));
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

      {/* ──────────────────────────────────────────────────────── */}
      {/* CONFIGURATION EXPORT CENTER                              */}
      {/* ──────────────────────────────────────────────────────── */}

      <div style={{ padding: "4rem 0 2rem" }}>
        <h1
          style={{
            fontSize: "2.25rem",
            fontWeight: 800,
            letterSpacing: "-0.04em",
            marginBottom: "0.5rem",
            color: "var(--text-main)",
          }}
        >
          Configuration Export Center
        </h1>
        <p
          style={{
            color: "var(--text-secondary)",
            fontSize: "1rem",
            maxWidth: "700px",
          }}
        >
          Download your latest configuration analysis or live scan results as a PDF report.
        </p>
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))",
          gap: "1.5rem",
          maxWidth: "1200px",
          paddingBottom: "4rem"
        }}
      >
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
            <svg width="24" height="24" fill="none" stroke="#EF4444" strokeWidth={2} viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 13h6m-6 3h4" />
            </svg>
          </div>
          <div>
            <h3 style={{ fontSize: "1.1rem", fontWeight: 700, color: "var(--text-main)", marginBottom: "0.35rem" }}>
              Configuration PDF Report
            </h3>
            <p style={{ color: "var(--text-muted)", fontSize: "0.85rem", lineHeight: 1.55, margin: 0 }}>
              Download a formatted configuration security report including compliance score, findings, risk register, and best practices.
            </p>
          </div>
          <button
            className="btn-primary"
            disabled={downloading.configPdf}
            onClick={handleConfigPdfDownload}
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
            {downloading.configPdf ? (
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
                <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
                Download Configuration PDF Report
              </>
            )}
          </button>
        </div>

        {/* Live Scan PDF Card */}
        {hasLiveScan && (
          <div
            className="card"
            style={{
              padding: "2rem 1.75rem",
              display: "flex",
              flexDirection: "column",
              alignItems: "flex-start",
              gap: "1rem",
              border: "1px solid rgba(37, 99, 235, 0.2)",
            }}
          >
            <div
              style={{
                width: "48px",
                height: "48px",
                borderRadius: "12px",
                background: "rgba(37, 99, 235, 0.08)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                flexShrink: 0,
              }}
            >
              <svg width="24" height="24" fill="none" stroke="#2563EB" strokeWidth={2} viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
              </svg>
            </div>
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.35rem" }}>
                <h3 style={{ fontSize: "1.1rem", fontWeight: 700, color: "var(--text-main)", margin: 0 }}>
                  Live Scan PDF Report
                </h3>
                <span style={{ fontSize: "0.7rem", fontWeight: 700, padding: "0.15rem 0.5rem", borderRadius: "9999px", background: "rgba(37, 99, 235, 0.1)", color: "#2563EB" }}>LIVE</span>
              </div>
              <p style={{ color: "var(--text-muted)", fontSize: "0.85rem", lineHeight: 1.55, margin: 0 }}>
                Download a comprehensive PDF report from your latest live SSH scan, including target host details, scan metadata, collected configuration sources, compliance score, and findings.
              </p>
            </div>
            <button
              className="btn-primary"
              disabled={downloading.liveScanPdf}
              onClick={handleConfigPdfDownload}
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
              {downloading.liveScanPdf ? (
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
                  <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                  </svg>
                  Download Live Scan PDF Report
                </>
              )}
            </button>
          </div>
        )}
      </div>
    </PageContainer>
  );
}
