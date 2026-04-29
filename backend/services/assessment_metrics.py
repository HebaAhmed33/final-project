"""
Assessment Metrics Service.

Computes compliance scores, severity breakdowns, and section-level summaries
from annotated assessment sections. All calculations are deterministic and
derived from actual control data — nothing is hardcoded.
"""


def _normalize_severity(severity: str) -> str:
    """Normalize severity to lowercase, default to 'unknown'."""
    return (severity or "unknown").strip().lower()


def _compute_control_status(ctrl: dict) -> str:
    """
    Determine the assessment status of a single control.

    Returns 'compliant', 'partial', or 'missing'.
    """
    if not ctrl.get("has_evidence"):
        return "missing"

    evidence_status = (ctrl.get("evidence_status") or "").strip().lower()
    if evidence_status in ("partial", "in progress", "in_progress", "incomplete"):
        return "partial"

    return "compliant"


def annotate_control_statuses(sections: list[dict]) -> None:
    """
    Mutate each control in each section to include:
      - status: 'compliant' | 'partial' | 'missing'
      - mapped_evidence_count: 1 if evidence present, else 0

    This should be called AFTER evidence mapping is applied.
    """
    for section in sections:
        for ctrl in section.get("controls", []):
            ctrl["status"] = _compute_control_status(ctrl)
            ctrl["mapped_evidence_count"] = 1 if ctrl.get("has_evidence") else 0


def compute_compliance_score(
    sections: list[dict],
    framework_id: str = "",
    routing: dict | None = None,
    all_sheets: list[dict] | None = None,
) -> dict:
    """
    Compute the overall compliance score across all sections.

    For PCI DSS, uses a risk-based scoring engine that applies weighted
    deductions for critical misconfigurations found in the actual data.
    For other frameworks, uses the standard GRC maturity scoring.

    Returns
    -------
    dict
        compliance_score, compliant_controls, partial_controls,
        missing_controls, total_controls
        (PCI only: also includes risk_score, control_score, findings)
    """
    total = 0
    compliant = 0
    partial = 0
    missing = 0

    for section in sections:
        for ctrl in section.get("controls", []):
            total += 1
            status = ctrl.get("status", "missing")
            if status == "compliant":
                compliant += 1
            elif status == "partial":
                partial += 1
            else:
                missing += 1

    # GRC maturity scoring: compliant = 100%, partial = 50%, missing = 0%
    score = round(((compliant + partial * 0.5) / total) * 100, 2) if total > 0 else 0.0

    result = {
        "compliance_score": score,
        "compliant_controls": compliant,
        "partial_controls": partial,
        "missing_controls": missing,
        "total_controls": total,
    }

    # ── PCI DSS: apply risk-based scoring engine ──────────────────────────
    fw = (framework_id or "").lower().replace(" ", "").replace("-", "").replace("_", "")
    if "pci" in fw and routing is not None:
        try:
            # Collect all controls flat from sections
            all_controls = []
            for section in sections:
                all_controls.extend(section.get("controls", []))

            from services.evidence_inference import compute_pci_risk_based_score
            pci_score = compute_pci_risk_based_score(
                controls=all_controls,
                routing=routing,
                all_sheets=all_sheets,
            )
            # Override the basic score with risk-based score
            result["compliance_score"] = pci_score["compliance_score"]
            result["control_score"] = pci_score["control_score"]
            result["risk_score"] = pci_score["risk_score"]
            result["total_deduction"] = pci_score["total_deduction"]
            result["risk_findings"] = pci_score["findings"]
            # Use counts from the risk engine (should match)
            result["compliant_controls"] = pci_score["compliant_controls"]
            result["partial_controls"] = pci_score["partial_controls"]
            result["missing_controls"] = pci_score["missing_controls"]
        except Exception:
            pass  # Fall back to standard scoring on error

    return result



def compute_severity_breakdown(sections: list[dict]) -> dict:
    """
    Compute compliant/partial/missing counts grouped by severity level.

    Returns
    -------
    dict
        Keyed by severity ('high', 'medium', 'low'), each containing
        compliant, partial, missing counts.
    """
    breakdown: dict[str, dict[str, int]] = {}

    for section in sections:
        for ctrl in section.get("controls", []):
            sev = _normalize_severity(ctrl.get("severity"))
            if sev not in breakdown:
                breakdown[sev] = {"compliant": 0, "partial": 0, "missing": 0, "total": 0}

            status = ctrl.get("status", "missing")
            breakdown[sev]["total"] += 1
            if status == "compliant":
                breakdown[sev]["compliant"] += 1
            elif status == "partial":
                breakdown[sev]["partial"] += 1
            else:
                breakdown[sev]["missing"] += 1

    return breakdown


def compute_section_summaries(sections: list[dict]) -> None:
    """
    Mutate each section to include its own compliance summary:
      - compliant_controls
      - partial_controls
      - missing_controls
      - compliance_score
    """
    for section in sections:
        controls = section.get("controls", [])
        total = len(controls)
        compliant = sum(1 for c in controls if c.get("status") == "compliant")
        partial = sum(1 for c in controls if c.get("status") == "partial")
        missing = total - compliant - partial

        section["compliant_controls"] = compliant
        section["partial_controls"] = partial
        section["missing_controls"] = missing
        section["compliance_score"] = round(((compliant + partial * 0.5) / total) * 100, 2) if total > 0 else 0.0


def get_top_missing_high_risk(sections: list[dict], limit: int = 5) -> list[dict]:
    """
    Return the top N missing high-severity controls across all sections.

    Each entry contains rule_id, control, name, section_key, section_name.
    """
    missing_high: list[dict] = []

    for section in sections:
        for ctrl in section.get("controls", []):
            if ctrl.get("status") == "missing" and _normalize_severity(ctrl.get("severity")) == "high":
                missing_high.append({
                    "rule_id": ctrl.get("rule_id", ""),
                    "control": ctrl.get("control", ""),
                    "name": ctrl.get("name", ""),
                    "section_key": section.get("section_key", ""),
                    "section_name": section.get("section_name", ""),
                })

    return missing_high[:limit]
