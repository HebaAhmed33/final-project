"""
Treatment Plan Generator — Level 3 (Standard-Driven Remediation).

Generates treatment actions from control gap analysis using remediation
text from the rule-based JSON configuration. Every remediation is tied
to the actual compliance standard, not generic AI text.

Due Date logic:
  critical → +7 days
  high     → +14 days
  medium   → +30 days
"""

from __future__ import annotations

from datetime import datetime, timezone, timedelta

# ---------------------------------------------------------------------------
# Standard-specific fallback remediation templates
# (used ONLY when a control has no remediation field in JSON config)
# ---------------------------------------------------------------------------

_STANDARD_FALLBACK: dict[str, dict[str, str]] = {
    "iso27001": {
        "prefix": "Per ISO 27001:2022 Annex A",
        "template": "Implement control {control_id} ({name}) in accordance with ISO 27001:2022 Annex A requirements. Document the implementation and assign an owner for ongoing monitoring.",
    },
    "hipaa": {
        "prefix": "Per HIPAA Security Rule",
        "template": "Implement safeguard {control_id} ({name}) as required by the HIPAA Security Rule (45 CFR Part 164). Document policies and procedures, and assign a responsible workforce member.",
    },
    "pci_dss": {
        "prefix": "Per PCI DSS v4.0",
        "template": "Implement {control_id} ({name}) as required by PCI DSS v4.0. Document evidence of compliance and validate during the next assessment cycle.",
    },
    "sama": {
        "prefix": "Per SAMA Cyber Security Framework",
        "template": "Implement {control_id} ({name}) as required by the SAMA Cyber Security Framework. Document implementation evidence and report to the Cybersecurity function.",
    },
}


def _compute_due_date(severity: str, base_date: datetime | None = None) -> str:
    """Compute due date based on severity level."""
    base = base_date or datetime.now(timezone.utc)
    sev = (severity or "medium").strip().lower()

    if sev == "critical":
        delta = timedelta(days=7)
    elif sev == "high":
        delta = timedelta(days=14)
    else:
        delta = timedelta(days=30)

    return (base + delta).strftime("%Y-%m-%d")


def _get_remediation_text(
    control: dict,
    framework_id: str,
) -> tuple[str, str]:
    """
    Get remediation text and its source.

    Priority:
      1. control["remediation"] from JSON config → source = "standard_config"
      2. Standard-specific fallback template    → source = "standard_template"
    """
    # Priority 1: Direct from JSON config
    remediation = (control.get("remediation") or "").strip()
    if remediation:
        return remediation, "standard_config"

    # Priority 2: Standard-specific template
    fw_key = framework_id.strip().lower().replace(" ", "").replace("-", "_")
    # Normalize "ISO 27001" → "iso27001"
    if "iso" in fw_key and "27001" in fw_key:
        fw_key = "iso27001"

    fallback = _STANDARD_FALLBACK.get(fw_key, _STANDARD_FALLBACK.get("iso27001"))
    control_id = control.get("control_id") or control.get("control") or control.get("rule_id", "")
    name = control.get("name", "Unknown Control")

    text = fallback["template"].format(control_id=control_id, name=name)
    return text, "standard_template"


def generate_treatment_plan(
    controls: list[dict],
    framework_id: str = "iso27001",
    base_date: datetime | None = None,
) -> dict:
    """
    Generate a Level 3 treatment plan from evaluated controls.

    Scope: Only includes controls that are:
      - status = "missing" or "partial"
      - severity = "critical" or "high"

    Each action includes:
      - risk_id (rule_id)
      - control_id
      - name
      - severity
      - status
      - treatment (remediation text from standard config)
      - due_date (computed from severity)
      - remediation_source ("standard_config" or "standard_template")

    Parameters
    ----------
    controls : list[dict]
        Evaluated controls with status, severity, remediation fields.
    framework_id : str
        Framework identifier for standard-specific fallbacks.
    base_date : datetime | None
        Base date for due date calculation. Defaults to now.

    Returns
    -------
    dict
        Treatment plan with total_actions and actions list.
    """
    actions = []

    for ctrl in controls:
        status = (ctrl.get("status") or "").strip().lower()
        severity = (ctrl.get("severity") or "medium").strip().lower()

        # Scope: only missing/partial + critical/high
        if status not in ("missing", "partial"):
            continue
        if severity not in ("critical", "high"):
            continue

        treatment_text, source = _get_remediation_text(ctrl, framework_id)
        due_date = _compute_due_date(severity, base_date)

        actions.append({
            "risk_id": ctrl.get("rule_id") or ctrl.get("control_id") or ctrl.get("risk_id", ""),
            "control_id": ctrl.get("control_id") or ctrl.get("control") or "",
            "name": ctrl.get("name") or ctrl.get("control_name", "Unknown"),
            "severity": severity,
            "status": status,
            "treatment": treatment_text,
            "due_date": due_date,
            "remediation_source": source,
            "owner": "Information Security",
        })

    # Sort: critical first, then high; within same severity, missing before partial
    severity_order = {"critical": 0, "high": 1}
    status_order = {"missing": 0, "partial": 1}
    actions.sort(key=lambda a: (
        severity_order.get(a["severity"], 9),
        status_order.get(a["status"], 9),
    ))

    return {
        "total_actions": len(actions),
        "framework": framework_id,
        "remediation_source": "standard_driven",
        "actions": actions,
    }
