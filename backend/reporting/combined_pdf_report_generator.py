"""
Combined PDF Report Generator.
Generates a clean, printable PDF from the combined report formatter output.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib import colors


# ---------------------------------------------------------------------------
# Style helpers
# ---------------------------------------------------------------------------

def _build_styles():
    """Return custom paragraph styles used throughout the report."""
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "ReportTitle", parent=base["Title"],
            fontSize=22, leading=28, spaceAfter=6,
        ),
        "heading": ParagraphStyle(
            "SectionHeading", parent=base["Heading2"],
            fontSize=14, leading=18, spaceBefore=18, spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "BodyText", parent=base["BodyText"],
            fontSize=10, leading=14, spaceAfter=4,
        ),
        "fallback": ParagraphStyle(
            "Fallback", parent=base["Italic"],
            fontSize=10, leading=14, textColor=colors.grey,
        ),
    }


_TABLE_STYLE_BASE = [
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 10),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ("TOPPADDING", (0, 0), (-1, -1), 4),
    ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
    ("BACKGROUND", (0, 0), (-1, 0), colors.Color(0.93, 0.93, 0.93)),
]

_TABLE_STYLE_COMPACT = _TABLE_STYLE_BASE + [
    ("FONTSIZE", (0, 0), (-1, -1), 9),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
]


# ---------------------------------------------------------------------------
# Section helpers
# ---------------------------------------------------------------------------

def _divider():
    return HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey,
                      spaceAfter=6, spaceBefore=2)


def _section_gap():
    return Spacer(1, 4)


def _add_title(elements, data, styles):
    title = data.get("title", "SmartISMS Combined Assessment Report")
    elements.append(Paragraph(title, styles["title"]))
    elements.append(_divider())


def _add_executive_summary(elements, data, styles):
    elements.append(Paragraph("Executive Summary", styles["heading"]))
    s = data.get("executive_summary")
    if not s:
        elements.append(Paragraph("No executive summary available.", styles["fallback"]))
        return

    rows = [
        ["Metric", "Value"],
        ["Compliance", f"{s.get('compliance_percentage', 'N/A')}%"],
        ["Total Controls", str(s.get("total_controls", "N/A"))],
        ["Passed Controls", str(s.get("passed_controls", "N/A"))],
        ["Failed Controls", str(s.get("failed_controls", "N/A"))],
        ["Total Risks", str(s.get("total_risks", "N/A"))],
        ["High Risks", str(s.get("high_risks", "N/A"))],
        ["Medium Risks", str(s.get("medium_risks", "N/A"))],
        ["Low Risks", str(s.get("low_risks", "N/A"))],
        ["Total Treatment Actions", str(s.get("total_actions", "N/A"))],
        ["Technical Checks", str(s.get("technical_total_checks", "N/A"))],
        ["Technical Passed", str(s.get("technical_passed_checks", "N/A"))],
        ["Technical Failed", str(s.get("technical_failed_checks", "N/A"))],
        ["Technical Risks", str(s.get("technical_total_risks", "N/A"))],
    ]
    table = Table(rows, colWidths=[120 * mm, 50 * mm])
    table.setStyle(TableStyle(_TABLE_STYLE_BASE))
    elements.append(table)


def _add_top_risks(elements, data, styles):
    elements.append(_section_gap())
    elements.append(_divider())
    elements.append(Paragraph("Top Risks", styles["heading"]))
    risks = data.get("top_risks")
    if not risks:
        elements.append(Paragraph("No top risks identified.", styles["fallback"]))
        return

    rows = [["Risk ID", "Name", "Score", "Level"]]
    for r in risks:
        rows.append([str(r.get("id", "")), str(r.get("name", "")),
                      str(r.get("score", "")), str(r.get("level", ""))])
    table = Table(rows, colWidths=[35 * mm, 70 * mm, 30 * mm, 35 * mm])
    table.setStyle(TableStyle(_TABLE_STYLE_BASE))
    elements.append(table)


def _add_controls_overview(elements, data, styles):
    elements.append(_section_gap())
    elements.append(_divider())
    elements.append(Paragraph("Controls Overview", styles["heading"]))
    controls = data.get("controls_overview")
    if not controls:
        elements.append(Paragraph("No controls data available.", styles["fallback"]))
        return

    rows = [["Control ID", "Name", "Status"]]
    for c in controls:
        rows.append([str(c.get("id", "")), str(c.get("name", "")),
                      str(c.get("status", "")).upper()])
    table = Table(rows, colWidths=[35 * mm, 95 * mm, 40 * mm])
    table.setStyle(TableStyle(_TABLE_STYLE_BASE))
    elements.append(table)


def _add_treatment_actions(elements, data, styles):
    elements.append(_section_gap())
    elements.append(_divider())
    elements.append(Paragraph("Treatment Actions", styles["heading"]))
    actions = data.get("treatment_actions")
    if not actions:
        elements.append(Paragraph("No treatment actions defined.", styles["fallback"]))
        return

    rows = [["Risk ID", "Risk Name", "Priority", "Action", "Timeline"]]
    for a in actions:
        rows.append([str(a.get("risk_id", "")), str(a.get("risk_name", "")),
                      str(a.get("priority", "")), str(a.get("action", "")),
                      str(a.get("timeline", ""))])
    table = Table(rows, colWidths=[25 * mm, 35 * mm, 22 * mm, 55 * mm, 25 * mm])
    table.setStyle(TableStyle(_TABLE_STYLE_COMPACT))
    elements.append(table)


def _add_technical_findings(elements, data, styles):
    elements.append(_section_gap())
    elements.append(_divider())
    elements.append(Paragraph("Technical Findings", styles["heading"]))
    findings = data.get("technical_findings")
    if not findings:
        elements.append(Paragraph("No technical findings available.", styles["fallback"]))
        return

    rows = [["Check ID", "Name", "Status", "Expected", "Actual"]]
    for f in findings:
        rows.append([str(f.get("id", "")), str(f.get("name", "")),
                      str(f.get("status", "")).upper(),
                      str(f.get("expected", "")), str(f.get("actual", ""))])
    table = Table(rows, colWidths=[28 * mm, 60 * mm, 25 * mm, 28 * mm, 28 * mm])
    table.setStyle(TableStyle(_TABLE_STYLE_BASE))
    elements.append(table)


def _add_technical_risks(elements, data, styles):
    elements.append(_section_gap())
    elements.append(_divider())
    elements.append(Paragraph("Technical Risks", styles["heading"]))
    risks = data.get("technical_risks")
    if not risks:
        elements.append(Paragraph("No technical risks identified.", styles["fallback"]))
        return

    rows = [["Risk ID", "Name", "Likelihood", "Impact", "Score", "Level"]]
    for r in risks:
        rows.append([str(r.get("id", "")), str(r.get("name", "")),
                      str(r.get("likelihood", "")), str(r.get("impact", "")),
                      str(r.get("score", "")), str(r.get("level", ""))])
    table = Table(rows, colWidths=[28 * mm, 50 * mm, 25 * mm, 22 * mm, 22 * mm, 22 * mm])
    table.setStyle(TableStyle(_TABLE_STYLE_BASE))
    elements.append(table)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_combined_pdf(report_data: dict, output_path: str) -> str:
    """
    Generate a combined executive PDF report.

    Parameters
    ----------
    report_data : dict
        Output from combined_report_formatter.format_combined_report().
    output_path : str
        Destination file path for the PDF.

    Returns
    -------
    str
        The *output_path* the PDF was written to.
    """
    styles = _build_styles()
    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        topMargin=20 * mm, bottomMargin=20 * mm,
        leftMargin=18 * mm, rightMargin=18 * mm,
    )

    elements = []
    _add_title(elements, report_data, styles)
    _add_executive_summary(elements, report_data, styles)
    _add_top_risks(elements, report_data, styles)
    _add_controls_overview(elements, report_data, styles)
    _add_treatment_actions(elements, report_data, styles)
    _add_technical_findings(elements, report_data, styles)
    _add_technical_risks(elements, report_data, styles)

    doc.build(elements)
    return output_path


# ---------------------------------------------------------------------------
# Smoke test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mock = {
        "title": "SmartISMS Combined Assessment Report",
        "executive_summary": {
            "compliance_percentage": 60.0,
            "total_controls": 5, "passed_controls": 3, "failed_controls": 2,
            "total_risks": 2, "high_risks": 2, "medium_risks": 0, "low_risks": 0,
            "total_actions": 2,
            "technical_total_checks": 5, "technical_passed_checks": 2,
            "technical_failed_checks": 3, "technical_total_risks": 3,
        },
        "top_risks": [
            {"id": "ISO-0801", "name": "Asset Management", "score": 9, "level": "high"},
        ],
        "controls_overview": [
            {"id": "ISO-0501", "name": "Information Security Policy", "status": "pass"},
            {"id": "ISO-0801", "name": "Asset Management", "status": "fail"},
        ],
        "treatment_actions": [
            {"risk_id": "ISO-0801", "risk_name": "Asset Management",
             "priority": "high", "action": "Immediate mitigation required", "timeline": "30 days"},
        ],
        "technical_findings": [
            {"id": "CFG-001", "name": "Firewall Rules", "status": "pass", "expected": True, "actual": True},
            {"id": "CFG-003", "name": "Backup Configuration", "status": "fail", "expected": True, "actual": False},
        ],
        "technical_risks": [
            {"id": "CFG-003", "name": "Backup Configuration",
             "likelihood": 3, "impact": 3, "score": 9, "level": "high"},
        ],
    }

    out = generate_combined_pdf(mock, "combined_report.pdf")
    print(f"PDF generated -> {out}")
