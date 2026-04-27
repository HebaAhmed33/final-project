"""
Tests for vendor risk classification, deduplication, and format-robustness.

Run:  python -m pytest test_vendor_fields.py -v
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from services.contextual_risk_generator import generate_risks_from_data


# ---------------------------------------------------------------------------
# Helper — build minimal inputs for generate_risks_from_data
# ---------------------------------------------------------------------------

def _make_inputs(vendor_rows=None, asset_rows=None):
    all_sheets = []
    if vendor_rows:
        all_sheets.append({"type": "vendors", "rows": vendor_rows})
    if asset_rows:
        all_sheets.append({"type": "assets", "rows": asset_rows})
    routing = {"routing_results": []}
    present_types = set()
    if vendor_rows:
        present_types.add("vendors")
    if asset_rows:
        present_types.add("assets")
    return routing, [], present_types, all_sheets


def _find_risks_for(risks, vendor_name):
    """Return all risks whose asset matches vendor_name."""
    return [r for r in risks if r.get("asset", "").lower() == vendor_name.lower()]


# ===================================================================
# 1. VENDOR CLASSIFICATION TESTS
# ===================================================================

def test_compliant_vendor_no_supply_chain():
    """Compliant vendors must NEVER get 'Supply Chain Attack'."""
    vendors = [
        {"vendor_name": "Microsoft", "compliance": "Compliant",
         "risk_level": "High", "service_type": "Cloud Infrastructure"},
        {"vendor_name": "AWS", "compliance": "Compliant",
         "risk_level": "High", "service_type": "Cloud Hosting"},
    ]
    routing, controls, pt, sheets = _make_inputs(vendor_rows=vendors)
    risks = generate_risks_from_data(routing, controls, pt, all_sheets=sheets)

    for v in ("Microsoft", "AWS"):
        v_risks = _find_risks_for(risks, v)
        threats = [r["threat"] for r in v_risks]
        assert "Supply Chain Attack" not in threats, (
            f"{v} is compliant but got 'Supply Chain Attack': {threats}"
        )
        assert any(r["threat"] == "Vendor Dependency" for r in v_risks), (
            f"{v} should have 'Vendor Dependency' risk"
        )


def test_compliant_low_crit_vendor_no_risk():
    """Compliant + low-criticality vendor should produce zero risks."""
    vendors = [
        {"vendor_name": "OfficeSupplyCo", "compliance": "Compliant",
         "risk_level": "Low", "service_type": "Office Supplies"},
    ]
    routing, controls, pt, sheets = _make_inputs(vendor_rows=vendors)
    risks = generate_risks_from_data(routing, controls, pt, all_sheets=sheets)
    v_risks = _find_risks_for(risks, "OfficeSupplyCo")
    assert len(v_risks) == 0, f"Compliant low-crit vendor should have no risks, got: {v_risks}"


def test_non_compliant_vendor_gets_high_risk():
    """Non-compliant vendors MUST get Supply Chain Attack (Critical)."""
    vendors = [
        {"vendor_name": "SecurePay", "compliance": "Non-Compliant",
         "risk_level": "High", "service_type": "Payment Processing"},
    ]
    routing, controls, pt, sheets = _make_inputs(vendor_rows=vendors)
    risks = generate_risks_from_data(routing, controls, pt, all_sheets=sheets)
    sp_risks = _find_risks_for(risks, "SecurePay")

    assert any(r["threat"] == "Supply Chain Attack" for r in sp_risks)
    sca = [r for r in sp_risks if r["threat"] == "Supply Chain Attack"][0]
    assert sca["risk_level"] == "Critical"


def test_empty_compliance_treated_as_review_pending():
    """Vendors with empty/None/unknown compliance -> review pending, NOT non-compliant."""
    for comp_val in ("", "None", "none", "missing", "N/A", "unknown"):
        vendors = [
            {"vendor_name": "TestVendor", "compliance": comp_val,
             "risk_level": "Medium", "service_type": "IT Services"},
        ]
        routing, controls, pt, sheets = _make_inputs(vendor_rows=vendors)
        risks = generate_risks_from_data(routing, controls, pt, all_sheets=sheets)
        tv_risks = _find_risks_for(risks, "TestVendor")

        threats = [r["threat"] for r in tv_risks]
        assert "Supply Chain Attack" not in threats, (
            f"compliance='{comp_val}' should NOT produce Supply Chain Attack"
        )
        assert any(r["threat"] == "Compliance Gap" for r in tv_risks), (
            f"compliance='{comp_val}' should produce 'Compliance Gap'"
        )


def test_review_pending_vendor():
    """Review Pending vendor -> Compliance Gap at High level."""
    vendors = [
        {"vendor_name": "PendingCo", "compliance": "Review Pending",
         "risk_level": "Medium", "service_type": "Consulting"},
    ]
    routing, controls, pt, sheets = _make_inputs(vendor_rows=vendors)
    risks = generate_risks_from_data(routing, controls, pt, all_sheets=sheets)
    v_risks = _find_risks_for(risks, "PendingCo")

    assert len(v_risks) == 1
    assert v_risks[0]["threat"] == "Compliance Gap"
    assert v_risks[0]["risk_level"] == "High"  # 3x4 = 12 -> High


# ===================================================================
# 2. DEDUPLICATION TESTS
# ===================================================================

def test_no_duplicate_root_causes():
    """No two generated risks should share the same threat + asset pair."""
    vendors = [
        {"vendor_name": "SecurePay", "compliance": "Non-Compliant",
         "risk_level": "High", "service_type": "Payment Processing"},
        {"vendor_name": "Microsoft", "compliance": "Compliant",
         "risk_level": "High", "service_type": "Cloud"},
    ]
    assets = [
        {"asset_name": "WebServer-01", "asset_type": "Server",
         "criticality": "High", "owner": "IT Ops"},
    ]
    routing, controls, pt, sheets = _make_inputs(vendor_rows=vendors, asset_rows=assets)
    risks = generate_risks_from_data(routing, controls, pt, all_sheets=sheets)

    seen_pairs = set()
    for r in risks:
        pair = (r["asset"], r["threat"])
        assert pair not in seen_pairs, f"Duplicate risk pair found: {pair}"
        seen_pairs.add(pair)


# ===================================================================
# 3. FORMAT-ROBUSTNESS: non-standard column names
# ===================================================================

def test_alternate_vendor_column_names():
    """Vendor rows with non-standard column names should still be processed."""
    vendors = [
        {"supplier": "AcmeCorp", "certification": "Non-Compliant",
         "criticality": "High", "scope": "IT Outsourcing"},
    ]
    routing, controls, pt, sheets = _make_inputs(vendor_rows=vendors)
    risks = generate_risks_from_data(routing, controls, pt, all_sheets=sheets)
    v_risks = _find_risks_for(risks, "AcmeCorp")

    assert len(v_risks) > 0, "Vendor with alternate column names should generate risks"
    threats = [r["threat"] for r in v_risks]
    assert "Supply Chain Attack" in threats, (
        f"AcmeCorp (non-compliant) should have Supply Chain Attack, got: {threats}"
    )


def test_alternate_asset_column_names():
    """Asset rows with non-standard column names should still classify and generate risks."""
    assets = [
        {"hostname": "DB-Prod-01", "device_type": "Database Server",
         "importance": "Critical", "responsible": "DBA Team"},
    ]
    routing, controls, pt, sheets = _make_inputs(asset_rows=assets)
    risks = generate_risks_from_data(routing, controls, pt, all_sheets=sheets)

    assert len(risks) > 0, "Assets with alternate column names should generate risks"
    # The hostname contains 'DB' so should be classified as Database
    db_risks = _find_risks_for(risks, "DB-Prod-01")
    assert len(db_risks) > 0, "DB-Prod-01 should generate database risks"


def test_completely_empty_vendor_row():
    """Rows with all empty fields should not crash the generator."""
    vendors = [
        {},
        {"vendor_name": "", "compliance": "", "service_type": ""},
    ]
    routing, controls, pt, sheets = _make_inputs(vendor_rows=vendors)
    risks = generate_risks_from_data(routing, controls, pt, all_sheets=sheets)
    # Should not crash — may produce "Unknown Vendor" risks at review-pending level
    assert isinstance(risks, list)


def test_missing_compliance_field_entirely():
    """Vendor rows that have NO compliance-related key at all -> review pending."""
    vendors = [
        {"vendor_name": "NoCompField", "service_type": "Cloud"},
    ]
    routing, controls, pt, sheets = _make_inputs(vendor_rows=vendors)
    risks = generate_risks_from_data(routing, controls, pt, all_sheets=sheets)
    v_risks = _find_risks_for(risks, "NoCompField")

    assert len(v_risks) > 0, "Vendor with no compliance field should still get a risk"
    assert v_risks[0]["threat"] == "Compliance Gap", "Missing compliance -> Compliance Gap"


# ===================================================================
# 4. FRAMEWORK-AWARE CONTROL WORDING
# ===================================================================

def test_framework_aware_control_iso():
    """ISO 27001 framework should produce ISO-specific control references."""
    assets = [
        {"asset_name": "Server-01", "asset_type": "Server",
         "criticality": "High", "owner": "IT Ops"},
    ]
    routing, controls, pt, sheets = _make_inputs(asset_rows=assets)
    risks = generate_risks_from_data(
        routing, controls, pt, all_sheets=sheets, framework_id="iso27001"
    )
    # At least one risk control should reference ISO 27001
    controls_text = " ".join(r.get("control", "") for r in risks)
    assert "ISO 27001" in controls_text, (
        f"ISO framework should produce ISO-referenced controls"
    )


def test_framework_aware_control_hipaa():
    """HIPAA framework should produce HIPAA-specific control references."""
    assets = [
        {"asset_name": "Server-01", "asset_type": "Server",
         "criticality": "High", "owner": "IT Ops"},
    ]
    routing, controls, pt, sheets = _make_inputs(asset_rows=assets)
    risks = generate_risks_from_data(
        routing, controls, pt, all_sheets=sheets, framework_id="hipaa"
    )
    controls_text = " ".join(r.get("control", "") for r in risks)
    assert "HIPAA" in controls_text, "HIPAA framework should produce HIPAA-referenced controls"


# ===================================================================
# 5. SCORING INTEGRITY
# ===================================================================

def test_scoring_unchanged():
    """Likelihood, impact, risk_level calculations must be consistent."""
    vendors = [
        {"vendor_name": "SecurePay", "compliance": "Non-Compliant",
         "risk_level": "High", "service_type": "Payment Processing"},
    ]
    routing, controls, pt, sheets = _make_inputs(vendor_rows=vendors)
    risks = generate_risks_from_data(routing, controls, pt, all_sheets=sheets)

    for r in risks:
        lh = r["likelihood"]
        imp = r["impact"]
        score = lh * imp
        expected = (
            "Critical" if score >= 16 else
            "High" if score >= 10 else
            "Medium" if score >= 5 else
            "Low"
        )
        assert r["risk_level"] == expected, (
            f"Risk {r['risk_id']}: {lh}x{imp}={score} should be {expected}, got {r['risk_level']}"
        )


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
