def recommend_standards(organization_type, available_standards):
    if organization_type not in ("bank", "hospital", "company"):
        return []
    return [
        s["id"] for s in available_standards
        if organization_type in s["applicable_organization_types"]
    ]


if __name__ == "__main__":
    available_standards = [
        {"id": "iso27001", "name": "ISO 27001", "applicable_organization_types": ["bank", "hospital", "company"]},
        {"id": "pci_dss", "name": "PCI DSS", "applicable_organization_types": ["bank"]},
        {"id": "hipaa", "name": "HIPAA", "applicable_organization_types": ["hospital"]},
        {"id": "sama", "name": "SAMA", "applicable_organization_types": ["bank"]}
    ]
    print(recommend_standards("bank", available_standards))
    print(recommend_standards("hospital", available_standards))
    print(recommend_standards("company", available_standards))
    print(recommend_standards("unknown", available_standards))
