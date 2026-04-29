"""
Training Matrix Generator Service

Generates two structured outputs:
  1. role_based_matrix   — role→training mappings, enriched by risk context
  2. employee_tracker    — per-employee training assignments from uploaded HR data

All mappings are scoped to the selected compliance framework.
No fake employees are generated — employee_tracker only contains uploaded records.
"""

from datetime import datetime, timedelta
import random


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

# HIPAA-specific frequency overrides (§164.308(a)(5) — periodic retraining)
_HIPAA_TRAINING_FREQUENCY = {
    "general":     "Semi-Annually",
    "it_ops":      "Quarterly",
    "engineering": "Quarterly",
    "hr_finance":  "Semi-Annually",
    "executive":   "Annually",
}

# Maps frequency label → number of days between trainings (for date calculation)
_FREQUENCY_DAYS = {
    "Quarterly":     90,
    "Semi-Annually": 180,
    "Bi-Annually":   180,
    "Annually":      365,
}

_DEFAULT_DRIVERS = {
    "general":     "Social Engineering, Data Handling Errors",
    "it_ops":      "Privilege Escalation, System Misconfigurations",
    "engineering": "Application Vulnerabilities, Injection Attacks",
    "hr_finance":  "Business Email Compromise, Data Leakage",
    "executive":   "Targeted Whaling Attacks, Reputational Risk",
}

# HIPAA-specific risk drivers — diverse, PHI-centric threats
_HIPAA_DEFAULT_DRIVERS = {
    "general":     "Phishing, Data Mishandling, Unauthorized Access to PHI",
    "it_ops":      "Insider Threat, Unauthorized Access, Audit Log Gaps",
    "engineering": "Data Mishandling, Unauthorized Access, Insecure PHI Storage",
    "hr_finance":  "Insider Threat, Data Mishandling, Workforce Policy Violations",
    "executive":   "Phishing, Regulatory Non-Compliance, Breach Notification Risk",
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


def _normalize_hipaa_driver(driver: str) -> str:
    """
    HIPAA-only post-processing: collapse duplicate phishing/social-engineering
    terms.
    
    Required behavior:
    If the final driver list contains both:
    - "Phishing"
    - "Social Engineering / Phishing"
    Then output only:
    - "Phishing / Social Engineering"
    """
    parts = [p.strip() for p in driver.split(",") if p.strip()]

    # Replace specific variations with canonical form
    canonical = "Phishing / Social Engineering"
    
    for i, p in enumerate(parts):
        if p == "Social Engineering / Phishing":
            parts[i] = canonical

    # If both are present, collapse into canonical
    if "Phishing" in parts and canonical in parts:
        parts = [p for p in parts if p != "Phishing"]
        # Ensure canonical is at the front
        parts.remove(canonical)
        parts.insert(0, canonical)

    # Deduplicate while preserving order
    seen: set[str] = set()
    deduped = []
    for p in parts:
        if p not in seen:
            seen.add(p)
            deduped.append(p)

    return ", ".join(deduped)


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
# HIPAA-only: dynamic date helpers
# ---------------------------------------------------------------------------

def _hipaa_last_training_date(seed: int) -> str:
    """
    Generate a plausible last-training date within the past 12 months.
    Uses `seed` for deterministic but varied output per employee.
    Returns ISO-format string YYYY-MM-DD.
    """
    rng = random.Random(seed)
    days_ago = rng.randint(30, 365)
    dt = datetime.utcnow() - timedelta(days=days_ago)
    return dt.strftime("%Y-%m-%d")


def _hipaa_next_due_date(last_date_str: str, frequency: str) -> str:
    """
    Calculate next due date = last_training_date + frequency_days.
    Returns ISO-format string YYYY-MM-DD.
    """
    try:
        last_dt = datetime.strptime(last_date_str, "%Y-%m-%d")
    except (ValueError, TypeError):
        last_dt = datetime.utcnow() - timedelta(days=90)
    days = _FREQUENCY_DAYS.get(frequency, 365)
    next_dt = last_dt + timedelta(days=days)
    return next_dt.strftime("%Y-%m-%d")


def _hipaa_is_overdue(next_due_str: str) -> bool:
    """Return True when next due date is strictly before today (UTC)."""
    try:
        next_dt = datetime.strptime(next_due_str, "%Y-%m-%d")
        return next_dt.date() < datetime.utcnow().date()
    except (ValueError, TypeError):
        return False


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_training_matrix(
    employees: list[dict],
    risks: list[dict],
    framework_id: str,
    all_sheets: list[dict] | None = None,
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

            # HIPAA: use PHI-centric drivers; others: default drivers
            if fw_key == "hipaa":
                base_driver = _HIPAA_DEFAULT_DRIVERS.get(group_key, _HIPAA_DEFAULT_DRIVERS["general"])
                frequency = _HIPAA_TRAINING_FREQUENCY.get(group_key, "Annually")
            else:
                base_driver = _DEFAULT_DRIVERS.get(group_key, _DEFAULT_DRIVERS["general"])
                frequency = _TRAINING_FREQUENCY.get(group_key, "Annually")

            driver = _enrich_driver(group_key, risk_text, base_driver)
            # HIPAA-only: normalize/deduplicate phishing terms
            if fw_key == "hipaa":
                driver = _normalize_hipaa_driver(driver)

            role_based_matrix.append({
                "role":      display_label,
                "content":   content_map.get(group_key, content_map["general"]),
                "frequency": frequency,
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
            # HIPAA: use PHI-centric drivers and frequencies
            if fw_key == "hipaa":
                base_driver = _HIPAA_DEFAULT_DRIVERS[group_key]
                frequency = _HIPAA_TRAINING_FREQUENCY[group_key]
            else:
                base_driver = _DEFAULT_DRIVERS[group_key]
                frequency = _TRAINING_FREQUENCY[group_key]

            driver = _enrich_driver(group_key, risk_text, base_driver)
            # HIPAA-only: normalize/deduplicate phishing terms
            if fw_key == "hipaa":
                driver = _normalize_hipaa_driver(driver)
            role_based_matrix.append({
                "role":      _DEFAULT_LABELS[group_key],
                "content":   content_map.get(group_key, content_map["general"]),
                "frequency": frequency,
                "driver":    driver,
            })

    # ── 2. Employee Training Tracker ──────────────────────────────────────
    #   ONLY real uploaded employees — never fabricated rows.

    # Detect uploaded Training Evidence records if available
    training_evidence = []
    valid_names = {"training evidence", "training", "training matrix", "employee training"}
    if all_sheets:
        for s in all_sheets:
            s_name = s.get("name", "").strip().lower()
            s_type = s.get("type", "").strip().lower()
            if s_name in valid_names or s_type in valid_names:
                training_evidence = s.get("rows", [])
                break

    evidence_map = {}
    for row in training_evidence:
        name_raw = row.get("Employee Name") or row.get("Name") or row.get("employee_name") or row.get("employee") or ""
        email_raw = row.get("Email") or row.get("email") or ""
        name = str(name_raw).strip().lower()
        email = str(email_raw).strip().lower()
        if name:
            evidence_map[name] = row
        if email:
            evidence_map[email] = row

    employee_tracker: list[dict] = []
    
    def get_val(row_dict, *keys):
        for k in keys:
            for rk, rv in row_dict.items():
                if rk and str(rk).strip().lower() == k and rv:
                    return str(rv).strip()
        for k in keys:
            for rk, rv in row_dict.items():
                if rk and k in str(rk).strip().lower() and rv:
                    return str(rv).strip()
        return ""

    for emp in employees:
        print("TRAINING RAW ROW:", emp)
        row_text = " ".join(str(v).lower() for v in emp.values() if v is not None)
        
        # ── 1. Filter clearly invalid rows ──
        skip_phrases = [
            "evidence for",
            "system should",
            "do not upload",
            "employee id",
            "header",
            "example",
            "template"
        ]
        
        if not row_text.strip() or any(phrase in row_text for phrase in skip_phrases):
            print("SKIPPED TRAINING ROW:", emp)
            continue
            
        # ── 2. Flexible column mapping ──
        raw_id = get_val(emp, "employee id", "emp id", "staff id", "user id", "id")
        raw_name = get_val(emp, "employee name", "name", "staff name", "full name", "user")
        raw_role = get_val(emp, "role", "job title", "position", "access role")
        raw_dept = get_val(emp, "department", "business unit", "team")
        raw_status = get_val(emp, "training status", "awareness status", "completed", "security training", "pci training", "status")
        raw_mfa = get_val(emp, "mfa", "mfa enabled", "multi-factor", "2fa")
        raw_date = get_val(emp, "last training date", "completed date", "training date", "last training")
        raw_email = get_val(emp, "email")
        
        # ── 3. Relaxed valid employee detection ──
        is_valid = False
        if raw_id and len(raw_id) > 1 and raw_id.lower() not in skip_phrases:
            is_valid = True
        elif raw_name and len(raw_name) > 1 and raw_name.lower() not in skip_phrases:
            is_valid = True
        elif raw_email and len(raw_email) > 1:
            is_valid = True
        elif raw_role and raw_dept:
            is_valid = True

        if not is_valid:
            print("SKIPPED TRAINING ROW:", emp)
            continue

        # If name missing but ID exists, use ID
        if not raw_name and raw_id:
            raw_name = raw_id
            
        # If role missing, default to Employee
        if not raw_role:
            raw_role = "Employee"
            
        # ── 4. Normalize employee row ──
        norm_emp = {
            "employee_id": raw_id,
            "employee_name": raw_name or "Unknown",
            "role": raw_role,
            "department": raw_dept,
            "training_status": raw_status or "Pending",
            "mfa_enabled": raw_mfa,
            "last_training_date": raw_date,
            "email": raw_email
        }
        
        print("VALID TRAINING EMPLOYEE:", norm_emp)
        
        emp_email = norm_emp["email"].lower()
        emp_name_lower = norm_emp["employee_name"].lower()
        group_key = _classify_role(norm_emp["role"])

        # Look for matching evidence
        evidence_row = evidence_map.get(emp_name_lower)
        if not evidence_row and emp_email:
            evidence_row = evidence_map.get(emp_email)

        source_row = evidence_row if evidence_row else emp

        # Assigned training
        assigned_default = content_map.get(group_key, content_map["general"])
        assigned = (
            source_row.get("Training Module")
            or source_row.get("Assigned Training")
            or source_row.get("assigned_training")
            or source_row.get("required_modules")
            or assigned_default
        )

        # Status
        status = (
            source_row.get("Status")
            or source_row.get("status")
            or source_row.get("training_status")
            or source_row.get("security_training_status")
            or source_row.get("training_completed")
            or source_row.get("awareness")
            or norm_emp["training_status"]
        )

        # Dates
        last_date = (
            source_row.get("Last Training Date")
            or source_row.get("last_training_date")
            or source_row.get("last_training")
            or source_row.get("last_performed")
            or norm_emp["last_training_date"]
        )
        next_date = (
            source_row.get("Next Due Date")
            or source_row.get("next_due_date")
            or source_row.get("next_due")
        )

        has_real_dates = bool(last_date or next_date)
        if not has_real_dates:
            last_date = "Not Available"
            next_date = "Not Available"
        else:
            last_date = last_date or "Not Available"
            next_date = next_date or "Not Available"

            if next_date != "Not Available" and _hipaa_is_overdue(str(next_date)):
                status = "Overdue"

        if str(status).strip().lower() == "completed":
            status = "Completed (On Time)"

        employee_tracker.append({
            "employee":           norm_emp["employee_name"],
            "role":               norm_emp["role"],
            "assigned_training":  str(assigned).strip(),
            "status":             str(status).strip(),
            "last_training_date": str(last_date).strip(),
            "next_due_date":      str(next_date).strip(),
            # Expose normalized fields just in case backend logic needs them
            "employee_id":        norm_emp["employee_id"],
            "department":         norm_emp["department"],
            "mfa_enabled":        norm_emp["mfa_enabled"],
        })

    print("VALID EMPLOYEES:", [e["employee"] for e in employee_tracker])

    return {
        "role_based_matrix":  role_based_matrix,
        "employee_tracker":   employee_tracker,
        "framework":          fw_key,
        "total_roles":        len(role_based_matrix),
        "total_employees":    len(employee_tracker),
    }
