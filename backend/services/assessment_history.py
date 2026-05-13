"""
Assessment History Service.

Persists assessment execution records to local JSON storage.
Each record captures framework, timestamp, scoring snapshot,
and whether evidence was used — enabling trend analysis and
export readiness.
"""

import json
import os
import uuid
from datetime import datetime, timezone

import portalocker

_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
_HISTORY_FILE = os.path.join(_DATA_DIR, "assessment_history.json")


def _load() -> list[dict]:
    if not os.path.exists(_HISTORY_FILE):
        return []
    with open(_HISTORY_FILE, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _save(records: list[dict]) -> None:
    os.makedirs(_DATA_DIR, exist_ok=True)
    with open(_HISTORY_FILE, "w", encoding="utf-8") as fh:
        portalocker.lock(fh, portalocker.LOCK_EX)
        json.dump(records, fh, indent=2, ensure_ascii=False)
        portalocker.unlock(fh)


def save_assessment_run(assessment_result: dict) -> dict:
    """
    Persist a snapshot of an assessment execution.

    Parameters
    ----------
    assessment_result : dict
        The full response from build_assessment().

    Returns
    -------
    dict
        The saved history record (subset of the full result).
    """
    record = {
        "id": str(uuid.uuid4()),
        "assessment_id": assessment_result.get("assessment_id", ""),
        "framework": assessment_result.get("framework", ""),
        "assessment_name": assessment_result.get("assessment_name", ""),
        "scope": assessment_result.get("scope", ""),
        "priority": assessment_result.get("priority", ""),
        "evidence_used": assessment_result.get("evidence_mapping") is not None,
        "evidence_source": assessment_result.get("evidence_source", ""),
        "compliance_score": assessment_result.get("compliance_score", 0),
        "compliant_controls": assessment_result.get("compliant_controls", 0),
        "partial_controls": assessment_result.get("partial_controls", 0),
        "missing_controls": assessment_result.get("missing_controls", 0),
        "total_controls": assessment_result.get("total_controls", 0),
        "severity_summary": assessment_result.get("severity_summary", {}),
        "top_missing_high_risk": assessment_result.get("top_missing_high_risk", []),
        "insights_count": len(assessment_result.get("insights", [])),
        "most_compliant_section": assessment_result.get("most_compliant_section"),
        "least_compliant_section": assessment_result.get("least_compliant_section"),
        "created_at": assessment_result.get("created_at", datetime.now(timezone.utc).isoformat()),
    }

    records = _load()
    records.append(record)
    _save(records)

    return record


def get_assessment_history() -> list[dict]:
    """Return all assessment execution history records, newest first."""
    records = _load()
    records.reverse()
    return records


def get_latest_assessment_run() -> dict | None:
    """Return the most recent assessment execution record, or None."""
    records = _load()
    return records[-1] if records else None


# ---------------------------------------------------------------------------
# Export readiness hook
# ---------------------------------------------------------------------------

def prepare_export_payload(assessment_result: dict) -> dict:
    """
    Prepare a clean, structured payload suitable for PDF/DOCX export.

    This is a placeholder hook — the actual renderer (e.g. ReportLab,
    python-docx) should consume this dict to generate the final file.

    Returns
    -------
    dict
        Export-ready payload with sections stripped of raw evidence_row
        data for clean rendering.
    """
    clean_sections = []
    for section in assessment_result.get("sections", []):
        clean_controls = []
        for ctrl in section.get("controls", []):
            clean_controls.append({
                "rule_id": ctrl.get("rule_id", ""),
                "control": ctrl.get("control", ""),
                "name": ctrl.get("name", ""),
                "description": ctrl.get("description", ""),
                "severity": ctrl.get("severity", ""),
                "required_evidence": ctrl.get("required_evidence", ""),
                "status": ctrl.get("status", "missing"),
                "has_evidence": ctrl.get("has_evidence", False),
                "mapped_evidence_count": ctrl.get("mapped_evidence_count", 0),
            })
        clean_sections.append({
            "section_key": section.get("section_key", ""),
            "section_name": section.get("section_name", ""),
            "controls_count": section.get("controls_count", 0),
            "compliant_controls": section.get("compliant_controls", 0),
            "partial_controls": section.get("partial_controls", 0),
            "missing_controls": section.get("missing_controls", 0),
            "compliance_score": section.get("compliance_score", 0),
            "controls": clean_controls,
        })

    return {
        "title": f"{assessment_result.get('framework', '')} Assessment Report",
        "assessment_name": assessment_result.get("assessment_name", ""),
        "framework": assessment_result.get("framework", ""),
        "scope": assessment_result.get("scope", ""),
        "priority": assessment_result.get("priority", ""),
        "generated_at": assessment_result.get("created_at", ""),
        "compliance_score": assessment_result.get("compliance_score", 0),
        "compliant_controls": assessment_result.get("compliant_controls", 0),
        "partial_controls": assessment_result.get("partial_controls", 0),
        "missing_controls": assessment_result.get("missing_controls", 0),
        "total_controls": assessment_result.get("total_controls", 0),
        "severity_summary": assessment_result.get("severity_summary", {}),
        "sections": clean_sections,
        "insights": assessment_result.get("insights", []),
        "top_missing_high_risk": assessment_result.get("top_missing_high_risk", []),
        "most_compliant_section": assessment_result.get("most_compliant_section"),
        "least_compliant_section": assessment_result.get("least_compliant_section"),
        "evidence_mapping": assessment_result.get("evidence_mapping"),
    }
