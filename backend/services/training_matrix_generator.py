"""
Training Matrix Generator Service

Generates two structured outputs:
  1. role_based_matrix   — role→training mappings, enriched by risk context
  2. employee_tracker    — per-employee training assignments from uploaded HR data

All mappings are scoped to the selected compliance framework.
No fake employees are generated — employee_tracker only contains uploaded records.
"""

from datetime import datetime, timedelta


# ---------------------------------------------------------------------------
# Role classification
# ---------------------------------------------------------------------------

_ROLE_PATTERNS = {
    "it_ops":      ["it", "admin", "ops", "system", "infrastructure", "sysadmin",
                    "network", "cloud", "devops", "soc", "security"],
    "engineering": ["dev", "eng", "software", "architect", "qa", "test",
                    "programmer", "frontend", "backend", "full stack", "fullstack"],
    "hr_finance":  ["hr", "human", "fin", "account", "legal", "payroll",
                    "recruit", "compliance officer", "counsel"],
    "executive":   ["exec", "dir", "vp", "chief", "ceo", "cto", "ciso",
                    "cfo", "coo", "president", "board", "c-suite", "head of"],
}


def _classify_role(role_text: str) -> str:
    """Map a free-text role string to a canonical role group key."""
    lower = role_text.lower()
    for group_key, keywords in _ROLE_PATTERNS.items():
        for kw in keywords:
            if kw in lower:
                return group_key
    return "general"


# ---------------------------------------------------------------------------
# Framework-specific training content
# ---------------------------------------------------------------------------

_TRAINING_CONTENT = {
    "iso27001": {
        "general":     "Security Awareness (ISO 27001 A.6.3), Phishing Prevention, Data Classification",
        "it_ops":      "Privileged Access Management (A.8.2–A.8.5), Incident Response (A.5.24–A.5.28), Cloud Security",
        "engineering": "Secure Coding Practices, OWASP Top 10, API Security (A.8.23, A.8.28), Code Review",
        "hr_finance":  "Data Privacy (GDPR alignment), BEC Prevention, Fraud Detection, Personnel Security (A.6.1–A.6.6)",
        "executive":   "Cyber Crisis Management, ISMS Governance (A.5.1–A.5.4), Board-Level Risk Briefing",
    },
    "hipaa": {
        "general":     "HIPAA Privacy & Security Awareness, PHI Handling, Breach Notification Procedures",
        "it_ops":      "ePHI Access Controls (§164.312), Audit Logging, Incident Response for PHI Breaches",
        "engineering": "Secure Development for Health Systems, ePHI Encryption, Application Security Testing",
        "hr_finance":  "HIPAA Administrative Safeguards, BAA Management, Workforce Sanctions Policy",
        "executive":   "HIPAA Compliance Oversight, Risk Analysis Leadership, OCR Audit Preparedness",
    },
    "pci_dss": {
        "general":     "PCI DSS Awareness, Cardholder Data Handling, Social Engineering Prevention",
        "it_ops":      "Network Segmentation (Req 1), Vulnerability Management (Req 5–6), Log Monitoring (Req 10)",
        "engineering": "Secure Coding (Req 6.5), Code Review, Web Application Security, Input Validation",
        "hr_finance":  "PCI DSS Policy Compliance, Fraud Detection, Secure Payment Processing Procedures",
        "executive":   "PCI DSS Governance, Compliance Reporting, QSA Audit Preparedness",
    },
}

_TRAINING_FREQUENCY = {
    "general":     "Annually",
    "it_ops":      "Bi-Annually",
    "engineering": "Annually",
    "hr_finance":  "Annually",
    "executive":   "Annually",
}

_DEFAULT_DRIVERS = {
    "general":     "Social Engineering, Data Handling Errors",
    "it_ops":      "Privilege Escalation, System Misconfigurations",
    "engineering": "Application Vulnerabilities, Injection Attacks",
    "hr_finance":  "Business Email Compromise, Data Leakage",
    "executive":   "Targeted Whaling Attacks, Reputational Risk",
}


# ---------------------------------------------------------------------------
# Risk-context enrichment
# ---------------------------------------------------------------------------

_RISK_DRIVER_KEYWORDS = {
    "ransomware":        "Ransomware Threats",
    "malware":           "Malware Proliferation",
    "phish":             "Social Engineering / Phishing",
    "social eng":        "Social Engineering",
    "sql":               "SQL Injection",
    "xss":               "Cross-Site Scripting",
    "api":               "API Abuse",
    "injection":         "Injection Attacks",
    "data exfiltration": "Data Exfiltration",
    "data leak":         "Data Leakage",
    "data loss":         "Data Loss",
    "misconfiguration":  "Infrastructure Misconfigurations",
    "unpatched":         "Unpatched Vulnerabilities",
    "cve":               "Known CVE Exploits",
    "access":            "Unauthorised Access",
    "credential":        "Credential Compromise",
    "vendor":            "Supply Chain / Vendor Risk",
    "supply chain":      "Supply Chain Compromise",
    "business continuity": "Business Continuity Gaps",
}

# Which risk keywords are relevant to which role groups
_RISK_RELEVANCE = {
    "it_ops":      ["ransomware", "malware", "misconfiguration", "unpatched",
                    "cve", "access", "credential", "business continuity"],
    "engineering": ["sql", "xss", "api", "injection"],
    "hr_finance":  ["phish", "social eng", "data leak", "data loss",
                    "data exfiltration"],
    "executive":   ["ransomware", "data exfiltration", "business continuity",
                    "vendor", "supply chain"],
    "general":     ["phish", "social eng", "data leak", "data loss"],
}


def _collect_risk_text(risks: list[dict]) -> str:
    """Flatten all risk descriptions into a single lowercase search string."""
    parts = []
    for r in risks:
        for key in ("threat", "risk_statement", "description", "title",
                    "vulnerability", "name", "risk_name"):
            val = r.get(key)
            if val:
                parts.append(str(val))
    return " ".join(parts).lower()


def _enrich_driver(group_key: str, risk_text: str, base_driver: str) -> str:
    """Append risk-context drivers relevant to this role group."""
    relevant_kws = _RISK_RELEVANCE.get(group_key, _RISK_RELEVANCE["general"])
    extras = []
    for kw in relevant_kws:
        if kw in risk_text:
            label = _RISK_DRIVER_KEYWORDS.get(kw)
            if label and label not in base_driver:
                extras.append(label)
    if not extras:
        return base_driver
    # Limit to 2 enrichments to keep the cell readable
    return base_driver + ", " + ", ".join(extras[:2])


# ---------------------------------------------------------------------------
# Framework normalisation  (mirrors treatment_plan_generator)
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
# Public API
# ---------------------------------------------------------------------------

def generate_training_matrix(
    employees: list[dict],
    risks: list[dict],
    framework_id: str,
) -> dict:
    """
    Generate a structured training matrix.

    Parameters
    ----------
    employees : list[dict]
        Uploaded employee records (from the training_matrix / employees sheet).
        Each dict should have at minimum: employee, role.
    risks : list[dict]
        Combined risk entries from the risk register (generated + uploaded).
    framework_id : str
        The selected compliance framework identifier.

    Returns
    -------
    dict  with keys:
        role_based_matrix   : list[dict] — one row per unique role group
        employee_tracker    : list[dict] — one row per uploaded employee (never fabricated)
    """
    fw_key = _normalise_framework(framework_id)
    content_map = _TRAINING_CONTENT.get(fw_key, _TRAINING_CONTENT["iso27001"])
    risk_text = _collect_risk_text(risks)

    # ── 1. Role-Based Matrix ──────────────────────────────────────────────
    role_based_matrix: list[dict] = []

    if employees:
        # Derive groups from actual uploaded employee roles
        group_roles: dict[str, set[str]] = {}
        for emp in employees:
            raw_role = emp.get("role", "")
            if not raw_role:
                continue
            group_key = _classify_role(raw_role)
            group_roles.setdefault(group_key, set()).add(raw_role)

        for group_key, raw_roles in sorted(group_roles.items()):
            display_label = ", ".join(sorted(raw_roles))
            base_driver = _DEFAULT_DRIVERS.get(group_key, _DEFAULT_DRIVERS["general"])
            driver = _enrich_driver(group_key, risk_text, base_driver)

            role_based_matrix.append({
                "role":      display_label,
                "content":   content_map.get(group_key, content_map["general"]),
                "frequency": _TRAINING_FREQUENCY.get(group_key, "Annually"),
                "driver":    driver,
            })
    else:
        # No employees uploaded → provide default enterprise mapping
        _DEFAULT_LABELS = {
            "general":     "All Employees",
            "it_ops":      "IT & Operations",
            "engineering": "Developers / Engineering",
            "hr_finance":  "HR & Finance",
            "executive":   "Executive Management",
        }
        for group_key in ("general", "it_ops", "engineering", "hr_finance", "executive"):
            base_driver = _DEFAULT_DRIVERS[group_key]
            driver = _enrich_driver(group_key, risk_text, base_driver)
            role_based_matrix.append({
                "role":      _DEFAULT_LABELS[group_key],
                "content":   content_map.get(group_key, content_map["general"]),
                "frequency": _TRAINING_FREQUENCY[group_key],
                "driver":    driver,
            })

    # ── 2. Employee Training Tracker ──────────────────────────────────────
    #   ONLY real uploaded employees — never fabricated rows.
    employee_tracker: list[dict] = []
    for emp in employees:
        # Resolve employee name from various field name conventions
        emp_name = (
            emp.get("name")
            or emp.get("employee_name")
            or emp.get("employee")
            or emp.get("full_name")
            or emp.get("staff_name")
            or "Unknown"
        )

        # Resolve role
        raw_role = (
            emp.get("role")
            or emp.get("job_title")
            or emp.get("position")
            or emp.get("designation")
            or "Employee"
        )

        group_key = _classify_role(raw_role)

        # Assigned training: use explicit modules if present, else derive from role
        assigned = (
            emp.get("required_modules")
            or content_map.get(group_key, content_map["general"])
        )

        # Training status: canonical key is "training" from normalizer
        status = (
            emp.get("training")
            or emp.get("training_status")
            or emp.get("security_training_status")
            or emp.get("training_completed")
            or emp.get("awareness")
            or "Pending"
        )

        # Dates
        last_date = (
            emp.get("last_training_date")
            or emp.get("last_training")
            or emp.get("last_performed")
            or "Not Available"
        )
        next_date = (
            emp.get("next_due_date")
            or emp.get("next_due")
            or "Not Available"
        )

        employee_tracker.append({
            "employee":           str(emp_name).strip(),
            "role":               str(raw_role).strip(),
            "assigned_training":  assigned,
            "status":             str(status).strip(),
            "last_training_date": str(last_date).strip(),
            "next_due_date":      str(next_date).strip(),
        })

    return {
        "role_based_matrix":  role_based_matrix,
        "employee_tracker":   employee_tracker,
        "framework":          fw_key,
        "total_roles":        len(role_based_matrix),
        "total_employees":    len(employee_tracker),
    }
