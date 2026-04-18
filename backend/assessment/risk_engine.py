def create_risks(evaluation_results):
    risks = []
    for r in evaluation_results:
        if r["status"] == "fail":
            likelihood = 3
            impact = 3
            score = likelihood * impact
            if score >= 9:
                level = "high"
            elif score >= 4:
                level = "medium"
            else:
                level = "low"
            risks.append({
                "id": r["control_id"],
                "name": r["control_name"],
                "likelihood": likelihood,
                "impact": impact,
                "score": score,
                "level": level
            })
    return risks


if __name__ == "__main__":
    sample_results = [
        {"control_id": "ISO-0501", "control_name": "Information Security Policy", "status": "pass", "expected": True, "actual": True},
        {"control_id": "ISO-0801", "control_name": "Asset Management", "status": "fail", "expected": True, "actual": False},
        {"control_id": "ISO-1201", "control_name": "Operational Security Procedures", "status": "fail", "expected": True, "actual": False}
    ]
    print(create_risks(sample_results))
