class NetworkRule:
    def __init__(self, id: str, source: str, destination: str, port: int, action: str, service: str):
        self.id = id
        self.source = source
        self.destination = destination
        self.port = port
        self.action = action
        self.service = service
