import json


def load_controls(standard_file):
    with open(standard_file, "r") as f:
        return json.load(f)


def evaluate(input_data, standard_file):
    controls = load_controls(standard_file)
    results = []
    for control in controls:
        check_key = control["check_key"]
        expected = control["expected"]
        actual = input_data.get(check_key)
        status = "pass" if actual == expected else "fail"
        results.append({
            "control_id": control["id"],
            "control_name": control["name"],
            "status": status,
            "expected": expected,
            "actual": actual
        })
    return results


if __name__ == "__main__":
    input_data = {
        "security_policy_exists": True,
        "security_organization_defined": True,
        "asset_inventory_maintained": False,
        "access_control_policy_exists": True,
        "operational_procedures_documented": False
    }
    # NOTE: ISO 27001 now uses grouped controls via framework_loader.
    # This demo uses nist.json as a flat-file example.
    results = evaluate(input_data, "backend/standards/nist.json")
    for r in results:
        print(f"{r['control_id']} | {r['control_name']} | {r['status']}")
