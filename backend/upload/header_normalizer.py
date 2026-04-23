"""
Header Normalization Service.

Maps messy, inconsistent Excel column headers to canonical field names.
Supports multiple aliases per canonical field and handles:
- case differences
- spaces, underscores, hyphens, dots, periods
- common naming variations (policy_name → control_name, etc.)
- singular/plural variations
- fuzzy substring matching as a fallback

Usage:
    canonical = normalize_header("Policy Name")  # → "control_name"
"""

import re

# ---------------------------------------------------------------------------
# Alias registry  (canonical_field → list of aliases)
# ---------------------------------------------------------------------------

_ALIAS_MAP: dict[str, list[str]] = {
    "control_id": [
        "control_id", "controlid", "control id", "id", "rule_id", "ruleid",
        "rule id", "control_ref", "ref", "reference", "control_number",
        "control number", "ctrl_id", "ctrl id", "no", "number", "code",
        "control code", "control identifier", "identifier", "clause",
        "annex", "section id", "requirement id", "req id",
    ],
    "control_name": [
        "control_name", "controlname", "control name", "name",
        "policy_name", "policyname", "policy name", "policy",
        "control_title", "control title", "title", "requirement",
        "control_description", "description", "policy title", "item",
        "security control", "requirement name", "measure", "control description",
        "objective", "control objective",
    ],
    "status": [
        "status", "state", "compliance_status", "compliance status",
        "result", "outcome", "finding", "assessment_status",
        "assessment status", "control_status", "control status", "value",
        "compliance", "implementation status", "implementation_status",
        "implemented", "implementation", "compliant",
    ],
    "owner": [
        "owner", "responsible", "assigned_to", "assigned to",
        "assignee", "control_owner", "control owner", "manager",
        "department", "team", "responsible party", "accountability",
    ],
    "due_date": [
        "due_date", "duedate", "due date", "deadline", "target_date",
        "target date", "completion_date", "completion date",
        "expected_date", "expected date", "date",
    ],
    "notes": [
        "notes", "note", "comment", "comments", "remarks", "remark",
        "observation", "observations", "detail", "details",
        "additional_info", "additional info", "additional information",
    ],
    "severity": [
        "severity", "priority", "risk_level", "risk level",
        "criticality", "impact", "risk", "importance",
    ],
    "evidence": [
        "evidence", "evidence_ref", "evidence ref", "proof",
        "attachment", "document", "required_evidence",
        "evidence reference", "artifact", "supporting document",
    ],
    "framework": [
        "framework", "standard", "reference framework", "reference_framework",
        "regulation", "standard name", "standard_name",
    ],
    "domain": [
        "domain", "category", "section", "group", "area",
        "clause", "annex", "control domain", "control_domain",
    ],
    "last_tested": [
        "last_tested", "last tested", "last_review", "last review",
        "test_date", "test date", "last_audit", "last audit",
        "review_date", "review date", "last_assessment",
    ],
}

# Build the reverse lookup once at import time
_REVERSE_LOOKUP: dict[str, str] = {}
for canonical, aliases in _ALIAS_MAP.items():
    for alias in aliases:
        _REVERSE_LOOKUP[alias] = canonical


def _clean_header(raw: str) -> str:
    """
    Aggressively clean a raw header string for matching.

    Strips whitespace, lowercases, removes dots/periods/underscores/hyphens,
    collapses multiple spaces, and handles common suffixes.
    """
    if not raw:
        return ""
    cleaned = raw.strip().lower()
    # Remove dots, periods
    cleaned = cleaned.replace(".", " ")
    # Replace hyphens, underscores with spaces
    cleaned = cleaned.replace("-", " ").replace("_", " ")
    # Collapse multiple spaces
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def normalize_header(raw_header: str) -> str:
    """
    Map a raw Excel column header to its canonical field name.

    Strategy:
      1. Clean and try exact alias match
      2. Try with underscores instead of spaces
      3. Try fuzzy substring match (header contains alias or alias contains header)
      4. Return the cleaned header if no match found (preserves unknown columns)
    """
    if not raw_header:
        return ""

    cleaned = _clean_header(raw_header)
    if not cleaned:
        return ""

    # 1. Exact match on cleaned form
    if cleaned in _REVERSE_LOOKUP:
        return _REVERSE_LOOKUP[cleaned]

    # 2. Try with underscores (some aliases use underscores)
    underscored = cleaned.replace(" ", "_")
    if underscored in _REVERSE_LOOKUP:
        return _REVERSE_LOOKUP[underscored]

    # 3. Try removing plural 's' at the end
    if cleaned.endswith("s") and len(cleaned) > 3:
        singular = cleaned[:-1]
        if singular in _REVERSE_LOOKUP:
            return _REVERSE_LOOKUP[singular]

    # 4. Fuzzy substring match — if the header contains a known alias
    #    or a known alias contains the header (for short headers like "id")
    best_match = None
    best_len = 0
    for alias, canonical in _REVERSE_LOOKUP.items():
        if len(alias) >= 3 and alias in cleaned and len(alias) > best_len:
            best_match = canonical
            best_len = len(alias)

    if best_match:
        return best_match

    # Return cleaned + underscored form for unknown columns
    return underscored


def normalize_headers(raw_headers: list) -> list[str]:
    """
    Normalize an entire row of Excel headers.

    Returns a list of canonical field names.
    """
    return [normalize_header(str(h) if h is not None else "") for h in raw_headers]


def get_canonical_fields() -> list[str]:
    """Return the list of all canonical field names."""
    return list(_ALIAS_MAP.keys())
