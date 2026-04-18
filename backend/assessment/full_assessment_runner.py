import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from assessment.input_mapper import map_input
from isms_core.rule_engine import evaluate
from isms_core.compliance_calculator import calculate_compliance
from assessment.result_formatter import format_results
from assessment.risk_engine import create_risks
from assessment.risk_register_formatter import format_risk_register
from assessment.heatmap_generator import generate_heatmap
from assessment.treatment_plan_generator import generate_treatment_plan
from assessment.assessment_output_builder import build_output


def run_full_assessment(raw_data, standard_file):
    input_data = map_input(raw_data)
    evaluation_results = evaluate(input_data, standard_file)
    compliance_result = calculate_compliance(evaluation_results)
    formatted_results = format_results(evaluation_results, compliance_result)
    risks = create_risks(evaluation_results)
    risk_register = format_risk_register(risks)
    heatmap = generate_heatmap(risks)
    treatment_plan = generate_treatment_plan(risks)
    return build_output(formatted_results, risk_register, heatmap, treatment_plan)


if __name__ == "__main__":
    import json
    raw_data = {
        "has_security_policy": True,
        "has_security_organization": True,
        "assets_defined": False,
        "has_access_policy": True,
        "has_operational_procedures": False
    }
    # NOTE: ISO 27001 now uses grouped controls via framework_loader.
    standard_file = os.path.join(os.path.dirname(__file__), "..", "standards", "pci_dss.json")
    result = run_full_assessment(raw_data, standard_file)
    print(json.dumps(result, indent=2))
