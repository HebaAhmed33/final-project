class Asset:
    def __init__(self, id: str, name: str, type: str, ip: str, owner: str, criticality: str):
        self.id = id
        self.name = name
        self.type = type
        self.ip = ip
        self.owner = owner
        self.criticality = criticality
