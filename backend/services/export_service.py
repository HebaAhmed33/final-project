"""
Export Service.

Generates Excel workbook and PDF report from the latest completed
assessment stored in data/assessments.json.
"""

import io
import json
import os
import re
from datetime import datetime

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
_ASSESSMENTS_FILE = os.path.join(_DATA_DIR, "assessments.json")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_assessments() -> list[dict]:
    """Load all assessment records from the JSON store."""
    if not os.path.exists(_ASSESSMENTS_FILE):
        return []
    with open(_ASSESSMENTS_FILE, "r", encoding="utf-8") as fh:
        return json.load(fh)


def get_latest_completed_assessment() -> dict | None:
    """
    Return the most recent assessment that contains a framework_assessment
    with populated data (compliance_score is not None).
    """
    records = _load_assessments()
    for rec in reversed(records):
        fa = rec.get("framework_assessment", {})
        if fa and fa.get("compliance_score") is not None:
            # Merge top-level metadata into the framework_assessment dict
            fa["_company_name"] = rec.get("assessment_name", "")
            fa["_file_name"] = rec.get("file_name", "")
            fa["_top_framework"] = rec.get("framework", "")
            fa["_top_created_at"] = rec.get("created_at", "")
            return fa
    return None


def _safe_filename(text: str) -> str:
    """Sanitise a string for use in a filename."""
    return re.sub(r"[^a-zA-Z0-9_\-]", "_", (text or "export").strip())[:60]


def _fmt_date(iso_str: str) -> str:
    """Format an ISO date string to YYYY-MM-DD, or return today."""
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return datetime.now().strftime("%Y-%m-%d")


# ---------------------------------------------------------------------------
# Excel export
# ---------------------------------------------------------------------------

_HEADER_FONT = Font(bold=True, color="FFFFFF", size=11)
_HEADER_FILL = PatternFill(start_color="111936", end_color="111936", fill_type="solid")
_HEADER_ALIGN = Alignment(horizontal="center", vertical="center", wrap_text=True)
_CELL_ALIGN = Alignment(vertical="top", wrap_text=True)
_THIN_BORDER = Border(
    left=Side(style="thin", color="D1D5DB"),
    right=Side(style="thin", color="D1D5DB"),
    top=Side(style="thin", color="D1D5DB"),
    bottom=Side(style="thin", color="D1D5DB"),
)


def _add_header_row(ws, headers: list[str], row: int = 1):
    """Write a styled header row."""
    for col_idx, header in enumerate(headers, start=1):
        cell = ws.cell(row=row, column=col_idx, value=header)
        cell.font = _HEADER_FONT
        cell.fill = _HEADER_FILL
        cell.alignment = _HEADER_ALIGN
        cell.border = _THIN_BORDER


def _write_rows(ws, rows: list[list], start_row: int = 2):
    """Write data rows with basic styling."""
    for r_idx, row_data in enumerate(rows, start=start_row):
        for c_idx, value in enumerate(row_data, start=1):
            cell = ws.cell(row=r_idx, column=c_idx, value=value)
            cell.alignment = _CELL_ALIGN
            cell.border = _THIN_BORDER


def _auto_width(ws, min_width: int = 12, max_width: int = 50):
    """Auto-adjust column widths."""
    for col in ws.columns:
        longest = min_width
        col_letter = col[0].column_letter
        for cell in col:
            if cell.value:
                longest = max(longest, min(len(str(cell.value)), max_width))
        ws.column_dimensions[col_letter].width = longest + 2


def build_excel_workbook(fa: dict) -> tuple[io.BytesIO, str]:
    """
    Build an Excel workbook from a framework_assessment dict.

    Returns (BytesIO buffer, suggested filename).
    """
    wb = openpyxl.Workbook()
    company = _safe_filename(fa.get("assessment_name") or fa.get("_company_name") or "assessment")
    date_str = _fmt_date(fa.get("created_at") or fa.get("_top_created_at", ""))

    # --- Sheet 1: Summary ---
    ws = wb.active
    ws.title = "Summary"
    summary_data = [
        ["Field", "Value"],
        ["Assessment Name", fa.get("assessment_name", "")],
        ["Framework", fa.get("framework", "")],
        ["Date", date_str],
        ["Compliance Score", f"{fa.get('compliance_score', 0)}%"],
        ["Total Controls", fa.get("total_controls", 0)],
        ["Compliant", fa.get("compliant_controls", 0)],
        ["Partial", fa.get("partial_controls", 0)],
        ["Missing", fa.get("missing_controls", 0)],
        ["Evidence Backed", "Yes" if fa.get("evidence_backed") else "No"],
    ]
    _add_header_row(ws, summary_data[0])
    _write_rows(ws, summary_data[1:])
    _auto_width(ws)

    # --- Sheet 2: SoA ---
    soa = fa.get("soa") or fa.get("statement_of_applicability")
    soa_entries = []
    if isinstance(soa, dict):
        soa_entries = soa.get("entries", [])
    elif isinstance(soa, list):
        soa_entries = soa

    if soa_entries:
        ws_soa = wb.create_sheet("SoA")
        headers = ["#", "Section", "Control No", "Control Title", "Applicable", "Status", "Implementation", "Reference"]
        _add_header_row(ws_soa, headers)
        rows = []
        for i, e in enumerate(soa_entries, 1):
            rows.append([
                i,
                e.get("section", ""),
                e.get("control_no", ""),
                e.get("control_title", ""),
                e.get("applicable", "Yes"),
                e.get("status", ""),
                e.get("implementation", e.get("remarks", "")),
                e.get("reference", ""),
            ])
        _write_rows(ws_soa, rows)
        _auto_width(ws_soa)

    # --- Sheet 3: Compliance Matrix ---
    cm = fa.get("compliance_matrix")
    cm_entries = []
    if isinstance(cm, dict):
        cm_entries = cm.get("entries", cm.get("controls", []))
    elif isinstance(cm, list):
        cm_entries = cm

    if cm_entries:
        ws_cm = wb.create_sheet("Compliance Matrix")
        headers = ["Control ID", "Control Name", "Status", "Evidence", "Gap", "Recommendation"]
        _add_header_row(ws_cm, headers)
        rows = []
        for e in cm_entries:
            rows.append([
                e.get("control_id", e.get("control_no", "")),
                e.get("control_name", e.get("control_title", "")),
                e.get("status", ""),
                e.get("evidence", e.get("evidence_summary", "")),
                e.get("gap", e.get("gap_description", "")),
                e.get("recommendation", ""),
            ])
        _write_rows(ws_cm, rows)
        _auto_width(ws_cm)

    # --- Sheet 4: High Risks ---
    rr = fa.get("risk_register", {})
    risk_entries = []
    if isinstance(rr, dict):
        risk_entries = rr.get("generated_risk_entries", []) + rr.get("uploaded_risk_entries", [])
    elif isinstance(rr, list):
        risk_entries = rr

    high_risks = []
    for r in risk_entries:
        try:
            l_val = float(r.get("likelihood", 0))
            i_val = float(r.get("impact", 0))
            if l_val * i_val >= 12:
                high_risks.append(r)
        except (ValueError, TypeError):
            level = (r.get("risk_level", r.get("level", "")) or "").lower()
            if level in ("high", "critical", "extreme"):
                high_risks.append(r)

    if high_risks:
        ws_hr = wb.create_sheet("High Risks")
        headers = ["Risk ID", "Risk Statement", "Threat", "Asset", "Likelihood", "Impact", "Risk Level"]
        _add_header_row(ws_hr, headers)
        rows = []
        for r in high_risks:
            rows.append([
                r.get("risk_id", r.get("id", "")),
                r.get("risk_statement", r.get("description", r.get("title", ""))),
                r.get("threat", r.get("vulnerability", "")),
                r.get("asset", r.get("asset_type", "")),
                r.get("likelihood", ""),
                r.get("impact", ""),
                r.get("risk_level", r.get("level", "")),
            ])
        _write_rows(ws_hr, rows)
        _auto_width(ws_hr)

    # --- Sheet 5: Risk Register (all) ---
    if risk_entries:
        ws_rr = wb.create_sheet("Risk Register")
        headers = ["Risk ID", "Risk Statement", "Threat", "Asset", "Likelihood", "Impact", "Risk Level", "Control", "Owner"]
        _add_header_row(ws_rr, headers)
        rows = []
        for r in risk_entries:
            ctrl = ""
            if r.get("iso_controls"):
                ctrl = ", ".join(r["iso_controls"]) if isinstance(r["iso_controls"], list) else str(r["iso_controls"])
            elif r.get("control"):
                ctrl = r["control"]
            elif r.get("rule_id"):
                ctrl = r["rule_id"]
            rows.append([
                r.get("risk_id", r.get("id", "")),
                r.get("risk_statement", r.get("description", r.get("title", ""))),
                r.get("threat", r.get("vulnerability", "")),
                r.get("asset", r.get("asset_type", "")),
                r.get("likelihood", ""),
                r.get("impact", ""),
                r.get("risk_level", r.get("level", "")),
                ctrl,
                r.get("owner", ""),
            ])
        _write_rows(ws_rr, rows)
        _auto_width(ws_rr)

    # --- Sheet 6: Treatment Plan ---
    tp = fa.get("risk_treatment_plan") or fa.get("treatment_plan")
    tp_entries = []
    if isinstance(tp, list):
        tp_entries = tp
    elif isinstance(tp, dict):
        tp_entries = tp.get("entries", tp.get("actions", []))

    if tp_entries:
        ws_tp = wb.create_sheet("Treatment Plan")
        headers = ["Risk ID", "Treatment", "Due Date"]
        _add_header_row(ws_tp, headers)
        rows = []
        for e in tp_entries:
            rows.append([
                e.get("risk_id", ""),
                e.get("treatment", e.get("action", "")),
                e.get("due_date", ""),
            ])
        _write_rows(ws_tp, rows)
        _auto_width(ws_tp)

    # --- Sheet 7: Vendor Checklist ---
    vc = fa.get("vendor_checklist")
    vc_entries = []
    if isinstance(vc, dict):
        vc_entries = vc.get("entries", vc.get("vendors", []))
    elif isinstance(vc, list):
        vc_entries = vc

    if vc_entries:
        ws_vc = wb.create_sheet("Vendor Checklist")
        headers = ["Vendor", "Risk Level", "Agreement", "Last Reviewed", "Status", "Notes"]
        _add_header_row(ws_vc, headers)
        rows = []
        for e in vc_entries:
            rows.append([
                e.get("vendor_name", e.get("vendor", e.get("name", ""))),
                e.get("risk_level", e.get("risk", "")),
                e.get("agreement_signed", e.get("agreement", "")),
                e.get("last_reviewed", e.get("review_date", "")),
                e.get("status", e.get("compliance_status", "")),
                e.get("notes", e.get("remarks", "")),
            ])
        _write_rows(ws_vc, rows)
        _auto_width(ws_vc)

    # --- Sheet 8: Training Matrix ---
    tm = fa.get("training_matrix") or fa.get("training_matrix_generated")
    tm_entries = []
    if isinstance(tm, dict):
        tm_entries = tm.get("entries", tm.get("employees", tm.get("records", [])))
    elif isinstance(tm, list):
        tm_entries = tm

    if tm_entries:
        ws_tm = wb.create_sheet("Training Matrix")
        headers = ["Employee", "Role", "Training Topic", "Risk Driver", "Status", "Completion Date", "Next Due"]
        _add_header_row(ws_tm, headers)
        rows = []
        for e in tm_entries:
            rows.append([
                e.get("employee_name", e.get("employee", e.get("name", ""))),
                e.get("role", e.get("department", "")),
                e.get("training_topic", e.get("topic", e.get("course", ""))),
                e.get("risk_driver", ""),
                e.get("status", ""),
                e.get("completion_date", e.get("completed", "")),
                e.get("next_due_date", e.get("next_due", "")),
            ])
        _write_rows(ws_tm, rows)
        _auto_width(ws_tm)

    # --- Sheet 9: Governance Calendar ---
    gc = fa.get("governance_calendar") or fa.get("governance_calendar_generated")
    gc_entries = []
    if isinstance(gc, dict):
        gc_entries = gc.get("entries", gc.get("events", gc.get("items", [])))
    elif isinstance(gc, list):
        gc_entries = gc

    if gc_entries:
        ws_gc = wb.create_sheet("Governance Calendar")
        headers = ["Activity", "Frequency", "Owner", "Next Due", "Status", "Notes"]
        _add_header_row(ws_gc, headers)
        rows = []
        for e in gc_entries:
            rows.append([
                e.get("activity", e.get("task", e.get("event", ""))),
                e.get("frequency", ""),
                e.get("owner", e.get("responsible", "")),
                e.get("next_due", e.get("due_date", "")),
                e.get("status", ""),
                e.get("notes", e.get("remarks", "")),
            ])
        _write_rows(ws_gc, rows)
        _auto_width(ws_gc)

    # Write to buffer
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)

    filename = f"assessment_export_{company}_{date_str}.xlsx"
    return buf, filename


# ---------------------------------------------------------------------------
# PDF export  (simple text-based PDF using only stdlib + openpyxl already available)
# ---------------------------------------------------------------------------

class _SimplePDF:
    """
    Minimal PDF generator using raw PDF operators.
    No external dependency (no reportlab / fpdf required).
    """

    def __init__(self):
        self._pages: list[list[str]] = []
        self._current_page: list[str] = []
        self._y = 750  # current y position (top of content area)
        self._page_bottom = 60
        self._line_height = 14
        self._font_size = 10

    def _new_page(self):
        if self._current_page:
            self._pages.append(self._current_page)
        self._current_page = []
        self._y = 750

    def _ensure_space(self, lines_needed: int = 1):
        if self._y - (lines_needed * self._line_height) < self._page_bottom:
            self._new_page()

    def add_title(self, text: str):
        self._ensure_space(3)
        self._current_page.append(f"BT /F1 16 Tf 50 {self._y} Td ({self._esc(text)}) Tj ET")
        self._y -= 28

    def add_heading(self, text: str):
        self._ensure_space(2)
        self._y -= 8  # spacing before heading
        self._current_page.append(f"BT /F1 12 Tf 50 {self._y} Td ({self._esc(text)}) Tj ET")
        self._y -= 20

    def add_line(self, text: str, indent: int = 50):
        # Split long lines
        max_chars = 95
        while len(text) > max_chars:
            cut = text[:max_chars].rfind(" ")
            if cut <= 0:
                cut = max_chars
            self._ensure_space()
            self._current_page.append(
                f"BT /F2 {self._font_size} Tf {indent} {self._y} Td ({self._esc(text[:cut])}) Tj ET"
            )
            self._y -= self._line_height
            text = text[cut:].lstrip()
        if text:
            self._ensure_space()
            self._current_page.append(
                f"BT /F2 {self._font_size} Tf {indent} {self._y} Td ({self._esc(text)}) Tj ET"
            )
            self._y -= self._line_height

    def add_blank(self):
        self._y -= 6

    @staticmethod
    def _esc(text: str) -> str:
        return (
            str(text)
            .replace("\\", "\\\\")
            .replace("(", "\\(")
            .replace(")", "\\)")
            .replace("\r", "")
            .replace("\n", " ")
        )

    def render(self) -> bytes:
        if self._current_page:
            self._pages.append(self._current_page)
            self._current_page = []

        objects: list[bytes] = []
        offsets: list[int] = []
        output = b""

        def add_obj(content: str) -> int:
            nonlocal output
            idx = len(objects) + 1
            offsets.append(len(output))
            obj_bytes = f"{idx} 0 obj\n{content}\nendobj\n".encode("latin-1", errors="replace")
            objects.append(obj_bytes)
            output += obj_bytes
            return idx

        header = b"%PDF-1.4\n"
        output += header

        # Font objects
        f1_id = add_obj("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>")
        f2_id = add_obj("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")

        # Resource dict string
        resources = f"<< /Font << /F1 {f1_id} 0 R /F2 {f2_id} 0 R >> >>"

        page_ids = []
        for page_cmds in self._pages:
            stream_content = "\n".join(page_cmds)
            stream_id = add_obj(
                f"<< /Length {len(stream_content)} >>\nstream\n{stream_content}\nendstream"
            )
            page_id = add_obj(
                f"<< /Type /Page /Parent PAGES_REF"
                f" /MediaBox [0 0 595 842]"
                f" /Contents {stream_id} 0 R"
                f" /Resources {resources} >>"
            )
            page_ids.append(page_id)

        kids = " ".join(f"{pid} 0 R" for pid in page_ids)
        pages_id = add_obj(
            f"<< /Type /Pages /Kids [{kids}] /Count {len(page_ids)} >>"
        )

        # Patch parent references
        new_output = output.replace(b"PAGES_REF", f"{pages_id} 0 R".encode())
        output = new_output

        catalog_id = add_obj(f"<< /Type /Catalog /Pages {pages_id} 0 R >>")

        # xref
        xref_offset = len(output)
        xref = f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n"
        for off in offsets:
            xref += f"{off:010d} 00000 n \n"
        output += xref.encode("latin-1")
        output += f"trailer\n<< /Size {len(objects) + 1} /Root {catalog_id} 0 R >>\n".encode()
        output += f"startxref\n{xref_offset}\n%%EOF\n".encode()

        return output


def build_pdf_report(fa: dict) -> tuple[io.BytesIO, str]:
    """
    Build a PDF report from a framework_assessment dict.

    Returns (BytesIO buffer, suggested filename).
    """
    pdf = _SimplePDF()
    company = fa.get("assessment_name") or fa.get("_company_name") or "Assessment"
    framework = fa.get("framework") or fa.get("_top_framework") or ""
    date_str = _fmt_date(fa.get("created_at") or fa.get("_top_created_at", ""))
    score = fa.get("compliance_score", 0)

    # --- Title Page ---
    pdf.add_title(f"{framework} Assessment Report")
    pdf.add_blank()
    pdf.add_line(f"Company / Assessment: {company}")
    pdf.add_line(f"Framework: {framework}")
    pdf.add_line(f"Date: {date_str}")
    pdf.add_line(f"Compliance Score: {score}%")
    pdf.add_line(f"Total Controls: {fa.get('total_controls', 0)}")
    pdf.add_line(f"Compliant: {fa.get('compliant_controls', 0)}")
    pdf.add_line(f"Partial: {fa.get('partial_controls', 0)}")
    pdf.add_line(f"Missing: {fa.get('missing_controls', 0)}")
    pdf.add_blank()

    # --- Key Findings ---
    pdf.add_heading("Key Findings")
    insights = fa.get("insights", [])
    if insights:
        for ins in insights[:10]:
            pdf.add_line(f"- {ins}", indent=60)
    else:
        pdf.add_line("No key findings available.")
    pdf.add_blank()

    # --- High Risks Summary ---
    pdf.add_heading("High Risks Summary")
    top_risks = fa.get("top_missing_high_risk", [])
    if top_risks:
        for r in top_risks:
            pdf.add_line(
                f"- [{r.get('rule_id', '')}] {r.get('name', '')} ({r.get('section_name', '')})",
                indent=60,
            )
    else:
        pdf.add_line("No high-risk items identified.")
    pdf.add_blank()

    # --- Risk Register summary ---
    rr = fa.get("risk_register", {})
    risk_entries = []
    if isinstance(rr, dict):
        risk_entries = rr.get("generated_risk_entries", []) + rr.get("uploaded_risk_entries", [])
    elif isinstance(rr, list):
        risk_entries = rr
    if risk_entries:
        pdf.add_heading("Risk Register Overview")
        pdf.add_line(f"Total risks identified: {len(risk_entries)}")
        high_count = 0
        for r in risk_entries:
            try:
                if float(r.get("likelihood", 0)) * float(r.get("impact", 0)) >= 12:
                    high_count += 1
            except (ValueError, TypeError):
                pass
        pdf.add_line(f"High / Critical risks: {high_count}")
        pdf.add_blank()

    # --- Treatment Plan Summary ---
    tp = fa.get("risk_treatment_plan") or fa.get("treatment_plan")
    tp_entries = []
    if isinstance(tp, list):
        tp_entries = tp
    elif isinstance(tp, dict):
        tp_entries = tp.get("entries", tp.get("actions", []))
    if tp_entries:
        pdf.add_heading("Treatment Plan Summary")
        pdf.add_line(f"Total treatment actions: {len(tp_entries)}")
        for e in tp_entries[:5]:
            pdf.add_line(
                f"- [{e.get('risk_id', '')}] {(e.get('treatment', e.get('action', '')))[:120]}",
                indent=60,
            )
        if len(tp_entries) > 5:
            pdf.add_line(f"  ... and {len(tp_entries) - 5} more actions.")
        pdf.add_blank()

    # --- Governance Calendar summary ---
    gc = fa.get("governance_calendar") or fa.get("governance_calendar_generated")
    gc_entries = []
    if isinstance(gc, dict):
        gc_entries = gc.get("entries", gc.get("events", gc.get("items", [])))
    elif isinstance(gc, list):
        gc_entries = gc
    if gc_entries:
        pdf.add_heading("Governance Calendar")
        pdf.add_line(f"Total scheduled activities: {len(gc_entries)}")
        for e in gc_entries[:5]:
            pdf.add_line(
                f"- {e.get('activity', e.get('task', ''))} | {e.get('frequency', '')} | Owner: {e.get('owner', e.get('responsible', ''))}",
                indent=60,
            )
        if len(gc_entries) > 5:
            pdf.add_line(f"  ... and {len(gc_entries) - 5} more items.")
        pdf.add_blank()

    # --- Training Matrix summary ---
    tm = fa.get("training_matrix") or fa.get("training_matrix_generated")
    tm_entries = []
    if isinstance(tm, dict):
        tm_entries = tm.get("entries", tm.get("employees", tm.get("records", [])))
    elif isinstance(tm, list):
        tm_entries = tm
    if tm_entries:
        pdf.add_heading("Training Matrix")
        pdf.add_line(f"Total training records: {len(tm_entries)}")
        pdf.add_blank()

    # --- Vendor Checklist summary ---
    vc = fa.get("vendor_checklist")
    vc_entries = []
    if isinstance(vc, dict):
        vc_entries = vc.get("entries", vc.get("vendors", []))
    elif isinstance(vc, list):
        vc_entries = vc
    if vc_entries:
        pdf.add_heading("Vendor Checklist")
        pdf.add_line(f"Total vendors assessed: {len(vc_entries)}")
        for e in vc_entries[:5]:
            vendor_name = e.get("vendor_name", e.get("vendor", e.get("name", "")))
            status = e.get("status", e.get("compliance_status", ""))
            pdf.add_line(f"- {vendor_name}: {status}", indent=60)
        if len(vc_entries) > 5:
            pdf.add_line(f"  ... and {len(vc_entries) - 5} more vendors.")
        pdf.add_blank()

    # --- Footer ---
    pdf.add_blank()
    pdf.add_line(f"Generated by SmartISMS / Aegis.One on {date_str}")

    buf = io.BytesIO(pdf.render())
    buf.seek(0)
    safe_company = _safe_filename(company)
    filename = f"assessment_report_{safe_company}_{date_str}.pdf"
    return buf, filename
