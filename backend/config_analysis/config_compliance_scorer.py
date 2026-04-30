"""
Configuration Compliance Scorer.

A SEPARATE scoring system for configuration-upload analysis.
This module does NOT reuse or import any assessment scoring logic.

Scoring algorithm:
  - Security Score from 0–100
  - Deductions per finding: High=25, Medium=10, Low=5
  - Score capped at 0 (cannot go negative)
  - Risk Level aligned with score:
      80–100 → Low Risk
      60–79  → Medium Risk
      <60    → High Risk
  - A compliance grade (A–F) is derived from the numeric score
  - Framework coverage percentage is computed from control mappings
"""

from __future__ import annotations

from typing import Any


# ---------------------------------------------------------------------------
# Severity weights — independent of assessment engine
# ---------------------------------------------------------------------------

_SEVERITY_DEDUCTION_MAP = {
    "cis": {"High": 25, "Medium": 10, "Low": 5},
    "nist": {"High": 30, "Medium": 15, "Low": 5},
    "iso27001": {"High": 20, "Medium": 10, "Low": 5},
}

_MAX_SCORE = 100


# ---------------------------------------------------------------------------
# Grade mapping
# ---------------------------------------------------------------------------

def _score_to_grade(score: float) -> str:
    """Convert a numeric compliance score to a letter grade."""
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    return "F"


def _score_to_level(score: float) -> str:
    """Convert a numeric compliance score to a risk level label."""
    if score >= 80:
        return "Low Risk"
    if score >= 60:
        return "Medium Risk"
    return "High Risk"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def score_config_compliance(
    findings: list[dict[str, Any]],
    total_controls: int = 0,
    mapped_controls: int = 0,
    framework: str = "cis",
) -> dict[str, Any]:
    """
    Compute a compliance score for configuration analysis findings.

    Parameters
    ----------
    findings : list[dict]
        Enriched findings from the config compliance engine (each has
        'severity' and optionally 'framework_control').
    total_controls : int
        Total number of controls in the selected framework standard.
    mapped_controls : int
        Number of controls that were actually matched by findings.
    framework : str
        The selected compliance framework (e.g., 'cis', 'nist', 'iso27001').

    Returns
    -------
    dict
        {
            "compliance_score": float,
            "grade": str,
            "risk_level": str,
            "total_deductions": float,
            "severity_breakdown": { "High": int, "Medium": int, "Low": int },
            "framework_coverage": {
                "total_controls": int,
                "matched_controls": int,
                "coverage_pct": float,
            },
        }
    """
    severity_breakdown = {"High": 0, "Medium": 0, "Low": 0}
    total_deductions = 0.0

    # Get the appropriate deduction weights for the selected framework
    fw_key = framework.lower() if framework else "cis"
    deduction_weights = _SEVERITY_DEDUCTION_MAP.get(fw_key, _SEVERITY_DEDUCTION_MAP["cis"])

    for f in findings:
        sev = f.get("severity", "Low")
        severity_breakdown[sev] = severity_breakdown.get(sev, 0) + 1
        total_deductions += deduction_weights.get(sev, 5)

    # Cap deductions at MAX_SCORE (score cannot go negative)
    capped_deductions = min(total_deductions, _MAX_SCORE)
    score = _MAX_SCORE - capped_deductions

    # Framework coverage
    coverage_pct = 0.0
    if total_controls > 0:
        coverage_pct = round((mapped_controls / total_controls) * 100, 1)

    return {
        "compliance_score": round(score, 1),
        "grade": _score_to_grade(score),
        "risk_level": _score_to_level(score),
        "total_deductions": round(total_deductions, 1),
        "severity_breakdown": severity_breakdown,
        "framework_coverage": {
            "total_controls": total_controls,
            "matched_controls": mapped_controls,
            "coverage_pct": coverage_pct,
        },
    }
