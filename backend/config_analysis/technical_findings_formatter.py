"""
Technical Findings Formatter.
Formats raw evaluation results into a structured summary and findings report.
"""


def format_technical_findings(evaluation_results: list) -> dict:
    """
    Format evaluation results into a summary and findings dictionary.

    Parameters
    ----------
    evaluation_results : list
        Output from config_analysis_runner.run_config_analysis().

    Returns
    -------
    dict
        Dictionary with 'summary' and 'findings' keys.
    """
    passed = sum(1 for r in evaluation_results if r["status"] == "pass")
    failed = sum(1 for r in evaluation_results if r["status"] == "fail")

    findings = [
        {
            "id": r["control_id"],
            "name": r["control_name"],
            "status": r["status"],
            "expected": r["expected"],
            "actual": r["actual"],
        }
        for r in evaluation_results
    ]

    return {
        "summary": {
            "total_checks": len(evaluation_results),
            "passed_checks": passed,
            "failed_checks": failed,
        },
        "findings": findings,
    }


if __name__ == "__main__":
    import json

    sample_results = [
        {"control_id": "CFG-001", "control_name": "Firewall Rules", "status": "pass", "expected": True, "actual": True},
        {"control_id": "CFG-002", "control_name": "System Logging", "status": "pass", "expected": True, "actual": True},
        {"control_id": "CFG-003", "control_name": "Backup Configuration", "status": "fail", "expected": True, "actual": False},
        {"control_id": "CFG-004", "control_name": "Network Segmentation", "status": "fail", "expected": True, "actual": False},
        {"control_id": "CFG-005", "control_name": "Remote Access Restriction", "status": "fail", "expected": True, "actual": False},
    ]
    print(json.dumps(format_technical_findings(sample_results), indent=2))
