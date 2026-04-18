class Risk:
    def __init__(self, id: str, name: str, asset_id: str, likelihood: int, impact: int, score: int, level: str, owner: str):
        self.id = id
        self.name = name
        self.asset_id = asset_id
        self.likelihood = likelihood
        self.impact = impact
        self.score = score
        self.level = level
        self.owner = owner
