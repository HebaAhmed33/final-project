def generate_treatment_plan(risks):
    actions = []
    for risk in risks:
        level = risk["level"]

        if level == "high":
            priority = "high"
            timeline = "30 days"
            action = "Immediate mitigation required"
        elif level == "medium":
            priority = "medium"
            timeline = "60 days"
            action = "Mitigation recommended"
        else:
            priority = "low"
            timeline = "90 days"
            action = "Monitor and improve control"

        actions.append({
            "risk_id": risk["id"],
            "risk_name": risk["name"],
            "priority": priority,
            "action": action,
            "timeline": timeline,
            "owner": "Security Team"
        })

    return {
        "total_actions": len(actions),
        "actions": actions
    }


if __name__ == "__main__":
    import json
    sample_risks = [
        {"id": "ISO-0801", "name": "Asset Management", "likelihood": 3, "impact": 3, "score": 9, "level": "high"},
        {"id": "ISO-1201", "name": "Operational Security Procedures", "likelihood": 3, "impact": 3, "score": 9, "level": "high"}
    ]
    print(json.dumps(generate_treatment_plan(sample_risks), indent=2))
