"""
Assessment Builder Service.

Combines framework control sections with optional uploaded evidence
to produce a complete, frontend-ready assessment payload including:
- per-control status annotation
- overall compliance score
- severity-aware breakdown
- section-level summaries
- rule-based smart insights
"""

import uuid
from datetime import datetime, timezone

from services.framework_loader import load_framework
from services.control_mapping import map_evidence_to_controls
from services.assessment_metrics import (
    annotate_control_statuses,
    compute_compliance_score,
    compute_severity_breakdown,
    compute_section_summaries,
    get_top_missing_high_risk,
)
from services.assessment_insights import generate_insights


def build_assessment(
    framework: str,
    uploaded_rows: list[dict] | None = None,
    assessment_name: str = "",
    scope: str = "",
    priority: str = "",
    notes: str = "",
) -> dict:
    """
    Build a structured assessment payload with full scoring and insights.

    Pipeline:
      1. Load framework grouped controls
      2. Map uploaded evidence rows (if any)
      3. Annotate every control with status
      4. Compute compliance score
      5. Compute severity breakdown
      6. Compute section-level summaries
      7. Generate smart insights
      8. Assemble final response

    Parameters
    ----------
    framework : str
        Framework identifier (e.g. "ISO 27001").
    uploaded_rows : list[dict] | None
        Optional parsed rows from an uploaded Excel file.
    assessment_name, scope, priority, notes : str
        Additional metadata.

    Returns
    -------
    dict
        Complete assessment payload.
    """
    # ── 1. Load framework ─────────────────────────────────────────────────
    framework_data = load_framework(framework)
    sections = framework_data["sections"]

    # ── 2. Map evidence if provided ───────────────────────────────────────
    mapping_result = None
    if uploaded_rows:
        mapping_result = map_evidence_to_controls(
            uploaded_rows=uploaded_rows,
            framework_sections=sections,
        )

        # Annotate each control with evidence data
        mapped_lookup: dict[str, dict] = {}
        for mc in mapping_result["mapped_controls"]:
            rid = (mc.get("rule_id") or "").lower()
            mapped_lookup[rid] = mc

        for section in sections:
            for ctrl in section.get("controls", []):
                rid = (ctrl.get("rule_id") or "").lower()
                if rid in mapped_lookup:
                    ctrl["has_evidence"] = True
                    ctrl["evidence_status"] = mapped_lookup[rid].get("evidence_status", "")
                    ctrl["evidence_row"] = mapped_lookup[rid].get("evidence_row", {})
                else:
                    ctrl["has_evidence"] = False
                    ctrl["evidence_status"] = ""
                    ctrl["evidence_row"] = {}
    else:
        # No evidence — mark every control as no-evidence
        for section in sections:
            for ctrl in section.get("controls", []):
                ctrl["has_evidence"] = False
                ctrl["evidence_status"] = ""
                ctrl["evidence_row"] = {}

    # ── 3. Annotate control statuses ──────────────────────────────────────
    annotate_control_statuses(sections)

    # ── 4. Compliance score ───────────────────────────────────────────────
    score_data = compute_compliance_score(sections)

    # ── 5. Severity breakdown ─────────────────────────────────────────────
    severity_breakdown = compute_severity_breakdown(sections)

    # ── 6. Section-level summaries ────────────────────────────────────────
    compute_section_summaries(sections)

    # ── 7. Smart insights ─────────────────────────────────────────────────
    insights = generate_insights(
        sections=sections,
        overall_score=score_data["compliance_score"],
        severity_breakdown=severity_breakdown,
        total_controls=score_data["total_controls"],
        compliant_controls=score_data["compliant_controls"],
        missing_controls=score_data["missing_controls"],
    )

    # ── 8. Assemble response ──────────────────────────────────────────────
    response = {
        "success": True,
        "message": f"{framework_data['framework']} assessment completed successfully.",
        "assessment_id": str(uuid.uuid4()),
        "framework": framework_data["framework"],
        "assessment_name": assessment_name,
        "scope": scope,
        "priority": priority,
        "notes": notes,
        "created_at": datetime.now(timezone.utc).isoformat(),

        # Compliance score
        "compliance_score": score_data["compliance_score"],
        "compliant_controls": score_data["compliant_controls"],
        "partial_controls": score_data["partial_controls"],
        "missing_controls": score_data["missing_controls"],
        "total_controls": score_data["total_controls"],

        # Severity breakdown
        "severity_summary": severity_breakdown,

        # Sections (each now includes its own summary)
        "total_sections": framework_data["total_sections"],
        "sections": sections,

        # Smart insights
        "insights": insights,

        # Top missing high-risk controls
        "top_missing_high_risk": get_top_missing_high_risk(sections),
    }

    # Evidence mapping summary
    if mapping_result:
        response["evidence_mapping"] = {
            "mapped_controls_count": mapping_result["mapped_count"],
            "unmapped_controls_count": mapping_result["unmapped_count"],
            "unmatched_rows_count": len(mapping_result["unmatched_rows"]),
        }
    else:
        response["evidence_mapping"] = None

    # Most / least compliant section
    scored = [s for s in sections if s.get("controls_count", 0) > 0]
    if scored:
        best = max(scored, key=lambda s: s.get("compliance_score", 0))
        worst = min(scored, key=lambda s: s.get("compliance_score", 0))
        response["most_compliant_section"] = {
            "section_key": best["section_key"],
            "section_name": best["section_name"],
            "compliance_score": best["compliance_score"],
        }
        response["least_compliant_section"] = {
            "section_key": worst["section_key"],
            "section_name": worst["section_name"],
            "compliance_score": worst["compliance_score"],
        }

    if framework_data.get("errors"):
        response["warnings"] = framework_data["errors"]

    return response
