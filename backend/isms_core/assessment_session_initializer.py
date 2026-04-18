from datetime import datetime, timezone


def initialize_session(company, selected_standard_ids):
    return {
        "company_id": company["id"],
        "company_name": company["name"],
        "organization_type": company["organization_type"],
        "selected_standard_ids": selected_standard_ids,
        "created_at": datetime.now(timezone.utc).isoformat()
    }


if __name__ == "__main__":
    import json
    company = {"id": "C001", "name": "Acme Corp", "organization_type": "bank", "sector": "Finance", "country": "SA"}
    selected = ["iso27001", "pci_dss", "sama"]
    print(json.dumps(initialize_session(company, selected), indent=2))
