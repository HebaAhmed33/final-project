"""
PCI DSS v4.0 — Rule-Based Evaluation Rules.

RISK-BASED evaluation covering the 12 PCI DSS requirements.

Unlike the previous presence-based approach, these rules now:
  1. Cross-reference multiple data sources for each control
  2. Require specific quality indicators, not just sheet existence
  3. Apply weighted severity for realistic scoring
"""

PCI_DSS_RULES: list[dict] = [
    # ── Req 1: Network Security Controls ──────────────────────────────────
    {
        "rule_id": "PCI-RE-001", "control_ref": "Req 1",
        "name": "Network Security Controls", "domain": "Network Security",
        "description": "Verify firewall/router configs protect cardholder data environments.",
        "severity": "critical", "eval_type": "boolean",
        "eval_config": {"signal": "has_network_rules", "expected": True},
        "remediation": "Deploy and document firewall rules protecting the cardholder data environment.",
    },
    # ── Req 1.3: Network Segmentation ─────────────────────────────────────
    {
        "rule_id": "PCI-RE-002", "control_ref": "Req 1.3",
        "name": "Network Segmentation", "domain": "Network Security",
        "description": "Verify network segmentation isolates cardholder data environment.",
        "severity": "critical", "eval_type": "boolean",
        "eval_config": {"signal": "has_deny_rules", "expected": True},
        "remediation": "Implement network segmentation with default-deny between CDE and other networks.",
    },
    # ── Req 1.4: No Overly Permissive Rules ───────────────────────────────
    {
        "rule_id": "PCI-RE-003", "control_ref": "Req 1.4",
        "name": "No Overly Permissive Rules", "domain": "Network Security",
        "description": "Verify no ANY/wildcard rules exist in firewall configs.",
        "severity": "high", "eval_type": "threshold",
        "eval_config": {"metric": "risky_rule_pct", "operator": "lte", "value": 0.0},
        "remediation": "Remove all ANY/wildcard rules. Apply least-privilege to all firewall entries.",
    },
    # ── Req 2: Secure System Configurations ──────────────────────────────
    {
        "rule_id": "PCI-RE-013", "control_ref": "Req 2",
        "name": "Secure System Configurations", "domain": "Configuration Management",
        "description": "Ensure vendor-supplied defaults and insecure configurations are changed.",
        "severity": "high", "eval_type": "evidence_keyword",
        "eval_config": {
            "keywords": ["hardening", "baseline", "configuration", "default password", "cis benchmark"],
            "evidence_sources": ["governance", "assets"],
            "match_mode": "any",
        },
        "remediation": "Apply CIS benchmarks or equivalent hardening standards to all systems in scope.",
    },
    # ── Req 3: Protect Stored Cardholder Data ─────────────────────────────
    {
        "rule_id": "PCI-RE-004", "control_ref": "Req 3",
        "name": "Protect Stored Cardholder Data", "domain": "Data Protection",
        "description": "Verify controls exist for stored cardholder data protection.",
        "severity": "critical", "eval_type": "evidence_keyword",
        "eval_config": {
            "keywords": ["encryption", "masking", "tokenization", "data retention", "aes"],
            "evidence_sources": ["governance", "assets"],
            "match_mode": "any",
        },
        "remediation": "Implement data encryption, masking, and retention policies for stored cardholder data.",
    },
    # ── Req 4: Encrypt Transmission of CHD ────────────────────────────────
    {
        "rule_id": "PCI-RE-005", "control_ref": "Req 4",
        "name": "Encrypt Transmission of CHD", "domain": "Data Protection",
        "description": "Verify cardholder data is encrypted during transmission over open networks.",
        "severity": "critical", "eval_type": "evidence_keyword",
        "eval_config": {
            "keywords": ["tls", "ssl", "encryption", "vpn", "ipsec"],
            "evidence_sources": ["network_rules", "governance"],
            "match_mode": "any",
        },
        "remediation": "Use strong cryptography (TLS 1.2+) for all CHD transmissions over open networks.",
    },
    # ── Req 5: Anti-Malware ───────────────────────────────────────────────
    {
        "rule_id": "PCI-RE-006", "control_ref": "Req 5",
        "name": "Anti-Malware", "domain": "Endpoint Security",
        "description": "Verify anti-malware solutions are deployed on all applicable systems.",
        "severity": "high", "eval_type": "evidence_keyword",
        "eval_config": {
            "keywords": ["antivirus", "anti-malware", "edr", "endpoint protection", "malware"],
            "evidence_sources": ["assets", "governance"],
            "match_mode": "any",
        },
        "remediation": "Deploy and maintain anti-malware on all systems commonly affected by malware.",
    },
    # ── Req 6: Secure Development ─────────────────────────────────────────
    {
        "rule_id": "PCI-RE-014", "control_ref": "Req 6",
        "name": "Develop and Maintain Secure Systems", "domain": "Secure Development",
        "description": "Verify patching, secure development, and vulnerability management.",
        "severity": "high", "eval_type": "evidence_keyword",
        "eval_config": {
            "keywords": ["patch", "vulnerability", "update", "owasp", "secure coding", "sdlc"],
            "evidence_sources": ["assets", "governance"],
            "match_mode": "any",
        },
        "remediation": "Implement patch management, vulnerability scanning, and secure SDLC.",
    },
    # ── Req 7: Restrict Access to CHD ─────────────────────────────────────
    {
        "rule_id": "PCI-RE-007", "control_ref": "Req 7",
        "name": "Restrict Access to CHD", "domain": "Access Control",
        "description": "Verify access to cardholder data is restricted by business need-to-know.",
        "severity": "critical", "eval_type": "evidence_keyword",
        "eval_config": {
            "keywords": ["rbac", "role-based", "need-to-know", "access review", "least privilege"],
            "evidence_sources": ["employees", "governance"],
            "match_mode": "any",
        },
        "remediation": "Implement role-based access control. Restrict CHD access to need-to-know only.",
    },
    # ── Req 8: Identify Users and Authenticate Access ─────────────────────
    {
        "rule_id": "PCI-RE-008", "control_ref": "Req 8",
        "name": "Identify Users and Authenticate Access", "domain": "Access Control",
        "description": "Verify unique IDs, strong authentication, and MFA for all CDE access.",
        "severity": "high", "eval_type": "evidence_keyword",
        "eval_config": {
            "keywords": ["mfa", "multi-factor", "two-factor", "2fa", "authentication"],
            "evidence_sources": ["employees", "governance"],
            "match_mode": "any",
        },
        "remediation": "Assign unique IDs to all users. Implement MFA for all CDE access.",
    },
    # ── Req 9: Physical Access ────────────────────────────────────────────
    {
        "rule_id": "PCI-RE-015", "control_ref": "Req 9",
        "name": "Restrict Physical Access", "domain": "Physical Security",
        "description": "Restrict physical access to cardholder data.",
        "severity": "high", "eval_type": "evidence_keyword",
        "eval_config": {
            "keywords": ["physical access", "badge", "cctv", "visitor", "data center"],
            "evidence_sources": ["governance", "assets"],
            "match_mode": "any",
        },
        "remediation": "Implement physical access controls, CCTV, and visitor management for CDE.",
    },
    # ── Req 10: Log and Monitor All Access ────────────────────────────────
    {
        "rule_id": "PCI-RE-009", "control_ref": "Req 10",
        "name": "Log and Monitor All Access", "domain": "Monitoring",
        "description": "Verify logging is enabled for all access to network resources and CHD.",
        "severity": "critical", "eval_type": "evidence_keyword",
        "eval_config": {
            "keywords": ["siem", "log", "audit trail", "monitoring", "alert"],
            "evidence_sources": ["governance", "network_rules"],
            "match_mode": "any",
        },
        "remediation": "Enable centralized audit logging. Implement daily log review processes.",
    },
    # ── Req 11: Test Security Systems ─────────────────────────────────────
    {
        "rule_id": "PCI-RE-016", "control_ref": "Req 11",
        "name": "Test Security Systems and Processes", "domain": "Security Testing",
        "description": "Regularly test security systems and processes.",
        "severity": "high", "eval_type": "evidence_keyword",
        "eval_config": {
            "keywords": ["penetration test", "pen test", "vulnerability scan", "security testing", "ids"],
            "evidence_sources": ["governance", "risk_register"],
            "match_mode": "any",
        },
        "remediation": "Conduct quarterly vulnerability scans and annual penetration tests.",
    },
    # ── Req 12: Information Security Policy ───────────────────────────────
    {
        "rule_id": "PCI-RE-010", "control_ref": "Req 12",
        "name": "Information Security Policy", "domain": "Governance",
        "description": "Verify a security policy addressing all PCI DSS requirements exists.",
        "severity": "critical", "eval_type": "evidence_keyword",
        "eval_config": {
            "keywords": ["security policy", "pci policy", "information security", "acceptable use"],
            "evidence_sources": ["governance"],
            "match_mode": "any",
        },
        "remediation": "Establish and maintain an information security policy addressing all PCI DSS requirements.",
    },
    # ── Req 12.6: Security Awareness Training ─────────────────────────────
    {
        "rule_id": "PCI-RE-017", "control_ref": "Req 12.6",
        "name": "Security Awareness Training", "domain": "People Security",
        "description": "Implement security awareness training for all personnel.",
        "severity": "high", "eval_type": "threshold",
        "eval_config": {"metric": "training_coverage_pct", "operator": "gte", "value": 80.0},
        "remediation": "Deploy mandatory security awareness training for all employees with annual refreshers.",
    },
    # ── Req 12.8: Third-Party Service Provider Management ─────────────────
    {
        "rule_id": "PCI-RE-011", "control_ref": "Req 12.8",
        "name": "Third-Party Service Provider Management", "domain": "Supplier Management",
        "description": "Verify policies for managing service providers with access to CHD.",
        "severity": "high", "eval_type": "field_present",
        "eval_config": {"required_fields": ["vendor_name", "risk_level"], "evidence_sources": ["vendors"]},
        "remediation": "Maintain a list of all service providers. Require PCI compliance from each.",
    },
    # ── Req 12.10: Incident Response Plan ─────────────────────────────────
    {
        "rule_id": "PCI-RE-012", "control_ref": "Req 12.10",
        "name": "Incident Response Plan", "domain": "Incident Management",
        "description": "Verify an incident response plan exists and is tested.",
        "severity": "critical", "eval_type": "evidence_keyword",
        "eval_config": {
            "keywords": ["incident response", "incident plan", "breach response", "incident management"],
            "evidence_sources": ["governance", "risk_register"],
            "match_mode": "any",
        },
        "remediation": "Develop and test an incident response plan covering cardholder data breaches.",
    },
]
