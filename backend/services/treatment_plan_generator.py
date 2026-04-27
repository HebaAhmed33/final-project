"""
Treatment Plan Generator Service

Generates one treatment action per risk from the Risk Register,
using rule-based mappings scoped to the selected compliance framework.
Due dates are calculated based on risk severity.
"""

from datetime import datetime, timedelta
import re

# ---------------------------------------------------------------------------
# Framework-specific treatment mappings
# ---------------------------------------------------------------------------

TREATMENT_MAP_ISO27001 = {
    "application_security": (
        "Mitigate: Implement parameterized queries, secure coding reviews, "
        "WAF protection, and regular DAST/SAST testing aligned with ISO 27001 "
        "application security controls."
    ),
    "access_control": (
        "Mitigate: Enforce role-based access control (RBAC), conduct periodic "
        "access reviews, implement least-privilege principles, and document "
        "authorization matrices per ISO 27001 Annex A.8.3."
    ),
    "api_security": (
        "Mitigate: Implement API gateway controls, enforce OAuth/token-based "
        "authentication, apply rate limiting, input validation on all endpoints, "
        "and conduct regular API security testing per ISO 27001 Annex A.8.23."
    ),
    "malware": (
        "Mitigate: Deploy endpoint detection and response (EDR), enforce "
        "anti-malware controls, conduct phishing awareness training, implement "
        "email filtering, and maintain incident response procedures per ISO 27001 "
        "Annex A.8.7 and A.6.3."
    ),
    "vulnerability_management": (
        "Mitigate: Implement automated patch management, monthly vulnerability "
        "scanning, emergency patch SLAs for critical CVEs, and documented "
        "remediation tracking."
    ),
    "misconfiguration": (
        "Mitigate: Establish secure configuration baselines, remove default "
        "credentials, implement configuration management processes, and conduct "
        "periodic hardening reviews per ISO 27001 Annex A.8.9."
    ),
    "encryption": (
        "Mitigate: Enforce TLS, certificate lifecycle management, encryption "
        "at rest, key rotation, and cryptographic policy reviews."
    ),
    "vendor_risk": (
        "Mitigate: Perform vendor security assessments, review DPAs/SLAs, "
        "require security evidence, and monitor supplier compliance."
    ),
    "network_security": (
        "Mitigate: Review firewall rules, implement network segmentation, "
        "restrict unnecessary traffic, deploy IDS/IPS, and validate perimeter "
        "controls per ISO 27001 Annex A.8.20–A.8.22."
    ),
    "policy_governance": (
        "Mitigate: Develop and enforce information security policies, assign "
        "control ownership, conduct management reviews, and track compliance "
        "gaps per ISO 27001 Annex A.5.1–A.5.4."
    ),
    "business_continuity": (
        "Mitigate: Develop and test business continuity plans, implement "
        "disaster recovery procedures, maintain backup schedules, and conduct "
        "periodic restoration testing per ISO 27001 Annex A.5.29–A.5.30."
    ),
    "audit_logging": (
        "Mitigate: Enable centralized logging, configure SIEM alerting, "
        "retain audit logs per policy, monitor for anomalous activity, and "
        "conduct periodic log reviews per ISO 27001 Annex A.8.15–A.8.16."
    ),
    "identity_access": (
        "Mitigate: Enforce MFA, strong password policy, privileged access "
        "reviews, and conditional access controls."
    ),
    "default": (
        "Mitigate: Apply relevant ISO 27001 controls, assign ownership, "
        "define remediation steps, and track closure evidence."
    ),
}

TREATMENT_MAP_HIPAA = {
    "application_security": (
        "Mitigate: Remediate application vulnerabilities affecting ePHI systems, "
        "implement secure coding practices, and validate input handling per "
        "HIPAA Technical Safeguards."
    ),
    "access_control": (
        "Mitigate: Implement role-based access to ePHI, enforce least-privilege, "
        "conduct periodic access reviews, and document authorization procedures "
        "per HIPAA §164.312(a)(1)."
    ),
    "api_security": (
        "Mitigate: Secure APIs handling ePHI with authentication, rate limiting, "
        "input validation, and encrypted transmission per HIPAA transmission "
        "security requirements."
    ),
    "malware": (
        "Mitigate: Deploy anti-malware on systems handling ePHI, conduct phishing "
        "awareness training for workforce, implement email security controls, and "
        "maintain malware incident response procedures per HIPAA §164.308(a)(5)."
    ),
    "vulnerability_management": (
        "Mitigate: Scan ePHI systems for vulnerabilities, apply patches within "
        "defined SLAs, document remediation, and validate through re-scanning."
    ),
    "misconfiguration": (
        "Mitigate: Harden ePHI system configurations, remove default accounts, "
        "apply CIS benchmarks, and document configuration standards per HIPAA "
        "Technical Safeguards."
    ),
    "identity_access": (
        "Mitigate: Enforce unique user identification, MFA, role-based access, "
        "and periodic access reviews for systems handling ePHI."
    ),
    "audit_logging": (
        "Mitigate: Enable audit controls, log access to ePHI, monitor "
        "suspicious activity, and retain logs according to policy."
    ),
    "encryption": (
        "Mitigate: Protect ePHI using encryption in transit and at rest, "
        "enforce secure transmission controls, and review key management."
    ),
    "vendor_risk": (
        "Mitigate: Review Business Associate Agreements, validate security "
        "responsibilities, and monitor third-party handling of ePHI."
    ),
    "network_security": (
        "Mitigate: Segment networks handling ePHI, review firewall rules, "
        "restrict traffic to authorized systems, and monitor network activity "
        "per HIPAA Technical Safeguards."
    ),
    "policy_governance": (
        "Mitigate: Develop ePHI security policies, assign a Security Officer, "
        "conduct risk analyses, and maintain documentation per HIPAA "
        "§164.308(a)(1)–(a)(2)."
    ),
    "business_continuity": (
        "Mitigate: Maintain backup procedures, disaster recovery plans, "
        "emergency mode operations, and periodic restoration testing."
    ),
    "default": (
        "Mitigate: Apply relevant HIPAA Security Rule safeguards, assign "
        "responsibility, document remediation, and verify protection of ePHI."
    ),
}

TREATMENT_MAP_PCI_DSS = {
    "application_security": (
        "Mitigate: Remediate injection weaknesses using secure coding, "
        "parameterized queries, code review, WAF rules, and PCI DSS "
        "application security testing."
    ),
    "access_control": (
        "Mitigate: Restrict access to cardholder data on a need-to-know basis, "
        "implement RBAC, conduct quarterly access reviews, and document "
        "authorization per PCI DSS Requirement 7."
    ),
    "api_security": (
        "Mitigate: Secure payment APIs with token-based authentication, "
        "rate limiting, input validation, and encrypted channels per PCI DSS "
        "Requirement 6."
    ),
    "malware": (
        "Mitigate: Deploy anti-malware on all systems in the cardholder data "
        "environment, maintain current signatures, conduct phishing awareness "
        "training, and log malware events per PCI DSS Requirement 5."
    ),
    "vulnerability_management": (
        "Mitigate: Apply security patches, maintain vulnerability scans, "
        "remediate critical findings within SLA, and document evidence."
    ),
    "misconfiguration": (
        "Mitigate: Remove default credentials, harden system configurations, "
        "apply vendor security guidelines, and validate against PCI DSS "
        "Requirement 2."
    ),
    "identity_access": (
        "Mitigate: Enforce MFA for administrative and cardholder data access, "
        "strong authentication, least privilege, and access reviews."
    ),
    "network_security": (
        "Mitigate: Review firewall rules, segment the cardholder data "
        "environment, restrict inbound/outbound traffic, and validate "
        "rule ownership."
    ),
    "encryption": (
        "Mitigate: Encrypt cardholder data in transit and at rest, manage "
        "keys securely, and validate cryptographic controls."
    ),
    "vendor_risk": (
        "Mitigate: Assess third-party service providers handling cardholder "
        "data, validate PCI DSS compliance, review contractual security "
        "obligations, and monitor ongoing compliance."
    ),
    "policy_governance": (
        "Mitigate: Maintain a formal security policy covering all PCI DSS "
        "requirements, assign ownership, conduct annual reviews, and track "
        "compliance evidence per Requirement 12."
    ),
    "business_continuity": (
        "Mitigate: Implement backup and recovery procedures for cardholder "
        "data systems, test disaster recovery plans, and document restoration "
        "evidence per PCI DSS operational requirements."
    ),
    "audit_logging": (
        "Mitigate: Enable logging on all CDE systems, retain audit trails, "
        "review logs daily, deploy automated alerting, and validate per "
        "PCI DSS Requirement 10."
    ),
    "default": (
        "Mitigate: Apply relevant PCI DSS requirements, define remediation "
        "ownership, collect evidence, and validate closure."
    ),
}

# Map normalised framework id → treatment dictionary
FRAMEWORK_TREATMENTS = {
    "iso27001":  TREATMENT_MAP_ISO27001,
    "iso_27001": TREATMENT_MAP_ISO27001,
    "hipaa":     TREATMENT_MAP_HIPAA,
    "pci_dss":   TREATMENT_MAP_PCI_DSS,
    "pci-dss":   TREATMENT_MAP_PCI_DSS,
    "pcidss":    TREATMENT_MAP_PCI_DSS,
}

# ---------------------------------------------------------------------------
# Category detection keywords
#
# Design principles for generalization:
#   - Mix single words (synonyms) AND short phrases for broad coverage
#   - Use root forms / stems where possible so inflections still match
#   - Avoid overly generic words that appear in unrelated contexts
#   - The scorer weights fields: threat=4, statement=3, control=2, asset=1
#   - Minimum score threshold prevents weak false-positive matches
# ---------------------------------------------------------------------------

CATEGORY_KEYWORDS = {
    "application_security": [
        "inject", "sql", "xss", "csrf", "cross-site", "owasp",
        "sast", "dast", "waf", "code review", "secure cod",
        "buffer overflow", "input validat", "sanitiz", "parameteriz",
        "web application vulnerab", "application vulnerab",
        "deserialization", "command execution",
    ],
    "api_security": [
        "api", "endpoint", "gateway", "oauth", "rate limit",
        "graphql", "rest service", "web service", "token",
        "api key", "api authenticat", "api authoriz", "webhook",
        "microservice", "service mesh",
    ],
    "malware": [
        "malware", "ransomware", "phishing", "trojan", "worm",
        "spyware", "keylog", "rootkit", "botnet", "virus",
        "social engineer", "spam", "fileless", "cryptojack",
        "crypto-min", "adware", "backdoor", "infect",
    ],
    "misconfiguration": [
        "misconfig", "default credential", "default password",
        "default account", "default setting", "harden",
        "insecure config", "open port", "unnecessary service",
        "security baseline", "benchmark", "cis benchmark",
        "weak config", "insecure default", "exposed service",
    ],
    "business_continuity": [
        "business continuity", "disaster recovery", "bcp", "drp",
        "backup", "restor", "failover", "redundan", "resilienc",
        "rpo", "rto", "outage", "service disrupt", "crisis",
        "emergency operat", "continuity plan", "recovery plan",
        "data loss prevent",
    ],
    "vendor_risk": [
        "vendor", "supplier", "third party", "third-party", "outsourc",
        "supply chain", "subcontract", "procurement", "dpa", "baa",
        "service provider", "partner risk", "vendor assess",
        "vendor complianc", "contract review", "sla review",
    ],
    "vulnerability_management": [
        "vulnerab", "patch", "unpatched", "cve", "exploit",
        "remote code execut", "end of life", "eol", "outdated",
        "zero-day", "0-day", "scan result", "penetrat",
        "security updat", "missing patch", "obsolete",
    ],
    "encryption": [
        "encrypt", "decrypt", "tls", "ssl", "certific",
        "cryptograph", "cipher", "key manag", "key rotat",
        "data at rest", "data in transit", "pki", "hash",
        "plaintext", "unencrypt", "cleartext",
    ],
    "network_security": [
        "firewall", "network segment", "dmz", "intrusion detect",
        "intrusion prevent", "ids", "ips", "perimeter",
        "lateral movement", "ddos", "port scan", "vlan",
        "network isolat", "routing", "switch", "network traffic",
        "packet filter", "network access control",
    ],
    "audit_logging": [
        "audit", "logging", "siem", "log retent", "log monitor",
        "event correlat", "security monitor", "anomaly detect",
        "alert", "log review", "audit trail", "forensic",
        "evidence collect", "traceabil",
    ],
    "policy_governance": [
        "policy", "governance", "compliance gap", "control missing",
        "non-complian", "regulat", "management review",
        "security framework", "risk management framework",
        "policy violat", "standard gap", "procedure missing",
        "documentation gap", "accountability",
    ],
    "access_control": [
        "rbac", "role-based", "authoriz", "privilege", "permiss",
        "least privilege", "access review", "access control",
        "unauthorized access", "excessive access", "user provision",
        "deprovision", "segregat", "separation of dut",
        "need to know", "need-to-know",
    ],
    "identity_access": [
        "mfa", "multi-factor", "password", "authenticat", "credential",
        "identity", "iam", "sso", "single sign", "brute force",
        "credential stuff", "account lockout", "session manag",
        "login", "logon",
    ],
}

# Minimum score to accept a classification (avoids weak false positives)
_MIN_SCORE_THRESHOLD = 2


def _normalize_text(raw: str) -> str:
    """
    Normalize text for keyword matching.

    Steps:
      1. Lowercase
      2. Strip punctuation (keep spaces and hyphens)
      3. Lightweight suffix stripping for common English endings
         so that 'misconfigured' matches 'misconfig',
         'injections' matches 'inject', etc.
    """
    text = str(raw).lower()
    # Replace punctuation (except hyphens) with spaces
    text = re.sub(r"[^\w\s-]", " ", text)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _stem_token(word: str) -> str:
    """Very lightweight suffix stripping for matching flexibility."""
    # Order matters: strip longest suffixes first
    for suffix in ("ation", "tion", "sion", "ment", "ness", "ence", "ance",
                    "ious", "ous", "ive", "ing", "able", "ible", "ure",
                    "ies", "ied", "ers", "ed", "es", "er", "ly", "al", "s"):
        if len(word) > len(suffix) + 3 and word.endswith(suffix):
            return word[:-len(suffix)]
    return word


def _normalise_framework(framework_raw: str) -> str:
    """Normalise a raw framework string to a lookup key."""
    if not framework_raw:
        return "iso27001"
    f = framework_raw.strip().lower()
    f = re.sub(r"[^a-z0-9]", "", f)  # strip non-alphanum
    if "hipaa" in f:
        return "hipaa"
    if "pci" in f:
        return "pci_dss"
    if "sama" in f:
        return "iso27001"  # SAMA maps to ISO controls
    return "iso27001"


def _detect_category(risk: dict) -> str:
    """
    Detect the risk category using multi-field weighted keyword scoring.

    Field weights:
      - threat / vulnerability  → 4  (strongest signal)
      - risk_statement / desc   → 3
      - control / rule_id       → 2
      - asset / asset_type      → 1

    The category with the highest aggregate score wins.
    If the best score is below _MIN_SCORE_THRESHOLD, returns "default"
    to avoid weak false-positive classifications.
    """
    # ── Build normalized searchable fields ─────────────────────────────────
    threat_text = _normalize_text(" ".join([
        str(risk.get("threat", "")),
        str(risk.get("vulnerability", "")),
    ]))

    statement_text = _normalize_text(" ".join([
        str(risk.get("risk_statement", "")),
        str(risk.get("description", "")),
        str(risk.get("title", "")),
        str(risk.get("name", "")),
        str(risk.get("risk_name", "")),
    ]))

    control_text = _normalize_text(" ".join([
        str(risk.get("control", "")),
        str(risk.get("controls", "")),
        str(risk.get("control_id", "")),
        str(risk.get("rule_id", "")),
        str(risk.get("iso_controls", "")),
        str(risk.get("mitigation", "")),
    ]))

    asset_text = _normalize_text(" ".join([
        str(risk.get("asset", "")),
        str(risk.get("asset_type", "")),
    ]))

    # ── Score each category ───────────────────────────────────────────────
    best_category = "default"
    best_score = 0

    for category, keywords in CATEGORY_KEYWORDS.items():
        score = 0
        for kw in keywords:
            # Check each weighted field independently
            if kw in threat_text:
                score += 4
            if kw in statement_text:
                score += 3
            if kw in control_text:
                score += 2
            if kw in asset_text:
                score += 1

        if score > best_score:
            best_score = score
            best_category = category

    # Require a minimum score to avoid weak matches
    if best_score < _MIN_SCORE_THRESHOLD:
        return "default"

    return best_category


def _compute_risk_score(risk: dict) -> int:
    """Compute the numeric risk score (likelihood × impact)."""
    try:
        raw_l = float(risk.get("likelihood", 0))
        raw_i = float(risk.get("impact", 0))
        if raw_l > 0 and raw_i > 0:
            l_score = max(1, min(5, round(raw_l)))
            i_score = max(1, min(5, round(raw_i)))
            return l_score * i_score
    except (TypeError, ValueError):
        pass

    # Fallback to textual risk level
    level = str(risk.get("risk_level", risk.get("level", "medium"))).lower()
    if level in ("critical", "extreme"):
        return 25
    if level == "high":
        return 12
    if level == "low":
        return 4
    return 9  # medium default


def _due_date(risk_score: int, base_date: datetime = None) -> str:
    """Return a DD/MM/YYYY due date based on severity."""
    if base_date is None:
        base_date = datetime.now()

    if risk_score >= 15:
        delta = 30
    elif risk_score >= 8:
        delta = 60
    else:
        delta = 90

    return (base_date + timedelta(days=delta)).strftime("%d/%m/%Y")


def generate_treatment_plan(risks: list, framework_id: str = "iso27001",
                            base_date: datetime = None) -> list:
    """
    Generate a treatment plan from a list of risk entries.

    Parameters
    ----------
    risks : list[dict]
        Combined risk entries (generated + uploaded) from the risk register.
    framework_id : str
        The selected compliance framework identifier.
    base_date : datetime, optional
        The reference date for due-date calculation (defaults to now).

    Returns
    -------
    list[dict]
        Each dict has keys: risk_id, treatment, due_date
    """
    print("USING NEW GENERATOR")
    fw_key = _normalise_framework(framework_id)
    treatment_map = FRAMEWORK_TREATMENTS.get(fw_key, TREATMENT_MAP_ISO27001)

    plan = []
    for idx, risk in enumerate(risks):
        risk_id = (
            risk.get("risk_id")
            or risk.get("id")
            or f"R{idx + 1}"
        )

        category = _detect_category(risk)
        print(f"{risk_id} -> {category}")
        treatment_text = treatment_map.get(category, treatment_map["default"])

        score = _compute_risk_score(risk)
        due = _due_date(score, base_date)

        plan.append({
            "risk_id": str(risk_id),
            "treatment": treatment_text,
            "due_date": due,
        })

    return plan
