"""
Validate the upload endpoint by sending the test workbook
exactly as the frontend does.
"""
import requests
import json

WORKBOOK = r"c:\new project\backend\test_grc_company_data.xlsx"

with open(WORKBOOK, "rb") as f:
    resp = requests.post(
        "http://localhost:8000/upload/assessment",
        files={
            "file": (
                "test_grc_company_data.xlsx",
                f,
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        },
        data={
            "assessment_name": "Q3 GRC Validation Test",
            "framework": "ISO 27001",
            "scope": "",
            "priority": "Medium",
            "notes": "",
        },
    )

data = resp.json()

print("=" * 60)
print("UPLOAD RESPONSE")
print("=" * 60)
print("HTTP Status:", resp.status_code)
print("Success:", data.get("success"))
print("Message:", data.get("message"))
print("Framework:", data.get("framework"))
print("Imported Count:", data.get("imported_count"))
print("Detected Sheets:", data.get("detected_sheets"))
print("Compliance Score:", data.get("compliance_score"))
print("Generated Modules:", data.get("generated_modules"))
print()

fa = data.get("framework_assessment", {})
print("=" * 60)
print("FRAMEWORK ASSESSMENT")
print("=" * 60)
print("Compliance Score:", fa.get("compliance_score"))
print("Total Controls:", fa.get("total_controls"))
print("Compliant:", fa.get("compliant_controls"))
print("Partial:", fa.get("partial_controls"))
print("Missing:", fa.get("missing_controls"))
print("Mode:", fa.get("mode_label"))
print()

rr = fa.get("risk_register", {})
print("=" * 60)
print("RISK REGISTER")
print("=" * 60)
print("Total Risks:", rr.get("total_risks"))
print("High Risks:", rr.get("high_risks"))
print("Generated Risks:", rr.get("generated_risks"))
print("Uploaded Risks:", rr.get("uploaded_risks"))
print()

tp = fa.get("treatment_plan", {})
print("=" * 60)
print("TREATMENT PLAN")
print("=" * 60)
print("Total Actions:", tp.get("total_actions"))
if tp.get("actions"):
    for a in tp["actions"][:5]:
        print("  - [{}] {} -> {}".format(a.get("priority"), a.get("risk_name"), a.get("timeline")))
print()

soa = fa.get("soa", {})
print("=" * 60)
print("SOA (Statement of Applicability)")
print("=" * 60)
print("Total Controls:", soa.get("total_controls"))
print("Applicable:", soa.get("applicable_count"))
print()

cm = fa.get("compliance_matrix", [])
print("=" * 60)
print("COMPLIANCE MATRIX: {} entries".format(len(cm)))
print("=" * 60)
if cm:
    for entry in cm[:5]:
        print("  {}: {} - {}".format(entry.get("requirement_id"), entry.get("status"), entry.get("gap", "")))
print()

vc = fa.get("vendor_checklist", [])
print("=" * 60)
print("VENDOR CHECKLIST: {} entries".format(len(vc)))
print("=" * 60)
if vc:
    for v in vc[:5]:
        print("  {}: {} - {}".format(v.get("vendor_name"), v.get("risk_level"), v.get("compliance_status")))
print()

tm = fa.get("training_matrix", [])
print("=" * 60)
print("TRAINING MATRIX: {} entries".format(len(tm)))
print("=" * 60)
if tm:
    for t in tm[:5]:
        print("  {}: {} - {}".format(t.get("employee"), t.get("training_status"), t.get("required_modules")))
print()

gc = fa.get("governance_calendar", [])
print("=" * 60)
print("GOVERNANCE CALENDAR: {} entries".format(len(gc)))
print("=" * 60)
if gc:
    for g in gc[:5]:
        print("  {}: {} - {} - {}".format(g.get("activity"), g.get("cadence"), g.get("responsible"), g.get("status")))
print()

ds = data.get("detection_summary", [])
print("=" * 60)
print("DETECTION SUMMARY")
print("=" * 60)
for d in ds:
    print("  " + d)
print()

# Sections summary
sections = fa.get("sections", [])
print("=" * 60)
print("SECTION PERFORMANCE: {} sections".format(len(sections)))
print("=" * 60)
for s in sections:
    print("  {} {}: score={}, pass={}, partial={}, missing={}".format(
        s.get("section_key", ""),
        s.get("section_name", ""),
        s.get("compliance_score", 0),
        s.get("compliant_controls", 0),
        s.get("partial_controls", 0),
        s.get("missing_controls", 0),
    ))
