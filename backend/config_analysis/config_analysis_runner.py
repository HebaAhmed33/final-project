"""
Configuration Analysis Runner.
Maps raw config data and evaluates it against a configuration baseline standard.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config_analysis.config_input_mapper import map_config_input
from isms_core.rule_engine import evaluate


def run_config_analysis(raw_config_data: dict, standard_file: str) -> list:
    """
    Run a configuration analysis against a baseline standard.

    Parameters
    ----------
    raw_config_data : dict
        Raw configuration key-value pairs.
    standard_file : str
        Path to the configuration baseline JSON standard.

    Returns
    -------
    list
        Evaluation results from the rule engine.
    """
    normalized = map_config_input(raw_config_data)
    results = evaluate(normalized, standard_file)
    return results


if __name__ == "__main__":
    import json

    raw = {
        "firewall_rules_defined": True,
        "logging_enabled": True,
        "backup_configured": False,
    }
    standard = os.path.join(os.path.dirname(__file__), "..", "standards", "config_baseline.json")
    results = run_config_analysis(raw, standard)
    print(json.dumps(results, indent=2))
