"""
Governance Calendar Generator Service

Generates a 6-month governance activity calendar scoped to the selected
compliance framework and enriched by detected risks.

No random or fake data — all activities are drawn from framework-specific
governance templates and refined based on actual Risk Register findings.
"""

from __future__ import annotations


# ---------------------------------------------------------------------------
# Framework normalisation  (consistent with training_matrix_generator)
# ---------------------------------------------------------------------------

def _normalise_framework(raw: str) -> str:
    if not raw:
        return "iso27001"
    f = raw.lower().replace(" ", "").replace("-", "").replace("_", "")
    if "hipaa" in f:
        return "hipaa"
    if "pci" in f:
        return "pci_dss"
    return "iso27001"


# ---------------------------------------------------------------------------
# Framework-specific baseline governance activities (6 months)
# ---------------------------------------------------------------------------

_BASELINE_ACTIVITIES: dict[str, list[str]] = {
    "iso27001": [
        "ISMS Kickoff & Scope Review",
        "Internal Audit – Annex A Controls Assessment",
        "Policy Review & Awareness Campaign",
        "Risk Register Review & Risk Treatment Update",
        "Management Review Meeting",
        "Corrective Action Follow-Up & Continual Improvement",
    ],
    "hipaa": [
        "HIPAA Security Rule Governance Review",
        "ePHI Access Review & Workforce Authorization Audit",
        "Audit Log Review & Monitoring Assessment",
        "Breach Response Tabletop Exercise",
        "Business Associate Agreement Review",
        "Management Compliance Review & Gap Remediation",
    ],
    "pci_dss": [
        "PCI DSS Scope Confirmation & Asset Inventory Review",
        "Firewall & Network Segmentation Review",
        "Vulnerability Scan Review & Remediation Tracking",
        "Access Review for Cardholder Data Systems",
        "Secure Coding & Payment Application Review",
        "Quarterly PCI Compliance Review & QSA Preparation",
    ],
}


# ---------------------------------------------------------------------------
# Risk-based enrichment mapping
# ---------------------------------------------------------------------------
# Maps detected risk keywords → governance focus areas that should be
# appended to the most relevant month's activity.

_RISK_ENRICHMENTS: dict[str, tuple[str, int]] = {
    # keyword in risk text → (enrichment suffix, target month index 0-5)
    "sql injection":        ("with focus on Application & API Security Review",      1),
    "injection":            ("with focus on Application Security Assessment",        1),
    "api abuse":            ("including API Security Posture Review",                4),
    "api":                  ("including API Security Posture Review",                4),
    "broken access":        ("with expanded Access Control Review",                  3),
    "access control":       ("with expanded Access Control Review",                  3),
    "privilege escalation": ("including Privileged Access Review",                   3),
    "vendor":               ("including Vendor / Third-Party Risk Review",           4),
    "supply chain":         ("including Supply Chain Risk Assessment",               4),
    "third party":          ("including Third-Party Due-Diligence Review",           4),
    "ransomware":           ("with Incident Response & Backup Verification",         1),
    "malware":              ("with Endpoint Protection Review",                      1),
    "misconfiguration":     ("with Configuration & Hardening Review",                1),
    "firewall":             ("with Firewall Rule Review & Network Hardening",        1),
    "policy gap":           ("including Policy Governance & Documentation Review",   2),
    "policy":               ("including Policy Compliance Review",                   2),
    "business continuity":  ("including BCP/DR Tabletop Exercise",                   5),
    "disaster recovery":    ("including DR Exercise & Recovery Testing",             5),
    "data loss":            ("with Data Loss Prevention Review",                     3),
    "data leak":            ("with Data Leakage Prevention Assessment",              3),
    "phishing":             ("with Social Engineering Awareness Assessment",         2),
    "unpatched":            ("with Patch Management Review",                         1),
}


# ---------------------------------------------------------------------------
# Helper: collect searchable risk text
# ---------------------------------------------------------------------------

def _collect_risk_text(risks: list[dict]) -> str:
    """Flatten risk entries into a single lowercase search string."""
    parts: list[str] = []
    for r in risks:
        for key in ("threat", "risk_statement", "description", "title",
                     "vulnerability", "name", "risk_name"):
            val = r.get(key)
            if val:
                parts.append(str(val))
    return " ".join(parts).lower()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_governance_calendar(
    risks: list[dict],
    framework_id: str,
    evidence_context: dict | None = None,
) -> list[dict]:
    """
    Generate a 6-month governance activity calendar.

    Parameters
    ----------
    risks : list[dict]
        Combined risk entries from the risk register (generated + uploaded).
    framework_id : str
        The selected compliance framework identifier.
    evidence_context : dict | None
        Optional evidence metadata (unused for now, reserved for future enrichment).

    Returns
    -------
    list[dict]  — each element has:
        month               : str   ("Month 1" … "Month 6")
        governance_activity : str   — framework-specific activity, optionally risk-enriched
    """
    fw_key = _normalise_framework(framework_id)
    baseline = list(_BASELINE_ACTIVITIES.get(fw_key, _BASELINE_ACTIVITIES["iso27001"]))
    risk_text = _collect_risk_text(risks)

    # ── Risk-based enrichment ─────────────────────────────────────────────
    # Track which months have already been enriched to avoid stacking
    enriched_months: set[int] = set()

    if risk_text:
        for keyword, (suffix, month_idx) in _RISK_ENRICHMENTS.items():
            if keyword in risk_text and month_idx not in enriched_months:
                baseline[month_idx] = f"{baseline[month_idx]} — {suffix}"
                enriched_months.add(month_idx)

    # ── Build output ──────────────────────────────────────────────────────
    return [
        {
            "month": f"Month {i + 1}",
            "governance_activity": activity,
        }
        for i, activity in enumerate(baseline)
    ]
