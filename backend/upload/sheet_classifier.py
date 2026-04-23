"""
Sheet Classifier & Multi-Sheet Data Normalizer.

Detects sheet types from Excel workbooks by analyzing sheet names and column
headers.  Each sheet type has a canonical column schema so downstream analysis
modules receive uniform data regardless of how the original Excel was authored.
"""

from __future__ import annotations

import re
from typing import Optional

# ---------------------------------------------------------------------------
# Sheet-type definitions
# ---------------------------------------------------------------------------
# Each type maps:
#   name_keywords  – substrings matched (case-insensitive) against sheet name
#   column_aliases – {canonical_field: [alias, …]}  for column normalization

# ---------------------------------------------------------------------------
# Sheet-type priority for name-based classification.
# More-specific types must appear BEFORE broader ones so that sheet names like
# "Applications Systems Inventory" or "Vendor-Managed Services Inventory" are
# matched by the correct type BEFORE the generic "asset" keyword fires.
# ---------------------------------------------------------------------------

SHEET_TYPES: dict[str, dict] = {
    # ── organization profile — must come first (very specific) ────────────
    "organization_profile": {
        "name_keywords": ["organization profile", "organisation profile",
                          "company profile", "company info", "company information",
                          "org profile", "org info", "organization info",
                          "organisation info", "about", "overview", "general info",
                          "general information", "entity profile", "business profile"],
        "column_aliases": {
            "field":    ["field", "item", "attribute", "parameter", "property",
                         "category", "label", "key", "name", "description", "topic"],
            "value":    ["value", "detail", "details", "answer", "response",
                         "data", "info", "information", "entry", "content", "result"],
            "notes":    ["notes", "comments", "remarks", "additional"],
        },
    },
    # ── applications must come before assets ──────────────────────────────
    "applications": {
        "name_keywords": ["application", "app", "systems inventory", "applications inventory",
                          "software inventory", "system", "applications systems"],
        "column_aliases": {
            "app_name":      ["application", "app_name", "app name", "name", "system",
                              "system_name", "system name", "software", "title",
                              "application name", "application system"],
            "app_type":      ["type", "app_type", "app type", "category", "classification"],
            "vendor":        ["vendor", "provider", "supplier", "developer", "manufacturer"],
            "version":       ["version", "ver", "release"],
            "owner":         ["owner", "app_owner", "app owner", "custodian", "responsible",
                              "business_owner", "business owner"],
            "criticality":   ["criticality", "critical", "importance", "priority",
                              "risk_level", "risk level"],
            "data_handled":  ["data_handled", "data handled", "data_type", "data type",
                              "data_classification", "data classification", "sensitive_data",
                              "pii", "processes sensitive data", "processes_sensitive_data",
                              "data sensitivity"],
            "hosting":       ["hosting", "deployment", "environment", "hosted", "cloud",
                              "on_prem", "on prem", "infrastructure", "hosting model"],
            "status":        ["status", "state", "active", "condition"],
            "notes":         ["notes", "comments", "remarks", "description"],
        },
    },
    # ── vendors must come before assets ───────────────────────────────────
    "vendors": {
        "name_keywords": ["vendor", "supplier", "third party", "third_party", "outsourc",
                          "managed service", "vendor-managed", "vendor managed",
                          "partner", "services inventory"],
        "column_aliases": {
            "vendor_name":  ["vendor", "vendor_name", "vendor name", "name", "supplier",
                             "company", "partner", "provider", "service_provider",
                             "service provider", "third party"],
            "service_type": ["service", "service_type", "service type", "category",
                             "type", "scope", "engagement", "service provided",
                             "services provided"],
            "risk_level":   ["risk", "risk_level", "risk level", "risk_rating",
                             "risk rating", "vendor_risk", "criticality", "priority"],
            "contract_status": ["contract", "contract_status", "contract status",
                                "agreement", "status", "state", "active",
                                "contract type"],
            "data_access":  ["data_access", "data access", "access_level", "access level",
                             "data_shared", "data shared", "data_handling",
                             "data sensitivity", "data handled"],
            "compliance":   ["compliance", "compliant", "certified", "certification",
                             "audit_status", "audit status", "soc2", "iso",
                             "compliance_status", "compliance status",
                             "certifications"],
            "owner":        ["owner", "manager", "responsible", "contact",
                             "relationship_manager", "relationship manager",
                             "account manager"],
            "sla":          ["sla", "service_level", "service level", "availability",
                             "uptime"],
            "notes":        ["notes", "comments", "remarks", "description", "details"],
        },
    },
    # ── assets (generic hardware/device inventory) ─────────────────────────
    "assets": {
        "name_keywords": ["asset", "hardware", "device", "endpoint",
                          "asset inventory"],
        "column_aliases": {
            "asset_name":   ["asset_name", "asset name", "name", "device", "hostname",
                             "device_name", "device name", "host", "asset",
                             "equipment", "equipment name"],
            "asset_type":   ["type", "asset_type", "asset type", "category",
                             "device_type", "device type", "classification"],
            "owner":        ["owner", "asset_owner", "asset owner", "custodian",
                             "responsible", "assigned_to", "assigned to", "manager"],
            "criticality":  ["criticality", "critical", "importance", "risk_level",
                             "risk level", "priority", "classification", "sensitivity"],
            "location":     ["location", "site", "region", "datacenter",
                             "data_center", "office", "branch"],
            "ip_address":   ["ip", "ip_address", "ip address", "ipv4", "address"],
            "os":           ["os", "operating_system", "operating system", "platform"],
            "status":       ["status", "state", "condition", "active"],
            "department":   ["department", "dept", "business_unit", "business unit",
                             "division"],
            "notes":        ["notes", "comments", "remarks", "description", "details"],
        },
    },
    "controls": {
        "name_keywords": ["control", "standard", "framework", "compliance",
                          "procedure",
                          "security controls", "isms controls", "control register",
                          "controls register", "controls list", "control list",
                          "requirements"],
        "column_aliases": {
            "control_id":   ["control_id", "controlid", "control id", "id", "rule_id",
                             "ruleid", "rule id", "ref", "reference", "control_number",
                             "control number", "no", "number", "code", "control code",
                             "clause", "control identifier", "identifier",
                             "requirement id", "req id", "section"],
            "control_name": ["control_name", "controlname", "control name", "name",
                             "policy_name", "policyname", "policy name", "policy",
                             "control_title", "control title", "title", "requirement",
                             "description", "item", "security control", "measure",
                             "control description", "requirement name", "objective",
                             "control objective", "document name"],
            "status":       ["status", "state", "compliance_status", "compliance status",
                             "result", "outcome", "finding", "assessment_status",
                             "assessment status", "control_status", "control status",
                             "implementation", "implemented", "compliance",
                             "implementation status", "implementation_status"],
            "owner":        ["owner", "responsible", "assigned_to", "assigned to",
                             "assignee", "control_owner", "control owner", "manager",
                             "department", "responsible party"],
            "severity":     ["severity", "priority", "risk_level", "risk level",
                             "criticality", "impact", "risk", "importance"],
            "evidence":     ["evidence", "evidence_ref", "evidence ref", "proof",
                             "attachment", "document", "required_evidence",
                             "reference", "artifact", "evidence reference",
                             "supporting document"],
            "domain":       ["domain", "category", "section", "group", "area",
                             "clause", "annex", "control domain"],
            "due_date":     ["due_date", "duedate", "due date", "deadline",
                             "target_date", "target date", "completion_date", "date"],
            "notes":        ["notes", "note", "comment", "comments", "remarks",
                             "remark", "observation", "details"],
        },
    },
    "network_rules": {
        "name_keywords": ["rule", "firewall", "inbound", "outbound", "acl",
                          "network rule", "security rule", "port",
                          "inbound and outbound", "network"],
        "column_aliases": {
            "rule_name":    ["rule", "rule_name", "rule name", "name",
                             "description", "title", "acl", "rule description"],
            "direction":    ["direction", "type", "flow", "traffic",
                             "inbound", "outbound", "in_out", "in out"],
            "source":       ["source", "src", "source_ip", "source ip", "from", "origin",
                             "source address"],
            "destination":  ["destination", "dest", "dst", "destination_ip",
                             "destination ip", "to", "target", "destination address"],
            "port":         ["port", "ports", "port_number", "port number",
                             "service_port", "dst_port", "destination_port",
                             "port range"],
            "protocol":     ["protocol", "proto", "service", "tcp", "udp"],
            "action":       ["action", "permit", "deny", "allow", "block",
                             "decision", "result", "status", "rule action"],
            "status":       ["status", "state", "enabled", "active"],
            "notes":        ["notes", "comments", "remarks", "description",
                             "justification", "reason"],
        },
    },
    "risk_register": {
        "name_keywords": ["risk", "heatmap", "heat map", "threat", "vulnerability",
                          "risk register", "risk heatmap", "risk assessment",
                          "risk matrix"],
        "column_aliases": {
            "risk_name":    ["risk", "risk_name", "risk name", "name", "title",
                             "threat", "description", "risk_description",
                             "risk description", "vulnerability"],
            "risk_id":      ["risk_id", "risk id", "id", "ref", "reference",
                             "number", "code", "risk number"],
            "category":     ["category", "type", "domain", "area", "classification",
                             "risk category", "risk type"],
            "likelihood":   ["likelihood", "probability", "chance",
                             "frequency", "occurrence"],
            "impact":       ["impact", "consequence", "severity", "damage", "effect"],
            "risk_level":   ["risk_level", "risk level", "level", "rating", "score",
                             "risk_rating", "risk rating", "risk_score",
                             "risk score", "overall risk"],
            "owner":        ["owner", "responsible", "assigned", "manager",
                             "risk_owner", "risk owner", "mitigator"],
            "mitigation":   ["mitigation", "treatment", "action", "control",
                             "response", "remediation", "countermeasure", "plan",
                             "treatment plan", "mitigation plan"],
            "status":       ["status", "state", "progress", "current_status",
                             "current status", "risk status"],
            "notes":        ["notes", "comments", "remarks", "details"],
        },
    },
    "governance": {
        "name_keywords": ["governance", "activity", "audit", "review",
                          "meeting", "committee", "governance activity"],
        "column_aliases": {
            "activity":       ["activity", "name", "title", "description",
                               "event", "meeting", "review", "audit",
                               "activity name", "activity description"],
            "activity_type":  ["type", "activity_type", "activity type",
                               "category", "classification"],
            "responsible":    ["responsible", "owner", "lead", "chairperson",
                               "manager", "organizer", "assigned",
                               "responsible party"],
            "frequency":      ["frequency", "schedule", "interval",
                               "recurrence", "cadence", "period"],
            "last_performed": ["last_performed", "last performed", "last_date",
                               "last date", "last_review", "last review",
                               "completed_date", "date", "last performed date"],
            "next_due":       ["next_due", "next due", "next_date", "next date",
                               "due_date", "due date", "upcoming", "deadline",
                               "next due date"],
            "status":         ["status", "state", "result", "outcome",
                               "finding", "completion", "completion status"],
            "notes":          ["notes", "comments", "remarks", "details",
                               "minutes", "action_items", "action items"],
        },
    },
    "employees": {
        "name_keywords": ["employee", "staff", "personnel", "people",
                          "user", "team member", "hr", "workforce",
                          "human resource"],
        "column_aliases": {
            "name":         ["name", "employee_name", "employee name", "full_name",
                             "full name", "staff_name", "person", "employee"],
            "role":         ["role", "title", "job_title", "job title",
                             "position", "designation", "job role"],
            "department":   ["department", "dept", "team", "division",
                             "business_unit", "business unit", "unit", "group"],
            "email":        ["email", "e_mail", "e-mail", "email_address", "mail",
                             "email address"],
            "access_level": ["access_level", "access level", "access", "clearance",
                             "permission", "privilege", "role_level",
                             "privileged_access", "privileged access",
                             "access rights"],
            "manager":      ["manager", "supervisor", "reports_to",
                             "reports to", "line_manager", "line manager"],
            "training":     ["training", "awareness", "certified", "training_status",
                             "training status", "security_training", "last_training",
                             "security training status", "security_training_status",
                             "training completed", "awareness training"],
            "status":       ["status", "state", "active",
                             "employment_status", "employment status"],
            "notes":        ["notes", "comments", "remarks", "details"],
        },
    },
}

# Flat reverse lookup built at import time
_SHEET_NAME_INDEX: list[tuple[str, list[str]]] = [
    (sheet_type, info["name_keywords"])
    for sheet_type, info in SHEET_TYPES.items()
]


# ---------------------------------------------------------------------------
# Classification helpers
# ---------------------------------------------------------------------------

def _clean(text: str) -> str:
    """Lowercase, strip, collapse whitespace/underscores/hyphens/dots."""
    return re.sub(r"[\s_\-\.]+", " ", text.strip().lower())


def classify_sheet_by_name(sheet_name: str) -> Optional[str]:
    """
    Classify a sheet by its name.  Returns the sheet type string or None.
    """
    cleaned = _clean(sheet_name)
    for sheet_type, keywords in _SHEET_NAME_INDEX:
        for kw in keywords:
            if kw in cleaned:
                return sheet_type
    return None


def classify_sheet_by_headers(headers: list[str]) -> Optional[str]:
    """
    Classify a sheet by examining its column headers.
    Returns the type with the most alias matches, or None if ambiguous.
    """
    cleaned_headers = [_clean(str(h)) for h in headers if h]

    best_type: Optional[str] = None
    best_score = 0

    for sheet_type, info in SHEET_TYPES.items():
        score = 0
        aliases = info["column_aliases"]
        for canonical, alias_list in aliases.items():
            for alias in alias_list:
                if alias in cleaned_headers:
                    score += 1
                    break  # count each canonical field once
        if score > best_score:
            best_score = score
            best_type = sheet_type

    # Need at least 2 matching canonical fields to classify
    return best_type if best_score >= 2 else None


def classify_sheet_by_data_heuristic(headers: list[str], sample_rows: list) -> Optional[str]:
    """
    Classify a sheet by examining sample data values when name and header
    matching both fail. Uses heuristics like:
    - presence of IP addresses → assets or network_rules
    - presence of email addresses → employees
    - presence of risk/likelihood words → risk_register
    """
    if not sample_rows:
        return None

    all_values = []
    for row in sample_rows[:10]:  # sample first 10 rows
        for cell in row:
            if cell is not None:
                all_values.append(str(cell).lower().strip())

    joined = " ".join(all_values)

    # Check for IP patterns → assets or network rules
    ip_pattern = re.compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
    has_ips = bool(ip_pattern.search(joined))

    # Check for email patterns → employees
    email_pattern = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
    has_emails = bool(email_pattern.search(joined))

    # Check for risk keywords → risk_register
    risk_keywords = {"high", "medium", "low", "critical", "likelihood", "impact",
                     "probability", "risk", "threat", "vulnerability"}
    risk_count = sum(1 for kw in risk_keywords if kw in joined)

    # Check for compliance keywords → controls
    compliance_keywords = {"compliant", "non-compliant", "partial", "implemented",
                          "not implemented", "in progress", "pass", "fail"}
    compliance_count = sum(1 for kw in compliance_keywords if kw in joined)

    # Check for governance keywords
    governance_keywords = {"annual", "quarterly", "monthly", "weekly",
                          "review", "audit", "meeting", "committee"}
    governance_count = sum(1 for kw in governance_keywords if kw in joined)

    if compliance_count >= 3:
        return "controls"
    if risk_count >= 3:
        return "risk_register"
    if has_emails and len(headers) >= 3:
        return "employees"
    if has_ips:
        # Check if it looks more like network rules or assets
        network_words = {"allow", "deny", "permit", "block", "tcp", "udp",
                        "inbound", "outbound", "port"}
        if any(w in joined for w in network_words):
            return "network_rules"
        return "assets"
    if governance_count >= 2:
        return "governance"

    return None


def classify_sheet(sheet_name: str, headers: list[str],
                   sample_rows: list = None) -> str:
    """
    Classify a sheet using name first, then headers, then data heuristic.
    Returns 'unknown' if no method matches.
    """
    by_name = classify_sheet_by_name(sheet_name)
    if by_name:
        return by_name
    by_headers = classify_sheet_by_headers(headers)
    if by_headers:
        return by_headers
    if sample_rows:
        by_data = classify_sheet_by_data_heuristic(headers, sample_rows)
        if by_data:
            return by_data
    return "unknown"


# ---------------------------------------------------------------------------
# Column normalization per sheet type
# ---------------------------------------------------------------------------

def normalize_columns_for_type(
    headers: list,
    sheet_type: str,
) -> list[str]:
    """
    Normalize raw Excel headers using the alias map for the given sheet type.

    Returns canonical field names.  Unknown columns are preserved as-is
    (lowercased, cleaned).
    """
    aliases = SHEET_TYPES.get(sheet_type, {}).get("column_aliases", {})

    # Build reverse lookup for this type
    reverse: dict[str, str] = {}
    for canonical, alias_list in aliases.items():
        for alias in alias_list:
            reverse[alias] = canonical

    result: list[str] = []
    for raw in headers:
        cleaned = _clean(str(raw)) if raw else ""
        canonical = reverse.get(cleaned)
        if canonical:
            result.append(canonical)
        else:
            # Try fuzzy: check if any alias is a substring of the header
            matched = False
            for alias, can in reverse.items():
                if len(alias) >= 4 and alias in cleaned:
                    result.append(can)
                    matched = True
                    break
            if not matched:
                result.append(cleaned.replace(" ", "_") if cleaned else "")
    return result
