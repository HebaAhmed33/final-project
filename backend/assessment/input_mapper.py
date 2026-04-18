FIELD_MAP = {
    "has_security_policy": "security_policy_exists",
    "has_security_organization": "security_organization_defined",
    "assets_defined": "asset_inventory_maintained",
    "has_access_policy": "access_control_policy_exists",
    "has_operational_procedures": "operational_procedures_documented"
}


def map_input(raw_data):
    input_data = {}
    for raw_key, normalized_key in FIELD_MAP.items():
        input_data[normalized_key] = raw_data.get(raw_key)
    return input_data


if __name__ == "__main__":
    raw_data = {
        "has_security_policy": True,
        "has_security_organization": True,
        "assets_defined": False,
        "has_access_policy": True,
        "has_operational_procedures": False
    }
    print(map_input(raw_data))
