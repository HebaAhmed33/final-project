"""
Sheet Router — routes each detected sheet to the correct analysis path.

Each analysis path:
  - Receives actual normalized row data for its sheet
  - Does basic extraction, counting, and flagging
  - Returns structured output with full traceability
  - Does NOT produce scores or framework-specific recommendations (Step 4)
"""

import uuid
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Analysis paths — one per sheet type
# ---------------------------------------------------------------------------

def _analyse_assets(rows: list[dict], sheet_name: str) -> dict:
    total = len(rows)
    by_criticality: dict[str, int] = {}
    unowned = 0

    for row in rows:
        crit = (row.get("criticality") or "unknown").strip().lower() or "unknown"
        by_criticality[crit] = by_criticality.get(crit, 0) + 1
        if not row.get("owner"):
            unowned += 1

    findings = []
    if total == 0:
        findings.append("Asset sheet is empty — no asset data available for analysis.")
    else:
        if unowned:
            findings.append(f"{unowned} of {total} assets have no assigned owner.")
        high = by_criticality.get("high", 0) + by_criticality.get("critical", 0)
        if high:
            findings.append(
                f"{high} high/critical assets detected — ensure access controls are applied."
            )

    return {
        "sheet_type": "assets",
        "sheet_name": sheet_name,
        "total_records": total,
        "by_criticality": by_criticality,
        "unowned_assets": unowned,
        "findings": findings,
    }


def _analyse_applications(rows: list[dict], sheet_name: str) -> dict:
    total = len(rows)
    by_criticality: dict[str, int] = {}
    unowned = 0
    stores_sensitive = 0

    for row in rows:
        crit = (row.get("criticality") or "unknown").strip().lower() or "unknown"
        by_criticality[crit] = by_criticality.get(crit, 0) + 1
        if not row.get("owner"):
            unowned += 1
        data = (row.get("data_handled") or "").lower()
        if any(k in data for k in ("pii", "phi", "sensitive", "confidential", "cardholder")):
            stores_sensitive += 1

    findings = []
    if total == 0:
        findings.append("Applications sheet is empty.")
    else:
        if unowned:
            findings.append(f"{unowned} applications have no assigned owner.")
        if stores_sensitive:
            findings.append(
                f"{stores_sensitive} applications handle sensitive/PII data — verify data protection controls."
            )

    return {
        "sheet_type": "applications",
        "sheet_name": sheet_name,
        "total_records": total,
        "by_criticality": by_criticality,
        "unowned_applications": unowned,
        "sensitive_data_apps": stores_sensitive,
        "findings": findings,
    }


def _analyse_vendors(rows: list[dict], sheet_name: str) -> dict:
    total = len(rows)
    by_risk: dict[str, int] = {}
    high_risk: list[str] = []
    no_compliance = 0

    for row in rows:
        risk = (row.get("risk_level") or "unknown").strip().lower() or "unknown"
        by_risk[risk] = by_risk.get(risk, 0) + 1
        if risk in ("high", "critical"):
            high_risk.append(row.get("vendor_name") or "Unknown Vendor")
        if not row.get("compliance"):
            no_compliance += 1

    findings = []
    if total == 0:
        findings.append("Vendor sheet is empty — no vendor data available.")
    else:
        if high_risk:
            findings.append(
                f"{len(high_risk)} high/critical-risk vendor(s): {', '.join(high_risk[:5])}."
            )
        if no_compliance:
            findings.append(
                f"{no_compliance} vendors have no compliance or certification recorded."
            )

    return {
        "sheet_type": "vendors",
        "sheet_name": sheet_name,
        "total_records": total,
        "by_risk": by_risk,
        "high_risk_vendors": high_risk,
        "no_compliance_count": no_compliance,
        "findings": findings,
    }


def _analyse_controls(rows: list[dict], sheet_name: str) -> dict:
    total = len(rows)

    # CRITICAL: if no rows, detect missing-controls state — do not inject fake data
    if total == 0:
        return {
            "sheet_type": "controls",
            "sheet_name": sheet_name,
            "total_records": 0,
            "no_controls_detected": True,
            "message": (
                "No existing controls implemented. "
                "Framework baseline will be generated in the next step."
            ),
            "by_status": {},
            "unowned_controls": 0,
            "findings": [
                "Controls sheet is present but contains no data — no implemented controls found."
            ],
        }

    by_status: dict[str, int] = {}
    unowned = 0

    for row in rows:
        raw_status = (row.get("status") or "unknown").strip().lower()
        # Normalize to canonical status values
        if raw_status in ("yes", "implemented", "compliant", "pass", "true", "1", "done", "complete"):
            status = "compliant"
        elif raw_status in ("no", "not implemented", "fail", "missing", "false", "0", "not done"):
            status = "missing"
        elif raw_status in ("partial", "in progress", "partially implemented", "ongoing"):
            status = "partial"
        else:
            status = raw_status or "unknown"

        by_status[status] = by_status.get(status, 0) + 1
        if not row.get("owner"):
            unowned += 1

    findings = []
    missing = by_status.get("missing", 0)
    partial = by_status.get("partial", 0)
    if missing:
        findings.append(f"{missing} controls are not implemented.")
    if partial:
        findings.append(f"{partial} controls are partially implemented.")
    if unowned:
        findings.append(f"{unowned} controls have no assigned owner.")

    return {
        "sheet_type": "controls",
        "sheet_name": sheet_name,
        "total_records": total,
        "no_controls_detected": False,
        "by_status": by_status,
        "unowned_controls": unowned,
        "findings": findings,
    }


def _analyse_risk_register(rows: list[dict], sheet_name: str) -> dict:
    total = len(rows)
    by_level: dict[str, int] = {}
    untreated: list[str] = []

    for row in rows:
        level = (
            row.get("risk_level") or row.get("level") or "unknown"
        ).strip().lower() or "unknown"
        by_level[level] = by_level.get(level, 0) + 1
        if not row.get("mitigation"):
            untreated.append(row.get("risk_name") or "Unnamed Risk")

    findings = []
    if total == 0:
        findings.append("Risk register sheet is empty.")
    else:
        high = by_level.get("high", 0) + by_level.get("critical", 0)
        if high:
            findings.append(f"{high} high/critical risks identified in risk register.")
        if untreated:
            findings.append(
                f"{len(untreated)} risks have no mitigation or treatment plan recorded."
            )

    return {
        "sheet_type": "risk_register",
        "sheet_name": sheet_name,
        "total_records": total,
        "by_level": by_level,
        "untreated_risks": untreated[:20],  # cap for payload size
        "findings": findings,
    }


def _analyse_network_rules(rows: list[dict], sheet_name: str) -> dict:
    total = len(rows)
    risky_rules: list[str] = []
    deny_count = 0

    _ANY_VALUES = {"any", "*", "0.0.0.0", "0.0.0.0/0", "all", "0"}

    for row in rows:
        action = (row.get("action") or "").strip().lower()
        source = (row.get("source") or "").strip().lower()
        dest = (row.get("destination") or "").strip().lower()
        port = (row.get("port") or "").strip().lower()
        name = row.get("rule_name") or "Unnamed Rule"

        if action in ("deny", "block", "drop"):
            deny_count += 1
        # Flag overly permissive allow rules
        elif source in _ANY_VALUES or dest in _ANY_VALUES or port in _ANY_VALUES:
            risky_rules.append(name)

    findings = []
    if total == 0:
        findings.append("Network rules sheet is empty.")
    else:
        if risky_rules:
            findings.append(
                f"{len(risky_rules)} rules use ANY/wildcard source, destination, or port — review required."
            )
        if deny_count == 0:
            findings.append(
                "No explicit deny rules found — default-allow posture may be in effect."
            )

    return {
        "sheet_type": "network_rules",
        "sheet_name": sheet_name,
        "total_records": total,
        "risky_rules_count": len(risky_rules),
        "risky_rules": risky_rules[:20],
        "deny_rules_count": deny_count,
        "findings": findings,
    }


def _analyse_governance(rows: list[dict], sheet_name: str) -> dict:
    total = len(rows)
    no_responsible = 0
    by_status: dict[str, int] = {}

    for row in rows:
        if not row.get("responsible"):
            no_responsible += 1
        status = (row.get("status") or "unknown").strip().lower() or "unknown"
        by_status[status] = by_status.get(status, 0) + 1

    findings = []
    if total == 0:
        findings.append("Governance activity sheet is empty.")
    else:
        if no_responsible:
            findings.append(
                f"{no_responsible} governance activities have no assigned responsible party."
            )
        pending = (
            by_status.get("pending", 0)
            + by_status.get("overdue", 0)
            + by_status.get("not done", 0)
            + by_status.get("incomplete", 0)
        )
        if pending:
            findings.append(f"{pending} governance activities are pending or overdue.")

    return {
        "sheet_type": "governance",
        "sheet_name": sheet_name,
        "total_records": total,
        "by_status": by_status,
        "no_responsible_count": no_responsible,
        "findings": findings,
        # Preserve raw rows so the governance calendar can be built from
        # routing data alone (all_sheets is not persisted to disk).
        "rows": rows,
    }


def _analyse_employees(rows: list[dict], sheet_name: str) -> dict:
    total = len(rows)
    no_training = 0
    privileged = 0

    for row in rows:
        training = (row.get("training") or "").strip().lower()
        if training in ("", "no", "none", "not completed", "false", "0"):
            no_training += 1
        access = (row.get("access_level") or "").strip().lower()
        if access in ("admin", "privileged", "superuser", "root", "full"):
            privileged += 1

    findings = []
    if total == 0:
        findings.append("Employee/personnel sheet is empty.")
    else:
        if no_training:
            findings.append(f"{no_training} employees have no recorded security training.")
        if privileged:
            findings.append(f"{privileged} employees have privileged/admin access — verify least-privilege.")

    return {
        "sheet_type": "employees",
        "sheet_name": sheet_name,
        "total_records": total,
        "no_security_training": no_training,
        "privileged_access_count": privileged,
        "findings": findings,
    }


def _analyse_unknown(rows: list[dict], sheet_name: str) -> dict:
    return {
        "sheet_type": "unknown",
        "sheet_name": sheet_name,
        "total_records": len(rows),
        "findings": [
            f"Sheet '{sheet_name}' could not be classified — {len(rows)} rows found. "
            "Data was preserved for reference."
        ],
        "rows": rows[:50],  # Preserve some raw data for potential manual review
    }


def _analyse_organization_profile(rows: list[dict], sheet_name: str) -> dict:
    """Analyse an organization profile / company info sheet."""
    total = len(rows)
    profile_data: dict[str, str] = {}

    for row in rows:
        field = (row.get("field") or row.get("name") or row.get("item") or "").strip()
        value = (row.get("value") or row.get("detail") or row.get("data") or "").strip()
        if field and value:
            profile_data[field] = value

    findings = []
    if total == 0:
        findings.append("Organization profile sheet is empty.")
    else:
        findings.append(
            f"Organization profile contains {len(profile_data)} data fields."
        )

    return {
        "sheet_type": "organization_profile",
        "sheet_name": sheet_name,
        "total_records": total,
        "profile_data": profile_data,
        "findings": findings,
    }



def _analyse_high_risk(rows: list[dict], sheet_name: str) -> dict:
    """Analyse a High-Risk mapping sheet — extract risks and ISO control references."""
    import re
    total = len(rows)
    parsed_risks: list[dict] = []

    for row in rows:
        rid = (row.get("risk_id") or "").strip()
        statement = (row.get("risk_statement") or "").strip()
        mapped_raw = (row.get("mapped_controls") or "").strip()
        rationale = (row.get("rationale") or "").strip()
        likelihood = (row.get("likelihood") or "").strip()
        impact = (row.get("impact") or "").strip()
        risk_level = (row.get("risk_level") or "").strip()

        # Parse ISO control references from comma/semicolon separated string
        # e.g. "A.5.17, A.8.16, A.8.24" or "A5.17; A8.16"
        iso_controls = []
        if mapped_raw:
            parts = re.split(r"[,;\n]+", mapped_raw)
            for part in parts:
                cleaned = part.strip()
                if cleaned:
                    # Normalize: "A5.17" -> "A.5.17", "ISO-A5.17-01" -> "A.5.17"
                    cleaned = cleaned.upper().replace("ISO-", "").replace("_", ".")
                    cleaned = re.sub(r"-\d+$", "", cleaned)
                    if re.match(r"A\.?\d+\.?\d+", cleaned):
                        # Ensure proper dot format
                        if "." not in cleaned:
                            m = re.match(r"([A-Z])(\d)(\d+)", cleaned)
                            if m:
                                cleaned = f"{m.group(1)}.{m.group(2)}.{m.group(3)}"
                        iso_controls.append(cleaned)

        if statement or iso_controls:
            parsed_risks.append({
                "risk_id": rid,
                "risk_statement": statement,
                "iso_controls": iso_controls,
                "rationale": rationale,
                "likelihood": likelihood,
                "impact": impact,
                "risk_level": risk_level,
            })

    # Expand to cross-framework mapping
    from services.cross_framework_map import map_risks_cross_framework
    enriched_risks = map_risks_cross_framework(parsed_risks)

    # Collect all unique ISO controls referenced
    all_iso_refs = sorted({c for r in parsed_risks for c in r.get("iso_controls", [])})

    findings = []
    if total == 0:
        findings.append("High-Risk sheet is empty.")
    else:
        findings.append(
            f"{len(parsed_risks)} high-priority risks identified, "
            f"referencing {len(all_iso_refs)} unique ISO controls."
        )
        covered_frameworks = set()
        for risk in enriched_risks:
            cov = risk.get("cross_framework_coverage", {})
            if cov.get("pci", 0) > 0: covered_frameworks.add("PCI DSS")
            if cov.get("hipaa", 0) > 0: covered_frameworks.add("HIPAA")
            if cov.get("nist", 0) > 0: covered_frameworks.add("NIST CSF")
            if cov.get("cis", 0) > 0: covered_frameworks.add("CIS")
        if covered_frameworks:
            findings.append(
                f"Cross-framework coverage extends to: {', '.join(sorted(covered_frameworks))}."
            )

    return {
        "sheet_type": "high_risk",
        "sheet_name": sheet_name,
        "total_records": total,
        "parsed_risks": enriched_risks,
        "all_iso_controls_referenced": all_iso_refs,
        "total_risks_parsed": len(parsed_risks),
        "findings": findings,
    }


# ---------------------------------------------------------------------------
# Dispatcher map
# ---------------------------------------------------------------------------

_ROUTE_MAP = {
    "assets":                _analyse_assets,
    "applications":          _analyse_applications,
    "vendors":               _analyse_vendors,
    "controls":              _analyse_controls,
    "risk_register":         _analyse_risk_register,
    "network_rules":         _analyse_network_rules,
    "governance":            _analyse_governance,
    "employees":             _analyse_employees,
    "organization_profile":  _analyse_organization_profile,
    "high_risk":             _analyse_high_risk,
}


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def route_sheets(sheets_with_rows: list[dict]) -> dict:
    """
    Route each detected sheet to the correct analysis path.

    Parameters
    ----------
    sheets_with_rows : list[dict]
        Each element must have keys:
            name, type, row_count, headers, normalized_headers, rows (list[dict])

    Returns
    -------
    dict with:
        run_id               : unique run identifier
        timestamp            : ISO timestamp
        total_sheets         : int
        controls_found       : bool  — True if a non-empty controls sheet was found
        no_controls_detected : bool  — True if controls are absent or empty
        has_assets           : bool
        has_vendors          : bool
        has_risks            : bool
        has_org_profile      : bool
        has_employees        : bool
        has_governance       : bool
        has_network_rules    : bool
        routing_results      : list of per-sheet analysis dicts (with traceability)
        summary              : aggregate metadata
        detection_summary    : human-readable list of what was detected
        warnings             : accumulated warnings from all sheets
    """
    routing_results = []
    controls_found = False
    has_assets = False
    has_vendors = False
    has_risks = False
    has_org_profile = False
    has_employees = False
    has_governance = False
    has_network_rules = False
    has_high_risk = False
    all_warnings: list[str] = []
    detection_lines: list[str] = []

    for sheet in sheets_with_rows:
        sheet_type = sheet.get("type", "unknown")
        sheet_name = sheet.get("name", "")
        rows = sheet.get("rows", [])
        row_count = len(rows)

        handler = _ROUTE_MAP.get(sheet_type, _analyse_unknown)
        result = handler(rows, sheet_name)

        # Attach traceability fields to every result
        result["source_sheet"] = sheet_name
        result["source_type"] = sheet_type
        result["record_count"] = row_count
        result["mapped_headers"] = sheet.get("normalized_headers", [])
        result["classification"] = sheet.get("classification", "unknown")

        routing_results.append(result)

        # Accumulate per-sheet warnings
        sheet_warnings = sheet.get("warnings", [])
        all_warnings.extend(sheet_warnings)

        # Build human-readable detection line
        type_labels = {
            "controls": "Controls",
            "assets": "Assets",
            "applications": "Applications",
            "vendors": "Vendors",
            "risk_register": "Risk Register",
            "network_rules": "Network Rules",
            "governance": "Governance Activities",
            "employees": "Employees",
            "organization_profile": "Organization Profile",
            "high_risk": "High-Risk Mapping",
        }
        label = type_labels.get(sheet_type, f"Unknown ({sheet_name})")
        if row_count > 0:
            detection_lines.append(f"✓ {label}: {row_count} records")
        elif sheet_type != "unknown":
            detection_lines.append(f"○ {label}: empty")

        # Track key data-presence flags
        if sheet_type == "controls" and not result.get("no_controls_detected"):
            controls_found = True
        if sheet_type in ("assets", "applications"):
            has_assets = True
        if sheet_type == "vendors":
            has_vendors = True
        if sheet_type == "risk_register":
            has_risks = True
        if sheet_type == "organization_profile":
            has_org_profile = True
        if sheet_type == "employees":
            has_employees = True
        if sheet_type == "governance":
            has_governance = True
        if sheet_type == "network_rules":
            has_network_rules = True
        if sheet_type == "high_risk":
            has_high_risk = True

    no_controls_detected = not controls_found

    return {
        "run_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_sheets": len(sheets_with_rows),
        "controls_found": controls_found,
        "no_controls_detected": no_controls_detected,
        "has_assets": has_assets,
        "has_vendors": has_vendors,
        "has_risks": has_risks,
        "has_org_profile": has_org_profile,
        "has_employees": has_employees,
        "has_governance": has_governance,
        "has_network_rules": has_network_rules,
        "has_high_risk": has_high_risk,
        "routing_results": routing_results,
        "summary": {
            "sheets_processed": [s.get("name") for s in sheets_with_rows],
            "sheet_types_found": sorted({s.get("type", "unknown") for s in sheets_with_rows}),
            "total_records": sum(len(s.get("rows", [])) for s in sheets_with_rows),
        },
        "detection_summary": detection_lines,
        "warnings": all_warnings,
    }
