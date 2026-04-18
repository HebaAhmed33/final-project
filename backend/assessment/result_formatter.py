def format_results(evaluation_results, compliance_result):
    controls = []
    for r in evaluation_results:
        controls.append({
            "id": r["control_id"],
            "name": r["control_name"],
            "status": r["status"],
            "expected": r["expected"],
            "actual": r["actual"]
        })
    return {
        "summary": compliance_result,
        "controls": controls
    }


if __name__ == "__main__":
    evaluation_results = [
        {"control_id": "ISO-0501", "control_name": "Information Security Policy", "status": "pass", "expected": True, "actual": True},
        {"control_id": "ISO-0801", "control_name": "Asset Management", "status": "fail", "expected": True, "actual": False}
    ]
    compliance_result = {
        "total_controls": 2,
        "passed_controls": 1,
        "failed_controls": 1,
        "compliance_percentage": 50.0
    }
    import json
    print(json.dumps(format_results(evaluation_results, compliance_result), indent=2))
