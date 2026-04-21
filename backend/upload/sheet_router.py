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
            "Verify sheet name matches expected types."
        ],
    }


# ---------------------------------------------------------------------------
# Dispatcher map
# ---------------------------------------------------------------------------

_ROUTE_MAP = {
    "assets":        _analyse_assets,
    "applications":  _analyse_applications,
    "vendors":       _analyse_vendors,
    "controls":      _analyse_controls,
    "risk_register": _analyse_risk_register,
    "network_rules": _analyse_network_rules,
    "governance":    _analyse_governance,
    "employees":     _analyse_employees,
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
        routing_results      : list of per-sheet analysis dicts (with traceability)
        summary              : aggregate metadata
    """
    routing_results = []
    controls_found = False
    has_assets = False
    has_vendors = False
    has_risks = False

    for sheet in sheets_with_rows:
        sheet_type = sheet.get("type", "unknown")
        sheet_name = sheet.get("name", "")
        rows = sheet.get("rows", [])

        handler = _ROUTE_MAP.get(sheet_type, _analyse_unknown)
        result = handler(rows, sheet_name)

        # Attach traceability fields to every result
        result["source_sheet"] = sheet_name
        result["source_type"] = sheet_type
        result["record_count"] = len(rows)
        result["mapped_headers"] = sheet.get("normalized_headers", [])

        routing_results.append(result)

        # Track key data-presence flags
        if sheet_type == "controls" and not result.get("no_controls_detected"):
            controls_found = True
        if sheet_type in ("assets", "applications"):
            has_assets = True
        if sheet_type == "vendors":
            has_vendors = True
        if sheet_type == "risk_register":
            has_risks = True

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
        "routing_results": routing_results,
        "summary": {
            "sheets_processed": [s.get("name") for s in sheets_with_rows],
            "sheet_types_found": sorted({s.get("type", "unknown") for s in sheets_with_rows}),
            "total_records": sum(len(s.get("rows", [])) for s in sheets_with_rows),
        },
    }
