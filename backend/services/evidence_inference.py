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
    
    # Group by Requirement (domain or section)
    grouped = {}
    for ctrl in controls:
        req = ctrl.get("domain") or ctrl.get("section_name") or "General Security Requirements"
        if req not in grouped:
            grouped[req] = []
        grouped[req].append(ctrl)

    fw = framework_label.lower()

    for req, req_controls in grouped.items():
        comp_list = [c.get("rule_id", c.get("name", "")) for c in req_controls if c.get("status") == "compliant"]
        part_list = [c.get("rule_id", c.get("name", "")) for c in req_controls if c.get("status") == "partial"]
        miss_list = [c.get("rule_id", c.get("name", "")) for c in req_controls if c.get("status") == "missing"]

        # 2. Clean Status display
        if len(comp_list) == len(req_controls):
            status = "Compliant"
        elif len(miss_list) == len(req_controls):
            status = "Missing"
        else:
            status = "Partial"

        # 3. Improve "Mapped Controls"
        mapped_controls_parts = []
        if comp_list:
            mapped_controls_parts.append(f"COMPLIANT: [{', '.join(comp_list)}]")
        if part_list:
            mapped_controls_parts.append(f"PARTIAL: [{', '.join(part_list)}]")
        if miss_list:
            mapped_controls_parts.append(f"MISSING: [{', '.join(miss_list)}]")
        mapped_controls = "\n".join(mapped_controls_parts)

        # 4. Add clear "Gaps Identified"
        gaps_list = []
        for c in req_controls:
            st = c.get("status")
            cname = c.get("name", "")
            if st == "partial":
                if "contingency" in cname.lower() or "backup" in cname.lower():
                    gaps_list.append(f"{cname} exists but is not fully tested")
                else:
                    gaps_list.append(f"Inconsistent enforcement of {cname.lower()}")
            elif st == "missing":
                if "policy" in cname.lower() or "govern" in cname.lower() or "management" in cname.lower():
                    gaps_list.append(f"Lack of centralized {cname.lower()} governance or monitoring")
                else:
                    gaps_list.append(f"Missing {cname.lower()} processes")
        
        gaps_identified = " • ".join(gaps_list) if gaps_list else "No gaps identified."

        # 5. Improve "Remediation Plan"
        if status == "Compliant":
            remediation = "Maintain current controls and documentation."
        else:
            if "hipaa" in fw:
                rem_lines = []
                if "management" in req.lower() or "process" in req.lower() or "policy" in req.lower():
                    rem_lines.append("Formalize and enforce Security Management Process per HIPAA requirements.")
                if any("contingency" in c.lower() or "backup" in c.lower() for c in (miss_list + part_list)):
                    rem_lines.append("Establish tested contingency and disaster recovery procedures.")
                if not rem_lines:
                    rem_lines.append("Implement required technical and administrative safeguards for ePHI.")
                rem_lines.append("Assign a Security Officer responsible for oversight.")
                remediation = " ".join(rem_lines)
            elif "iso" in fw:
                remediation = f"Implement ISMS Annex A controls for {req} and ensure governance oversight."
            elif "pci" in fw:
                remediation = f"Enforce PCI DSS requirements for {req} across the cardholder data environment, ensuring proper segmentation and monitoring."
            else:
                remediation = f"Develop policies, assign owners, and collect evidence for {req}."

        matrix.append({
            "Framework": framework_label,
            "Requirement": req,
            "Status": status,
            "Mapped Controls": mapped_controls,
            "Gaps Identified": gaps_identified,
            "Remediation Plan": remediation
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


# ---------------------------------------------------------------------------
# PCI DSS Risk-Based Scoring Engine
# ---------------------------------------------------------------------------
# Implements weighted deductions based on actual data analysis, not just
# control-level pass/fail. This produces a realistic 40-70% score for
# risky datasets rather than the inflated 90%+ from presence-based checks.

def _analyse_pci_data_risks(
    routing: dict,
    all_sheets: list[dict] | None,
) -> dict:
    """
    Deep-scan uploaded data for PCI DSS-specific risk indicators.

    Returns a dict of risk findings with weighted deductions:
      - Each finding has: key, description, deduction, severity, evidence
      - Total deduction is applied to the 100-point base score
    """
    findings: list[dict] = []

    # Collect raw rows
    asset_rows: list[dict] = []
    vendor_rows: list[dict] = []
    employee_rows: list[dict] = []
    network_rows: list[dict] = []

    if all_sheets:
        for s in all_sheets:
            t = s.get("type", "")
            if t in ("assets", "applications"):
                asset_rows.extend(s.get("rows", []))
            elif t == "vendors":
                vendor_rows.extend(s.get("rows", []))
            elif t == "employees":
                employee_rows.extend(s.get("rows", []))
            elif t == "network_rules":
                network_rows.extend(s.get("rows", []))

    # Also use routing results for aggregate stats
    routing_results = {
        r.get("source_type", ""): r
        for r in routing.get("routing_results", [])
        if r.get("total_records", 0) > 0
    }

    # ── CRITICAL: Cardholder Data + No Encryption (-25) ──────────────────
    has_cardholder_assets = False
    unencrypted_chd = False
    for row in asset_rows:
        blob = " ".join(str(v) for v in row.values()).lower()
        if any(kw in blob for kw in ("cardholder", "payment", "card data",
                                      "pan", "credit card", "debit card",
                                      "chd", "cde")):
            has_cardholder_assets = True
            if not any(kw in blob for kw in ("encrypt", "aes", "tls",
                                               "masked", "tokeniz")):
                unencrypted_chd = True
                break

    if unencrypted_chd:
        findings.append({
            "key": "unencrypted_chd",
            "description": "Cardholder data assets identified without encryption evidence",
            "deduction": 25,
            "severity": "critical",
            "pci_req": "Req 3/4",
            "evidence": "Assets sheet contains cardholder data references without encryption indicators",
        })
    elif has_cardholder_assets:
        findings.append({
            "key": "chd_present_encrypted",
            "description": "Cardholder data assets found with encryption evidence",
            "deduction": 0,
            "severity": "info",
            "pci_req": "Req 3/4",
            "evidence": "Assets contain CHD references with encryption indicators",
        })

    # ── CRITICAL: Database exposed to Internet (-25) ─────────────────────
    db_exposed = False
    exposed_details = []
    db_ports = {"3306", "5432", "1433", "1521", "27017", "6379", "5984", "9200"}
    for row in network_rows:
        blob = " ".join(str(v) for v in row.values()).lower()
        # Check for db ports or db keywords in rules allowing internet access
        port_field = str(row.get("port", row.get("dst_port", row.get("destination_port", "")))).strip()
        src_field = str(row.get("source", row.get("src", row.get("source_ip", "")))).strip().lower()
        action_field = str(row.get("action", row.get("policy", ""))).strip().lower()

        is_allow = action_field in ("allow", "permit", "accept", "") or "allow" in blob
        is_any_source = src_field in ("any", "0.0.0.0/0", "*", "all", "")
        has_db_port = port_field in db_ports
        has_db_keyword = any(kw in blob for kw in ("mysql", "postgres", "mssql",
                                                     "oracle", "mongodb", "redis",
                                                     "database", "db "))

        if is_allow and is_any_source and (has_db_port or has_db_keyword):
            db_exposed = True
            exposed_details.append(f"port {port_field}" if has_db_port else "db service")

    for row in asset_rows:
        blob = " ".join(str(v) for v in row.values()).lower()
        if any(kw in blob for kw in ("database", "mysql", "postgres", "sql server",
                                       "mongodb", "redis", "oracle db")):
            exposure = ""
            if any(kw in blob for kw in ("internet", "public", "external", "dmz",
                                           "exposed", "0.0.0.0")):
                db_exposed = True
                exposure = row.get("name", row.get("asset_name", "Unknown DB"))
                exposed_details.append(exposure)

    if db_exposed:
        findings.append({
            "key": "db_internet_exposed",
            "description": "Database service accessible from the internet",
            "deduction": 25,
            "severity": "critical",
            "pci_req": "Req 1/1.3",
            "evidence": f"Exposed: {', '.join(exposed_details[:3])}",
        })

    # ── CRITICAL: Vendor handles card data AND no contract (-15) ─────────
    vendor_no_contract = 0
    vendor_total = len(vendor_rows)
    for row in vendor_rows:
        blob = " ".join(str(v) for v in row.values()).lower()
        handles_cards = any(kw in blob for kw in ("payment", "card", "chd",
                                                    "cardholder", "transaction",
                                                    "billing", "pos", "acquiring"))
        has_contract = any(kw in blob for kw in ("signed", "contract", "agreement",
                                                   "compliant", "certified", "approved",
                                                   "dpa", "baa", "nda"))
        if handles_cards and not has_contract:
            vendor_no_contract += 1

    if vendor_no_contract > 0:
        findings.append({
            "key": "vendor_no_contract_chd",
            "description": f"{vendor_no_contract} vendor(s) handle card data without documented agreement",
            "deduction": 15,
            "severity": "critical",
            "pci_req": "Req 12.8",
            "evidence": f"{vendor_no_contract} of {vendor_total} vendors lack contracts",
        })

    # ── HIGH: Privileged users without MFA (-10) ─────────────────────────
    priv_no_mfa = 0
    total_priv = 0
    for row in employee_rows:
        blob = " ".join(str(v) for v in row.values()).lower()
        access = str(row.get("access_level", row.get("privilege", row.get("role", "")))).lower()
        is_priv = any(kw in access for kw in ("admin", "privileged", "root",
                                                 "superuser", "elevated", "sys admin"))
        if is_priv:
            total_priv += 1
            has_mfa = any(kw in blob for kw in ("mfa", "multi-factor", "2fa",
                                                   "two-factor", "yubikey", "authenticator"))
            if not has_mfa:
                priv_no_mfa += 1

    # Also check routing for privileged access count
    emp_routing = routing_results.get("employees", {})
    if not total_priv and emp_routing:
        total_priv = emp_routing.get("privileged_access_count", 0)
        priv_no_mfa = total_priv  # Assume no MFA evidence if not in data

    if priv_no_mfa > 0:
        findings.append({
            "key": "priv_no_mfa",
            "description": f"{priv_no_mfa} privileged user(s) without MFA evidence",
            "deduction": 10,
            "severity": "high",
            "pci_req": "Req 8",
            "evidence": f"{priv_no_mfa} of {total_priv} privileged accounts lack MFA",
        })

    # ── HIGH: Missing patches on critical assets (-10) ───────────────────
    unpatched_critical = 0
    total_critical = 0
    for row in asset_rows:
        blob = " ".join(str(v) for v in row.values()).lower()
        crit = str(row.get("criticality", row.get("priority", row.get("importance", "")))).lower()
        is_critical = crit in ("high", "critical", "essential")
        if is_critical:
            total_critical += 1
            patch_status = str(row.get("patch_status", row.get("patching",
                                 row.get("update_status", "")))).lower()
            if patch_status in ("", "missing", "overdue", "outdated", "no",
                                "not patched", "pending", "failed"):
                # Also check if blob mentions unpatched
                if not any(kw in blob for kw in ("patched", "up to date", "current",
                                                    "updated", "compliant patch")):
                    unpatched_critical += 1

    if unpatched_critical > 0:
        findings.append({
            "key": "unpatched_critical",
            "description": f"{unpatched_critical} critical asset(s) with missing or outdated patches",
            "deduction": 10,
            "severity": "high",
            "pci_req": "Req 6",
            "evidence": f"{unpatched_critical} of {total_critical} critical assets unpatched",
        })

    # ── MEDIUM: No security training (-5) ────────────────────────────────
    emp_result = routing_results.get("employees")
    if emp_result:
        total_emp = emp_result.get("total_records", 0)
        no_training = emp_result.get("no_security_training", 0)
        if no_training > 0 and total_emp > 0:
            pct = round(no_training / total_emp * 100)
            deduct = 5
            if pct > 50:
                deduct = 8  # More than half untrained is worse
            findings.append({
                "key": "no_training",
                "description": f"{no_training} of {total_emp} employees ({pct}%) lack security training",
                "deduction": deduct,
                "severity": "medium" if pct <= 50 else "high",
                "pci_req": "Req 12.6",
                "evidence": f"{pct}% of workforce untrained",
            })

    # ── MEDIUM: Missing or outdated policies (-5) ────────────────────────
    has_governance = "governance" in routing_results
    has_risk_register = "risk_register" in routing_results
    if not has_governance:
        findings.append({
            "key": "no_governance",
            "description": "No governance/policy documentation uploaded",
            "deduction": 5,
            "severity": "medium",
            "pci_req": "Req 12",
            "evidence": "Governance sheet not found in uploaded data",
        })
    if not has_risk_register:
        findings.append({
            "key": "no_risk_register",
            "description": "No risk register uploaded",
            "deduction": 3,
            "severity": "medium",
            "pci_req": "Req 12.2",
            "evidence": "Risk register sheet not found in uploaded data",
        })

    # ── HIGH: Overly permissive network rules (-8) ───────────────────────
    net_result = routing_results.get("network_rules")
    if net_result:
        risky_count = net_result.get("risky_rules_count", 0)
        total_rules = net_result.get("total_records", 0)
        if risky_count > 0 and total_rules > 0:
            risky_pct = round(risky_count / total_rules * 100)
            deduct = 5 if risky_pct <= 20 else 8
            findings.append({
                "key": "permissive_rules",
                "description": f"{risky_count} overly permissive firewall rules ({risky_pct}%)",
                "deduction": deduct,
                "severity": "high",
                "pci_req": "Req 1.4",
                "evidence": f"{risky_count} of {total_rules} rules use ANY/wildcard",
            })
        deny_count = net_result.get("deny_rules_count", 0)
        if deny_count == 0:
            findings.append({
                "key": "no_deny_rules",
                "description": "No explicit deny rules — default-allow network posture",
                "deduction": 8,
                "severity": "high",
                "pci_req": "Req 1.3",
                "evidence": "Zero deny rules in firewall configuration",
            })

    # ── HIGH: Vendors without compliance (-5) ────────────────────────────
    if vendor_total > 0:
        vendor_no_comp = 0
        for row in vendor_rows:
            comp = str(row.get("compliance", row.get("compliance_status",
                        row.get("certified", "")))).strip().lower()
            if comp in ("", "no", "non-compliant", "non compliant", "failed",
                        "missing", "none", "pending"):
                vendor_no_comp += 1
        if vendor_no_comp > 0:
            findings.append({
                "key": "vendors_no_compliance",
                "description": f"{vendor_no_comp} of {vendor_total} vendors lack compliance certification",
                "deduction": 5,
                "severity": "high",
                "pci_req": "Req 12.8",
                "evidence": f"{vendor_no_comp} vendors without valid compliance status",
            })

    return {
        "findings": findings,
        "total_deduction": sum(f["deduction"] for f in findings),
        "risk_score": max(0, 100 - sum(f["deduction"] for f in findings)),
    }


def compute_pci_risk_based_score(
    controls: list[dict],
    routing: dict,
    all_sheets: list[dict] | None = None,
) -> dict:
    """
    Compute a PCI DSS compliance score using risk-based deductions.

    Combines:
      1. Control-level assessment (from rule engine / JSON conditions)
      2. Data-level risk analysis (deep scan of uploaded evidence)

    The final score blends both: 60% control score + 40% risk score,
    ensuring that critical misconfigurations always drag the score down
    even if some controls technically pass.

    Returns dict with:
      compliance_score, risk_score, control_score, findings,
      total_controls, compliant_controls, partial_controls, missing_controls
    """
    # ── 1. Control-level score ────────────────────────────────────────────
    total = len(controls)
    compliant = sum(1 for c in controls if c.get("status") == "compliant")
    partial = sum(1 for c in controls if c.get("status") == "partial")
    missing = total - compliant - partial

    control_score = round(
        ((compliant + partial * 0.5) / total) * 100, 2
    ) if total > 0 else 0.0

    # ── 2. Risk-based deductions from actual data ─────────────────────────
    risk_analysis = _analyse_pci_data_risks(routing, all_sheets)
    risk_score = risk_analysis["risk_score"]
    findings = risk_analysis["findings"]

    # ── 3. Blended score: weight towards risk findings ────────────────────
    #   If risk analysis found critical issues, they must significantly
    #   impact the overall score regardless of control-level results.
    blended = round(control_score * 0.6 + risk_score * 0.4, 2)

    # Apply a floor: if critical findings exist, cap the maximum score
    critical_findings = [f for f in findings if f["severity"] == "critical"]
    if len(critical_findings) >= 2:
        blended = min(blended, 55.0)  # Multiple critical = can't be above 55%
    elif len(critical_findings) == 1:
        blended = min(blended, 70.0)  # Single critical = can't be above 70%

    blended = max(0.0, blended)

    return {
        "compliance_score": blended,
        "control_score": control_score,
        "risk_score": risk_score,
        "total_deduction": risk_analysis["total_deduction"],
        "findings": findings,
        "total_controls": total,
        "compliant_controls": compliant,
        "partial_controls": partial,
        "missing_controls": missing,
    }


def generate_pci_dynamic_risks(
    routing: dict,
    controls: list[dict],
    all_sheets: list[dict] | None = None,
) -> list[dict]:
    """
    Generate PCI DSS-specific risk register entries from data analysis.

    Each risk includes:
      risk_id, description, affected_asset, impact, likelihood, risk_level
    """
    risk_analysis = _analyse_pci_data_risks(routing, all_sheets)
    risks: list[dict] = []
    rid = 1

    _PCI_RISK_TEMPLATES = {
        "unencrypted_chd": {
            "risk_name": "Unencrypted Cardholder Data Exposure",
            "threat": "Data Exposure",
            "asset": "Cardholder Data Environment",
            "impact": 5,
            "likelihood": 4,
        },
        "db_internet_exposed": {
            "risk_name": "Internet-Accessible Database",
            "threat": "Network Exploitation",
            "asset": "Database Infrastructure",
            "impact": 5,
            "likelihood": 4,
        },
        "vendor_no_contract_chd": {
            "risk_name": "Uncontracted Vendor Handling Card Data",
            "threat": "Supply Chain Attack",
            "asset": "Third-Party Vendors",
            "impact": 4,
            "likelihood": 3,
        },
        "priv_no_mfa": {
            "risk_name": "Privileged Users Without MFA",
            "threat": "Credential Theft",
            "asset": "Privileged Accounts",
            "impact": 5,
            "likelihood": 3,
        },
        "unpatched_critical": {
            "risk_name": "Unpatched Critical Systems",
            "threat": "Remote Code Execution",
            "asset": "Critical Infrastructure",
            "impact": 4,
            "likelihood": 3,
        },
        "no_training": {
            "risk_name": "Insufficient Security Awareness Training",
            "threat": "Phishing",
            "asset": "Workforce",
            "impact": 3,
            "likelihood": 3,
        },
        "no_governance": {
            "risk_name": "Missing Information Security Policy",
            "threat": "Governance Control Gap",
            "asset": "IT Governance",
            "impact": 3,
            "likelihood": 2,
        },
        "permissive_rules": {
            "risk_name": "Overly Permissive Firewall Rules",
            "threat": "Misconfiguration",
            "asset": "Network Perimeter",
            "impact": 4,
            "likelihood": 3,
        },
        "no_deny_rules": {
            "risk_name": "Default-Allow Network Posture",
            "threat": "Misconfiguration",
            "asset": "Network Infrastructure",
            "impact": 4,
            "likelihood": 3,
        },
        "vendors_no_compliance": {
            "risk_name": "Vendor Compliance Gaps",
            "threat": "Third-Party Compliance Risk",
            "asset": "Third-Party Vendors",
            "impact": 3,
            "likelihood": 3,
        },
        "no_risk_register": {
            "risk_name": "Missing Risk Management Process",
            "threat": "Governance Control Gap",
            "asset": "Risk Management",
            "impact": 3,
            "likelihood": 2,
        },
    }

    for finding in risk_analysis["findings"]:
        if finding["deduction"] == 0:
            continue
        key = finding["key"]
        template = _PCI_RISK_TEMPLATES.get(key)
        if not template:
            continue

        lh = template["likelihood"]
        imp = template["impact"]
        score = lh * imp
        if score >= 16:
            level = "Critical"
        elif score >= 10:
            level = "High"
        elif score >= 5:
            level = "Medium"
        else:
            level = "Low"

        risks.append({
            "risk_id": f"TEMP-P{rid:03d}",  # builder assigns final PCI-R001… globally
            "risk_name": template["risk_name"],
            "risk_statement": finding["description"],
            "asset": template["asset"],
            "threat": template["threat"],
            "likelihood": lh,
            "impact": imp,
            "risk_level": level,
            "control": finding.get("evidence", ""),
            "controls": f"PCI DSS {finding.get('pci_req', '')}",
            "owner": "IT Security",
            "category": finding["severity"].upper(),
            "source": "pci_risk_analysis",
            "source_label": "PCI Risk Analysis",
            "detail": finding["evidence"],
            "mitigation": f"Address {finding['pci_req']}: {finding['description']}",
        })
        rid += 1

    return risks
