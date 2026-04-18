"""
Multi-Standard Assessment Runner.
Runs the full assessment pipeline against multiple standards and collects results.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from assessment.full_assessment_runner import run_full_assessment


def run_multi_standard_assessment(raw_data: dict, standard_files: list) -> dict:
    """
    Run the full assessment for each standard file and return collected results.

    Parameters
    ----------
    raw_data : dict
        Raw input for the compliance assessment.
    standard_files : list[str]
        List of paths to standard JSON files.

    Returns
    -------
    dict
        Dictionary with a 'standards' key containing per-standard results.
    """
    standards = []
    for sf in standard_files:
        output = run_full_assessment(raw_data, sf)
        standards.append({
            "standard_file": sf,
            "assessment_output": output,
        })
    return {"standards": standards}


if __name__ == "__main__":
    import json

    raw_data = {
        "has_security_policy": True,
        "has_security_organization": True,
        "assets_defined": False,
        "has_access_policy": True,
        "has_operational_procedures": False,
    }

    base = os.path.join(os.path.dirname(__file__), "..", "standards")
    standard_files = [
        # NOTE: ISO 27001 now uses grouped controls via framework_loader.
        os.path.join(base, "pci_dss.json"),
        os.path.join(base, "nist.json"),
    ]

    result = run_multi_standard_assessment(raw_data, standard_files)
    print(json.dumps(result, indent=2))
