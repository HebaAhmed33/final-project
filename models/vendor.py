class Vendor:
    def __init__(self, id: str, name: str, criticality: str, has_iso_cert: bool, contract_start: str, contract_end: str):
        self.id = id
        self.name = name
        self.criticality = criticality
        self.has_iso_cert = has_iso_cert
        self.contract_start = contract_start
        self.contract_end = contract_end
