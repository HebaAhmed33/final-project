def format_risk_register(risks):
    sorted_risks = sorted(risks, key=lambda r: r["score"], reverse=True)
    high = sum(1 for r in risks if r["level"] == "high")
    medium = sum(1 for r in risks if r["level"] == "medium")
    low = sum(1 for r in risks if r["level"] == "low")
    top_risks = [
        {"id": r["id"], "name": r["name"], "score": r["score"], "level": r["level"]}
        for r in sorted_risks[:5]
    ]
    return {
        "total_risks": len(risks),
        "high_risks": high,
        "medium_risks": medium,
        "low_risks": low,
        "top_risks": top_risks,
        "all_risks": sorted_risks
    }


if __name__ == "__main__":
    import json
    sample_risks = [
        {"id": "ISO-0801", "name": "Asset Management", "likelihood": 3, "impact": 3, "score": 9, "level": "high"},
        {"id": "ISO-1201", "name": "Operational Security Procedures", "likelihood": 3, "impact": 3, "score": 9, "level": "high"}
    ]
    print(json.dumps(format_risk_register(sample_risks), indent=2))
