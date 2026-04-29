import json
from services.framework_loader import load_framework
from services.framework_aware_builder import build_framework_aware_assessment

routing = {
    "routing_results": [
        {"source_type": "employees", "total_records": 10},
        {"source_type": "assets", "total_records": 10},
        {"source_type": "vendors", "total_records": 10},
        {"source_type": "network_rules", "total_records": 10},
        {"source_type": "governance", "total_records": 10},
        {"source_type": "risk_register", "total_records": 10}
    ]
}

res = build_framework_aware_assessment(
    framework_id="ISO 27001",
    routing=routing,
    uploaded_controls=[],
    assessment_name="Test ISO",
    scope="",
    priority="Medium",
    notes="",
    all_sheets=[]
)

print("Compliance Score:", res.get("compliance_score"))
print("High Risks:", len(res.get("risk_register", [])))
print("Gap Analysis Items:", len(res.get("gap_analysis", [])))
print("Treatment Plan Items:", len(res.get("treatment_plan", [])))
