"""
Framework-Aware Assessment Builder  (Step 4 + cleanup)

Separates output into clear, distinct concepts:
  - framework_gap_analysis  : controls the selected framework requires but are missing/partial
  - risk_register           : derived from UPLOADED risk register rows (not from missing controls)
  - vendor_findings         : from uploaded vendor/supplier data
  - network_findings        : from uploaded network rules data
  - recommended_actions     : specific actionable items per framework and data context
  - insights                : framework-specific narrative summary

No static outputs. All results are derived from:
  1. The selected framework (controls to assess against)
  2. The uploaded data context (which controls are relevant)
  3. The routing results (sheet-level findings from Step 3)
"""

import uuid
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Domain relevance map
# ---------------------------------------------------------------------------

_DOMAIN_TRIGGERS: dict[str, list[str]] = {
    "access control":           ["assets", "applications", "employees", "vendors"],
    "asset management":         ["assets", "applications"],
    "asset inventory":          ["assets", "applications"],
    "supplier management":      ["vendors"],
    "vendor management":        ["vendors"],
    "third party":              ["vendors"],
    "network security":         ["network_rules"],
    "network protection":       ["network_rules"],
    "network segmentation":     ["network_rules"],
    "monitoring":               ["governance", "network_rules", "assets"],
    "audit":                    ["governance", "network_rules"],
    "audit log":                ["governance", "network_rules"],
    "data protection":          ["applications", "vendors", "assets"],
    "data recovery":            ["assets", "applications", "risk_register"],
    "data backup":              ["assets", "applications", "risk_register"],
    "incident management":      ["governance", "risk_register"],
    "incident response":        ["governance", "risk_register"],
    "resilience":               ["assets", "applications", "risk_register"],
    "configuration management": ["network_rules", "assets"],
    "secure configuration":     ["network_rules", "assets"],
    "governance":               ["governance"],
    "policy":                   ["governance"],
    "risk management":          ["risk_register"],
    "people controls":          ["employees"],
    "physical controls":        ["assets"],
    "technological controls":   ["assets", "applications", "network_rules"],
    "cardholder":               ["applications", "vendors"],
    "phi protection":           ["applications", "vendors"],
    "remote access":            ["network_rules", "assets"],
}


def _get_present_sheet_types(routing: dict) -> set[str]:
    present: set[str] = set()
    for r in routing.get("routing_results", []):
        if r.get("total_records", 0) > 0:
            t = r.get("source_type", "")
            if t and t != "unknown":
                present.add(t)
    return present


def _is_domain_relevant(domain: str, present_types: set[str]) -> bool:
    if not present_types:
        return True
    dk = domain.strip().lower()
    triggers = _DOMAIN_TRIGGERS.get(dk)
    if triggers is not None:
        return bool(set(triggers) & present_types)
    for known, triggers in _DOMAIN_TRIGGERS.items():
        for word in known.split():
            if len(word) >= 4 and word in dk:
                if set(triggers) & present_types:
                    return True
    return len(present_types) >= 2


def _filter_relevant_controls(sections: list[dict], present_types: set[str]) -> list[dict]:
    result: list[dict] = []
    for section in sections:
        sk = section.get("section_key", "")
        sn = section.get("section_name", "")
        for ctrl in section.get("controls", []):
            domain = ctrl.get("domain") or sn
            if _is_domain_relevant(domain, present_types):
                result.append({**ctrl, "section_key": sk, "section_name": sn})
    return result


# ---------------------------------------------------------------------------
# Status normalization
# ---------------------------------------------------------------------------

def _normalize_status(raw: str) -> str:
    v = (raw or "").strip().lower()
    if v in ("yes", "implemented", "compliant", "pass", "true", "1", "done",
             "complete", "full", "yes - implemented"):
        return "compliant"
    if v in ("partial", "in progress", "partially implemented", "ongoing", "in_progress"):
        return "partial"
    return "missing"


# ---------------------------------------------------------------------------
# Control matching — uploaded controls sheet → framework controls
# ---------------------------------------------------------------------------

def _keyword_overlap(a: str, b: str) -> int:
    wa = {w.lower() for w in a.split() if len(w) >= 4}
    wb = {w.lower() for w in b.split() if len(w) >= 4}
    return len(wa & wb)


def _map_controls_to_framework(
    uploaded_rows: list[dict],
    relevant_controls: list[dict],
) -> list[dict]:
    by_rule_id = {
        (c.get("rule_id") or "").strip().lower(): c
        for c in relevant_controls if c.get("rule_id")
    }
    matched_ids: set[str] = set()

    for row in uploaded_rows:
        row_id = (row.get("control_id") or "").strip().lower()
        row_name = (row.get("control_name") or "").strip()
        row_status = _normalize_status(row.get("status", ""))

        matched_ctrl: dict | None = None
        match_method: str | None = None

        if row_id:
            # 1. Exact match on rule_id
            if row_id in by_rule_id:
                matched_ctrl = by_rule_id[row_id]
                match_method = "exact_id"
            else:
                # 2. Fuzzy/Substring match on rule_id or control code
                for ctrl in relevant_controls:
                    c_id = (ctrl.get("rule_id") or "").lower()
                    c_ctrl = (ctrl.get("control") or "").lower()
                    
                    if (c_id and row_id in c_id) or (c_ctrl and (row_id == c_ctrl or row_id.replace("iso-", "") == c_ctrl)):
                        matched_ctrl = ctrl
                        match_method = "fuzzy_id"
                        break

        if not matched_ctrl and row_name:
            best_score, best_ctrl = 0, None
            for ctrl in relevant_controls:
                # 3. Enhanced Keyword Match
                score = _keyword_overlap(row_name, ctrl.get("name", ""))
                if score > best_score:
                    best_score, best_ctrl = score, ctrl
            
            # Lower threshold to 1 keyword to catch partial matches like "Cryptography"
            if best_score >= 1:
                matched_ctrl = best_ctrl
                match_method = "keyword"

        if matched_ctrl is not None:
            rid = (matched_ctrl.get("rule_id") or "").lower()
            if rid not in matched_ids:
                matched_ids.add(rid)
                matched_ctrl["has_evidence"] = True
                matched_ctrl["evidence_row"] = row
                matched_ctrl["evidence_status"] = row_status
                matched_ctrl["status"] = row_status
                matched_ctrl["source"] = "uploaded"
                matched_ctrl["match_method"] = match_method
                matched_ctrl["reason"] = (
                    f"Matched from uploaded controls sheet (method: {match_method})."
                )

    return relevant_controls


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def _score_flat(controls: list[dict]) -> dict:
    total = len(controls)
    compliant = sum(1 for c in controls if c.get("status") == "compliant")
    partial   = sum(1 for c in controls if c.get("status") == "partial")
    missing   = total - compliant - partial
    # GRC maturity scoring: compliant = 100%, partial = 50%, missing = 0%
    # This reflects coverage and maturity, not strict binary mapping
    score     = round(((compliant + partial * 0.5) / total) * 100, 2) if total > 0 else 0.0
    return {
        "compliance_score":  score,
        "total_controls":    total,
        "compliant_controls": compliant,
        "partial_controls":  partial,
        "missing_controls":  missing,
    }


def _build_sections(annotated: list[dict]) -> list[dict]:
    seen: dict[str, dict] = {}
    for ctrl in annotated:
        sk = ctrl.get("section_key") or ctrl.get("domain", "General")
        sn = ctrl.get("section_name") or ctrl.get("domain", "General")
        if sk not in seen:
            seen[sk] = {"section_key": sk, "section_name": sn, "controls": []}
        seen[sk]["controls"].append(ctrl)

    sections = []
    for sec in seen.values():
        ctrls   = sec["controls"]
        total   = len(ctrls)
        comp    = sum(1 for c in ctrls if c.get("status") == "compliant")
        part    = sum(1 for c in ctrls if c.get("status") == "partial")
        missing = total - comp - part
        sec.update({
            "controls_count":    total,
            "compliant_controls": comp,
            "partial_controls":  part,
            "missing_controls":  missing,
            "compliance_score":  round(((comp + part * 0.5) / total) * 100, 2) if total > 0 else 0.0,
        })
        sections.append(sec)
    return sections


def _severity_breakdown(controls: list[dict]) -> dict:
    bd: dict[str, dict] = {}
    for ctrl in controls:
        sev = (ctrl.get("severity") or "unknown").lower()
        bd.setdefault(sev, {"compliant": 0, "partial": 0, "missing": 0, "total": 0})
        status = ctrl.get("status", "missing")
        bd[sev]["total"] += 1
        bd[sev][status] = bd[sev].get(status, 0) + 1
    return bd


# ---------------------------------------------------------------------------
# Gap analysis — separate from risk register
# ---------------------------------------------------------------------------

def _build_gap_analysis(controls: list[dict], framework_label: str) -> dict:
    """
    Summarises framework control gaps — what the framework requires
    but is currently missing or partial.

    This is NOT the risk register; it is a compliance gap assessment.
    """
    gaps = [c for c in controls if c.get("status") in ("missing", "partial")]
    critical_gaps = [
        c for c in gaps
        if (c.get("severity") or "").lower() in ("critical", "high")
    ]
    by_domain: dict[str, int] = {}
    for c in gaps:
        domain = c.get("domain") or c.get("section_name", "General")
        by_domain[domain] = by_domain.get(domain, 0) + 1

    return {
        "framework":       framework_label,
        "total_gaps":      len(gaps),
        "critical_gaps":   len(critical_gaps),
        "by_domain":       by_domain,
        "top_critical_gaps": [
            {
                "rule_id":      c.get("rule_id", ""),
                "name":         c.get("name", ""),
                "severity":     c.get("severity", ""),
                "domain":       c.get("domain") or c.get("section_name", ""),
                "status":       c.get("status", "missing"),
                "source":       c.get("source", ""),
                "reason":       c.get("reason", ""),
            }
            for c in critical_gaps
        ][:10],
    }


# ---------------------------------------------------------------------------
# Risk register — from UPLOADED risk data, not from missing controls
# ---------------------------------------------------------------------------

def _build_risk_register_from_routing(routing: dict) -> dict:
    """
    Extract the actual risk register from uploaded risk_register sheet data.
    This is real uploaded risk data — NOT derived from missing framework controls.

    If no risk register sheet was uploaded, returns an empty register with a note.
    """
    rr_result = next(
        (r for r in routing.get("routing_results", [])
         if r.get("source_type") == "risk_register"),
        None,
    )

    if rr_result is None or rr_result.get("total_records", 0) == 0:
        return {
            "source":       "none",
            "note":         "No risk register sheet was uploaded.",
            "total_risks":  0,
            "high_risks":   0,
            "medium_risks": 0,
            "low_risks":    0,
            "by_level":     {},
            "untreated_risks": [],
            "all_risks":    [],
        }

    by_level = rr_result.get("by_level", {})
    untreated = rr_result.get("untreated_risks", [])
    total = rr_result.get("total_records", 0)

    high   = by_level.get("high", 0) + by_level.get("critical", 0)
    medium = by_level.get("medium", 0)
    low    = by_level.get("low", 0)

    return {
        "source":          "uploaded_risk_register",
        "source_sheet":    rr_result.get("source_sheet", ""),
        "total_risks":     total,
        "high_risks":      high,
        "medium_risks":    medium,
        "low_risks":       low,
        "by_level":        by_level,
        "untreated_count": len(untreated),
        "untreated_risks": untreated[:20],
        "findings":        rr_result.get("findings", []),
    }


# ---------------------------------------------------------------------------
# Vendor & network findings — from routing results
# ---------------------------------------------------------------------------

def _extract_vendor_findings(routing: dict) -> dict | None:
    result = next(
        (r for r in routing.get("routing_results", [])
         if r.get("source_type") == "vendors"),
        None,
    )
    if result is None or result.get("total_records", 0) == 0:
        return None
    return {
        "source_sheet":     result.get("source_sheet", ""),
        "total_vendors":    result.get("total_records", 0),
        "by_risk":          result.get("by_risk", {}),
        "high_risk_vendors": result.get("high_risk_vendors", []),
        "no_compliance_count": result.get("no_compliance_count", 0),
        "findings":         result.get("findings", []),
    }


def _extract_network_findings(routing: dict) -> dict | None:
    result = next(
        (r for r in routing.get("routing_results", [])
         if r.get("source_type") == "network_rules"),
        None,
    )
    if result is None or result.get("total_records", 0) == 0:
        return None
    return {
        "source_sheet":      result.get("source_sheet", ""),
        "total_rules":       result.get("total_records", 0),
        "risky_rules_count": result.get("risky_rules_count", 0),
        "risky_rules":       result.get("risky_rules", []),
        "deny_rules_count":  result.get("deny_rules_count", 0),
        "findings":          result.get("findings", []),
    }


def _extract_asset_findings(routing: dict) -> dict | None:
    result = next(
        (r for r in routing.get("routing_results", [])
         if r.get("source_type") in ("assets", "applications")),
        None,
    )
    if result is None or result.get("total_records", 0) == 0:
        return None
    return {
        "source_sheet":    result.get("source_sheet", ""),
        "total_assets":    result.get("total_records", 0),
        "by_criticality":  result.get("by_criticality", {}),
        "unowned_assets":  result.get("unowned_assets", 0),
        "findings":        result.get("findings", []),
    }


# ---------------------------------------------------------------------------
# Recommended actions — specific per framework + data context
# ---------------------------------------------------------------------------

_FRAMEWORK_ACTION_TEMPLATES: dict[str, list[str]] = {
    "iso27001": [
        "Establish an Information Security Management System (ISMS) policy aligned to ISO 27001:2022.",
        "Complete an asset inventory and assign owners to all information assets.",
        "Define and document scope, roles, and responsibilities for information security.",
        "Conduct a formal risk assessment using ISO 27001 methodology.",
        "Implement A.7 Physical Controls for all identified physical assets.",
        "Apply A.8 Technological Controls including network segmentation and cryptography.",
    ],
    "pci_dss": [
        "Implement and document an access control policy restricting access to cardholder data.",
        "Enable audit logging across all systems in the cardholder data environment.",
        "Define and deploy firewall/router configurations protecting cardholder data.",
        "Establish a tested data backup and recovery procedure for cardholder systems.",
        "Restrict and authenticate all remote access to cardholder data environments.",
    ],
    "hipaa": [
        "Implement technical access controls restricting access to ePHI to authorised parties.",
        "Enable audit logging on all systems handling electronic Protected Health Information.",
        "Establish and test a data backup plan for all ePHI storage systems.",
        "Document and test an incident response plan covering ePHI breaches.",
        "Apply encryption or equivalent measures on ePHI transmitted over networks.",
    ],
    "nist": [
        "Build and maintain a complete asset inventory aligned to NIST CSF Identify function.",
        "Implement least-privilege access controls (NIST PR.AC).",
        "Enable and review audit logs for anomalous activity (NIST DE.AE).",
        "Establish incident response procedures (NIST RS.RP).",
        "Apply network segmentation to limit blast radius of security incidents (NIST PR.PT).",
    ],
    "cis": [
        "Establish secure configuration baselines for all enterprise assets (CIS Control 4).",
        "Implement centralized audit log management and retention (CIS Control 8).",
        "Configure and test data recovery procedures (CIS Control 11).",
        "Apply network segmentation to restrict unnecessary inter-segment traffic (CIS Control 12).",
        "Manage and control remote access to enterprise resources (CIS Control 12).",
    ],
    "sama": [
        "Align cybersecurity governance with SAMA Cybersecurity Framework domains.",
        "Implement identity and access management controls for all banking systems.",
        "Establish a third-party risk management programme covering all vendors.",
        "Enable security monitoring and SIEM aligned to SAMA detection requirements.",
        "Document and test cyber incident response and crisis management procedures.",
    ],
}

_CONTEXT_ACTION_TEMPLATES: dict[str, str] = {
    "vendors":       "Perform third-party risk assessments for all {high_risk_count} high-risk vendor(s) identified.",
    "network_rules": "Review and remediate {risky_count} overly permissive firewall rules (ANY source/destination/port).",
    "assets":        "Assign owners to {unowned} unowned assets and classify all assets by criticality.",
    "risk_register": "Develop mitigation plans for {untreated} risks currently lacking any treatment record.",
    "employees":     "Enrol employees in security awareness training; {no_training} employees have no training record.",
}


def _build_recommended_actions(
    framework_id: str,
    relevant_controls: list[dict],
    routing: dict,
    present_types: set[str],
) -> list[dict]:
    """
    Generate specific, prioritised recommended actions.

    Combines:
      1. Framework-specific baseline actions (from framework template)
      2. Data-context actions (from routing findings — vendors, network, assets)
    """
    actions: list[dict] = []
    priority_order = 1

    # ── Framework-specific actions ────────────────────────────────────────
    fw_templates = _FRAMEWORK_ACTION_TEMPLATES.get(framework_id, [])
    # Only include actions whose keywords are relevant to the uploaded data
    for template in fw_templates:
        actions.append({
            "priority":   priority_order,
            "action":     template,
            "source":     "framework",
            "framework":  framework_id.upper(),
            "triggered_by": "framework_requirement",
        })
        priority_order += 1

    # ── Context-specific actions from routing findings ─────────────────────
    for r in routing.get("routing_results", []):
        sheet_type = r.get("source_type", "")
        template   = _CONTEXT_ACTION_TEMPLATES.get(sheet_type)
        if not template or r.get("total_records", 0) == 0:
            continue

        if sheet_type == "vendors":
            high_count = len(r.get("high_risk_vendors", []))
            if high_count > 0:
                actions.append({
                    "priority":    priority_order,
                    "action":      template.format(high_risk_count=high_count),
                    "source":      "uploaded_vendors",
                    "source_sheet": r.get("source_sheet", ""),
                    "triggered_by": f"{high_count} high-risk vendor(s) detected",
                })
                priority_order += 1

        elif sheet_type == "network_rules":
            risky = r.get("risky_rules_count", 0)
            if risky > 0:
                actions.append({
                    "priority":    priority_order,
                    "action":      template.format(risky_count=risky),
                    "source":      "uploaded_network_rules",
                    "source_sheet": r.get("source_sheet", ""),
                    "triggered_by": f"{risky} permissive rules found",
                })
                priority_order += 1

        elif sheet_type in ("assets", "applications"):
            unowned = r.get("unowned_assets", r.get("unowned_applications", 0))
            if unowned > 0:
                actions.append({
                    "priority":    priority_order,
                    "action":      template.format(unowned=unowned),
                    "source":      "uploaded_assets",
                    "source_sheet": r.get("source_sheet", ""),
                    "triggered_by": f"{unowned} assets with no owner",
                })
                priority_order += 1

        elif sheet_type == "risk_register":
            untreated = len(r.get("untreated_risks", []))
            if untreated > 0:
                actions.append({
                    "priority":    priority_order,
                    "action":      template.format(untreated=untreated),
                    "source":      "uploaded_risk_register",
                    "source_sheet": r.get("source_sheet", ""),
                    "triggered_by": f"{untreated} untreated risks",
                })
                priority_order += 1

        elif sheet_type == "employees":
            no_training = r.get("no_security_training", 0)
            if no_training > 0:
                actions.append({
                    "priority":    priority_order,
                    "action":      template.format(no_training=no_training),
                    "source":      "uploaded_employees",
                    "source_sheet": r.get("source_sheet", ""),
                    "triggered_by": f"{no_training} untrained employees",
                })
                priority_order += 1

    return actions


# ---------------------------------------------------------------------------
# Framework-specific insights
# ---------------------------------------------------------------------------

def _build_insights(
    framework_id: str,
    framework_label: str,
    score_data: dict,
    routing: dict,
    no_controls: bool,
    present_types: set[str],
) -> list[str]:
    insights: list[str] = []
    score        = score_data["compliance_score"]
    missing_ctrl = score_data["missing_controls"]

    # ── Opening — always framework-specific ───────────────────────────────
    if no_controls:
        insights.append(
            f"GRC Intelligence Mode: {framework_label} compliance has been inferred "
            f"from uploaded organizational data ({', '.join(sorted(present_types)) or 'data'}). "
            f"{score_data['compliant_controls']} controls show strong evidence, "
            f"{score_data['partial_controls']} show partial evidence, and "
            f"{score_data['missing_controls']} require additional documentation."
        )
    else:
        insights.append(
            f"{framework_label} compliance score: {score:.0f}%. "
            f"{score_data['compliant_controls']} controls are implemented, "
            f"{missing_ctrl} are missing, "
            f"{score_data['partial_controls']} are partially in place."
        )

    # ── Score narrative ───────────────────────────────────────────────────
    if score >= 80:
        insights.append(
            f"Strong {framework_label} compliance posture. "
            "Focus on closing the remaining partial and missing controls."
        )
    elif score >= 50:
        insights.append(
            f"Moderate {framework_label} compliance. "
            f"{missing_ctrl} controls still need full implementation."
        )
    else:
        insights.append(
            f"Low {framework_label} compliance. "
            f"Immediate remediation is required — {missing_ctrl} controls are unaddressed."
        )

    # ── Framework-specific contextual notes ───────────────────────────────
    if framework_id == "pci_dss" and "network_rules" in present_types:
        insights.append(
            "PCI DSS Requirement 1 mandates documented firewall and router configurations. "
            "Uploaded network rules require review against cardholder data environment scope."
        )
    if framework_id == "hipaa" and "applications" in present_types:
        insights.append(
            "HIPAA requires technical safeguards on all systems handling ePHI. "
            "Review uploaded application inventory for ePHI data handling."
        )
    if framework_id == "nist" and "risk_register" in present_types:
        insights.append(
            "NIST CSF Respond and Recover functions require documented risk treatment plans. "
            "Uploaded risk register shows untreated risks that need formal responses."
        )
    if framework_id == "iso27001" and "vendors" in present_types:
        insights.append(
            "ISO 27001 Annex A.5.19–5.22 covers supplier relationships. "
            "Uploaded vendor data should be reviewed against third-party security requirements."
        )
    if framework_id == "cis" and "assets" in present_types:
        insights.append(
            "CIS Control 1 (Asset Inventory) is foundational. "
            "Ensure all uploaded assets are inventoried and classified."
        )

    # ── Data-context notes (sourced from routing, shared only when data warrants it) ──
    vendor_r = next(
        (r for r in routing.get("routing_results", [])
         if r.get("source_type") == "vendors" and r.get("total_records", 0) > 0),
        None,
    )
    if vendor_r:
        hrc = len(vendor_r.get("high_risk_vendors", []))
        if hrc > 0:
            insights.append(
                f"{hrc} high-risk vendor(s) detected in uploaded data. "
                "Vendor risk assessments and contractual security requirements should be documented."
            )

    network_r = next(
        (r for r in routing.get("routing_results", [])
         if r.get("source_type") == "network_rules" and r.get("total_records", 0) > 0),
        None,
    )
    if network_r and network_r.get("risky_rules_count", 0) > 0:
        insights.append(
            f"{network_r['risky_rules_count']} network rules use ANY/wildcard "
            "source, destination, or port — review against least-privilege network principles."
        )

    return insights


# ---------------------------------------------------------------------------
# SoA builder
# ---------------------------------------------------------------------------

def _build_soa(relevant_controls: list[dict], framework_id: str = "", risks: list[dict] | None = None) -> dict:
    print("USING UPDATED SOA GENERATOR")
    is_hipaa = (framework_id.lower() == "hipaa")
    is_pci = False  # Bypassed old PCI SoA logic
    entries = []
    for ctrl in relevant_controls:
        status = ctrl.get("status", "missing")
        ev  = ctrl.get("evidence_row", {})
        has_evidence = ctrl.get("has_evidence", False)

        if has_evidence:
            applicable = "Yes"
            remarks = ctrl.get("reason", "")
        else:
            applicable = "No"
            remarks = "No supporting evidence found in uploaded data"
        
        sec_key = ctrl.get('section_key', '').strip()
        sec_name = ctrl.get('section_name', '').strip()
        
        if is_hipaa and sec_key and sec_name and sec_key.lower() in sec_name.lower():
            section_str = sec_name
        elif is_hipaa and sec_key and sec_name and sec_name.lower() in sec_key.lower():
            section_str = sec_key
        else:
            section_str = f"{sec_key} {sec_name}".strip()
        
        if is_hipaa:
            # 1. Dynamic Implementation Overview
            if status == "compliant":
                cname = ctrl.get("name", "").lower()
                cdomain = (ctrl.get("domain") or "").lower()
                if "access" in cname:
                    implementation = "Role-based access control (RBAC) is enforced across clinical systems with periodic access reviews"
                elif "audit" in cname:
                    implementation = "Audit logging is enabled for systems handling ePHI, with monitoring of suspicious activities"
                elif "transmission" in cname or "encrypt" in cname:
                    implementation = "Secure transmission protocols and encryption are enforced for data in transit"
                elif "workforce" in cname or "workforce" in cdomain:
                    implementation = "Workforce access and authorization processes are maintained using employee records and role assignments."
                elif "training" in cname or "awareness" in cname:
                    implementation = "Security awareness training is tracked through employee training records and pending training gaps are monitored."
                elif "associate" in cname or "vendor" in cname or "associate" in cdomain:
                    implementation = "Business Associate relationships are tracked through vendor records and BAA agreement evidence."
                elif "device" in cname or "media" in cname:
                    implementation = "Asset inventory supports device and media accountability for systems handling patient data."
                else:
                    implementation = "Technical and administrative safeguards are fully implemented to protect ePHI"
            elif status == "partial":
                cname = ctrl.get("name", "").lower()
                if "contingency" in cname or "backup" in cname or "recovery" in cname:
                    implementation = "Backup and disaster recovery procedures are defined but require testing and validation"
                else:
                    implementation = "Safeguards are partially implemented; further enhancements required to fully protect patient data"
            else:
                implementation = "Not Implemented"
                

            # 2. Dynamic Evidence References
            if not has_evidence and applicable == "No":
                ref = "—"
            elif ev.get("reference") and ev.get("reference") != "System Inference Engine":
                ref = ev.get("reference")
            else:
                domain = (ctrl.get("domain") or "").lower()
                cname = ctrl.get("name", "").lower()
                if "employee" in domain or "training" in cname or "workforce" in cname:
                    ref = "HR Records / Training Data"
                elif "asset" in domain or "device" in cname or "workstation" in cname:
                    ref = "Asset Inventory"
                elif "network" in domain or "transmission" in cname:
                    ref = "Network Configuration"
                elif "vendor" in domain or "third-party" in cname or "business associate" in cname:
                    ref = "Vendor Records / BAA Agreements"
                elif "policy" in domain or "governance" in cname or "management" in cname:
                    ref = "Policies & Procedures"
                else:
                    ref = "System Configuration / Logs"
        else:
            implementation = {
                "compliant": "Fully Implemented",
                "partial":   "Partially Implemented",
            }.get(status, "Not Implemented")
            
            ref = (
                ev.get("reference")
                or ev.get("evidence_reference")
                or ("Uploaded evidence" if ctrl.get("has_evidence") else "—")
            )

        entries.append({
            "section":       section_str,
            "control_no":    ctrl.get("rule_id", ""),
            "control_title": ctrl.get("name", ""),
            "applicable":    applicable,
            "remarks":       remarks,
            "implementation": implementation,
            "reference":     ref,
            "status":        status,
            "source":        ctrl.get("source", "framework_derived"),
        })
        
    return {
        "total_controls":    len(entries),
        "applicable_count":  sum(1 for e in entries if e["applicable"] == "Yes"),
        "not_applicable_count": sum(1 for e in entries if e["applicable"] == "No"),
        "entries":           entries,
    }


# ---------------------------------------------------------------------------
# Extra Matrices / Calendars
# ---------------------------------------------------------------------------

def _build_vendor_checklist(
    all_sheets: list[dict] | None,
    framework_id: str = "",
) -> list[dict]:
    """
    Build vendor / business-associate checklist with full security evaluation.

    Each row is enriched with deterministic fields derived from the vendor's
    service_type and compliance status:
      certifications, agreement, encryption, sla, monitoring, risk_level
    """
    if not all_sheets:
        return []
    sheet = next((s for s in all_sheets if s.get("type") == "vendors"), None)
    if not sheet:
        return []

    # --- keyword sets for service-type categorisation ---
    _CLOUD_KW   = {"cloud", "saas", "iaas", "paas", "aws", "azure", "gcp", "hosting"}
    _EHR_KW     = {"ehr", "emr", "electronic health", "clinical", "patient record"}
    _BILLING_KW = {"billing", "revenue", "claims", "payment", "financial", "accounting", "rcm"}
    _BACKUP_KW  = {"backup", "storage", "disaster", "recovery", "archive", "dr"}
    _TELE_KW    = {"telehealth", "telemedicine", "remote care", "virtual visit", "video"}
    _INTEG_KW   = {"integration", "api", "middleware", "interoperability", "hl7", "fhir"}

    def _matches(svc_lower: str, keywords: set[str]) -> bool:
        return any(k in svc_lower for k in keywords)

    checklist: list[dict] = []
    for row in sheet.get("rows", []):
        raw_vendor = row.get("vendor_name", row.get("vendor", row.get("vendor_id", "")))
        vendor_name = str(raw_vendor).strip() if raw_vendor is not None else ""
        
        # ── 1. Filter invalid rows ──
        row_text = " ".join(str(v).lower() for v in row.values() if v is not None)
        
        skip_phrases = [
            "evidence for third-party",
            "evidence for third party",
            "service provider risk",
            "pci should flag",
            "system should infer",
            "evidence input only",
            "vendor id"
        ]
        if any(phrase in row_text for phrase in skip_phrases):
            print("SKIPPED INVALID VENDOR ROW:", row)
            continue

        skip_names = [
            "vendor id", "services", "none", "n/a", "unknown", ""
        ]
        if not vendor_name or len(vendor_name) < 2 or vendor_name.lower() in skip_names:
            print("SKIPPED INVALID VENDOR ROW:", row)
            continue
        if any(phrase in vendor_name.lower() for phrase in skip_phrases):
            print("SKIPPED INVALID VENDOR ROW:", row)
            continue

        # ── 2. Read explicit mapping from Excel ──
        service_provided = str(row.get("service_type") or row.get("service") or row.get("services") or "Services").strip()
        raw_contract = str(row.get("contract") or row.get("agreement") or row.get("compliance") or "No").strip()
        raw_encryption = str(row.get("encryption") or row.get("data_protection") or "No").strip()
        raw_sla = str(row.get("sla") or row.get("service_level_agreement") or "Undefined").strip()
        raw_monitoring = str(row.get("monitoring") or row.get("review") or "None").strip()

        is_compliant_contract = raw_contract.lower() in ("yes", "compliant", "signed", "certified", "approved", "active")
        
        # Parse Contract
        agreement = "Yes" if is_compliant_contract else "No"
        
        # Parse Encryption
        if "yes" in raw_encryption.lower() or "aes" in raw_encryption.lower() or "tls" in raw_encryption.lower():
            encryption = "Yes"
        else:
            encryption = "No"

        # Parse SLA
        if "yes" in raw_sla.lower() or "defined" in raw_sla.lower():
            sla = "Defined"
        else:
            sla = "Undefined"

        # Parse Monitoring
        if "monthly" in raw_monitoring.lower() or "continuous" in raw_monitoring.lower():
            monitoring = "Monthly"
        else:
            monitoring = "None"
            
        certifications = "PCI DSS, SOC 2" if is_compliant_contract else "Missing"

        # ── 4. Dynamic Risk Logic ─────────────────────────────────────────────────
        missing_count = 0
        if agreement == "No": missing_count += 1
        if encryption == "No": missing_count += 1
        if sla == "Undefined": missing_count += 1

        if missing_count == 3:
            risk_level = "High"
        elif missing_count > 0:
            risk_level = "Medium"
        else:
            risk_level = "Low"

        checklist.append({
            "vendor_name":       vendor_name,
            "service_provided":  service_provided,
            "certifications":    certifications,
            "agreement":         agreement,
            "encryption":        encryption,
            "sla":               sla,
            "monitoring":        monitoring,
            "risk_level":        risk_level,
            "compliance_status": "Compliant" if agreement == "Yes" else "Missing",
            "action_required":   "Perform security review" if agreement == "No" else "Review annually",
        })

    print("VALID VENDORS:", [v['vendor_name'] for v in checklist])
    return checklist

def _build_training_matrix(all_sheets: list[dict] | None) -> list[dict]:
    if not all_sheets: return []
    sheet = next((s for s in all_sheets if s.get("type") == "employees"), None)
    if not sheet: return []
    matrix = []
    for row in sheet.get("rows", []):
        matrix.append({
            "employee": row.get("name") or row.get("employee_name", "Unknown"),
            "role": row.get("role", "General Employee"),
            "training_status": row.get("training") or row.get("training_status", "None"),
            "required_modules": "Admin Awareness" if (row.get("access_level") or "").lower() in ("admin", "privileged") else "General Security Awareness"
        })
    return matrix

def _build_governance_calendar(all_sheets: list[dict] | None) -> list[dict]:
    """
    Build the governance calendar from the uploaded Governance Activity sheet.

    Canonical field names (produced by normalize_columns_for_type for 'governance'):
      activity        — activity name / title / description
      responsible     — owner / lead / manager
      frequency       — cadence / schedule / interval / recurrence
      next_due        — due date / deadline / upcoming
      last_performed  — last review / completed date
      status          — state / outcome / completion
      notes           — comments / remarks / minutes
    """
    if not all_sheets:
        return []
    sheet = next((s for s in all_sheets if s.get("type") == "governance"), None)
    if not sheet:
        return []
    calendar = []
    for row in sheet.get("rows", []):
        # activity: canonical key is 'activity' (aliases: name, title, description, event, meeting, review, audit)
        activity = (
            row.get("activity")
            or row.get("activity_type")
            or ""
        ).strip() or "Unknown Activity"

        # responsible: canonical key is 'responsible' (aliases: owner, lead, chairperson, manager, organizer, assigned)
        responsible = (
            row.get("responsible")
            or ""
        ).strip() or "Unassigned"

        # cadence: canonical key is 'frequency' (aliases: schedule, interval, recurrence, cadence, period)
        cadence = (
            row.get("frequency")
            or ""
        ).strip() or "Annual"

        # due date: canonical key is 'next_due' (aliases: next date, due_date, due date, upcoming, deadline)
        due_date = (
            row.get("next_due")
            or row.get("last_performed")
            or ""
        )
        if due_date and not isinstance(due_date, str):
            due_date = str(due_date)
        due_date = (due_date or "").strip() or None

        # status: canonical key is 'status' (aliases: state, result, outcome, finding, completion)
        status = (
            row.get("status")
            or "Pending"
        ).strip()

        entry: dict = {
            "activity":    activity,
            "cadence":     cadence,
            "responsible": responsible,
            "status":      status,
        }
        if due_date:
            entry["due_date"] = due_date
        if row.get("notes"):
            entry["notes"] = str(row["notes"]).strip()

        calendar.append(entry)
    return calendar

# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def build_framework_aware_assessment(
    framework_id: str,
    routing: dict,
    uploaded_controls: list[dict],
    assessment_name: str = "",
    scope: str = "",
    priority: str = "",
    notes: str = "",
    all_sheets: list[dict] | None = None,
) -> dict:
    """
    Build a framework-aware assessment from routing results and optional uploaded controls.

    Returns a structured payload with clearly separated concepts:
      framework_gap_analysis  — what the framework requires but is missing
      risk_register           — actual risks from uploaded risk register sheet
      vendor_findings         — from uploaded vendor data
      network_findings        — from uploaded network rules data
      recommended_actions     — specific actions per framework + data context
      insights                — framework-specific narrative summary
    """
    from services.framework_loader import load_framework

    no_controls  = routing.get("no_controls_detected", True) or not uploaded_controls
    present_types = _get_present_sheet_types(routing)

    # ── 1. Load framework ─────────────────────────────────────────────────
    try:
        framework_data = load_framework(framework_id)
    except ValueError as exc:
        return {"success": False, "message": str(exc), "framework": framework_id}

    framework_label = framework_data["framework"]
    all_sections    = framework_data.get("sections", [])

    # ── 2. Filter controls to data context ───────────────────────────────
    relevant_controls = _filter_relevant_controls(all_sections, present_types)
    if not relevant_controls:
        relevant_controls = [
            {**c, "section_key": s.get("section_key", ""),
             "section_name": s.get("section_name", "")}
            for s in all_sections for c in s.get("controls", [])
        ]

    # ── 3. Annotate controls ──────────────────────────────────────────────
    import logging, os
    _builder_log = logging.getLogger("runtime_proof")
    if not _builder_log.handlers:
        _builder_log.setLevel(logging.DEBUG)
        _fh = logging.FileHandler(
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "runtime_proof.log"),
            mode="a", encoding="utf-8",
        )
        _fh.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
        _builder_log.addHandler(_fh)
    _builder_log.warning("=" * 70)
    _builder_log.warning("[RUNTIME PROOF] build_framework_aware_assessment called")
    _builder_log.warning("[RUNTIME PROOF]   framework        : %s (%s)", framework_id, framework_label)
    _builder_log.warning("[RUNTIME PROOF]   no_controls      : %s", no_controls)
    _builder_log.warning("[RUNTIME PROOF]   present_types    : %s", sorted(present_types))
    _builder_log.warning("[RUNTIME PROOF]   relevant_controls: %d", len(relevant_controls))
    _builder_log.warning("[RUNTIME PROOF]   uploaded_controls: %d", len(uploaded_controls))
    _builder_log.warning("=" * 70)

    # ── 4. Assess Controls (Rule-Based Engine — PRIMARY) ─────────────────
    from services.rule_engine_bridge import evaluate_controls_with_rule_engine

    _builder_log.warning("[RUNTIME PROOF] >>> ENTERING RULE ENGINE PATH")
    _builder_log.warning("[RUNTIME PROOF]   framework_id     : %s", framework_id)

    relevant_controls = evaluate_controls_with_rule_engine(
        framework_id=framework_id,
        controls=relevant_controls,
        routing=routing,
        present_types=present_types,
        all_sheets=all_sheets,
    )

    if no_controls:
        mode_label = "Rule-Based Assessment — Controls evaluated from rule engine + JSON config"
    else:
        mode_label = "Hybrid Rule-Based Assessment — Rule engine + uploaded control overrides"
        # Override with explicit manual mappings from uploaded controls sheet
        relevant_controls = _map_controls_to_framework(uploaded_controls, relevant_controls)
    # ── 4b. High-Risk sheet boost ────────────────────────────────────────
    #   If a High-Risk mapping sheet is present, use its ISO control
    #   references as HIGH-CONFIDENCE evidence to boost control statuses.
    high_risk_result = next(
        (r for r in routing.get("routing_results", [])
         if r.get("source_type") == "high_risk" and r.get("total_records", 0) > 0),
        None,
    )
    cross_framework_mapping = []
    if high_risk_result:
        parsed_risks = high_risk_result.get("parsed_risks", [])
        all_iso_refs = set(high_risk_result.get("all_iso_controls_referenced", []))
        _builder_log.warning("[RUNTIME PROOF] >>> HIGH-RISK boost: %d risks, %d ISO refs",
                             len(parsed_risks), len(all_iso_refs))

        # Build lookup: ISO control ref -> set of risk IDs referencing it
        from services.cross_framework_map import _normalize_control_ref
        ref_to_risks: dict[str, list[str]] = {}
        for risk in parsed_risks:
            for iso_ref in risk.get("iso_controls", []):
                norm = _normalize_control_ref(iso_ref)
                ref_to_risks.setdefault(norm, []).append(risk.get("risk_id", ""))

        # Boost controls that are referenced by high-risk entries
        for ctrl in relevant_controls:
            ctrl_ref = _normalize_control_ref(ctrl.get("control", ctrl.get("rule_id", "")))
            if ctrl_ref in ref_to_risks:
                # High-risk sheet references this control → strong evidence
                current = ctrl.get("status", "missing")
                if current == "missing":
                    ctrl["status"] = "partial"
                    ctrl["has_evidence"] = True
                    ctrl["reason"] = (
                        f"Referenced by high-risk mapping "
                        f"(risks: {', '.join(ref_to_risks[ctrl_ref][:3])}). "
                        f"Partial evidence from risk analysis."
                    )
                    ctrl["source"] = "high_risk_mapping"
                elif current == "partial":
                    ctrl["status"] = "compliant"
                    ctrl["has_evidence"] = True
                    ctrl["reason"] = (
                        f"Strong evidence: referenced by high-risk mapping "
                        f"AND supported by organizational data."
                    )
                    ctrl["source"] = "high_risk_boosted"
                # If already compliant, keep it

        # Build cross-framework mapping output
        cross_framework_mapping = parsed_risks

    # ── 5. Score (framework controls only) ───────────────────────────────
    fw_norm = framework_id.lower().replace(" ", "").replace("-", "").replace("_", "")
    if "pci" in fw_norm:
        # PCI DSS: use risk-based scoring engine
        from services.evidence_inference import compute_pci_risk_based_score
        score_data = compute_pci_risk_based_score(
            controls=relevant_controls,
            routing=routing,
            all_sheets=all_sheets,
        )
    else:
        score_data = _score_flat(relevant_controls)

    # ── 6. Rebuild sections ───────────────────────────────────────────────
    sections  = _build_sections(relevant_controls)
    severity  = _severity_breakdown(relevant_controls)

    # ── 7. Framework gap analysis (separate from risk register) ───────────
    gap_analysis = _build_gap_analysis(relevant_controls, framework_label)

    # ── 7. Risk register — from UPLOADED risk sheet + generated from data gaps
    uploaded_risk_register = _build_risk_register_from_routing(routing)

    # Generate additional risks from data patterns and control gaps
    from services.contextual_risk_generator import generate_risks_from_data
    generated_risks = generate_risks_from_data(routing, relevant_controls, present_types, all_sheets=all_sheets, framework_id=framework_id)

    # PCI DSS: also generate PCI-specific dynamic risks from data analysis
    if "pci" in fw_norm:
        from services.evidence_inference import generate_pci_dynamic_risks
        pci_risks = generate_pci_dynamic_risks(routing, relevant_controls, all_sheets)
        # Merge PCI risks, avoiding duplicates by risk_name
        existing_names = {r.get("risk_name", "").lower() for r in generated_risks}
        for pr in pci_risks:
            if pr.get("risk_name", "").lower() not in existing_names:
                generated_risks.append(pr)
                existing_names.add(pr.get("risk_name", "").lower())
    # Normalize uploaded risks (if any)
    uploaded_rr_entries = []
    if all_sheets:
        rr_sheet = next((s for s in all_sheets if s.get("type") == "risk_register"), None)
        if rr_sheet:
            for i, row in enumerate(rr_sheet.get("rows", [])):
                stmt = (row.get("risk_statement") or row.get("risk_name") or "").strip()
                threat = (row.get("threat") or "").strip()
                ctrl = (row.get("mitigation") or row.get("control") or "").strip()
                
                # Filter out empty or generic rows per user request
                if not stmt:
                    continue
                if threat == "Unspecified Threat":
                    continue
                if "Mapped via ISO" in ctrl:
                    continue

                uploaded_rr_entries.append({
                    "risk_id": row.get("risk_id") or f"U{i+1}",
                    "risk_statement": stmt,
                    "asset": row.get("asset") or "Business Asset",
                    "threat": threat or "Identified Risk",
                    "likelihood": row.get("likelihood") or 3,
                    "impact": row.get("impact") or 3,
                    "risk_level": row.get("risk_level") or row.get("level") or "Medium",
                    "control": ctrl or "Pending Mitigation",
                    "owner": row.get("owner") or "Risk Owner",
                    "source": "uploaded",
                    "source_label": "Uploaded Risk Heatmap",
                })

    # Merge: uploaded risks take priority, generated risks supplement
    all_risks = uploaded_risk_register.get("findings", []) if uploaded_risk_register.get("source") != "none" else []
    risk_register = {
        "source":          uploaded_risk_register.get("source", "none"),
        "source_sheet":    uploaded_risk_register.get("source_sheet", ""),
        "total_risks":     uploaded_risk_register.get("total_risks", 0) + len(generated_risks),
        "uploaded_risks":  uploaded_risk_register.get("total_risks", 0),
        "generated_risks": len(generated_risks),
        "high_risks":      uploaded_risk_register.get("high_risks", 0) + sum(1 for r in generated_risks if r.get("risk_level", "").lower() in ("high", "critical")),
        "medium_risks":    uploaded_risk_register.get("medium_risks", 0) + sum(1 for r in generated_risks if r.get("risk_level", "").lower() == "medium"),
        "low_risks":       uploaded_risk_register.get("low_risks", 0) + sum(1 for r in generated_risks if r.get("risk_level", "").lower() == "low"),
        "by_level":        uploaded_risk_register.get("by_level", {}),
        "untreated_count": uploaded_risk_register.get("untreated_count", 0),
        "untreated_risks": uploaded_risk_register.get("untreated_risks", []),
        "findings":        all_risks,
        "generated_risk_entries": generated_risks,
        "uploaded_risk_entries": uploaded_rr_entries,
    }

    def _is_placeholder(r) -> bool:
        if not isinstance(r, dict):
            return False
        rid = str(r.get("risk_id", r.get("id", "")))
        th = str(r.get("threat", ""))
        ct = str(r.get("control", r.get("mitigation", "")))
        ast = str(r.get("asset", ""))
        if rid.startswith("RSK-"): return True
        if th == "Identified Risk": return True
        if "Mapped via ISO27001" in ct: return True
        if ast == "Business Asset": return True
        return False

    risk_register["generated_risk_entries"] = [r for r in risk_register["generated_risk_entries"] if not _is_placeholder(r)]
    risk_register["uploaded_risk_entries"] = [r for r in risk_register["uploaded_risk_entries"] if not _is_placeholder(r)]
    risk_register["findings"] = [r for r in risk_register["findings"] if not _is_placeholder(r)]
    risk_register["untreated_risks"] = [r for r in risk_register["untreated_risks"] if not _is_placeholder(r)]

    if "pci" in fw_norm:
        def normalize_final_pci_risks(final_risks: list[dict]) -> list[dict]:
            groups = {}
            
            for r in final_risks:
                text_blob = " ".join(str(v) for v in r.values()).lower()
                if any(x in text_blob for x in ("evidence input only", "system should infer", "evidence for third-party", "prompt", "instruction")):
                    continue
                
                asset = str(r.get("asset", "")).strip()
                if asset.lower() in ("asset id", "vendor id", "employee id", "rule id", "policy id", "asset_id", "vendor_name", "asset_name", "vendor name", "asset name", "unnamed asset"):
                    continue

                stmt = str(r.get("risk_statement") or r.get("risk_name") or "").strip()
                ctrl = str(r.get("control") or r.get("mitigation") or r.get("controls") or r.get("pci_requirement") or "").strip()
                threat = str(r.get("threat", "Unspecified Threat")).strip()
                pci_req = str(r.get("pci_requirement") or r.get("controls") or "").strip()
                
                try:
                    lh = int(r.get("likelihood", 3))
                    imp = int(r.get("impact", 3))
                except (ValueError, TypeError):
                    lh, imp = 3, 3
                score = lh * imp
                
                # Identify critical risks (encryption, exposure, patches, MFA)
                is_critical = False
                stmt_lower = stmt.lower()
                if any(x in stmt_lower or x in threat.lower() for x in (
                    "cardholder", "unencrypted", "patch", "mfa", "multi-factor", "internet-exposed", "sql injection", "default-allow", "default allow"
                )):
                    is_critical = True
                    # Boost critical risks to ensure they appear in the top 5
                    if score < 16:
                        score = 16
                
                # 1. Strict Semantic Deduplication Key: Same Root Cause (Threat) + Same PCI Req
                group_key = (threat.lower(), pci_req.lower())
                
                if group_key not in groups:
                    groups[group_key] = {
                        "risks": [],
                        "assets": [],
                        "stmts": []
                    }
                
                groups[group_key]["risks"].append((score, is_critical, r))
                if asset and asset not in groups[group_key]["assets"]:
                    groups[group_key]["assets"].append(asset)
                if stmt not in groups[group_key]["stmts"]:
                    groups[group_key]["stmts"].append(stmt)
                    
            collapsed = []
            for gkey, gdata in groups.items():
                # Pick strongest version
                gdata["risks"].sort(key=lambda x: (x[0], x[1]), reverse=True)
                best_score, best_is_crit, best_r = gdata["risks"][0]
                base = dict(best_r)
                
                assets = gdata["assets"]
                stmts = gdata["stmts"]
                threat_name = base.get("threat", "Identified Risk")
                tl = threat_name.lower()
                
                if len(assets) > 1:
                    if "unmanaged" in tl:
                        base["risk_statement"] = "Multiple unmanaged assets detected bypassing security controls"
                    elif "vendor" in tl or "supply chain" in tl or "third-party" in tl:
                        base["risk_statement"] = f"Vendor compliance gaps detected across {len(assets)} third-party suppliers"
                    elif "training" in tl or "phish" in tl:
                        base["risk_statement"] = "Workforce training gaps detected increasing social engineering susceptibility"
                    elif "network" in tl or "misconfiguration" in tl or "default-allow" in tl:
                        if any("rule" in s.lower() or "allow" in s.lower() for s in stmts):
                            base["risk_statement"] = f"Overly permissive network rules detected across {len(assets)} configurations"
                        else:
                            base["risk_statement"] = f"Multiple {tl} vulnerabilities detected across {len(assets)} assets"
                    else:
                        base["risk_statement"] = f"Systemic {tl} risk identified affecting {len(assets)} assets"
                        
                    if len(assets) > 8:
                        base["asset"] = ", ".join(assets[:8]) + f" (+{len(assets) - 8} others)"
                    else:
                        base["asset"] = ", ".join(assets)
                
                # 2. Priority Filtering: flag generic weak risks
                is_generic = False
                if "unmanaged" in tl or "vendor" in tl or "training" in tl:
                    # Downgrade generic risks if they are not explicitly high/critical
                    if best_score < 12:
                        is_generic = True
                
                collapsed.append({
                    "score": best_score,
                    "is_critical": best_is_crit,
                    "is_generic": is_generic,
                    "risk": base
                })
                
            def normalize_text(text: str) -> str:
                t = text.lower().strip()
                if "deny rule" in t or "default-allow" in t or "unrestricted network" in t:
                    return "default allow network configuration"
                if "training" in t or "phish" in t:
                    return "workforce training gaps"
                if "vendor" in t or "third-party" in t or "supply chain" in t:
                    return "vendor compliance gaps"
                return t
                
            # 3. Final Deduplication (Strict)
            final_deduped = {}
            for item in collapsed:
                r = item["risk"]
                stmt_norm = normalize_text(r.get("risk_statement", ""))
                th_norm = r.get("threat", "").lower().strip()
                ctrl_norm = r.get("control", r.get("mitigation", "")).lower().strip()
                
                key = (th_norm, stmt_norm, ctrl_norm)
                if key not in final_deduped:
                    final_deduped[key] = item
                else:
                    # Keep the highest impact x likelihood
                    if item["score"] > final_deduped[key]["score"]:
                        final_deduped[key] = item
                        
            # 4. Final Sort & Cut (Target 10-12 risks max)
            final_list = list(final_deduped.values())
            final_list.sort(key=lambda x: (x["score"], x["is_critical"], not x["is_generic"]), reverse=True)
            
            final_cleaned = []
            for item in final_list[:12]:
                final_cleaned.append(item["risk"])
                
            # 5. Final Sequencing
            for i, risk in enumerate(final_cleaned, start=1):
                risk["risk_id"] = f"PCI-R{str(i).zfill(3)}"
                
            return final_cleaned

        all_pci_risks = risk_register["generated_risk_entries"] + risk_register["uploaded_risk_entries"]
        final_pci_risks = normalize_final_pci_risks(all_pci_risks)
        
        print("FINAL PCI RISK IDS:", [r.get("risk_id") for r in final_pci_risks])
        print("FINAL PCI RISK COUNT:", len(final_pci_risks))
        
        risk_register["generated_risk_entries"] = final_pci_risks
        risk_register["uploaded_risk_entries"] = []

    # ── 8. Treatment plan — applied to ALL risks (uploaded + generated)
    all_risks_for_treatment = [
        {
            "rule_id":      c.get("rule_id", c.get("risk_id", "")),
            "control_id":   c.get("rule_id", c.get("risk_id", "")),
            "control_name": c.get("name", c.get("risk_name", "")),
            "name":         c.get("name", c.get("risk_name", "Unknown")),
            "status":       c.get("status", "missing"),
            "severity":     c.get("severity", c.get("risk_level", "medium")),
        }
        for c in relevant_controls
        if c.get("status") in ("missing", "partial")
        and (c.get("severity") or "").lower() in ("critical", "high")
    ]
    # Add generated risks to treatment plan
    for gr in risk_register["generated_risk_entries"]:
        all_risks_for_treatment.append({
            "rule_id":      gr.get("risk_id", ""),
            "control_id":   gr.get("risk_id", ""),
            "control_name": gr.get("risk_name", ""),
            "name":         gr.get("risk_name", "Unknown"),
            "status":       "identified",
            "severity":     gr.get("risk_level", "medium"),
            "threat":       gr.get("threat", ""),
            "risk_statement": gr.get("risk_statement", ""),
            "control":      gr.get("control", ""),
            "asset":        gr.get("asset", "")
        })

    # ── 8. Risk-based treatment plan — one action per Risk Register row ──
    #   Uses the new services/treatment_plan_generator which provides
    #   framework-aware treatment text and severity-driven due dates.
    from services.treatment_plan_generator import generate_treatment_plan as generate_risk_treatment
    all_rr_entries = (
        risk_register.get("generated_risk_entries", [])
        + risk_register.get("uploaded_risk_entries", [])
    )
    risk_treatment_plan = generate_risk_treatment(
        risks=all_rr_entries,
        framework_id=framework_id,
    )
    
    # Assign it to both for backward compatibility with older frontends,
    # but using the new robust generator.
    treatment_plan = {
        "total_actions": len(risk_treatment_plan),
        "framework": framework_id,
        "remediation_source": "risk_driven",
        "actions": risk_treatment_plan
    }

    # ── 9. Contextual findings ────────────────────────────────────────────
    vendor_findings  = _extract_vendor_findings(routing)
    network_findings = _extract_network_findings(routing)
    asset_findings   = _extract_asset_findings(routing)

    # ── 10. Recommended actions ───────────────────────────────────────────
    recommended_actions = _build_recommended_actions(
        framework_id, relevant_controls, routing, present_types
    )

    # ── 11. Insights ──────────────────────────────────────────────────────
    insights = _build_insights(
        framework_id, framework_label, score_data, routing, no_controls, present_types
    )

    # ── 12. SoA ───────────────────────────────────────────────────────────
    # Moved to after Risk Register generation to allow risk-aware status mapping

    # ── 13. Compliance Matrix ─────────────────────────────────────────────
    from services.evidence_inference import build_compliance_matrix
    compliance_matrix = build_compliance_matrix(relevant_controls, framework_label)

    # ── 14. Training Matrix (backend-generated, framework-aware) ──────────
    from services.training_matrix_generator import generate_training_matrix
    _emp_sheet = next((s for s in (all_sheets or []) if s.get("type") == "employees"), None)
    _raw_employees = _emp_sheet.get("rows", []) if _emp_sheet else []
    training_matrix_generated = generate_training_matrix(
        employees=_raw_employees,
        risks=(
            risk_register.get("generated_risk_entries", [])
            + risk_register.get("uploaded_risk_entries", [])
        ),
        framework_id=framework_id,
        all_sheets=all_sheets,
    )

    # ── 15. Governance Calendar (backend-generated, framework-aware) ──────
    from services.governance_calendar_generator import generate_governance_calendar
    governance_calendar_generated = generate_governance_calendar(
        risks=(
            risk_register.get("generated_risk_entries", [])
            + risk_register.get("uploaded_risk_entries", [])
        ),
        framework_id=framework_id,
    )
    # ── FINAL UI DEDUPLICATION PASS ───────────────────────────────────────
    if "pci" in fw_norm:
        def get_theme(text: str) -> str:
            t = text.lower()
            if any(x in t for x in ("default-allow", "no explicit deny", "unrestricted network access")):
                return "default_allow_network"
            if any(x in t for x in ("lack security training", "security awareness", "phishing susceptibility", "training")):
                return "workforce_training_gap"
            if any(x in t for x in ("vendor compliance", "third-party suppliers", "lack compliance certification", "vendor")):
                return "vendor_compliance_gap"
            return t.strip()

        final_list = risk_register.get("generated_risk_entries", []) + risk_register.get("uploaded_risk_entries", [])
        
        final_deduped = {}
        for r in final_list:
            stmt = str(r.get("risk_statement") or "").strip()
            theme = get_theme(stmt)
            
            try:
                score = int(r.get("likelihood", 3)) * int(r.get("impact", 3))
            except:
                score = 9
                
            if theme not in final_deduped:
                final_deduped[theme] = {"score": score, "risk": r}
            else:
                if score > final_deduped[theme]["score"]:
                    final_deduped[theme] = {"score": score, "risk": r}
                    
        # Apply final list and re-sequence
        final_risks = [item["risk"] for item in final_deduped.values()]
        
        for i, risk in enumerate(final_risks, start=1):
            risk["risk_id"] = f"PCI-R{i:03d}"
            
        risk_register["generated_risk_entries"] = final_risks
        risk_register["uploaded_risk_entries"] = []
        
        print("UI RISK REGISTER COUNT:", len(risk_register["generated_risk_entries"]))
        print("UI RISK REGISTER STATEMENTS:", [r.get("risk_statement") for r in risk_register["generated_risk_entries"]])

        # ── OVERRIDE PCI RISK TREATMENT PLAN (1:1 with Risk Register) ──
        pci_treatment_actions = []
        from datetime import timedelta
        import re
        
        for r in final_risks:
            stmt = str(r.get("risk_statement", ""))
            threat_txt = str(r.get("threat", ""))
            ctrl_txt = str(r.get("control", ""))
            
            # Normalize text for matching: replace punctuation with space so 'default-allow' becomes 'default allow'
            full_text = f"{stmt} {threat_txt} {ctrl_txt}".lower()
            full_text = re.sub(r'[^\w\s]', ' ', full_text)
            
            # Action Mapping - Guaranteed Coverage with Strict Priority Evaluation
            if any(k in full_text for k in ("database exposed", "public database", "sql injection", "database")):
                action = "Restrict database access via firewall rules and disable public exposure"
            elif any(k in full_text for k in ("default allow", "no explicit deny", "no deny rules", "unrestricted network", "unrestricted access", "permissive network", "network rules")):
                action = "Implement deny-by-default firewall policy and restrict inbound traffic"
            elif any(k in full_text for k in ("network segmentation", "segmentation", "flat network", "isolate")):
                action = "Implement network segmentation to isolate critical systems and cardholder data"
            elif any(k in full_text for k in ("training", "phish", "awareness", "social engineering", "lack security training")):
                action = "Implement mandatory security awareness training program"
            elif any(k in full_text for k in ("insider", "least privilege", "privilege")):
                action = "Implement user monitoring, access controls, and least privilege enforcement"
            elif any(k in full_text for k in ("vendor", "third party", "thirdparty", "supply chain", "supplier", "compliance certification")):
                action = "Perform vendor risk assessment and enforce PCI compliance requirements"
            elif any(k in full_text for k in ("accountability", "ownership", "responsibility")):
                action = "Assign asset ownership and define responsibility for all systems"
            elif any(k in full_text for k in ("malware", "antivirus", "ransomware", "virus", "endpoint protection")):
                action = "Deploy and maintain anti-malware solutions across all endpoints"
            elif any(k in full_text for k in ("patch", "vulnerabilit", "update")):
                action = "Implement automated patch management and remediate missing patches"
            elif any(k in full_text for k in ("cardholder", "unencrypted", "encryption", "plaintext", "cleartext", "tls", "cryptograph")):
                action = "Encrypt cardholder data at rest and in transit using strong cryptography"
            elif any(k in full_text for k in ("mfa", "multi factor", "multifactor", "authentication", "password")):
                action = "Enforce Multi-Factor Authentication (MFA) for all administrative and remote access"
            elif any(k in full_text for k in ("unmanaged", "inventory", "unknown asset", "asset management", "unauthorized")):
                action = "Establish asset inventory and continuous asset monitoring program"
            else:
                # Absolute fallback mapped to asset management to avoid generic wording
                action = "Establish asset inventory and continuous asset monitoring program"
            
            # Priority Mapping
            level = str(r.get("risk_level", "Medium")).capitalize()
            if level in ("Extreme", "Critical"):
                priority = "Critical"
                days = 7
            elif level == "High":
                priority = "High"
                days = 14
            elif level == "Low":
                priority = "Low"
                days = 60
            else:
                priority = "Medium"
                days = 30
                
            # Owner Mapping based on the chosen action
            owner = "IT Security"
            action_lower = action.lower()
            if "network" in action_lower or "firewall" in action_lower or "segmentation" in action_lower:
                owner = "Network / DevOps"
            elif "training" in action_lower or "awareness" in action_lower:
                owner = "HR / Security"
            elif "vendor" in action_lower or "supplier" in action_lower:
                owner = "Procurement / Security"
            elif "database" in action_lower or "sql" in action_lower:
                owner = "DBA / Security"
            
            due_date = (datetime.now(timezone.utc) + timedelta(days=days)).strftime("%Y-%m-%d")
            
            pci_treatment_actions.append({
                "risk_id": r.get("risk_id", ""),
                "rule_id": r.get("risk_id", ""),
                "risk_statement": stmt,
                "treatment": action,
                "action": action,
                "recommended_action": action,
                "priority": priority,
                "severity": priority,
                "owner": owner,
                "timeline": f"{days} days",
                "due_date": due_date,
                "status": "Open"
            })
            
        risk_treatment_plan = pci_treatment_actions
        treatment_plan["actions"] = pci_treatment_actions
        treatment_plan["total_actions"] = len(pci_treatment_actions)
        treatment_plan["remediation_source"] = "risk_register_direct"

    # ── 12. SoA (Risk-Aware) ──────────────────────────────────────────────
    soa_risks = risk_register.get("generated_risk_entries", []) + risk_register.get("uploaded_risk_entries", [])
    soa = _build_soa(relevant_controls, framework_id, risks=soa_risks)

    # ── 16. Assemble response ─────────────────────────────────────────────
    response = {
        "success":          True,
        "message":          f"{framework_label} — {mode_label} completed.",
        "assessment_id":    str(uuid.uuid4()),
        "framework":        framework_label,
        "framework_id":     framework_id,
        "assessment_name":  assessment_name,
        "scope":            scope,
        "priority":         priority,
        "notes":            notes,
        "created_at":       datetime.now(timezone.utc).isoformat(),
        "mode_label":       mode_label,
        "no_controls_detected": no_controls,
        "evidence_backed":  not no_controls,
        "evidence_source":  "uploaded_controls_sheet" if not no_controls else "framework_baseline",

        # Data context
        "present_data_types":        sorted(present_types),
        "relevant_controls_count":   len(relevant_controls),
        "total_framework_controls":  framework_data.get("total_controls", 0),

        # Compliance score (framework controls)
        "compliance_score":   score_data["compliance_score"],
        "total_controls":     score_data["total_controls"],
        "compliant_controls": score_data["compliant_controls"],
        "partial_controls":   score_data["partial_controls"],
        "missing_controls":   score_data["missing_controls"],

        # Sections + severity (for charts)
        "total_sections":   len(sections),
        "sections":         sections,
        "severity_summary": severity,

        # ── SEPARATED CONCEPTS ────────────────────────────────────────────

        # 1. Framework control gaps (what compliance framework requires but is missing)
        "framework_gap_analysis": gap_analysis,

        # 2. Risk register — from UPLOADED risk data (not from missing controls)
        "risk_register": risk_register,

        # 3. Treatment plan — for high/critical framework gaps
        "treatment_plan": treatment_plan,

        # 3b. Risk-based treatment plan — one action per Risk Register entry
        "risk_treatment_plan": risk_treatment_plan,

        # 4. Contextual data findings
        "vendor_findings":  vendor_findings,
        "network_findings": network_findings,
        "asset_findings":   asset_findings,

        # 5. Specific recommended actions (framework + data driven)
        "recommended_actions": recommended_actions,

        # 6. Narrative insights
        "insights":              insights,
        "top_missing_high_risk": gap_analysis["top_critical_gaps"],

        # 7. Statement of Applicability
        "soa": soa,

        # 8. Compliance Matrix (requirements → inferred controls → gaps → remediation)
        "compliance_matrix": compliance_matrix,

        # 9. Extra matrices based on user request logic
        "vendor_checklist": _build_vendor_checklist(all_sheets, framework_id),
        "training_matrix": _build_training_matrix(all_sheets),
        "training_matrix_generated": training_matrix_generated,
        "governance_calendar": _build_governance_calendar(all_sheets),
        "governance_calendar_generated": governance_calendar_generated,

        # 10. Cross-Framework Mapping (from High-Risk sheet)
        "cross_framework_mapping": [r for r in cross_framework_mapping if not _is_placeholder(r)],
        "has_high_risk_data": len([r for r in cross_framework_mapping if not _is_placeholder(r)]) > 0,

        # 12. Traceability
        "traceability": {
            "framework_id":       framework_id,
            "framework_label":    framework_label,
            "no_controls_detected": no_controls,
            "data_context":       sorted(present_types),
            "controls_from_upload": sum(
                1 for c in relevant_controls if c.get("source") == "uploaded"
            ),
            "controls_inferred":  sum(
                1 for c in relevant_controls if c.get("source") == "framework_derived"
            ),
            "run_id":             routing.get("run_id", ""),
            "routing_timestamp":  routing.get("timestamp", ""),
        },
    }

    # ── 17. PCI DSS FINAL SoA OVERRIDE (on sections — the actual UI source) ──
    # The frontend builds the SOA tab from response.sections for non-HIPAA frameworks.
    # This block runs AFTER risk dedup, AFTER response assembly, RIGHT BEFORE return.
    # NOTE: framework_id comes in as "PCI DSS" (with space) from the frontend,
    #       so we use fw_norm (defined at line 1138) which strips spaces/dashes.
    if "pci" in fw_norm:
        # ── DEBUG: Inspect actual control object shape ──
        print("=" * 80)
        print("FRAMEWORK ID:", framework_id)
        print("SECTION COUNT:", len(response.get("sections", [])))
        print("SECTION SAMPLE:", response["sections"][0] if response.get("sections") else None)
        for sec in response.get("sections", []):
            for c in sec.get("controls", []):
                print("CONTROL OBJECT:", c)
        print("=" * 80)

        # ── Build risk text from final risk register ──
        final_risks = response["risk_register"].get("generated_risk_entries", [])
        risk_text = " ".join([
            f"{r.get('risk_statement', '')} {r.get('threat', '')} {r.get('control', '')}"
            for r in final_risks
        ]).lower()

        has_default_allow = any(k in risk_text for k in ("default-allow", "default allow", "no explicit deny", "permissive rules", "permissive network", "unrestricted network", "overly permissive"))
        has_segmentation  = any(k in risk_text for k in ("network segmentation", "segmentation", "isolate", "flat network"))
        has_vendor        = any(k in risk_text for k in ("vendor", "third-party", "third party", "supply chain", "supplier", "service provider"))
        has_training      = any(k in risk_text for k in ("training", "security awareness", "accountability", "phish", "social engineering"))
        has_malware       = any(k in risk_text for k in ("malware", "antivirus", "virus", "ransomware", "endpoint protection"))
        has_db_exposed    = any(k in risk_text for k in ("database exposed", "public database", "database accessible from internet", "internet-accessible database", "sql injection"))

        print(f"[PCI SoA] risk_text length={len(risk_text)}")
        print(f"[PCI SoA] has_default_allow={has_default_allow}, has_segmentation={has_segmentation}, has_vendor={has_vendor}, has_training={has_training}, has_malware={has_malware}, has_db_exposed={has_db_exposed}")

        # ── Apply overrides to EVERY control in sections ──
        for section in response.get("sections", []):
            for c in section.get("controls", []):
                # Resolve control key from ALL possible fields
                control_key = (
                    c.get("rule_id")
                    or c.get("control_no")
                    or c.get("id")
                    or c.get("control_id")
                    or c.get("control")
                    or ""
                )
                control_title = (c.get("title") or c.get("control_title") or c.get("name") or "").lower()
                cur_status = (c.get("status") or "").lower()

                # ── Assign domain so frontend avoids "System Inference Engine" ──
                if any(k in control_title for k in ("network", "firewall", "segmentation", "permissive", "port", "protocol", "overly")):
                    c["domain"] = "technological"
                elif any(k in control_title for k in ("vendor", "provider", "third-party", "supply", "service provider")):
                    c["domain"] = "vendor"
                elif any(k in control_title for k in ("malware", "antivirus", "endpoint", "anti-malware")):
                    c["domain"] = "technological"
                elif any(k in control_title for k in ("encrypt", "protect", "stored", "transmission", "develop", "secure", "patch", "vulnerability", "configuration")):
                    c["domain"] = "technological"
                elif any(k in control_title for k in ("physical", "restrict physical")):
                    c["domain"] = "physical"
                elif any(k in control_title for k in ("policy", "governance", "training", "access", "awareness", "accountability", "security management", "information security", "incident", "log", "monitor", "identify", "authenticate", "restrict access")):
                    c["domain"] = "organizational"
                else:
                    c["domain"] = "organizational"

                # ── Match by BOTH ID and title for robustness ──
                # PCI-003 / PCI-RE-003 / "overly permissive" / "no overly permissive"
                is_003 = control_key in ("PCI-003", "PCI-RE-003") or "overly permissive" in control_title or "permissive rules" in control_title
                # PCI-010 / PCI-RE-010 / "information security policy"
                is_010 = control_key in ("PCI-010", "PCI-RE-010") or "information security policy" in control_title
                # PCI-001 / PCI-RE-001 / "network security controls"
                is_001 = control_key in ("PCI-001", "PCI-RE-001") or "network security controls" in control_title
                # PCI-002 / PCI-RE-002 / "network segmentation"
                is_002 = control_key in ("PCI-002", "PCI-RE-002") or "network segmentation" in control_title
                # PCI-006 / PCI-RE-006 / "anti-malware"
                is_006 = control_key in ("PCI-006", "PCI-RE-006") or "anti-malware" in control_title
                # PCI-011 / PCI-RE-011 / "third-party" / "service provider"
                is_011 = control_key in ("PCI-011", "PCI-RE-011") or "third-party service provider" in control_title or "service provider management" in control_title
                # PCI-017 / PCI-RE-017 / "security awareness training"
                is_017 = control_key in ("PCI-017", "PCI-RE-017") or "security awareness training" in control_title

                # ── Apply risk-aware status overrides ──
                if is_003 and has_default_allow and cur_status == "compliant":
                    c["status"] = "partial"
                    c["domain"] = "technological"
                    print(f"[PCI SoA] OVERRIDE {control_key} -> PARTIAL (default-allow)")

                if is_001 and has_db_exposed and cur_status == "compliant":
                    c["status"] = "partial"
                    c["domain"] = "technological"
                    print(f"[PCI SoA] OVERRIDE {control_key} -> PARTIAL (db exposed)")

                if is_002 and has_segmentation and cur_status == "compliant":
                    c["status"] = "partial"
                    c["domain"] = "technological"
                    print(f"[PCI SoA] OVERRIDE {control_key} -> PARTIAL (segmentation)")

                if is_010 and has_training and cur_status == "compliant":
                    c["status"] = "partial"
                    c["domain"] = "organizational"
                    print(f"[PCI SoA] OVERRIDE {control_key} -> PARTIAL (training/policy)")

                if is_017 and has_training and cur_status == "compliant":
                    c["status"] = "partial"
                    c["domain"] = "organizational"
                    print(f"[PCI SoA] OVERRIDE {control_key} -> PARTIAL (awareness training)")

                if is_011 and has_vendor and cur_status == "compliant":
                    c["status"] = "partial"
                    c["domain"] = "vendor"
                    print(f"[PCI SoA] OVERRIDE {control_key} -> PARTIAL (vendor)")

                if is_006 and has_malware and cur_status == "compliant":
                    c["status"] = "partial"
                    c["domain"] = "technological"
                    print(f"[PCI SoA] OVERRIDE {control_key} -> PARTIAL (malware)")

        # ── Sync soa["entries"] from the now-modified sections ──
        final_soa_entries = []
        for section in response.get("sections", []):
            for c in section.get("controls", []):
                control_key = c.get("rule_id") or c.get("control_no") or c.get("id") or c.get("control_id") or c.get("control") or ""
                control_title = (c.get("title") or c.get("control_title") or c.get("name") or "").lower()
                status = (c.get("status") or "missing").lower()
                domain = (c.get("domain") or "").lower()

                # Reference from domain
                if "vendor" in domain or "supplier" in domain:
                    reference = "Vendor Records / Third-Party Data"
                elif "technological" in domain:
                    reference = "Network Rules / Asset Data"
                elif "organizational" in domain:
                    reference = "Employee Records / Governance Data"
                elif "physical" in domain:
                    reference = "Asset Inventory / Facilities Data"
                else:
                    reference = "Organizational Data"

                # Implementation text
                if status == "compliant":
                    impl = "Control is implemented and supported by available data context."
                elif status == "partial":
                    impl = "Control is partially implemented; improvements required."
                else:
                    impl = "Control is not implemented; no supporting evidence found."

                final_soa_entries.append({
                    "section": section.get("section_name", section.get("section_key", "")),
                    "control_no": str(control_key),
                    "control_title": c.get("name") or c.get("title") or c.get("control_title") or "",
                    "applicable": "Yes",
                    "remarks": "N/A",
                    "implementation": impl,
                    "reference": reference,
                    "status": status,
                })

        response["soa"]["entries"] = final_soa_entries
        response["statement_of_applicability"] = final_soa_entries

        print("AFTER PCI SOA OVERRIDE:", [(c.get("rule_id"), c.get("control_no"), c.get("title"), c.get("name"), c.get("status"), c.get("reference"), c.get("domain")) for s in response.get("sections", []) for c in s.get("controls", [])])

        # ── 18. Sync Compliance Matrix for PCI ──
        # Rebuild compliance matrix so it perfectly matches the overridden SoA sections, grouped by logical domain
        all_pci_controls = [c for s in response.get("sections", []) for c in s.get("controls", [])]
        
        matrix_groups = {}
        for c in all_pci_controls:
            cid = str(c.get("rule_id") or c.get("control_no") or c.get("id") or "").upper()
            
            domain_group = "General Requirements"
            if "001" in cid or "002" in cid or "003" in cid:
                domain_group = "Network Security"
            elif "004" in cid or "005" in cid:
                domain_group = "Data Protection"
            elif "006" in cid:
                domain_group = "Endpoint Security"
            elif "007" in cid or "008" in cid:
                domain_group = "Access Control"
            elif "009" in cid:
                domain_group = "Monitoring"
            elif "010" in cid:
                domain_group = "Governance"
            elif "011" in cid:
                domain_group = "Supplier Management"
            elif "012" in cid or "017" in cid:
                domain_group = "Incident & General Management"

            if domain_group not in matrix_groups:
                matrix_groups[domain_group] = []
            matrix_groups[domain_group].append(c)

        pci_matrix = []
        
        # Ensure consistent ordering
        domain_order = [
            "Network Security", "Data Protection", "Endpoint Security", 
            "Access Control", "Monitoring", "Governance", 
            "Supplier Management", "Incident & General Management", "General Requirements"
        ]
        
        for req_name in domain_order:
            if req_name not in matrix_groups:
                continue
            
            req_controls = matrix_groups[req_name]
            
            comp_list = []
            part_list = []
            miss_list = []
            gaps = []

            for c in req_controls:
                st = (c.get("status") or "missing").lower()
                cid = str(c.get("rule_id") or c.get("control_no") or c.get("id") or c.get("name") or "")
                cname = (c.get("name") or c.get("title") or "").lower()
                c_display_name = c.get("name") or c.get("title") or cid

                if st == "compliant":
                    comp_list.append(cid)
                elif st == "partial":
                    part_list.append(cid)
                    if cid in ("PCI-010", "PCI-RE-010") or "governance" in cname or "policy" in cname:
                        gaps.append(f"Workforce training and governance gaps identified in {c_display_name}")
                    elif "contingency" in cname or "backup" in cname:
                        gaps.append(f"{c_display_name} exists but is not fully tested")
                    else:
                        gaps.append(f"Inconsistent enforcement of {c_display_name.lower()}")
                else:
                    miss_list.append(cid)
                    if "policy" in cname or "govern" in cname or "management" in cname:
                        gaps.append(f"Lack of centralized {cname} governance or monitoring")
                    else:
                        gaps.append(f"Missing {cname} processes")

            if miss_list:
                req_status = "Missing"
            elif part_list:
                req_status = "Partial"
            else:
                req_status = "Compliant"

            mapped_controls_parts = []
            if comp_list:
                mapped_controls_parts.append(f"COMPLIANT:\n[{', '.join(comp_list)}]")
            if part_list:
                mapped_controls_parts.append(f"PARTIAL:\n[{', '.join(part_list)}]")
            if miss_list:
                mapped_controls_parts.append(f"MISSING:\n[{', '.join(miss_list)}]")

            mapped_controls = "\n\n".join(mapped_controls_parts)
            gaps_identified = " • ".join(gaps) if gaps else "No gaps identified."

            if req_status == "Compliant":
                remediation = "Maintain current controls and documentation."
            else:
                if req_name == "Network Security":
                    remediation = "Implement network segmentation, restrict inbound/outbound traffic, and enforce deny-by-default firewall rules to protect the cardholder data environment."
                elif req_name == "Data Protection":
                    remediation = "Ensure encryption of cardholder data at rest and in transit using strong cryptographic protocols and secure key management practices."
                elif req_name == "Endpoint Security":
                    remediation = "Deploy and maintain anti-malware solutions across all endpoints and implement continuous monitoring for malicious activity."
                elif req_name == "Access Control":
                    remediation = "Enforce least privilege access, implement strong authentication mechanisms, and apply multi-factor authentication for all sensitive systems."
                elif req_name == "Monitoring":
                    remediation = "Enable centralized logging, implement real-time monitoring, and establish alerting mechanisms for suspicious activities."
                elif req_name == "Governance":
                    remediation = "Develop and enforce information security policies, conduct regular security awareness training, and establish clear accountability structures."
                elif req_name == "Supplier Management":
                    remediation = "Perform vendor risk assessments, enforce PCI compliance requirements in contracts, and continuously monitor third-party security posture."
                elif req_name == "Incident & General Management":
                    remediation = "Establish and test an incident response plan, including detection, containment, eradication, and recovery procedures."
                else:
                    remediation = f"Enforce PCI DSS requirements for {req_name} across the cardholder data environment."

            pci_matrix.append({
                "Framework": "PCI DSS",
                "Requirement": req_name,
                "Status": req_status,
                "Mapped Controls": mapped_controls,
                "Gaps Identified": gaps_identified,
                "Remediation Plan": remediation
            })

        response["compliance_matrix"] = pci_matrix

        # ── Override Governance Calendar dynamically using finalized PCI data ──
        from services.governance_calendar_generator import generate_governance_calendar
        final_cal = generate_governance_calendar(
            risks=final_list,
            framework_id=framework_id,
            soa_sections=response.get("sections"),
            compliance_matrix=response.get("compliance_matrix"),
            vendor_checklist=response.get("vendor_checklist"),
            training_matrix=response.get("training_matrix_generated")
        )
        response["governance_calendar_generated"] = final_cal
        response["governance_calendar"] = final_cal
        print("FINAL PCI GOVERNANCE CALENDAR:", response.get("governance_calendar"))

    return response
