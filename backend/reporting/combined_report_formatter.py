"""
Combined Executive Report Formatter.
Formats the unified combined output into a structured report dictionary.
"""


def format_combined_report(combined_output: dict) -> dict:
    """
    Format combined output into a unified executive report dictionary.

    Parameters
    ----------
    combined_output : dict
        Output from full_combined_runner.run_full_combined_analysis().

    Returns
    -------
    dict
        Structured report dictionary ready for PDF generation or display.
    """
    assessment = combined_output["assessment"]
    technical = combined_output["technical_analysis"]

    summary = assessment["assessment_summary"]
    risk_register = assessment["risk_register"]
    treatment_plan = assessment["treatment_plan"]
    tech_summary = technical["findings"]["summary"]

    return {
        "title": "SmartISMS Combined Assessment Report",
        "executive_summary": {
            "compliance_percentage": summary["compliance_percentage"],
            "total_controls": summary["total_controls"],
            "passed_controls": summary["passed_controls"],
            "failed_controls": summary["failed_controls"],
            "total_risks": risk_register["total_risks"],
            "high_risks": risk_register["high_risks"],
            "medium_risks": risk_register["medium_risks"],
            "low_risks": risk_register["low_risks"],
            "total_actions": treatment_plan["total_actions"],
            "technical_total_checks": tech_summary["total_checks"],
            "technical_passed_checks": tech_summary["passed_checks"],
            "technical_failed_checks": tech_summary["failed_checks"],
            "technical_total_risks": len(technical["risks"]),
        },
        "top_risks": risk_register["top_risks"],
        "controls_overview": assessment["controls"],
        "treatment_actions": treatment_plan["actions"],
        "technical_findings": technical["findings"]["findings"],
        "technical_risks": technical["risks"],
    }


if __name__ == "__main__":
    import json

    combined_output = {
        "assessment": {
            "assessment_summary": {
                "total_controls": 5, "passed_controls": 3,
                "failed_controls": 2, "compliance_percentage": 60.0,
            },
            "controls": [
                {"id": "ISO-0501", "name": "Information Security Policy", "status": "pass"},
                {"id": "ISO-0801", "name": "Asset Management", "status": "fail"},
            ],
            "risk_register": {
                "total_risks": 1, "high_risks": 1, "medium_risks": 0, "low_risks": 0,
                "top_risks": [{"id": "ISO-0801", "name": "Asset Management", "score": 9, "level": "high"}],
                "all_risks": [],
            },
            "heatmap": {"grid": []},
            "treatment_plan": {
                "total_actions": 1,
                "actions": [{"risk_id": "ISO-0801", "risk_name": "Asset Management", "priority": "high", "action": "Immediate mitigation required", "timeline": "30 days"}],
            },
        },
        "technical_analysis": {
            "findings": {
                "summary": {"total_checks": 5, "passed_checks": 2, "failed_checks": 3},
                "findings": [
                    {"id": "CFG-001", "name": "Firewall Rules", "status": "pass", "expected": True, "actual": True},
                    {"id": "CFG-003", "name": "Backup Configuration", "status": "fail", "expected": True, "actual": False},
                ],
            },
            "risks": [
                {"id": "CFG-003", "name": "Backup Configuration", "likelihood": 3, "impact": 3, "score": 9, "level": "high"},
            ],
        },
    }

    print(json.dumps(format_combined_report(combined_output), indent=2))
