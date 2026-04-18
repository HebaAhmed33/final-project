import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from assessment.input_mapper import map_input
from isms_core.rule_engine import evaluate


def run_assessment(raw_data, standard_file):
    input_data = map_input(raw_data)
    results = evaluate(input_data, standard_file)
    return results


if __name__ == "__main__":
    raw_data = {
        "has_security_policy": True,
        "has_security_organization": True,
        "assets_defined": False,
        "has_access_policy": True,
        "has_operational_procedures": False
    }
    # NOTE: ISO 27001 now uses grouped controls via framework_loader.
    standard_file = os.path.join(os.path.dirname(__file__), "..", "standards", "pci_dss.json")
    results = run_assessment(raw_data, standard_file)
    for r in results:
        print(f"{r['control_id']} | {r['control_name']} | {r['status']}")
