"""
Technical Risk Engine.
Generates risk entries from failed configuration checks.
"""


def _classify_level(score: int) -> str:
    """Return risk level based on score."""
    if score >= 9:
        return "high"
    if score >= 4:
        return "medium"
    return "low"


def create_technical_risks(evaluation_results: list) -> list:
    """
    Generate a risk entry for each failed evaluation check.

    Parameters
    ----------
    evaluation_results : list
        Output from config_analysis_runner.run_config_analysis().

    Returns
    -------
    list
        List of technical risk dictionaries.
    """
    risks = []
    for r in evaluation_results:
        if r["status"] != "fail":
            continue
        likelihood = 3
        impact = 3
        score = likelihood * impact
        risks.append({
            "id": r["control_id"],
            "name": r["control_name"],
            "likelihood": likelihood,
            "impact": impact,
            "score": score,
            "level": _classify_level(score),
        })
    return risks


if __name__ == "__main__":
    import json

    sample_results = [
        {"control_id": "CFG-001", "control_name": "Firewall Rules", "status": "pass", "expected": True, "actual": True},
        {"control_id": "CFG-003", "control_name": "Backup Configuration", "status": "fail", "expected": True, "actual": False},
        {"control_id": "CFG-004", "control_name": "Network Segmentation", "status": "fail", "expected": True, "actual": False},
    ]
    print(json.dumps(create_technical_risks(sample_results), indent=2))
