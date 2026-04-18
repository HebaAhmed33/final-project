def format_executive_report(assessment_output):
    summary = assessment_output["assessment_summary"]
    risk_register = assessment_output["risk_register"]
    treatment_plan = assessment_output["treatment_plan"]

    return {
        "title": "SmartISMS Assessment Report",
        "executive_summary": {
            "compliance_percentage": summary["compliance_percentage"],
            "total_controls": summary["total_controls"],
            "passed_controls": summary["passed_controls"],
            "failed_controls": summary["failed_controls"],
            "total_risks": risk_register["total_risks"],
            "high_risks": risk_register["high_risks"],
            "medium_risks": risk_register["medium_risks"],
            "low_risks": risk_register["low_risks"],
            "total_actions": treatment_plan["total_actions"]
        },
        "top_risks": risk_register["top_risks"],
        "controls_overview": assessment_output["controls"],
        "treatment_actions": treatment_plan["actions"]
    }


if __name__ == "__main__":
    import json
    assessment_output = {
        "assessment_summary": {
            "total_controls": 5, "passed_controls": 3, "failed_controls": 2, "compliance_percentage": 60.0
        },
        "controls": [
            {"id": "ISO-0501", "name": "Information Security Policy", "status": "pass", "expected": True, "actual": True}
        ],
        "risk_register": {
            "total_risks": 2, "high_risks": 2, "medium_risks": 0, "low_risks": 0,
            "top_risks": [{"id": "ISO-0801", "name": "Asset Management", "score": 9, "level": "high"}],
            "all_risks": []
        },
        "heatmap": {"grid": []},
        "treatment_plan": {
            "total_actions": 2,
            "actions": [{"risk_id": "ISO-0801", "risk_name": "Asset Management", "priority": "high", "action": "Immediate mitigation required", "timeline": "30 days", "owner": "Security Team"}]
        }
    }
    print(json.dumps(format_executive_report(assessment_output), indent=2))
