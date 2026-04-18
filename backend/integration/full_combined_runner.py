"""
Full Combined Analysis Runner.
Orchestrates the assessment pipeline and config analysis into a unified result.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from assessment.full_assessment_runner import run_full_assessment
from config_analysis.config_input_mapper import map_config_input
from isms_core.rule_engine import evaluate
from config_analysis.technical_findings_formatter import format_technical_findings
from config_analysis.technical_risk_engine import create_technical_risks
from integration.combined_output_builder import build_combined_output


def run_full_combined_analysis(raw_data: dict, raw_config_data: dict,
                               standard_file: str, config_standard_file: str) -> dict:
    """
    Run both the assessment and config analysis pipelines, then combine results.

    Parameters
    ----------
    raw_data : dict
        Raw input for the compliance assessment.
    raw_config_data : dict
        Raw configuration key-value pairs.
    standard_file : str
        Path to the compliance standard JSON (e.g. pci_dss.json).
    config_standard_file : str
        Path to the config baseline JSON (e.g. config_baseline.json).

    Returns
    -------
    dict
        Unified output from build_combined_output.
    """
    # 1. Run assessment
    assessment_output = run_full_assessment(raw_data, standard_file)

    # 2. Run config analysis
    normalized_config = map_config_input(raw_config_data)
    config_results = evaluate(normalized_config, config_standard_file)
    technical_findings = format_technical_findings(config_results)
    technical_risks = create_technical_risks(config_results)

    # 3. Combine
    return build_combined_output(assessment_output, technical_findings, technical_risks)


if __name__ == "__main__":
    import json

    raw_data = {
        "has_security_policy": True,
        "has_security_organization": True,
        "assets_defined": False,
        "has_access_policy": True,
        "has_operational_procedures": False,
    }
    raw_config_data = {
        "firewall_rules_defined": True,
        "logging_enabled": True,
        "backup_configured": False,
    }

    base = os.path.join(os.path.dirname(__file__), "..", "standards")
    # NOTE: ISO 27001 now uses grouped controls via framework_loader.
    standard_file = os.path.join(base, "pci_dss.json")
    config_standard_file = os.path.join(base, "config_baseline.json")

    result = run_full_combined_analysis(raw_data, raw_config_data, standard_file, config_standard_file)
    print(json.dumps(result, indent=2))
