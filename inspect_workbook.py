"""
Inspect the test workbook to understand actual column names and data.
Run from project root: python inspect_workbook.py
"""
import sys, json
sys.path.insert(0, "backend")
from upload.parsers import parse_all_sheets
from upload.sheet_router import route_sheets

with open("test_iso_evidence.xlsx", "rb") as f:
    contents = f.read()

sheets = parse_all_sheets(contents, "test_iso_evidence.xlsx")
for s in sheets:
    name = s["name"]
    stype = s["type"]
    row_count = s["row_count"]
    print(f"=== Sheet: {name!r}  type={stype}  rows={row_count} ===")
    print(f"  Raw headers       : {s['headers']}")
    print(f"  Normalized headers: {s['normalized_headers']}")
    for i, row in enumerate(s["rows"][:3]):
        print(f"  Row {i}: {json.dumps(row, ensure_ascii=False, default=str)}")
    print()

# Full routing + framework assessment
routing = route_sheets(sheets)
print("=== ROUTING no_controls_detected:", routing["no_controls_detected"])
for r in routing["routing_results"]:
    print(f"  {r['source_sheet']!r}  type={r['source_type']}  records={r['total_records']}")
    if r.get("findings"):
        for f in r["findings"]:
            print(f"    finding: {f}")

print()

# Framework assessment
from services.framework_aware_builder import build_framework_aware_assessment
controls_sheet = next((s for s in sheets if s["type"] == "controls" and s["row_count"] > 0), None)
controls_rows = controls_sheet["rows"] if controls_sheet else []
print(f"Controls rows available: {len(controls_rows)}")
if controls_rows:
    print("  Sample control row:", json.dumps(controls_rows[0], ensure_ascii=False, default=str))

fa = build_framework_aware_assessment(
    framework_id="iso27001",
    routing=routing,
    uploaded_controls=controls_rows,
    assessment_name="Debug Run",
    all_sheets=sheets,
)

print()
print("=== FRAMEWORK ASSESSMENT RESULTS ===")
print(f"  compliance_score : {fa.get('compliance_score')}")
print(f"  total_controls   : {fa.get('total_controls')}")
print(f"  compliant        : {fa.get('compliant_controls')}")
print(f"  partial          : {fa.get('partial_controls')}")
print(f"  missing          : {fa.get('missing_controls')}")
print(f"  no_controls_detected: {fa.get('no_controls_detected')}")
print(f"  evidence_backed  : {fa.get('evidence_backed')}")

print()
print("=== SOA (first 3 entries) ===")
soa = fa.get("soa", {})
for e in soa.get("entries", [])[:3]:
    print(f"  {json.dumps(e, ensure_ascii=False, default=str)}")

print()
print("=== GOVERNANCE CALENDAR (first 3) ===")
gc = fa.get("governance_calendar", [])
for row in gc[:3]:
    print(f"  {json.dumps(row, ensure_ascii=False, default=str)}")

print()
print("=== VENDOR CHECKLIST (first 3) ===")
vc = fa.get("vendor_checklist", [])
for row in vc[:3]:
    print(f"  {json.dumps(row, ensure_ascii=False, default=str)}")
