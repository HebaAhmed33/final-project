"""
Configuration Compliance Engine.

Maps raw configuration analysis findings against a compliance framework
(CIS, NIST, ISO 27001) to produce a framework-aware compliance report.

ISOLATION RULES:
  - Does NOT import from services/framework_aware_builder.py
  - Does NOT import from assessment/ modules
  - Does NOT reuse assessment scoring
  - Reads standards/*.json as READ-ONLY (never writes)
  - Uses config_compliance_scorer for its own scoring system
"""

from __future__ import annotations

import json
import os
from typing import Any

from config_analysis.config_compliance_scorer import score_config_compliance
from config_analysis.config_risk_register import build_config_risk_register, generate_best_practices


# ---------------------------------------------------------------------------
# Standard file resolution
# ---------------------------------------------------------------------------

_STANDARDS_DIR = os.path.join(os.path.dirname(__file__), "..", "standards")

_FRAMEWORK_FILE_MAP: dict[str, str] = {
    "cis":      "cis.json",
    "nist":     "nist.json",
    "iso27001": "config_baseline.json",   # ISO uses the config baseline for config analysis
}

# Human-readable labels
_FRAMEWORK_LABELS: dict[str, str] = {
    "cis":      "CIS Controls",
    "nist":     "NIST SP 800-53",
    "iso27001": "ISO 27001 (Config Baseline)",
}


def _resolve_framework_id(raw_framework: str) -> str:
    """Normalize user input to a canonical framework key."""
    key = raw_framework.strip().lower().replace(" ", "_").replace("-", "_")
    # Common aliases
    aliases = {
        "iso":   "iso27001",
        "iso_27001": "iso27001",
        "pci":   "pci_dss",
        "nist_800_53": "nist",
        "nist_sp_800_53": "nist",
    }
    return aliases.get(key, key)


def _load_framework_controls(framework_id: str) -> list[dict[str, Any]]:
    """Load framework controls from the standards directory (READ-ONLY)."""
    filename = _FRAMEWORK_FILE_MAP.get(framework_id)
    if not filename:
        raise ValueError(
            f"Unsupported framework '{framework_id}' for configuration analysis. "
            f"Supported: {', '.join(_FRAMEWORK_FILE_MAP.keys())}"
        )
    filepath = os.path.join(_STANDARDS_DIR, filename)
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"Framework file not found: {filepath}")

    with open(filepath, "r", encoding="utf-8") as fh:
        return json.load(fh)


# ---------------------------------------------------------------------------
# Finding-to-framework mapping
# ---------------------------------------------------------------------------

# Category → framework control mapping (per framework)
# These are used to enrich raw_config_analyzer findings with the correct
# control reference from the selected framework.

_CIS_CATEGORY_MAP: dict[str, str] = {
    "Integrity":            "CIS Control 4 — Secure Configuration of Enterprise Assets",
    "Access Control":       "CIS Control 6 — Access Control Management",
    "Network Security":     "CIS Control 13 — Network Monitoring and Defense",
    "Encryption":           "CIS Control 3 — Data Protection",
    "Secrets Management":   "CIS Control 6 — Access Control Management",
    "Information Disclosure": "CIS Control 3 — Data Protection",
    "Error Handling":       "CIS Control 4 — Secure Configuration of Enterprise Assets",
    "Input Validation":     "CIS Control 16 — Application Software Security",
}

_NIST_CATEGORY_MAP: dict[str, str] = {
    "Access Control":       "NIST AC — Access Control",
    "Integrity":            "NIST SI — System and Information Integrity",
    "Network Security":     "NIST SC — System and Communications Protection",
    "Encryption":           "NIST SC-28 — Protection of Information at Rest",
    "Secrets Management":   "NIST IA — Identification and Authentication",
    "Information Disclosure": "NIST RA — Risk Assessment",
    "Error Handling":       "NIST SA — System and Services Acquisition",
    "Input Validation":     "NIST SI-10 — Information Input Validation",
}

_ISO_CATEGORY_MAP: dict[str, str] = {
    "Integrity":            "A.12.2 — Protection from malware",
    "Access Control":       "A.9.4 — System and application access control",
    "Network Security":     "A.13.1 — Network controls",
    "Encryption":           "A.10.1 — Policy on use of cryptographic controls",
    "Secrets Management":   "A.9.2 — User access management",
    "Information Disclosure": "A.18.1 — Compliance with legal and contractual requirements",
    "Error Handling":       "A.14.2 — Security in development and support processes",
    "Input Validation":     "A.14.2 — Security in development and support processes",
}

_CATEGORY_MAPS: dict[str, dict[str, str]] = {
    "cis":      _CIS_CATEGORY_MAP,
    "nist":     _NIST_CATEGORY_MAP,
    "iso27001": _ISO_CATEGORY_MAP,
}


def _enrich_findings_with_framework(
    findings: list[dict[str, Any]],
    framework_id: str,
) -> list[dict[str, Any]]:
    """Add framework-specific control references to each finding."""
    category_map = _CATEGORY_MAPS.get(framework_id, {})
    enriched: list[dict[str, Any]] = []
    for f in findings:
        item = dict(f)
        category = f.get("category", "")
        item["framework_control"] = category_map.get(category, "No direct mapping")
        item["framework_id"] = framework_id
        enriched.append(item)
    return enriched


# ---------------------------------------------------------------------------
# Compliance check against framework controls
# ---------------------------------------------------------------------------

def _check_config_against_framework(
    config_data: dict[str, Any],
    controls: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Evaluate structured config key-value pairs against framework controls.

    Each control has a `check_key` and `expected` value. We compare the config
    data and report pass/fail per control.

    Returns a list of control evaluation results.
    """
    results: list[dict[str, Any]] = []
    for ctrl in controls:
        check_key = ctrl.get("check_key", "")
        expected = ctrl.get("expected")
        actual = config_data.get(check_key)

        if actual is None:
            status = "not_evaluated"
            actual_display = "N/A (key not present)"
        elif bool(actual) == bool(expected):
            status = "pass"
            actual_display = actual
        else:
            status = "fail"
            actual_display = actual

        results.append({
            "control_id": ctrl.get("id", ""),
            "control_name": ctrl.get("name", ""),
            "domain": ctrl.get("domain", ""),
            "severity": ctrl.get("severity", "medium"),
            "description": ctrl.get("description", ""),
            "expected": expected,
            "actual": actual_display,
            "status": status,
        })
    return results


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def run_config_compliance_analysis(
    raw_analysis: dict[str, Any],
    framework: str = "cis",
    parsed_config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Run a framework-aware compliance analysis on a configuration upload.

    Parameters
    ----------
    raw_analysis : dict
        The output from raw_config_analyzer.analyze_raw_config().
        Contains: config_type, components, summary, findings, recommendations.
    framework : str
        Framework to map against: 'cis', 'nist', or 'iso27001'.
    parsed_config : dict, optional
        Structured config key-value pairs (for JSON/YAML/ENV uploads).
        When provided, controls are also evaluated against these values.

    Returns
    -------
    dict
        Full compliance report with enriched findings, control evaluations,
        and compliance scoring.
    """
    framework_id = _resolve_framework_id(framework)
    framework_label = _FRAMEWORK_LABELS.get(framework_id, framework_id.upper())

    # Load framework controls (READ-ONLY)
    try:
        controls = _load_framework_controls(framework_id)
    except (ValueError, FileNotFoundError) as exc:
        return {
            "error": str(exc),
            "framework": framework_id,
            "framework_label": framework_label,
        }

    # 1. Enrich raw config findings with framework control references
    raw_findings = raw_analysis.get("findings", [])
    enriched_findings = _enrich_findings_with_framework(raw_findings, framework_id)

    # 2. If structured config data is available, run control checks
    control_evaluations: list[dict[str, Any]] = []
    if parsed_config and isinstance(parsed_config, dict):
        # Exclude raw_text wrapper keys
        config_kv = {
            k: v for k, v in parsed_config.items()
            if k not in ("raw_text", "source_type")
        }
        if config_kv:
            control_evaluations = _check_config_against_framework(config_kv, controls)

    # 3. Count mapped controls for coverage calculation
    mapped_categories = {
        f.get("category") for f in raw_findings if f.get("category")
    }
    category_map = _CATEGORY_MAPS.get(framework_id, {})
    mapped_controls = sum(1 for cat in mapped_categories if cat in category_map)

    # 4. Compute compliance score (separate from assessment scoring)
    all_scorable = list(enriched_findings)
    # Also add failed control evaluations as deductions
    for ev in control_evaluations:
        if ev["status"] == "fail":
            all_scorable.append({
                "severity": ev.get("severity", "medium").capitalize(),
                "category": ev.get("domain", ""),
            })

    score_result = score_config_compliance(
        findings=all_scorable,
        total_controls=len(controls),
        mapped_controls=mapped_controls,
        framework=framework_id,
    )

    # 5. Build recommendations
    recommendations = raw_analysis.get("recommendations", [])
    # Add recommendations for failed control evaluations
    for ev in control_evaluations:
        if ev["status"] == "fail":
            recommendations.append(
                f"[{ev['control_id']}] {ev['control_name']}: "
                f"Expected {ev['expected']}, found {ev['actual']}. "
                f"Review and remediate."
            )

    # 6. Build risk register from enriched findings
    risk_register = build_config_risk_register(
        findings=enriched_findings,
        framework_label=framework_label,
    )

    # 7. Generate best practices based on findings
    best_practices = generate_best_practices(enriched_findings)

    # 8. Assemble final report
    return {
        "framework": framework_id,
        "framework_label": framework_label,
        "config_type": raw_analysis.get("config_type", "unknown"),
        "components": raw_analysis.get("components", []),
        "summary": raw_analysis.get("summary", {}),
        "compliance": score_result,
        "findings": enriched_findings,
        "control_evaluations": control_evaluations,
        "risk_register": risk_register,
        "best_practices": best_practices,
        "recommendations": recommendations,
    }
