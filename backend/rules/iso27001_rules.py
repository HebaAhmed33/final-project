"""
ISO 27001:2022 — Rule-Based Evaluation Rules.

Covers Annex A controls organised by section:
  A5 — Organizational Controls
  A6 — People Controls
  A7 — Physical Controls
  A8 — Technological Controls

Each rule maps to a specific control and defines HOW to evaluate
compliance from uploaded organizational data.
"""

ISO27001_RULES: list[dict] = [
    # ══════════════════════════════════════════════════════════════════════
    # A5 — Organizational Controls
    # ══════════════════════════════════════════════════════════════════════
    {
        "rule_id": "ISO-RE-A5-001",
        "control_ref": "A.5.1",
        "name": "Information Security Policy",
        "description": "Verify that an information security policy exists and is documented.",
        "domain": "Organizational Controls",
        "severity": "critical",
        "eval_type": "evidence_keyword",
        "eval_config": {
            "keywords": ["security policy", "information security", "isms policy"],
            "evidence_sources": ["governance", "controls"],
            "match_mode": "any",
        },
        "remediation": "Develop and formally approve an Information Security Policy aligned to ISO 27001.",
    },
    {
        "rule_id": "ISO-RE-A5-002",
        "control_ref": "A.5.2",
        "name": "Information Security Roles and Responsibilities",
        "description": "Verify that security roles and responsibilities are defined and assigned.",
        "domain": "Organizational Controls",
        "severity": "high",
        "eval_type": "evidence_keyword",
        "eval_config": {
            "keywords": ["roles", "responsibilities", "security officer", "ciso"],
            "evidence_sources": ["governance", "employees"],
            "match_mode": "any",
        },
        "remediation": "Define and document information security roles. Assign a responsible owner for the ISMS.",
    },
    {
        "rule_id": "ISO-RE-A5-003",
        "control_ref": "A.5.3",
        "name": "Segregation of Duties",
        "description": "Verify that conflicting duties are segregated to reduce risk of fraud or error.",
        "domain": "Organizational Controls",
        "severity": "high",
        "eval_type": "evidence_keyword",
        "eval_config": {
            "keywords": ["segregation", "separation of duties", "dual control"],
            "evidence_sources": ["governance", "employees"],
            "match_mode": "any",
        },
        "remediation": "Implement segregation of duties for critical processes. Document in the ISMS.",
    },
    {
        "rule_id": "ISO-RE-A5-004",
        "control_ref": "A.5.19",
        "name": "Information Security in Supplier Relationships",
        "description": "Verify that supplier/vendor security requirements are defined and monitored.",
        "domain": "Supplier Management",
        "severity": "high",
        "eval_type": "field_present",
        "eval_config": {
            "required_fields": ["vendor_name", "risk_level", "compliance"],
            "evidence_sources": ["vendors"],
        },
        "remediation": "Establish a supplier security management process. Require compliance attestations from all vendors.",
    },
    {
        "rule_id": "ISO-RE-A5-005",
        "control_ref": "A.5.24",
        "name": "Incident Management Planning",
        "description": "Verify that an incident management plan and response procedures exist.",
        "domain": "Incident Management",
        "severity": "critical",
        "eval_type": "evidence_keyword",
        "eval_config": {
            "keywords": ["incident", "response plan", "incident management"],
            "evidence_sources": ["governance", "risk_register"],
            "match_mode": "any",
        },
        "remediation": "Develop an Incident Response Plan. Define escalation paths and communication procedures.",
    },
    {
        "rule_id": "ISO-RE-A5-006",
        "control_ref": "A.5.29",
        "name": "Information Security During Disruption",
        "description": "Verify that business continuity plans include information security considerations.",
        "domain": "Resilience",
        "severity": "high",
        "eval_type": "evidence_keyword",
        "eval_config": {
            "keywords": ["business continuity", "disaster recovery", "disruption"],
            "evidence_sources": ["governance", "risk_register"],
            "match_mode": "any",
        },
        "remediation": "Include information security in business continuity and disaster recovery planning.",
    },

    # ══════════════════════════════════════════════════════════════════════
    # A6 — People Controls
    # ══════════════════════════════════════════════════════════════════════
    {
        "rule_id": "ISO-RE-A6-001",
        "control_ref": "A.6.1",
        "name": "Screening",
        "description": "Verify that background verification checks are conducted for personnel.",
        "domain": "People Controls",
        "severity": "medium",
        "eval_type": "boolean",
        "eval_config": {
            "signal": "has_employee_records",
            "expected": True,
        },
        "remediation": "Implement pre-employment background screening procedures for all employees.",
    },
    {
        "rule_id": "ISO-RE-A6-002",
        "control_ref": "A.6.3",
        "name": "Information Security Awareness, Education and Training",
        "description": "Verify that employees receive security awareness training with adequate coverage.",
        "domain": "People Controls",
        "severity": "high",
        "eval_type": "threshold",
        "eval_config": {
            "metric": "training_coverage_pct",
            "operator": "gte",
            "value": 60.0,
        },
        "remediation": "Implement a mandatory security awareness training programme for all employees.",
    },
    {
        "rule_id": "ISO-RE-A6-003",
        "control_ref": "A.6.5",
        "name": "Responsibilities After Termination",
        "description": "Verify that post-termination security responsibilities are documented.",
        "domain": "People Controls",
        "severity": "high",
        "eval_type": "evidence_keyword",
        "eval_config": {
            "keywords": ["termination", "offboarding", "post-employment", "exit"],
            "evidence_sources": ["governance", "employees"],
            "match_mode": "any",
        },
        "remediation": "Document post-employment security responsibilities and offboarding procedures.",
    },
    {
        "rule_id": "ISO-RE-A6-004",
        "control_ref": "A.6.6",
        "name": "Confidentiality / Non-Disclosure Agreements",
        "description": "Verify that NDA or confidentiality agreements are in place.",
        "domain": "People Controls",
        "severity": "high",
        "eval_type": "evidence_keyword",
        "eval_config": {
            "keywords": ["nda", "non-disclosure", "confidentiality agreement"],
            "evidence_sources": ["employees", "vendors"],
            "match_mode": "any",
        },
        "remediation": "Require signed NDAs from all employees, contractors, and third-party vendors.",
    },
    {
        "rule_id": "ISO-RE-A6-005",
        "control_ref": "A.6.7",
        "name": "Remote Working",
        "description": "Verify that remote working security measures are implemented.",
        "domain": "People Controls",
        "severity": "high",
        "eval_type": "evidence_keyword",
        "eval_config": {
            "keywords": ["remote", "vpn", "telework", "work from home"],
            "evidence_sources": ["network_rules", "governance"],
            "match_mode": "any",
        },
        "remediation": "Define a Remote Working Security Policy including VPN, endpoint protection, and data handling.",
    },

    # ══════════════════════════════════════════════════════════════════════
    # A7 — Physical Controls
    # ══════════════════════════════════════════════════════════════════════
    {
        "rule_id": "ISO-RE-A7-001",
        "control_ref": "A.7.1",
        "name": "Physical Security Perimeters",
        "description": "Verify that physical security perimeters are defined for sensitive areas.",
        "domain": "Physical Controls",
        "severity": "high",
        "eval_type": "boolean",
        "eval_config": {
            "signal": "has_asset_inventory",
            "expected": True,
        },
        "remediation": "Define physical security perimeters. Document boundaries and access controls for secure areas.",
    },
    {
        "rule_id": "ISO-RE-A7-002",
        "control_ref": "A.7.4",
        "name": "Physical Security Monitoring",
        "description": "Verify that physical security monitoring (CCTV, guards, alarms) exists.",
        "domain": "Physical Controls",
        "severity": "medium",
        "eval_type": "evidence_keyword",
        "eval_config": {
            "keywords": ["cctv", "surveillance", "monitoring", "alarm", "guard"],
            "evidence_sources": ["assets", "governance"],
            "match_mode": "any",
        },
        "remediation": "Implement physical security monitoring: CCTV, intrusion alarms, and access logging.",
    },
    {
        "rule_id": "ISO-RE-A7-003",
        "control_ref": "A.7.10",
        "name": "Storage Media",
        "description": "Verify that storage media management procedures exist (lifecycle, disposal).",
        "domain": "Physical Controls",
        "severity": "medium",
        "eval_type": "evidence_keyword",
        "eval_config": {
            "keywords": ["storage media", "disposal", "sanitization", "decommission"],
            "evidence_sources": ["assets", "governance"],
            "match_mode": "any",
        },
        "remediation": "Implement storage media lifecycle management including secure disposal procedures.",
    },

    # ══════════════════════════════════════════════════════════════════════
    # A8 — Technological Controls
    # ══════════════════════════════════════════════════════════════════════
    {
        "rule_id": "ISO-RE-A8-001",
        "control_ref": "A.8.1",
        "name": "User Endpoint Devices",
        "description": "Verify that endpoint device security policies and controls exist.",
        "domain": "Technological Controls",
        "severity": "high",
        "eval_type": "boolean",
        "eval_config": {
            "signal": "has_asset_inventory",
            "expected": True,
        },
        "remediation": "Define endpoint security policy. Deploy endpoint protection on all user devices.",
    },
    {
        "rule_id": "ISO-RE-A8-002",
        "control_ref": "A.8.3",
        "name": "Privileged Access Rights",
        "description": "Verify that privileged access is restricted and monitored.",
        "domain": "Technological Controls",
        "severity": "critical",
        "eval_type": "boolean",
        "eval_config": {
            "signal": "has_access_levels",
            "expected": True,
        },
        "remediation": "Implement least-privilege access. Review and restrict all privileged accounts.",
    },
    {
        "rule_id": "ISO-RE-A8-003",
        "control_ref": "A.8.20",
        "name": "Network Security",
        "description": "Verify that network security controls (firewalls, segmentation) are in place.",
        "domain": "Technological Controls",
        "severity": "critical",
        "eval_type": "boolean",
        "eval_config": {
            "signal": "has_network_rules",
            "expected": True,
        },
        "remediation": "Deploy and configure firewall rules. Implement network segmentation to limit lateral movement.",
    },
    {
        "rule_id": "ISO-RE-A8-004",
        "control_ref": "A.8.21",
        "name": "Security of Network Services",
        "description": "Verify that network services are secured and monitored.",
        "domain": "Technological Controls",
        "severity": "high",
        "eval_type": "threshold",
        "eval_config": {
            "metric": "risky_rule_pct",
            "operator": "lte",
            "value": 10.0,
        },
        "remediation": "Review all network service rules. Remove overly permissive ANY/wildcard entries.",
    },
    {
        "rule_id": "ISO-RE-A8-005",
        "control_ref": "A.8.22",
        "name": "Segregation of Networks",
        "description": "Verify that network segmentation / deny rules are implemented.",
        "domain": "Technological Controls",
        "severity": "high",
        "eval_type": "boolean",
        "eval_config": {
            "signal": "has_deny_rules",
            "expected": True,
        },
        "remediation": "Implement default-deny network policy. Segment networks by sensitivity and business function.",
    },
    {
        "rule_id": "ISO-RE-A8-006",
        "control_ref": "A.8.24",
        "name": "Use of Cryptography",
        "description": "Verify that cryptographic controls (encryption, key management) are in place.",
        "domain": "Technological Controls",
        "severity": "high",
        "eval_type": "evidence_keyword",
        "eval_config": {
            "keywords": ["encryption", "cryptography", "tls", "ssl", "key management"],
            "evidence_sources": ["network_rules", "governance"],
            "match_mode": "any",
        },
        "remediation": "Define a cryptography policy. Ensure encryption in transit and at rest for sensitive data.",
    },
    {
        "rule_id": "ISO-RE-A8-007",
        "control_ref": "A.8.16",
        "name": "Monitoring Activities",
        "description": "Verify that security monitoring and log review processes exist.",
        "domain": "Technological Controls",
        "severity": "high",
        "eval_type": "boolean",
        "eval_config": {
            "signal": "has_governance_activities",
            "expected": True,
        },
        "remediation": "Implement SIEM or log management. Establish regular log review processes.",
    },
]
