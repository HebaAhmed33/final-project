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
    # ── applications must come before assets ──────────────────────────────
    "applications": {
        "name_keywords": ["application", "app", "systems inventory", "applications inventory",
                          "software inventory", "system"],
        "column_aliases": {
            "app_name":      ["application", "app_name", "app name", "name", "system",
                              "system_name", "system name", "software", "title"],
            "app_type":      ["type", "app_type", "app type", "category", "classification"],
            "vendor":        ["vendor", "provider", "supplier", "developer", "manufacturer"],
            "version":       ["version", "ver", "release"],
            "owner":         ["owner", "app_owner", "app owner", "custodian", "responsible",
                              "business_owner", "business owner"],
            "criticality":   ["criticality", "critical", "importance", "priority",
                              "risk_level", "risk level"],
            # Bug 4 fix: "processes sensitive data" alias explicitly listed
            "data_handled":  ["data_handled", "data handled", "data_type", "data type",
                              "data_classification", "data classification", "sensitive_data",
                              "pii", "processes sensitive data", "processes_sensitive_data"],
            "hosting":       ["hosting", "deployment", "environment", "hosted", "cloud",
                              "on_prem", "on prem", "infrastructure"],
            "status":        ["status", "state", "active", "condition"],
            "notes":         ["notes", "comments", "remarks", "description"],
        },
    },
    # ── vendors must come before assets ───────────────────────────────────
    "vendors": {
        # Bug 1 fix: "vendor-managed" and "vendor managed" keywords added
        "name_keywords": ["vendor", "supplier", "third party", "third_party", "outsourc",
                          "managed service", "vendor-managed", "vendor managed",
                          "partner", "services inventory"],
        "column_aliases": {
            "vendor_name":  ["vendor", "vendor_name", "vendor name", "name", "supplier",
                             "company", "partner", "provider", "service_provider"],
            # Keep "service" alias so raw columns named "Service" normalise correctly
            "service_type": ["service", "service_type", "service type", "category",
                             "type", "scope", "engagement"],
            "risk_level":   ["risk", "risk_level", "risk level", "risk_rating",
                             "risk rating", "vendor_risk", "criticality", "priority"],
            "contract_status": ["contract", "contract_status", "contract status",
                                "agreement", "status", "state", "active"],
            "data_access":  ["data_access", "data access", "access_level", "access level",
                             "data_shared", "data shared", "data_handling"],
            "compliance":   ["compliance", "compliant", "certified", "certification",
                             "audit_status", "audit status", "soc2", "iso",
                             "compliance_status", "compliance status"],
            "owner":        ["owner", "manager", "responsible", "contact",
                             "relationship_manager", "relationship manager"],
            "sla":          ["sla", "service_level", "service level", "availability", "uptime"],
            "notes":        ["notes", "comments", "remarks", "description", "details"],
        },
    },
    # ── assets (generic hardware/device inventory) ─────────────────────────
    "assets": {
        # Bug 1 fix: removed generic "inventory" keyword; asset sheets must say
        # "asset", "hardware", "device", or "endpoint" — NOT just "inventory".
        "name_keywords": ["asset", "hardware", "device", "endpoint"],
        "column_aliases": {
            "asset_name":   ["asset_name", "asset name", "name", "device", "hostname",
                             "device_name", "device name", "host"],
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
            "department":   ["department", "dept", "business_unit", "business unit", "division"],
            "notes":        ["notes", "comments", "remarks", "description", "details"],
        },
    },
    "controls": {
        # Bug 3 fix: "configurations" keyword added so a sheet literally named
        # "Configurations" is routed as controls, not left as "unknown".
        "name_keywords": ["control", "standard", "framework", "compliance", "policy",
                          "policies", "procedure", "configuration", "configurations"],
        "column_aliases": {
            "control_id":   ["control_id", "controlid", "control id", "id", "rule_id",
                             "ruleid", "rule id", "ref", "reference", "control_number",
                             "control number", "no", "number", "code", "control code", "clause"],
            "control_name": ["control_name", "controlname", "control name", "name",
                             "policy_name", "policyname", "policy name", "policy",
                             "control_title", "control title", "title", "requirement",
                             "description", "item", "security control", "measure"],
            "status":       ["status", "state", "compliance_status", "compliance status",
                             "result", "outcome", "finding", "assessment_status",
                             "assessment status", "control_status", "control status",
                             "implementation", "implemented", "compliance"],
            "owner":        ["owner", "responsible", "assigned_to", "assigned to",
                             "assignee", "control_owner", "control owner", "manager",
                             "department"],
            "severity":     ["severity", "priority", "risk_level", "risk level",
                             "criticality", "impact", "risk"],
            "evidence":     ["evidence", "evidence_ref", "evidence ref", "proof",
                             "attachment", "document", "required_evidence",
                             "reference", "artifact"],
            "domain":       ["domain", "category", "section", "group", "area",
                             "clause", "annex"],
            "due_date":     ["due_date", "duedate", "due date", "deadline",
                             "target_date", "target date", "completion_date", "date"],
            "notes":        ["notes", "note", "comment", "comments", "remarks",
                             "remark", "observation", "details"],
        },
    },
    "network_rules": {
        "name_keywords": ["rule", "firewall", "inbound", "outbound", "acl",
                          "network rule", "security rule", "port"],
        "column_aliases": {
            "rule_name":    ["rule", "rule_name", "rule name", "name",
                             "description", "title", "acl"],
            "direction":    ["direction", "type", "flow", "traffic",
                             "inbound", "outbound", "in_out"],
            "source":       ["source", "src", "source_ip", "source ip", "from", "origin"],
            "destination":  ["destination", "dest", "dst", "destination_ip",
                             "destination ip", "to", "target"],
            "port":         ["port", "ports", "port_number", "port number",
                             "service_port", "dst_port", "destination_port"],
            "protocol":     ["protocol", "proto", "service", "tcp", "udp"],
            "action":       ["action", "permit", "deny", "allow", "block",
                             "decision", "result", "status"],
            "status":       ["status", "state", "enabled", "active"],
            "notes":        ["notes", "comments", "remarks", "description", "justification"],
        },
    },
    "risk_register": {
        "name_keywords": ["risk", "heatmap", "heat map", "threat", "vulnerability"],
        "column_aliases": {
            "risk_name":    ["risk", "risk_name", "risk name", "name", "title",
                             "threat", "description", "risk_description"],
            "risk_id":      ["risk_id", "risk id", "id", "ref", "reference",
                             "number", "code"],
            "category":     ["category", "type", "domain", "area", "classification"],
            "likelihood":   ["likelihood", "probability", "chance",
                             "frequency", "occurrence"],
            "impact":       ["impact", "consequence", "severity", "damage", "effect"],
            "risk_level":   ["risk_level", "risk level", "level", "rating", "score",
                             "risk_rating", "risk rating", "risk_score"],
            "owner":        ["owner", "responsible", "assigned", "manager",
                             "risk_owner", "risk owner", "mitigator"],
            "mitigation":   ["mitigation", "treatment", "action", "control",
                             "response", "remediation", "countermeasure", "plan"],
            "status":       ["status", "state", "progress", "current_status"],
            "notes":        ["notes", "comments", "remarks", "details"],
        },
    },
    "governance": {
        "name_keywords": ["governance", "activity", "audit", "review",
                          "meeting", "committee"],
        "column_aliases": {
            "activity":       ["activity", "name", "title", "description",
                               "event", "meeting", "review", "audit"],
            "activity_type":  ["type", "activity_type", "activity type",
                               "category", "classification"],
            "responsible":    ["responsible", "owner", "lead", "chairperson",
                               "manager", "organizer", "assigned"],
            "frequency":      ["frequency", "schedule", "interval",
                               "recurrence", "cadence", "period"],
            "last_performed": ["last_performed", "last performed", "last_date",
                               "last date", "last_review", "last review",
                               "completed_date", "date"],
            "next_due":       ["next_due", "next due", "next_date", "next date",
                               "due_date", "due date", "upcoming", "deadline"],
            "status":         ["status", "state", "result", "outcome",
                               "finding", "completion"],
            "notes":          ["notes", "comments", "remarks", "details",
                               "minutes", "action_items"],
        },
    },
    "employees": {
        "name_keywords": ["employee", "staff", "personnel", "people",
                          "user", "team member", "hr"],
        "column_aliases": {
            "name":         ["name", "employee_name", "employee name", "full_name",
                             "full name", "staff_name", "person"],
            "role":         ["role", "title", "job_title", "job title",
                             "position", "designation"],
            "department":   ["department", "dept", "team", "division",
                             "business_unit", "business unit", "unit", "group"],
            "email":        ["email", "e_mail", "e-mail", "email_address", "mail"],
            # Bug 4 fix: "privileged access" alias explicitly listed (multi-word, lowercased)
            "access_level": ["access_level", "access level", "access", "clearance",
                             "permission", "privilege", "role_level",
                             "privileged_access", "privileged access"],
            "manager":      ["manager", "supervisor", "reports_to",
                             "reports to", "line_manager"],
            # Bug 4 fix: "security training status" alias explicitly listed (multi-word, lowercased)
            "training":     ["training", "awareness", "certified", "training_status",
                             "training status", "security_training", "last_training",
                             "security training status", "security_training_status"],
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
    """Lowercase, strip, collapse whitespace/underscores."""
    return re.sub(r"[\s_-]+", " ", text.strip().lower())


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


def classify_sheet(sheet_name: str, headers: list[str]) -> str:
    """
    Classify a sheet using name first, then headers as fallback.
    Returns 'unknown' if neither method matches.
    """
    by_name = classify_sheet_by_name(sheet_name)
    if by_name:
        return by_name
    by_headers = classify_sheet_by_headers(headers)
    return by_headers or "unknown"


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
        canonical = reverse.get(cleaned, cleaned.replace(" ", "_"))
        result.append(canonical)
    return result
