def generate_heatmap(risks):
    grid = {}
    for l in range(1, 6):
        for i in range(1, 6):
            grid[(l, i)] = 0

    for risk in risks:
        key = (risk["likelihood"], risk["impact"])
        if key in grid:
            grid[key] += 1

    result = []
    for l in range(1, 6):
        for i in range(1, 6):
            result.append({
                "likelihood": l,
                "impact": i,
                "count": grid[(l, i)]
            })

    return {"grid": result}


if __name__ == "__main__":
    import json
    sample_risks = [
        {"id": "ISO-0801", "name": "Asset Management", "likelihood": 3, "impact": 3, "score": 9, "level": "high"},
        {"id": "ISO-1201", "name": "Operational Security Procedures", "likelihood": 3, "impact": 3, "score": 9, "level": "high"}
    ]
    print(json.dumps(generate_heatmap(sample_risks), indent=2))
