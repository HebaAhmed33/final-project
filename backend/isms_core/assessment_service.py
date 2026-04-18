import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from assessment.full_assessment_runner import run_full_assessment
from isms_core.report_history_manager import save_report


def run_and_save_assessment(company, raw_data, standard_file):
    assessment_output = run_full_assessment(raw_data, standard_file)
    stored_report = {
        "company_id": company["id"],
        "company_name": company["name"],
        "organization_type": company["organization_type"],
        "standard_file": standard_file,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "assessment_output": assessment_output
    }
    save_report(company["id"], stored_report)
    return stored_report


if __name__ == "__main__":
    import json
    company = {"id": "C001", "name": "Acme Corp", "organization_type": "bank", "sector": "Finance", "country": "SA"}
    raw_data = {
        "has_security_policy": True,
        "has_security_organization": True,
        "assets_defined": False,
        "has_access_policy": True,
        "has_operational_procedures": False
    }
    # NOTE: ISO 27001 now uses grouped controls via framework_loader.
    standard_file = os.path.join(os.path.dirname(__file__), "..", "standards", "pci_dss.json")
    result = run_and_save_assessment(company, raw_data, standard_file)
    print(json.dumps(result, indent=2))
