"""
Configuration Risk Register Generator.

Converts configuration analysis findings into a business-level risk register.
Also generates best-practice recommendations based on the findings.

ISOLATION: This module is part of the Configuration Engine only.
It does NOT import from the Assessment Engine.
"""

from __future__ import annotations

from typing import Any


# ---------------------------------------------------------------------------
# Impact / Likelihood matrix
# ---------------------------------------------------------------------------

_SEVERITY_TO_IMPACT: dict[str, str] = {
    "High":   "High",
    "Medium": "Medium",
    "Low":    "Low",
}

_CATEGORY_LIKELIHOOD: dict[str, str] = {
    "Integrity":            "High",
    "Network Security":     "High",
    "Encryption":           "High",
    "Access Control":       "Medium",
    "Secrets Management":   "High",
    "Input Validation":     "Medium",
    "Information Disclosure": "Medium",
    "Error Handling":       "Low",
}

_IMPACT_SCORE = {"High": 3, "Medium": 2, "Low": 1}
_LIKELIHOOD_SCORE = {"High": 3, "Medium": 2, "Low": 1}

_TREATMENT_MAP: dict[str, str] = {
    "High":   "Mitigate",
    "Medium": "Mitigate",
    "Low":    "Accept",
}


# ---------------------------------------------------------------------------
# Risk statement templates
# ---------------------------------------------------------------------------

_SPECIFIC_RISK_STATEMENTS: dict[str, str] = {
    "FW-001": "Execution of unrestricted directories may lead to injection of malicious firewall rules.",
    "FW-002": "Firewall rule files may be modified without detection due to missing integrity verification.",
    "FW-003": "Executing scripts without permission validation may allow unauthorized modification of firewall rules.",
    "FW-004": "Default-allow policies may permit unauthorized or malicious traffic into the network.",
    "FW-005": "Unvalidated shell variables may allow injection of unauthorized firewall rules.",
    "FW-006": "Broad allow-all rules may expose internal network services to external exploitation.",
    "FW-007": "Malformed firewall rules may be applied without validation, disrupting network connectivity.",
    "FW-008": "Unauthorized users may inject firewall rules if executable permissions are abused.",
    "NGX-001": "Lack of TLS certificates may result in plaintext transmission of sensitive data.",
    "NGX-002": "Use of weak or deprecated TLS protocols may allow attackers to intercept and decrypt traffic.",
    "NGX-003": "Server version disclosure may assist attackers in identifying and exploiting known vulnerabilities.",
    "SH-001": "Missing strict shell mode may cause errors to be ignored, resulting in unpredictable execution state.",
    "SH-002": "Sourcing files from world-writable directories may result in unauthorized code execution.",
    "SH-003": "Unquoted variables in privileged commands may lead to arbitrary command execution or logic bypass.",
    "GEN-001": "Plaintext credentials in configuration files may be compromised, leading to unauthorized access.",
    "GEN-002": "World-writable permissions may permit unauthorized users to tamper with critical system files.",
}

_RISK_STATEMENTS: dict[str, str] = {
    "Integrity":            "Configuration integrity may be compromised, allowing unauthorized modifications",
    "Access Control":       "Insufficient access controls could permit unauthorized system access",
    "Network Security":     "Network boundaries may be bypassed, exposing internal services to external threats",
    "Encryption":           "Sensitive data may be transmitted or stored without adequate encryption",
    "Secrets Management":   "Credentials or secrets may be exposed, enabling unauthorized access",
    "Input Validation":     "Unvalidated input could be exploited for injection or privilege escalation",
    "Information Disclosure": "System information may be leaked, aiding reconnaissance by attackers",
    "Error Handling":       "Errors may be silently ignored, masking security-relevant failures",
}


# ---------------------------------------------------------------------------
# Risk register builder
# ---------------------------------------------------------------------------

def build_config_risk_register(
    findings: list[dict[str, Any]],
    framework_label: str = "",
) -> list[dict[str, Any]]:
    """
    Generate a risk register from enriched configuration findings.

    Each finding produces one risk entry with:
      risk_id, finding_id, risk_statement, impact, likelihood,
      risk_score (1-9), treatment, recommendation, framework.
    """
    register: list[dict[str, Any]] = []

    for idx, f in enumerate(findings, start=1):
        category = f.get("category", "")
        severity = f.get("severity", "Low")

        impact = _SEVERITY_TO_IMPACT.get(severity, "Low")
        likelihood = _CATEGORY_LIKELIHOOD.get(category, "Medium")

        impact_val = _IMPACT_SCORE.get(impact, 1)
        likelihood_val = _LIKELIHOOD_SCORE.get(likelihood, 1)
        risk_score = impact_val * likelihood_val

        finding_id = f.get("id", "")
        risk_statement = _SPECIFIC_RISK_STATEMENTS.get(
            finding_id,
            _RISK_STATEMENTS.get(
                category,
                f"Misconfiguration detected: {f.get('title', 'Unknown issue')}",
            )
        )

        register.append({
            "risk_id": f"R-{idx:03d}",
            "finding_id": f.get("id", ""),
            "risk_statement": risk_statement,
            "impact": impact,
            "likelihood": likelihood,
            "risk_score": risk_score,
            "treatment": _TREATMENT_MAP.get(impact, "Accept"),
            "recommendation": f.get("recommendation", ""),
            "framework": framework_label,
        })

    # Sort by risk_score descending
    register.sort(key=lambda r: r["risk_score"], reverse=True)
    return register


# ---------------------------------------------------------------------------
# Best practices generator
# ---------------------------------------------------------------------------

_BEST_PRACTICES_POOL: list[dict[str, str]] = [
    {
        "category": "Integrity",
        "title": "Implement File Integrity Monitoring",
        "description": "Deploy FIM tools (e.g. AIDE, OSSEC) to detect unauthorized changes to critical configuration files and firewall rules.",
    },
    {
        "category": "Access Control",
        "title": "Enforce Least-Privilege Access",
        "description": "Restrict file permissions and ownership so only authorized accounts can modify security configurations. Use chmod 0600/0700 and root ownership.",
    },
    {
        "category": "Network Security",
        "title": "Default-Deny Firewall Policy",
        "description": "Set all firewall chain default policies to DROP/REJECT. Only explicitly allow required traffic flows after validation.",
    },
    {
        "category": "Encryption",
        "title": "Enforce TLS 1.2+ Everywhere",
        "description": "Disable SSLv2, SSLv3, TLS 1.0, and TLS 1.1 on all endpoints. Configure only TLSv1.2 and TLSv1.3 with strong cipher suites.",
    },
    {
        "category": "Secrets Management",
        "title": "Use a Secrets Manager",
        "description": "Remove plaintext credentials from configuration files. Inject secrets at runtime via HashiCorp Vault, AWS Secrets Manager, or environment variables.",
    },
    {
        "category": "Input Validation",
        "title": "Sanitize All Dynamic Inputs",
        "description": "Quote all shell variables, validate user-supplied values before use in privileged commands, and avoid constructing commands from untrusted input.",
    },
    {
        "category": "Error Handling",
        "title": "Enable Strict Error Handling",
        "description": "Use 'set -euo pipefail' in shell scripts. Log all errors to a centralized system and alert on critical failures.",
    },
    {
        "category": "Information Disclosure",
        "title": "Minimize Information Exposure",
        "description": "Disable server version headers, directory listings, and stack traces in production. Return generic error pages to end users.",
    },
]


def generate_best_practices(
    findings: list[dict[str, Any]],
    max_practices: int = 5,
) -> list[dict[str, str]]:
    """
    Select the top 3–5 best practices relevant to the detected finding categories.

    Practices are deduplicated and prioritized by the severity of related findings.
    """
    # Collect categories with their max severity weight
    category_weight: dict[str, int] = {}
    sev_w = {"High": 3, "Medium": 2, "Low": 1}
    for f in findings:
        cat = f.get("category", "")
        w = sev_w.get(f.get("severity", "Low"), 1)
        category_weight[cat] = max(category_weight.get(cat, 0), w)

    # Filter and rank best practices
    relevant = [
        (bp, category_weight.get(bp["category"], 0))
        for bp in _BEST_PRACTICES_POOL
        if bp["category"] in category_weight
    ]
    relevant.sort(key=lambda x: x[1], reverse=True)

    return [bp for bp, _ in relevant[:max_practices]]
