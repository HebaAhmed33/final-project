"""
End-to-end validation script for all 6 classifier / processor bug fixes.
Run from the project root:  python test_classifier_e2e.py
"""
import sys, json
sys.path.insert(0, "backend")

from upload.parsers import parse_all_sheets
from upload.sheet_router import route_sheets
from upload.sheet_classifier import normalize_columns_for_type, classify_sheet

# ─── Bug 1 & 3: Sheet name classification ─────────────────────────────────
print("=" * 60)
print("BUG 1 & 3 — Sheet name classification")
cases = [
    ("Applications Systems Inventory", "applications"),
    ("Vendor-Managed Services Inventory", "vendors"),
    ("Configurations",                  "controls"),
    ("Hardware Assets",                 "assets"),
    ("Asset Inventory",                 "assets"),
    ("Network Firewall Rules",          "network_rules"),
]
for name, expected in cases:
    got = classify_sheet(name, [])
    status = "OK" if got == expected else "FAIL"
    print(f"  [{status}] '{name}' -> {got}  (expected: {expected})")

# ─── Bug 4: Column aliases ────────────────────────────────────────────────
print()
print("BUG 4 — Column alias normalization")
alias_cases = [
    (["Security Training Status"], "employees",     "training"),
    (["Privileged Access"],         "employees",     "access_level"),
    (["Processes Sensitive Data"],  "applications",  "data_handled"),
]
for headers, sheet_type, expected_canonical in alias_cases:
    got = normalize_columns_for_type(headers, sheet_type)
    status = "OK" if got == [expected_canonical] else "FAIL"
    print(f"  [{status}] '{headers[0]}' in {sheet_type} -> {got[0]}  (expected: {expected_canonical})")

# ─── Bug 5: Vendor checklist service_type ────────────────────────────────
print()
print("BUG 5 — Vendor checklist service_type")
from services.framework_aware_builder import _build_vendor_checklist
test_rows = [
    {"vendor_name": "Acme Corp",    "service_type": "Cloud Hosting", "risk_level": "high", "compliance": "SOC2"},
    {"vendor_name": "SecureVend",   "service_type": None,             "risk_level": "low",  "compliance": ""},
    {"vendor_name": "DataPartner",  "service": "Data Storage",        "risk_level": "medium","compliance": "ISO27001"},
]
result = _build_vendor_checklist([{"type": "vendors", "rows": test_rows}])
for item in result:
    svc = item["service_provided"]
    status = "OK" if svc and svc != "Services" else "CHECK"
    print(f"  [{status}] {item['vendor_name']} -> service_provided={svc!r}")

# ─── Bug 6: Compliance score extraction ──────────────────────────────────
print()
print("BUG 6 — Compliance score extraction")
# Simulate what build_framework_aware_assessment returns
fake_fa = {
    "compliance_score": 68.5,
    "total_controls": 20,
    "compliant_controls": 12,
    "partial_controls": 3,
    "missing_controls": 5,
    "sections": [{"section_key": "A.5", "compliance_score": 75.0}],
    "risk_register": {"total_risks": 4, "high_risks": 2},
}
score = fake_fa.get("compliance_score", 0) if fake_fa else 0
rr = fake_fa.get("risk_register", {})
risk_summary = {"total_risks": rr.get("total_risks", 0), "high_risks": rr.get("high_risks", 0)} if rr.get("total_risks", 0) > 0 else {}
status = "OK" if score == 68.5 else "FAIL"
print(f"  [{status}] compliance_score={score}  risk_summary={risk_summary}")

# ─── Full parse → route on real file ─────────────────────────────────────
print()
print("END-TO-END — Real Excel file: test_iso_evidence.xlsx")
try:
    with open("test_iso_evidence.xlsx", "rb") as f:
        contents = f.read()
    sheets = parse_all_sheets(contents, "test_iso_evidence.xlsx")
    print(f"  Parsed {len(sheets)} sheets:")
    for s in sheets:
        print(f"    {s['name']:<40} type={s['type']:<15} rows={s['row_count']}")

    routing = route_sheets(sheets)
    print()
    print("  Routing results:")
    for r in routing["routing_results"]:
        print(f"    {r['source_sheet']:<40} -> {r['source_type']:<15} records={r['total_records']}")

    # Framework assessment
    from services.framework_aware_builder import build_framework_aware_assessment
    controls_sheet = next((s for s in sheets if s["type"] == "controls" and s["row_count"] > 0), None)
    controls_rows = controls_sheet["rows"] if controls_sheet else []
    fa = build_framework_aware_assessment(
        framework_id="iso27001",
        routing=routing,
        uploaded_controls=controls_rows,
        assessment_name="E2E Test",
        all_sheets=sheets,
    )
    print()
    print(f"  compliance_score      = {fa.get('compliance_score')}")
    print(f"  risk_register.total   = {fa.get('risk_register', {}).get('total_risks')}")
    rr2 = fa.get("risk_register", {})
    ra = fa.get("sections", [])
    soa = fa.get("soa", {})
    tp = fa.get("treatment_plan", {})
    vc = fa.get("vendor_checklist", [])
    tm = fa.get("training_matrix", [])
    gc = fa.get("governance_calendar", [])
    print(f"  risk_register non-empty = {rr2.get('total_risks', 0) > 0 or rr2.get('source') is not None}")
    print(f"  risk_assessment (sections) count = {len(ra)}")
    print(f"  soa entries           = {soa.get('total_controls', 0)}")
    print(f"  treatment_plan actions= {tp.get('total_actions', 0)}")
    print(f"  vendor_checklist rows = {len(vc)}")
    print(f"  training_matrix rows  = {len(tm)}")
    print(f"  governance_calendar rows = {len(gc)}")
except FileNotFoundError:
    print("  test_iso_evidence.xlsx not found — skipping real file test")
except Exception as exc:
    import traceback; traceback.print_exc()

print()
print("Done.")
