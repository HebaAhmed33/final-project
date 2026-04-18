import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from isms_core.report_history_manager import get_reports, get_latest_report


def summarize_company_reports(company_id):
    reports = get_reports(company_id)
    latest = get_latest_report(company_id)
    if latest:
        created_at = latest.get("created_at", "")
        compliance = latest.get("assessment_output", {}).get("assessment_summary", {}).get("compliance_percentage", 0.0)
    else:
        created_at = ""
        compliance = 0.0
    return {
        "company_id": company_id,
        "total_reports": len(reports),
        "latest_report_created_at": created_at,
        "latest_compliance_percentage": compliance
    }


if __name__ == "__main__":
    import json
    print(json.dumps(summarize_company_reports("C001"), indent=2))
