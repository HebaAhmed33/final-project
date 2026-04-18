"""
Combined Output Builder.
Merges assessment output and technical analysis into a single unified dictionary.
"""


def build_combined_output(assessment_output: dict, technical_findings: dict, technical_risks: list) -> dict:
    """
    Build a unified output combining assessment and technical analysis results.

    Parameters
    ----------
    assessment_output : dict
        Output from the assessment pipeline.
    technical_findings : dict
        Output from technical_findings_formatter.format_technical_findings().
    technical_risks : list
        Output from technical_risk_engine.create_technical_risks().

    Returns
    -------
    dict
        Unified dictionary with 'assessment' and 'technical_analysis' keys.
    """
    return {
        "assessment": assessment_output,
        "technical_analysis": {
            "findings": technical_findings,
            "risks": technical_risks,
        },
    }


if __name__ == "__main__":
    import json

    assessment = {
        "assessment_summary": {"total_controls": 5, "passed_controls": 3, "failed_controls": 2, "compliance_percentage": 60.0}
    }
    findings = {
        "summary": {"total_checks": 5, "passed_checks": 2, "failed_checks": 3},
        "findings": [{"id": "CFG-001", "name": "Firewall Rules", "status": "pass", "expected": True, "actual": True}],
    }
    risks = [
        {"id": "CFG-003", "name": "Backup Configuration", "likelihood": 3, "impact": 3, "score": 9, "level": "high"}
    ]

    print(json.dumps(build_combined_output(assessment, findings, risks), indent=2))
