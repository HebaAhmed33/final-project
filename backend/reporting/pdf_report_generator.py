"""
PDF Report Generator for SmartISMS Executive Reports.
Generates clean, printable PDF documents from executive report data.
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
    """Return a dict of custom paragraph styles used throughout the report."""
    base = getSampleStyleSheet()
    styles = {
        "title": ParagraphStyle(
            "ReportTitle",
            parent=base["Title"],
            fontSize=22,
            leading=28,
            spaceAfter=6,
        ),
        "heading": ParagraphStyle(
            "SectionHeading",
            parent=base["Heading2"],
            fontSize=14,
            leading=18,
            spaceBefore=18,
            spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "BodyText",
            parent=base["BodyText"],
            fontSize=10,
            leading=14,
            spaceAfter=4,
        ),
        "fallback": ParagraphStyle(
            "Fallback",
            parent=base["Italic"],
            fontSize=10,
            leading=14,
            textColor=colors.grey,
        ),
    }
    return styles


# ---------------------------------------------------------------------------
# Section builders
# ---------------------------------------------------------------------------

def _section_divider():
    """Horizontal rule used between sections."""
    return HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey,
                      spaceAfter=6, spaceBefore=2)


def _add_title(elements, report_data, styles):
    """Add the report title."""
    title = report_data.get("title", "SmartISMS Assessment Report")
    elements.append(Paragraph(title, styles["title"]))
    elements.append(_section_divider())


def _add_executive_summary(elements, report_data, styles):
    """Add the Executive Summary section."""
    elements.append(Paragraph("Executive Summary", styles["heading"]))
    summary = report_data.get("executive_summary")
    if not summary:
        elements.append(Paragraph("No executive summary available.", styles["fallback"]))
        return

    rows = [
        ["Metric", "Value"],
        ["Compliance", f"{summary.get('compliance_percentage', 'N/A')}%"],
        ["Total Controls", str(summary.get("total_controls", "N/A"))],
        ["Passed Controls", str(summary.get("passed_controls", "N/A"))],
        ["Failed Controls", str(summary.get("failed_controls", "N/A"))],
        ["Total Risks", str(summary.get("total_risks", "N/A"))],
        ["High Risks", str(summary.get("high_risks", "N/A"))],
        ["Medium Risks", str(summary.get("medium_risks", "N/A"))],
        ["Low Risks", str(summary.get("low_risks", "N/A"))],
        ["Total Treatment Actions", str(summary.get("total_actions", "N/A"))],
    ]

    table = Table(rows, colWidths=[120 * mm, 50 * mm])
    table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.Color(0.93, 0.93, 0.93)),
    ]))
    elements.append(table)


def _add_top_risks(elements, report_data, styles):
    """Add the Top Risks section."""
    elements.append(Spacer(1, 4))
    elements.append(_section_divider())
    elements.append(Paragraph("Top Risks", styles["heading"]))

    risks = report_data.get("top_risks")
    if not risks:
        elements.append(Paragraph("No top risks identified.", styles["fallback"]))
        return

    rows = [["Risk ID", "Name", "Score", "Level"]]
    for r in risks:
        rows.append([
            str(r.get("id", "")),
            str(r.get("name", "")),
            str(r.get("score", "")),
            str(r.get("level", "")),
        ])

    table = Table(rows, colWidths=[35 * mm, 70 * mm, 30 * mm, 35 * mm])
    table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.Color(0.93, 0.93, 0.93)),
    ]))
    elements.append(table)


def _add_controls_overview(elements, report_data, styles):
    """Add the Controls Overview section."""
    elements.append(Spacer(1, 4))
    elements.append(_section_divider())
    elements.append(Paragraph("Controls Overview", styles["heading"]))

    controls = report_data.get("controls_overview")
    if not controls:
        elements.append(Paragraph("No controls data available.", styles["fallback"]))
        return

    rows = [["Control ID", "Name", "Status"]]
    for c in controls:
        rows.append([
            str(c.get("id", "")),
            str(c.get("name", "")),
            str(c.get("status", "")).upper(),
        ])

    table = Table(rows, colWidths=[35 * mm, 95 * mm, 40 * mm])
    table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.Color(0.93, 0.93, 0.93)),
    ]))
    elements.append(table)


def _add_treatment_actions(elements, report_data, styles):
    """Add the Treatment Actions section."""
    elements.append(Spacer(1, 4))
    elements.append(_section_divider())
    elements.append(Paragraph("Treatment Actions", styles["heading"]))

    actions = report_data.get("treatment_actions")
    if not actions:
        elements.append(Paragraph("No treatment actions defined.", styles["fallback"]))
        return

    rows = [["Risk ID", "Risk Name", "Priority", "Action", "Timeline"]]
    for a in actions:
        rows.append([
            str(a.get("risk_id", "")),
            str(a.get("risk_name", "")),
            str(a.get("priority", "")),
            str(a.get("action", "")),
            str(a.get("timeline", "")),
        ])

    table = Table(rows, colWidths=[25 * mm, 35 * mm, 22 * mm, 55 * mm, 25 * mm])
    table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.Color(0.93, 0.93, 0.93)),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    elements.append(table)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_executive_pdf(report_data: dict, output_path: str) -> str:
    """
    Generate a clean, professional, printable executive PDF report.

    Parameters
    ----------
    report_data : dict
        Output from ``executive_report_formatter.format_executive_report``.
    output_path : str
        Destination file path for the PDF.

    Returns
    -------
    str
        The *output_path* the PDF was written to.
    """
    styles = _build_styles()

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
    )

    elements = []

    _add_title(elements, report_data, styles)
    _add_executive_summary(elements, report_data, styles)
    _add_top_risks(elements, report_data, styles)
    _add_controls_overview(elements, report_data, styles)
    _add_treatment_actions(elements, report_data, styles)

    doc.build(elements)
    return output_path


# ---------------------------------------------------------------------------
# Quick smoke-test with mock data
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mock_report = {
        "title": "SmartISMS Assessment Report",
        "executive_summary": {
            "compliance_percentage": 60.0,
            "total_controls": 5,
            "passed_controls": 3,
            "failed_controls": 2,
            "total_risks": 2,
            "high_risks": 2,
            "medium_risks": 0,
            "low_risks": 0,
            "total_actions": 2,
        },
        "top_risks": [
            {"id": "ISO-0801", "name": "Asset Management", "score": 9, "level": "high"},
            {"id": "ISO-1201", "name": "Operations Security", "score": 8, "level": "high"},
        ],
        "controls_overview": [
            {"id": "ISO-0501", "name": "Information Security Policy", "status": "pass"},
            {"id": "ISO-0601", "name": "Organization of Info Security", "status": "pass"},
            {"id": "ISO-0701", "name": "Human Resource Security", "status": "pass"},
            {"id": "ISO-0801", "name": "Asset Management", "status": "fail"},
            {"id": "ISO-1201", "name": "Operations Security", "status": "fail"},
        ],
        "treatment_actions": [
            {
                "risk_id": "ISO-0801",
                "risk_name": "Asset Management",
                "priority": "high",
                "action": "Immediate mitigation required",
                "timeline": "30 days",
            },
            {
                "risk_id": "ISO-1201",
                "risk_name": "Operations Security",
                "priority": "high",
                "action": "Review and implement operational controls",
                "timeline": "45 days",
            },
        ],
    }

    out = generate_executive_pdf(mock_report, "executive_report.pdf")
    print(f"PDF generated -> {out}")
