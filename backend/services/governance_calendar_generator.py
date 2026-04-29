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

def _generate_pci_dynamic_calendar(
    risks: list[dict],
    soa_sections: list[dict] | None = None,
    compliance_matrix: list[dict] | None = None,
    vendor_checklist: list[dict] | None = None,
    training_matrix: dict | None = None,
) -> list[dict]:
    # Detect gaps across all sources
    has_network = False
    has_vuln = False
    has_training = False
    has_vendor = False
    has_monitor = False
    has_incident = False
    has_access = False

    risk_text = _collect_risk_text(risks)
    
    if any(x in risk_text for x in ("firewall", "segmentation", "default-allow", "network", "001", "002", "003")):
        has_network = True
    if any(x in risk_text for x in ("vulnerability", "patch", "malware", "unpatched", "005", "006")):
        has_vuln = True
    if any(x in risk_text for x in ("training", "phishing", "awareness", "010")):
        has_training = True
    if any(x in risk_text for x in ("vendor", "third-party", "011")):
        has_vendor = True
    if any(x in risk_text for x in ("log", "monitor", "siem", "alert", "009", "10.")):
        has_monitor = True
    if any(x in risk_text for x in ("incident", "breach", "tabletop", "012", "12.")):
        has_incident = True
    if any(x in risk_text for x in ("access", "mfa", "privilege", "007", "008", "7.", "8.")):
        has_access = True

    if soa_sections:
        for sec in soa_sections:
            if sec.get("status", "").lower() != "compliant":
                title = sec.get("title", "").lower()
                if "network" in title or "firewall" in title: has_network = True
                if "vulnerabilit" in title or "endpoint" in title: has_vuln = True
                if "access" in title: has_access = True
                if "monitor" in title or "log" in title or "009" in title: has_monitor = True
                if "govern" in title or "aware" in title or "010" in title: has_training = True
                if "supplier" in title or "vendor" in title or "011" in title: has_vendor = True
                if "incident" in title or "breach" in title or "012" in title: has_incident = True

    if compliance_matrix:
        for r in compliance_matrix:
            if r.get("Status", "").lower() != "compliant":
                req = r.get("Requirement", "").lower()
                if "network" in req: has_network = True
                if "endpoint" in req: has_vuln = True
                if "access control" in req: has_access = True
                if "monitoring" in req or "009" in req: has_monitor = True
                if "governance" in req or "010" in req: has_training = True
                if "supplier" in req or "011" in req: has_vendor = True
                if "incident" in req or "012" in req: has_incident = True

    if vendor_checklist:
        if any(v.get("risk_level", "").lower() in ("high", "medium") for v in vendor_checklist):
            has_vendor = True

    if training_matrix and training_matrix.get("employee_tracker"):
        if any(e.get("status", "").lower() in ("pending", "overdue") for e in training_matrix["employee_tracker"]):
            has_training = True

    print("PCI CALENDAR FLAGS:", {
        "training": has_training,
        "monitoring": has_monitor,
        "incident": has_incident,
        "vendor": has_vendor,
        "network": has_network,
    })

    # Month 1
    m1 = "PCI DSS Scope Confirmation & Asset Inventory Review"
    
    # Month 2
    m2 = "Firewall & Network Segmentation Review" if has_network else "Secure Coding & Payment Application Review"
    if has_network:
        m2 += " — with Endpoint Protection Review"
        
    # Month 3
    m3 = "Vulnerability Scan Review & Remediation Tracking" if has_vuln else "Physical Security & Media Control Audit"
    if has_training:
        m3 += " — with Phishing Simulation Campaign"
        
    # Month 4
    m4 = "Access Review for Cardholder Data Systems"
    if has_monitor:
        m4 += " — with Log Monitoring & SIEM Review"
        
    # Month 5
    m5 = "Vendor Risk Review" if has_vendor else "Data Retention & Disposal Review"
    if has_vendor:
        m5 += " — including PCI compliance evidence review for service providers"
        
    # Month 6
    m6 = "Quarterly PCI Compliance Review & QSA Preparation"
    if has_incident:
        m6 += " — with Incident Response Tabletop Exercise"
        
    months = [m1, m2, m3, m4, m5, m6]

    return [
        {
            "month": f"Month {i + 1}",
            "governance_activity": activity,
        }
        for i, activity in enumerate(months)
    ]

def generate_governance_calendar(
    risks: list[dict],
    framework_id: str,
    evidence_context: dict | None = None,
    soa_sections: list[dict] | None = None,
    compliance_matrix: list[dict] | None = None,
    vendor_checklist: list[dict] | None = None,
    training_matrix: dict | None = None,
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
        Optional evidence metadata.
    """
    fw_key = _normalise_framework(framework_id)
    
    if fw_key == "pci_dss":
        return _generate_pci_dynamic_calendar(
            risks=risks,
            soa_sections=soa_sections,
            compliance_matrix=compliance_matrix,
            vendor_checklist=vendor_checklist,
            training_matrix=training_matrix
        )

    baseline = list(_BASELINE_ACTIVITIES.get(fw_key, _BASELINE_ACTIVITIES["iso27001"]))
    risk_text = _collect_risk_text(risks)

    # ── Risk-based enrichment ─────────────────────────────────────────────
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
