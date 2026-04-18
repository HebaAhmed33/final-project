def build_output(formatted_results, risk_register, heatmap, treatment_plan):
    return {
        "assessment_summary": formatted_results["summary"],
        "controls": formatted_results["controls"],
        "risk_register": risk_register,
        "heatmap": heatmap,
        "treatment_plan": treatment_plan
    }


if __name__ == "__main__":
    import json
    formatted_results = {
        "summary": {"total_controls": 2, "passed_controls": 1, "failed_controls": 1, "compliance_percentage": 50.0},
        "controls": [
            {"id": "ISO-0501", "name": "Information Security Policy", "status": "pass", "expected": True, "actual": True},
            {"id": "ISO-0801", "name": "Asset Management", "status": "fail", "expected": True, "actual": False}
        ]
    }
    risk_register = {"total_risks": 1, "high_risks": 1, "medium_risks": 0, "low_risks": 0, "top_risks": [], "all_risks": []}
    heatmap = {"grid": []}
    treatment_plan = {"total_actions": 1, "actions": []}
    print(json.dumps(build_output(formatted_results, risk_register, heatmap, treatment_plan), indent=2))
