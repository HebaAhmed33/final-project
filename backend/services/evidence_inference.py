"""
Evidence Inference Engine — GRC Intelligence Core.

Infers ISO 27001 (and other framework) control compliance status from
uploaded organizational data instead of requiring a pre-built control register.

Maps each framework control to data-sheet types that can provide evidence,
examines actual uploaded data quality, and returns PASS / PARTIAL / MISSING.

This is the heart of the GRC intelligence platform:
  "I am not uploading controls, I am uploading reality.
   The system must build controls from it."
"""

from __future__ import annotations
import logging
import os

# File-based logger for runtime proof — guaranteed capture
_log = logging.getLogger("runtime_proof")
_log.setLevel(logging.DEBUG)
if not _log.handlers:
    _fh = logging.FileHandler(
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "runtime_proof.log"),
        mode="a", encoding="utf-8",
    )
    _fh.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
    _log.addHandler(_fh)


# ---------------------------------------------------------------------------
# Control → Evidence source mapping
# ---------------------------------------------------------------------------
# Each entry maps a control rule_id (or keyword pattern from control name/domain)
# to the sheet types + data signals that constitute evidence.
#
# evidence_sources: which sheet types provide evidence
# pass_signals: data conditions that indicate PASS
# partial_signals: data conditions that indicate PARTIAL

_ISO27001_EVIDENCE_MAP: dict[str, dict] = {
    # ── A5: Organizational Controls ──────────────────────────────────────
    "organizational controls": {
        "evidence_sources": ["governance", "risk_register"],
        "pass_signals": ["has_governance_activities", "has_risk_register"],
        "partial_signals": ["has_governance_activities", "has_risk_register"],
    },
    "information security policy": {
        "evidence_sources": ["governance", "controls"],
        "pass_signals": ["has_governance_activities"],
        "partial_signals": ["has_governance_activities"],
    },

    # ── A6: People Controls ──────────────────────────────────────────────
    "screening": {
        "evidence_sources": ["employees"],
        "pass_signals": ["has_employee_records"],
        "partial_signals": ["has_employee_records"],
    },
    "terms and conditions of employment": {
        "evidence_sources": ["employees"],
        "pass_signals": ["has_employee_records"],
        "partial_signals": ["has_employee_records"],
    },
    "information security awareness": {
        "evidence_sources": ["employees"],
        "pass_signals": ["high_training_coverage"],
        "partial_signals": ["has_some_training"],
    },
    "education and training": {
        "evidence_sources": ["employees"],
        "pass_signals": ["high_training_coverage"],
        "partial_signals": ["has_some_training"],
    },
    "disciplinary process": {
        "evidence_sources": ["governance", "employees"],
        "pass_signals": ["has_governance_activities"],
        "partial_signals": ["has_employee_records"],
    },
    "responsibilities after termination": {
        "evidence_sources": ["employees", "governance"],
        "pass_signals": ["has_employee_records", "has_governance_activities"],
        "partial_signals": ["has_employee_records"],
    },
    "confidentiality": {
        "evidence_sources": ["employees", "vendors"],
        "pass_signals": ["has_employee_records"],
        "partial_signals": ["has_employee_records"],
    },
    "non-disclosure": {
        "evidence_sources": ["employees", "vendors"],
        "pass_signals": ["has_employee_records"],
        "partial_signals": ["has_employee_records"],
    },
    "remote working": {
        "evidence_sources": ["network_rules", "employees"],
        "pass_signals": ["has_network_rules", "has_employee_records"],
        "partial_signals": ["has_network_rules"],
    },
    "information security event reporting": {
        "evidence_sources": ["governance", "risk_register"],
        "pass_signals": ["has_governance_activities"],
        "partial_signals": ["has_risk_register"],
    },

    # ── A7: Physical Controls ────────────────────────────────────────────
    "physical security perimeter": {
        "evidence_sources": ["assets"],
        "pass_signals": ["has_asset_inventory"],
        "partial_signals": ["has_asset_inventory"],
    },
    "physical entry": {
        "evidence_sources": ["assets", "employees"],
        "pass_signals": ["has_asset_inventory"],
        "partial_signals": ["has_asset_inventory"],
    },
    "securing offices": {
        "evidence_sources": ["assets"],
        "pass_signals": ["has_asset_inventory"],
        "partial_signals": ["has_asset_inventory"],
    },
    "physical security monitoring": {
        "evidence_sources": ["assets", "governance"],
        "pass_signals": ["has_asset_inventory", "has_governance_activities"],
        "partial_signals": ["has_asset_inventory"],
    },
    "protecting against physical": {
        "evidence_sources": ["assets"],
        "pass_signals": ["has_asset_inventory"],
        "partial_signals": ["has_asset_inventory"],
    },
    "equipment siting": {
        "evidence_sources": ["assets"],
        "pass_signals": ["has_asset_locations"],
        "partial_signals": ["has_asset_inventory"],
    },
    "storage media": {
        "evidence_sources": ["assets"],
        "pass_signals": ["has_asset_inventory"],
        "partial_signals": ["has_asset_inventory"],
    },
    "clear desk": {
        "evidence_sources": ["governance", "employees"],
        "pass_signals": ["has_governance_activities"],
        "partial_signals": ["has_employee_records"],
    },
    "equipment maintenance": {
        "evidence_sources": ["assets"],
        "pass_signals": ["has_asset_inventory"],
        "partial_signals": ["has_asset_inventory"],
    },
    "secure disposal": {
        "evidence_sources": ["assets", "governance"],
        "pass_signals": ["has_asset_inventory"],
        "partial_signals": ["has_asset_inventory"],
    },
    "cabling security": {
        "evidence_sources": ["assets", "network_rules"],
        "pass_signals": ["has_asset_inventory"],
        "partial_signals": ["has_asset_inventory"],
    },
    "utility support": {
        "evidence_sources": ["assets"],
        "pass_signals": ["has_asset_inventory"],
        "partial_signals": ["has_asset_inventory"],
    },

    # ── A8: Technological Controls ───────────────────────────────────────
    "network services": {
        "evidence_sources": ["network_rules"],
        "pass_signals": ["has_network_rules", "low_risky_rules"],
        "partial_signals": ["has_network_rules"],
    },
    "segregation in networks": {
        "evidence_sources": ["network_rules"],
        "pass_signals": ["has_deny_rules", "has_network_rules"],
        "partial_signals": ["has_network_rules"],
    },
    "network segmentation": {
        "evidence_sources": ["network_rules"],
        "pass_signals": ["has_deny_rules", "has_network_rules"],
        "partial_signals": ["has_network_rules"],
    },
    "web filtering": {
        "evidence_sources": ["network_rules"],
        "pass_signals": ["has_deny_rules"],
        "partial_signals": ["has_network_rules"],
    },
    "cryptography": {
        "evidence_sources": ["network_rules", "assets"],
        "pass_signals": ["has_network_rules"],
        "partial_signals": ["has_network_rules"],
    },
    "access control": {
        "evidence_sources": ["employees", "assets", "network_rules"],
        "pass_signals": ["has_access_levels", "has_network_rules"],
        "partial_signals": ["has_employee_records"],
    },
    "user access management": {
        "evidence_sources": ["employees"],
        "pass_signals": ["has_access_levels"],
        "partial_signals": ["has_employee_records"],
    },
    "privileged access": {
        "evidence_sources": ["employees"],
        "pass_signals": ["has_access_levels"],
        "partial_signals": ["has_employee_records"],
    },
    "asset management": {
        "evidence_sources": ["assets", "applications"],
        "pass_signals": ["has_asset_inventory", "has_asset_owners"],
        "partial_signals": ["has_asset_inventory"],
    },
    "asset inventory": {
        "evidence_sources": ["assets", "applications"],
        "pass_signals": ["has_asset_inventory"],
        "partial_signals": ["has_asset_inventory"],
    },
    "supplier": {
        "evidence_sources": ["vendors"],
        "pass_signals": ["has_vendor_records", "has_vendor_compliance"],
        "partial_signals": ["has_vendor_records"],
    },
    "vendor": {
        "evidence_sources": ["vendors"],
        "pass_signals": ["has_vendor_records", "has_vendor_compliance"],
        "partial_signals": ["has_vendor_records"],
    },
    "third party": {
        "evidence_sources": ["vendors"],
        "pass_signals": ["has_vendor_records"],
        "partial_signals": ["has_vendor_records"],
    },
    "incident management": {
        "evidence_sources": ["governance", "risk_register"],
        "pass_signals": ["has_governance_activities", "has_risk_register"],
        "partial_signals": ["has_governance_activities"],
    },
    "incident response": {
        "evidence_sources": ["governance", "risk_register"],
        "pass_signals": ["has_governance_activities"],
        "partial_signals": ["has_risk_register"],
    },
    "risk management": {
        "evidence_sources": ["risk_register"],
        "pass_signals": ["has_risk_register", "has_risk_treatments"],
        "partial_signals": ["has_risk_register"],
    },
    "risk assessment": {
        "evidence_sources": ["risk_register"],
        "pass_signals": ["has_risk_register"],
        "partial_signals": ["has_risk_register"],
    },
    "data protection": {
        "evidence_sources": ["assets", "applications", "vendors"],
        "pass_signals": ["has_asset_inventory"],
        "partial_signals": ["has_asset_inventory"],
    },
    "backup": {
        "evidence_sources": ["assets", "governance"],
        "pass_signals": ["has_asset_inventory", "has_governance_activities"],
        "partial_signals": ["has_asset_inventory"],
    },
    "monitoring": {
        "evidence_sources": ["governance", "network_rules"],
        "pass_signals": ["has_governance_activities", "has_network_rules"],
        "partial_signals": ["has_governance_activities"],
    },
    "audit": {
        "evidence_sources": ["governance"],
        "pass_signals": ["has_governance_activities"],
        "partial_signals": ["has_governance_activities"],
    },
    "configuration management": {
        "evidence_sources": ["network_rules", "assets"],
        "pass_signals": ["has_network_rules"],
        "partial_signals": ["has_asset_inventory"],
    },
    "secure development": {
        "evidence_sources": ["applications", "governance"],
        "pass_signals": ["has_applications"],
        "partial_signals": ["has_applications"],
    },
}

# Domain-level fallback mapping (section name → sheet types)
_DOMAIN_EVIDENCE_MAP: dict[str, list[str]] = {
    "people controls":          ["employees", "governance"],
    "physical controls":        ["assets"],
    "technological controls":   ["network_rules", "assets", "applications"],
    "organizational controls":  ["governance", "risk_register", "vendors"],
    "access control":           ["employees", "network_rules"],
    "asset management":         ["assets", "applications"],
    "supplier management":      ["vendors"],
    "network security":         ["network_rules"],
    "risk management":          ["risk_register"],
}


# ---------------------------------------------------------------------------
# Data signal evaluator
# ---------------------------------------------------------------------------

def _evaluate_data_signals(routing: dict) -> dict[str, bool]:
    """
    Examine routing results and compute boolean data-quality signals
    that determine whether specific controls have evidence.
    """
    signals: dict[str, bool] = {}

    for r in routing.get("routing_results", []):
        st = r.get("source_type", "")
        total = r.get("total_records", 0)

        if st == "employees" and total > 0:
            signals["has_employee_records"] = True
            no_training = r.get("no_security_training", 0)
            trained = total - no_training
            signals["has_some_training"] = trained > 0
            signals["high_training_coverage"] = (trained / total) >= 0.6 if total > 0 else False
            signals["has_access_levels"] = r.get("privileged_access_count", 0) > 0 or total > 0

        elif st in ("assets", "applications") and total > 0:
            signals["has_asset_inventory"] = True
            signals["has_applications"] = (st == "applications") or signals.get("has_applications", False)
            unowned = r.get("unowned_assets", r.get("unowned_applications", 0))
            signals["has_asset_owners"] = (total - unowned) > 0
            by_crit = r.get("by_criticality", {})
            signals["has_asset_classifications"] = len(by_crit) > 1
            # Check if location data exists (via findings)
            signals["has_asset_locations"] = total > 0

        elif st == "vendors" and total > 0:
            signals["has_vendor_records"] = True
            no_compliance = r.get("no_compliance_count", 0)
            signals["has_vendor_compliance"] = (total - no_compliance) > 0
            signals["has_high_risk_vendors"] = len(r.get("high_risk_vendors", [])) > 0

        elif st == "network_rules" and total > 0:
            signals["has_network_rules"] = True
            risky = r.get("risky_rules_count", 0)
            signals["low_risky_rules"] = risky == 0
            signals["has_deny_rules"] = r.get("deny_rules_count", 0) > 0

        elif st == "governance" and total > 0:
            signals["has_governance_activities"] = True

        elif st == "risk_register" and total > 0:
            signals["has_risk_register"] = True
            untreated = r.get("untreated_risks", [])
            signals["has_risk_treatments"] = total > len(untreated)

    return signals


# ---------------------------------------------------------------------------
# Control inference
# ---------------------------------------------------------------------------

def _match_control_to_evidence(ctrl: dict, section_name: str = "") -> dict | None:
    """
    Find the best evidence mapping entry for a framework control.
    Uses control name, domain, and section name for semantic matching.
    """
    ctrl_name = (ctrl.get("name") or "").lower()
    ctrl_domain = (ctrl.get("domain") or "").lower()
    ctrl_desc = (ctrl.get("description") or "").lower()
    section = section_name.lower()

    # Try exact keyword matches against control name
    best_match = None
    best_score = 0

    for keyword, mapping in _ISO27001_EVIDENCE_MAP.items():
        score = 0
        kw_lower = keyword.lower()
        if kw_lower in ctrl_name:
            score += 3
        if kw_lower in ctrl_domain:
            score += 2
        if kw_lower in ctrl_desc:
            score += 1
        if kw_lower in section:
            score += 1

        if score > best_score:
            best_score = score
            best_match = mapping

    return best_match if best_score > 0 else None


def infer_control_status(
    ctrl: dict,
    section_name: str,
    signals: dict[str, bool],
    present_types: set[str],
) -> tuple[str, str, str]:
    """
    Infer a single control's compliance status from data signals.

    Returns (status, reason, match_source) where:
      status: 'compliant' | 'partial' | 'missing'
      reason: human-readable explanation
      match_source: which data was used
    """
    ctrl_name = ctrl.get("name", "Unknown")

    # Try specific keyword match
    mapping = _match_control_to_evidence(ctrl, section_name)

    if mapping:
        evidence_types = mapping["evidence_sources"]
        pass_sigs = mapping["pass_signals"]
        partial_sigs = mapping["partial_signals"]

        # Check if any evidence source sheet is present
        has_relevant_data = any(t in present_types for t in evidence_types)

        if not has_relevant_data:
            return ("missing",
                    f"No relevant data uploaded for '{ctrl_name}'. "
                    f"Expected: {', '.join(evidence_types)}.",
                    "no_data")

        # Check PASS signals
        pass_count = sum(1 for s in pass_sigs if signals.get(s, False))
        if pass_count >= len(pass_sigs) and len(pass_sigs) > 0:
            sources = [t for t in evidence_types if t in present_types]
            return ("compliant",
                    f"Strong evidence inferred from uploaded {', '.join(sources)} data.",
                    f"inferred_from_{'+'.join(sources)}")

        # Check PARTIAL signals
        partial_count = sum(1 for s in partial_sigs if signals.get(s, False))
        if partial_count > 0:
            sources = [t for t in evidence_types if t in present_types]
            return ("partial",
                    f"Partial evidence inferred from uploaded {', '.join(sources)} data. "
                    f"Additional documentation may strengthen compliance.",
                    f"inferred_from_{'+'.join(sources)}")

        # Has relevant sheet type but signals don't match
        sources = [t for t in evidence_types if t in present_types]
        return ("partial",
                f"Relevant data exists in {', '.join(sources)} but "
                f"evidence quality is incomplete for '{ctrl_name}'.",
                f"weak_inference_from_{'+'.join(sources)}")

    # Fallback: domain-level matching
    section_lower = section_name.lower()
    for domain_key, domain_types in _DOMAIN_EVIDENCE_MAP.items():
        if domain_key in section_lower:
            has_data = any(t in present_types for t in domain_types)
            if has_data:
                sources = [t for t in domain_types if t in present_types]
                return ("partial",
                        f"Domain-level evidence from {', '.join(sources)} "
                        f"partially covers '{ctrl_name}'.",
                        f"domain_inference_{'+'.join(sources)}")

    # No match at all — but if we have rich data, give minimal partial
    if len(present_types) >= 3:
        return ("partial",
                f"Organizational data coverage is broad ({len(present_types)} data types). "
                f"Indirect evidence may support '{ctrl_name}'.",
                "broad_coverage_inference")

    return ("missing",
            f"No evidence found for '{ctrl_name}' in uploaded data.",
            "no_evidence")


# ---------------------------------------------------------------------------
# Bulk inference
# ---------------------------------------------------------------------------

def infer_all_controls(
    controls: list[dict],
    routing: dict,
    present_types: set[str],
) -> list[dict]:
    """
    Infer compliance status for all controls based on uploaded data.

    Mutates each control dict in place AND returns the list.
    """
    # ── PHASE 1 RUNTIME PROOF ─────────────────────────────────────────────
    _log.warning("=" * 70)
    _log.warning("[RUNTIME PROOF] evidence_inference.infer_all_controls called")
    _log.warning("[RUNTIME PROOF]   controls to evaluate : %d", len(controls))
    _log.warning("[RUNTIME PROOF]   present sheet types   : %s", sorted(present_types))
    _log.warning("=" * 70)

    signals = _evaluate_data_signals(routing)

    _log.warning("[RUNTIME PROOF]   data signals evaluated: %d", len(signals))
    for sig_name, sig_val in sorted(signals.items()):
        _log.warning("[RUNTIME PROOF]     signal: %s = %s", sig_name, sig_val)

    for ctrl in controls:
        section_name = ctrl.get("section_name", ctrl.get("domain", ""))
        status, reason, match_source = infer_control_status(
            ctrl, section_name, signals, present_types
        )

        ctrl["status"] = status
        ctrl["has_evidence"] = status != "missing"
        ctrl["evidence_status"] = status
        ctrl["evidence_row"] = {}
        ctrl["source"] = "inferred"
        ctrl["match_method"] = match_source
        ctrl["reason"] = reason

    # ── Summary ───────────────────────────────────────────────────────────
    compliant = sum(1 for c in controls if c.get("status") == "compliant")
    partial   = sum(1 for c in controls if c.get("status") == "partial")
    missing   = sum(1 for c in controls if c.get("status") == "missing")
    _log.warning("-" * 70)
    _log.warning("[RUNTIME PROOF] inference complete — compliant=%d  partial=%d  missing=%d  total=%d",
                 compliant, partial, missing, len(controls))
    _log.warning("=" * 70)

    return controls


# ---------------------------------------------------------------------------
# Compliance matrix builder
# ---------------------------------------------------------------------------

def build_compliance_matrix(
    controls: list[dict],
    framework_label: str,
) -> list[dict]:
    """
    Build a compliance matrix: requirement → inferred control → gap → remediation.
    """
    matrix = []
    for ctrl in controls:
        status = ctrl.get("status", "missing")
        if status == "compliant":
            gap = "None"
            remediation = "Maintain current controls and documentation."
        elif status == "partial":
            gap = "Incomplete evidence or coverage"
            remediation = (
                f"Strengthen documentation and evidence for "
                f"'{ctrl.get('name', '')}'. Formalize existing practices."
            )
        else:
            gap = "No evidence of implementation"
            remediation = (
                f"Implement '{ctrl.get('name', '')}' control. "
                f"Develop policy, assign owner, and collect evidence."
            )

        matrix.append({
            "requirement_id": ctrl.get("rule_id", ""),
            "requirement": ctrl.get("name", ""),
            "domain": ctrl.get("domain", ctrl.get("section_name", "")),
            "inferred_control": ctrl.get("match_method", "none"),
            "status": status,
            "gap": gap,
            "remediation": remediation,
            "severity": ctrl.get("severity", "medium"),
            "source": ctrl.get("source", ""),
        })
    return matrix


# ---------------------------------------------------------------------------
# Risk register builder — generates risks from data gaps
# ---------------------------------------------------------------------------

def generate_risks_from_data(
    routing: dict,
    controls: list[dict],
    present_types: set[str],
) -> list[dict]:
    """
    Generate risk entries from identified gaps in uploaded data
    AND from actual uploaded risk register data.
    """
    risks: list[dict] = []
    risk_id = 1

    # Risks from data analysis
    for r in routing.get("routing_results", []):
        st = r.get("source_type", "")
        total = r.get("total_records", 0)
        if total == 0:
            continue

        if st == "employees":
            no_training = r.get("no_security_training", 0)
            if no_training > 0:
                risks.append({
                    "risk_id": f"GRC-R{risk_id:03d}",
                    "risk_name": "Insufficient Security Awareness Training",
                    "category": "People",
                    "likelihood": "High" if no_training > total * 0.5 else "Medium",
                    "impact": "High",
                    "risk_level": "High" if no_training > total * 0.5 else "Medium",
                    "source": "employees",
                    "detail": f"{no_training} of {total} employees lack security training.",
                    "mitigation": "Implement mandatory security awareness program.",
                })
                risk_id += 1
            priv = r.get("privileged_access_count", 0)
            if priv > 0:
                risks.append({
                    "risk_id": f"GRC-R{risk_id:03d}",
                    "risk_name": "Privileged Access Exposure",
                    "category": "Access Control",
                    "likelihood": "Medium",
                    "impact": "High",
                    "risk_level": "High",
                    "source": "employees",
                    "detail": f"{priv} users with privileged/admin access.",
                    "mitigation": "Review privileged access, enforce least-privilege.",
                })
                risk_id += 1

        elif st in ("assets", "applications"):
            unowned = r.get("unowned_assets", r.get("unowned_applications", 0))
            if unowned > 0:
                risks.append({
                    "risk_id": f"GRC-R{risk_id:03d}",
                    "risk_name": "Unowned Assets",
                    "category": "Asset Management",
                    "likelihood": "Medium",
                    "impact": "Medium",
                    "risk_level": "Medium",
                    "source": st,
                    "detail": f"{unowned} assets have no assigned owner.",
                    "mitigation": "Assign ownership to all assets.",
                })
                risk_id += 1

        elif st == "vendors":
            high_risk = r.get("high_risk_vendors", [])
            if high_risk:
                risks.append({
                    "risk_id": f"GRC-R{risk_id:03d}",
                    "risk_name": "High-Risk Third-Party Vendors",
                    "category": "Supplier Management",
                    "likelihood": "Medium",
                    "impact": "High",
                    "risk_level": "High",
                    "source": "vendors",
                    "detail": f"{len(high_risk)} high-risk vendors: {', '.join(high_risk[:3])}.",
                    "mitigation": "Conduct vendor risk assessments and enforce SLAs.",
                })
                risk_id += 1
            no_comp = r.get("no_compliance_count", 0)
            if no_comp > 0:
                risks.append({
                    "risk_id": f"GRC-R{risk_id:03d}",
                    "risk_name": "Vendor Compliance Gaps",
                    "category": "Supplier Management",
                    "likelihood": "Medium",
                    "impact": "Medium",
                    "risk_level": "Medium",
                    "source": "vendors",
                    "detail": f"{no_comp} vendors lack compliance certifications.",
                    "mitigation": "Require compliance attestation from all vendors.",
                })
                risk_id += 1

        elif st == "network_rules":
            risky = r.get("risky_rules_count", 0)
            if risky > 0:
                risks.append({
                    "risk_id": f"GRC-R{risk_id:03d}",
                    "risk_name": "Overly Permissive Network Rules",
                    "category": "Network Security",
                    "likelihood": "High",
                    "impact": "High",
                    "risk_level": "Critical",
                    "source": "network_rules",
                    "detail": f"{risky} firewall rules use ANY/wildcard.",
                    "mitigation": "Restrict rules to least-privilege, remove wildcards.",
                })
                risk_id += 1
            if r.get("deny_rules_count", 0) == 0:
                risks.append({
                    "risk_id": f"GRC-R{risk_id:03d}",
                    "risk_name": "No Explicit Deny Rules",
                    "category": "Network Security",
                    "likelihood": "Medium",
                    "impact": "High",
                    "risk_level": "High",
                    "source": "network_rules",
                    "detail": "No explicit deny rules found — default-allow posture.",
                    "mitigation": "Implement default-deny firewall policy.",
                })
                risk_id += 1

    # Add risks from missing critical controls
    for ctrl in controls:
        if ctrl.get("status") == "missing" and (
            ctrl.get("severity", "").lower() in ("high", "critical")
        ):
            risks.append({
                "risk_id": f"GRC-R{risk_id:03d}",
                "risk_name": f"Missing Control: {ctrl.get('name', '')}",
                "category": ctrl.get("domain", ctrl.get("section_name", "General")),
                "likelihood": "Medium",
                "impact": "High",
                "risk_level": "High",
                "source": "framework_gap",
                "detail": ctrl.get("reason", ""),
                "mitigation": f"Implement {ctrl.get('name', '')} control.",
            })
            risk_id += 1

    return risks
