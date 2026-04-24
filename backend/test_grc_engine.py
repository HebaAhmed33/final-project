"""
End-to-end test: verify GRC intelligence engine produces non-zero scores
when real company data (no controls) is uploaded.
"""
import json
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from services.framework_aware_builder import build_framework_aware_assessment

# Simulate routing results from uploaded company data (NO controls sheet)
mock_routing = {
    "run_id": "test-001",
    "timestamp": "2026-04-23T00:00:00Z",
    "total_sheets": 6,
    "controls_found": False,
    "no_controls_detected": True,
    "has_assets": True,
    "has_vendors": True,
    "has_risks": True,
    "has_employees": True,
    "has_governance": True,
    "has_network_rules": True,
    "routing_results": [
        {
            "source_type": "assets",
            "source_sheet": "Assets",
            "total_records": 15,
            "by_criticality": {"high": 3, "medium": 7, "low": 5},
            "unowned_assets": 2,
            "findings": ["2 of 15 assets have no assigned owner."],
        },
        {
            "source_type": "employees",
            "source_sheet": "Employees",
            "total_records": 20,
            "no_security_training": 5,
            "privileged_access_count": 3,
            "findings": ["5 employees have no recorded security training."],
        },
        {
            "source_type": "vendors",
            "source_sheet": "Vendors",
            "total_records": 8,
            "by_risk": {"high": 2, "medium": 4, "low": 2},
            "high_risk_vendors": ["CloudHost Inc", "DataPipe Ltd"],
            "no_compliance_count": 3,
            "findings": ["2 high-risk vendors detected."],
        },
        {
            "source_type": "network_rules",
            "source_sheet": "Network Rules",
            "total_records": 12,
            "risky_rules_count": 3,
            "risky_rules": ["Allow Any SSH", "Allow Any RDP", "Open HTTP"],
            "deny_rules_count": 2,
            "findings": ["3 rules use ANY/wildcard."],
        },
        {
            "source_type": "governance",
            "source_sheet": "Governance",
            "total_records": 6,
            "by_status": {"completed": 3, "pending": 2, "overdue": 1},
            "no_responsible_count": 1,
            "findings": ["1 governance activity has no responsible party."],
            "rows": [
                {"activity": "Security Review", "responsible": "CISO", "frequency": "Quarterly", "status": "completed"},
                {"activity": "Risk Assessment", "responsible": "Risk Manager", "frequency": "Annual", "status": "pending"},
            ],
        },
        {
            "source_type": "risk_register",
            "source_sheet": "Risks",
            "total_records": 5,
            "by_level": {"high": 2, "medium": 2, "low": 1},
            "untreated_risks": ["Data Breach Risk"],
            "findings": ["2 high risks identified."],
        },
    ],
    "summary": {"total_records": 66},
    "detection_summary": [],
    "warnings": [],
}

# Mock all_sheets for vendor checklist, training matrix, governance calendar
mock_all_sheets = [
    {
        "type": "vendors",
        "rows": [
            {"vendor_name": "CloudHost Inc", "service_type": "Cloud Hosting", "risk_level": "High", "compliance": ""},
            {"vendor_name": "DataPipe Ltd", "service_type": "Data Processing", "risk_level": "High", "compliance": "SOC2"},
        ],
    },
    {
        "type": "employees",
        "rows": [
            {"name": "Alice", "role": "Admin", "training": "Completed", "access_level": "Admin"},
            {"name": "Bob", "role": "Developer", "training": "None", "access_level": "Standard"},
        ],
    },
    {
        "type": "governance",
        "rows": [
            {"activity": "Security Review", "responsible": "CISO", "frequency": "Quarterly", "status": "completed"},
            {"activity": "Risk Assessment", "responsible": "Risk Manager", "frequency": "Annual", "status": "pending"},
        ],
    },
]

result = build_framework_aware_assessment(
    framework_id="iso27001",
    routing=mock_routing,
    uploaded_controls=[],  # NO controls
    assessment_name="GRC Intelligence Test",
    all_sheets=mock_all_sheets,
)

print("=" * 60)
print("GRC INTELLIGENCE ENGINE TEST RESULTS")
print("=" * 60)
print(f"Success:            {result['success']}")
print(f"Mode:               {result['mode_label']}")
print(f"Framework:          {result['framework']}")
print(f"")
print(f"COMPLIANCE SCORE:   {result['compliance_score']}%")
print(f"  Compliant:        {result['compliant_controls']}")
print(f"  Partial:          {result['partial_controls']}")
print(f"  Missing:          {result['missing_controls']}")
print(f"  Total controls:   {result['total_controls']}")
print(f"")
print(f"RISK REGISTER:")
rr = result.get("risk_register", {})
print(f"  Total risks:      {rr.get('total_risks', 0)}")
print(f"  High risks:       {rr.get('high_risks', 0)}")
print(f"  Generated:        {rr.get('generated_risks', 0)}")
print(f"")
print(f"TREATMENT PLAN:")
tp = result.get("treatment_plan", {})
print(f"  Total actions:    {tp.get('total_actions', 0)}")
print(f"")
print(f"SOA entries:        {result.get('soa', {}).get('total_controls', 0)}")
print(f"Compliance matrix:  {len(result.get('compliance_matrix', []))} entries")
print(f"Vendor checklist:   {len(result.get('vendor_checklist', []))} entries")
print(f"Training matrix:    {len(result.get('training_matrix', []))} entries")
print(f"Gov calendar:       {len(result.get('governance_calendar', []))} entries")
print(f"")
print(f"INSIGHTS:")
for i, insight in enumerate(result.get("insights", []), 1):
    print(f"  {i}. {insight}")
print(f"")

# Verify key assertions
score = result["compliance_score"]
assert score > 0, f"FAIL: Score is {score}%, expected > 0%"
assert result["compliant_controls"] > 0 or result["partial_controls"] > 0, "FAIL: No compliant or partial controls"
assert result.get("compliance_matrix"), "FAIL: No compliance matrix"
assert rr.get("total_risks", 0) > 0, "FAIL: No risks generated"
assert tp.get("total_actions", 0) > 0, "FAIL: No treatment actions"
assert result.get("soa", {}).get("total_controls", 0) > 0, "FAIL: No SOA entries"

print("=" * 60)
print("ALL ASSERTIONS PASSED")
print(f"Score: {score}% (was 0% before fix)")
print("=" * 60)
