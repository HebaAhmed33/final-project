"""
Header Normalization Service.

Maps messy, inconsistent Excel column headers to canonical field names.
Supports multiple aliases per canonical field and handles:
- case differences
- spaces, underscores, hyphens
- common naming variations (policy_name → control_name, etc.)

Usage:
    canonical = normalize_header("Policy Name")  # → "control_name"
"""

# ---------------------------------------------------------------------------
# Alias registry  (canonical_field → list of aliases)
# ---------------------------------------------------------------------------

_ALIAS_MAP: dict[str, list[str]] = {
    "control_id": [
        "control_id", "controlid", "control id", "id", "rule_id", "ruleid",
        "rule id", "control_ref", "ref", "reference", "control_number",
        "control number", "ctrl_id", "ctrl id", "no", "number", "code", "control code",
    ],
    "control_name": [
        "control_name", "controlname", "control name", "name",
        "policy_name", "policyname", "policy name", "policy",
        "control_title", "control title", "title", "requirement",
        "control_description", "description", "policy title", "item", "security control",
    ],
    "status": [
        "status", "state", "compliance_status", "compliance status",
        "result", "outcome", "finding", "assessment_status",
        "assessment status", "control_status", "control status", "value", "compliance",
    ],
    "owner": [
        "owner", "responsible", "assigned_to", "assigned to",
        "assignee", "control_owner", "control owner", "manager",
        "department", "team",
    ],
    "due_date": [
        "due_date", "duedate", "due date", "deadline", "target_date",
        "target date", "completion_date", "completion date",
        "expected_date", "expected date", "date",
    ],
    "notes": [
        "notes", "note", "comment", "comments", "remarks", "remark",
        "observation", "observations", "detail", "details",
        "additional_info", "additional info",
    ],
    "severity": [
        "severity", "priority", "risk_level", "risk level",
        "criticality", "impact", "risk",
    ],
    "evidence": [
        "evidence", "evidence_ref", "evidence ref", "proof",
        "attachment", "document", "required_evidence",
    ],
}

# Build the reverse lookup once at import time
_REVERSE_LOOKUP: dict[str, str] = {}
for canonical, aliases in _ALIAS_MAP.items():
    for alias in aliases:
        _REVERSE_LOOKUP[alias] = canonical


def normalize_header(raw_header: str) -> str:
    """
    Map a raw Excel column header to its canonical field name.

    Returns the original (cleaned) header if no alias match is found,
    so unknown columns are preserved rather than dropped.
    """
    if not raw_header:
        return ""
    cleaned = raw_header.strip().lower().replace("-", "_").replace(" ", "_")
    # Remove double underscores
    while "__" in cleaned:
        cleaned = cleaned.replace("__", "_")
    cleaned = cleaned.strip("_")

    return _REVERSE_LOOKUP.get(cleaned, cleaned)


def normalize_headers(raw_headers: list) -> list[str]:
    """
    Normalize an entire row of Excel headers.

    Returns a list of canonical field names.
    """
    return [normalize_header(str(h) if h is not None else "") for h in raw_headers]


def get_canonical_fields() -> list[str]:
    """Return the list of all canonical field names."""
    return list(_ALIAS_MAP.keys())
